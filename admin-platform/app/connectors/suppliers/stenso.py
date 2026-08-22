from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from lxml import html

from .contract import CategoryRecord, ProductDetail, ProductSummary, SupplierConnector
from .http_client import ReadOnlyHttpClient


_PRICE_RE = re.compile(r"(?:€|EUR)?\s*\d+(?:[.,]\d{1,2})?\s*(?:€|лв\.?|BGN)?", re.I)
_REF_RE = re.compile(r"(?:Реф\.?|Reference|Код|SKU)\s*:?\s*([A-Z0-9._/-]+)", re.I)


class StensoPublicConnector(SupplierConnector):
    key = "stenso_public"
    read_only = True

    def __init__(
        self,
        *,
        base_url: str,
        catalog_roots: list[dict],
        http_client: ReadOnlyHttpClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        host = urlparse(self.base_url).hostname or "stenso.net"
        self.http = http_client or ReadOnlyHttpClient(allowed_hosts={host, f"www.{host}"})
        self.catalog_roots = list(catalog_roots)

    def health_check(self) -> dict:
        response = self.http.get(self.base_url)
        return {
            "ok": response.status_code == 200,
            "http_status": response.status_code,
            "connector": self.key,
            "read_only": True,
        }

    def list_categories(self) -> list[CategoryRecord]:
        # Catalog roots are Super-Admin source configuration. Operator does not
        # paste URLs. Later connectors may discover a full category tree live.
        result = []
        for item in self.catalog_roots:
            result.append(
                CategoryRecord(
                    key=str(item["key"]),
                    name=str(item["label"]),
                    url=str(item["url"]),
                    product_count=item.get("product_count"),
                    parent_key=item.get("parent_key"),
                )
            )
        return result

    def _category(self, key: str) -> CategoryRecord:
        for category in self.list_categories():
            if category.key == key:
                return category
        raise KeyError(f"Unknown configured supplier category: {key}")

    @staticmethod
    def _text(node) -> str:
        return " ".join(x.strip() for x in node.itertext() if x.strip())

    @staticmethod
    def _normalize_size_label(value: str) -> str | None:
        cleaned = re.sub(r"\s+", " ", (value or "")).strip()
        # Conservative size contract: simple numeric footwear sizes only.
        if re.fullmatch(r"\d{2}(?:[.,]5)?", cleaned):
            return cleaned.replace(",", ".")
        return None

    def _parse_variant_availability(self, tree) -> list[dict]:
        """Parse size/variant availability from semantic HTML state.

        IMPORTANT:
        - Never infer availability from visual color alone.
        - Prefer disabled attribute, aria-disabled, data attributes and
          availability-related classes.
        - Return only clearly identifiable size controls.
        """
        variants: list[dict] = []
        seen: set[str] = set()

        candidates = tree.xpath(
            '//button | //label | //option | //input | '
            '//*[@role="button"] | //*[@data-size] | //*[@data-value]'
        )

        unavailable_tokens = {
            "disabled",
            "unavailable",
            "not-available",
            "not_available",
            "out-of-stock",
            "out_of_stock",
            "sold-out",
            "sold_out",
        }
        available_tokens = {
            "available",
            "in-stock",
            "in_stock",
            "selected",
            "active",
        }

        for node in candidates:
            text_value = self._text(node)
            raw_values = [
                text_value,
                node.get("value") or "",
                node.get("data-size") or "",
                node.get("data-value") or "",
                node.get("title") or "",
                node.get("aria-label") or "",
            ]

            size = None
            for raw in raw_values:
                size = self._normalize_size_label(raw)
                if size:
                    break
            if not size or size in seen:
                continue

            classes = (node.get("class") or "").casefold()
            aria_disabled = (node.get("aria-disabled") or "").strip().casefold()
            disabled_attr = node.get("disabled") is not None
            data_available = (
                node.get("data-available")
                or node.get("data-stock")
                or node.get("data-in-stock")
                or ""
            ).strip().casefold()

            unavailable = (
                disabled_attr
                or aria_disabled == "true"
                or any(token in classes for token in unavailable_tokens)
                or data_available in {"0", "false", "no", "out", "out_of_stock"}
            )

            available = (
                not unavailable
                and (
                    any(token in classes for token in available_tokens)
                    or aria_disabled == "false"
                    or data_available in {"1", "true", "yes", "in", "in_stock"}
                    or node.tag in {"button", "label", "option", "input"}
                )
            )

            status = "OUT_OF_STOCK" if unavailable else ("IN_STOCK" if available else "UNKNOWN")
            variants.append(
                {
                    "type": "SIZE",
                    "value": size,
                    "availability": status,
                    "source_disabled": bool(unavailable),
                }
            )
            seen.add(size)

        return variants

    def list_products(
        self,
        category_key: str,
        *,
        page: int = 1,
        limit: int = 100,
    ) -> list[ProductSummary]:
        category = self._category(category_key)
        url = category.url
        if page > 1:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}page={page}"

        response = self.http.get(url)
        tree = html.fromstring(response.content)
        tree.make_links_absolute(url)

        # Stenso/PrestaShop category pages expose product links containing
        # /produkt/. Use link semantics instead of brittle CSS class names.
        seen = set()
        products: list[ProductSummary] = []

        for anchor in tree.xpath('//a[@href]'):
            href = anchor.get("href") or ""
            if "/produkt/" not in href:
                continue

            normalized = href.split("#", 1)[0]
            if normalized in seen:
                continue

            name = self._text(anchor)
            if len(name) < 8:
                # Prefer enclosing article/div text when anchor itself is image-only.
                parent = anchor.getparent()
                if parent is not None:
                    name = self._text(parent)

            if len(name) < 8:
                continue

            seen.add(normalized)
            # Availability/price may live outside the <a> but inside the
            # surrounding product card/article. Walk up to the nearest semantic
            # product container before extracting commercial text.
            context_node = anchor
            for _ in range(4):
                parent = context_node.getparent()
                if parent is None:
                    break
                context_node = parent
                tag = (context_node.tag or "").lower() if isinstance(context_node.tag, str) else ""
                classes = (context_node.get("class") or "").lower()
                if tag in {"article", "li"} or "product" in classes:
                    break

            context = self._text(context_node) if context_node is not None else name
            price_match = _PRICE_RE.search(context)

            availability = None
            lower = context.casefold()
            if (
                "последна наличност" in lower
                or "last items in stock" in lower
                or "limited stock" in lower
            ):
                availability = "LOW_STOCK"
            elif "изчерпан" in lower or "out of stock" in lower:
                availability = "OUT_OF_STOCK"
            elif "в наличност" in lower or "in stock" in lower:
                availability = "IN_STOCK"

            images = anchor.xpath('.//img/@src | .//img/@data-src | .//img/@data-lazy-src')
            image_url = images[0] if images else None
            if image_url:
                image_url = urljoin(url, image_url)

            products.append(
                ProductSummary(
                    source_key=normalized,
                    name=re.sub(r"\s+", " ", name).strip()[:500],
                    url=normalized,
                    price_text=price_match.group(0).strip() if price_match else None,
                    availability_text=availability,
                    image_url=image_url,
                )
            )
            if len(products) >= limit:
                break

        return products

    def get_product(self, source_key: str) -> ProductDetail:
        url = source_key
        if not url.startswith(("http://", "https://")):
            url = urljoin(self.base_url + "/", source_key.lstrip("/"))

        response = self.http.get(url)
        tree = html.fromstring(response.content)
        tree.make_links_absolute(url)

        h1 = tree.xpath('//h1[1]')
        name = self._text(h1[0]) if h1 else self._text(tree)[:200]

        page_text = self._text(tree)
        ref_match = _REF_RE.search(page_text)
        price_match = _PRICE_RE.search(page_text)

        availability = None
        low = page_text.lower()
        if "последна наличност" in low or "last items in stock" in low:
            availability = "LOW_STOCK"
        elif "изчерпан" in low or "out of stock" in low:
            availability = "OUT_OF_STOCK"
        elif "в наличност" in low or "in stock" in low:
            availability = "IN_STOCK"

        image_urls = []
        for src in tree.xpath('//img/@src | //img/@data-src | //img/@data-lazy-src'):
            absolute = urljoin(url, src)
            if absolute not in image_urls:
                image_urls.append(absolute)

        variants = self._parse_variant_availability(tree)

        if variants:
            statuses = {v["availability"] for v in variants}
            if statuses == {"OUT_OF_STOCK"}:
                availability = "OUT_OF_STOCK"
            elif "IN_STOCK" in statuses and "OUT_OF_STOCK" in statuses:
                availability = "PARTIAL_VARIANT_AVAILABILITY"
            elif "IN_STOCK" in statuses:
                availability = "IN_STOCK"

        # Phase 2 contract deliberately does not invent EAN/MPN values.
        return ProductDetail(
            source_key=url,
            name=re.sub(r"\s+", " ", name).strip(),
            url=url,
            reference=ref_match.group(1) if ref_match else None,
            price_text=price_match.group(0).strip() if price_match else None,
            availability_text=availability,
            images=tuple(image_urls[:20]),
            variants=tuple(variants),
            facts={
                "availability_scope": "VARIANT" if variants else "PRODUCT",
                "variant_count": len(variants),
            },
        )
