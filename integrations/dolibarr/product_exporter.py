from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional
import csv
import json


DOLIBARR_PRODUCT_HEADERS = [
    "№* (p.ref)",
    "Име* (p.label)",
    "Тип* (p.fk_product_type)",
    "За продажба* (p.tosell)",
    "За покупка* (p.tobuy)",
    "Описание (p.description)",
    "Публичен URL (p.url)",
    "Митнически|Стока|ХС код (p.customcode)",
    "Код на държава (p.fk_country)",
    "Счетоводен код (продажба) (p.accountancy_code_sell)",
    "Счетоводен код (вътреобщностна продажба) (p.accountancy_code_sell_intra)",
    "Счетоводен код (експортна продажба) (p.accountancy_code_sell_export)",
    "Счетоводен код (покупка) (p.accountancy_code_buy)",
    "Счетоводен код (вътреобщностна покупка) (p.accountancy_code_buy_intra)",
    "Счетоводен код (импортна покупка) (p.accountancy_code_buy_export)",
    "Бележка (публична) (p.note_public)",
    "Бележка (лична) (p.note)",
    "Weight (p.weight)",
    "Мярка за тегло (p.weight_units)",
    "Length (p.length)",
    "Мярка за дължина (p.length_units)",
    "Width (p.width)",
    "Мярка за ширина (p.width_units)",
    "Height (p.height)",
    "Мярка за височина (p.height_units)",
    "Surface (p.surface)",
    "Мярка за повърхност (p.surface_units)",
    "Volume (p.volume)",
    "Мярка за обем (p.volume_units)",
    "Продължителност (p.duration)",
    "Естество на продукта (суров/произведен) (p.finished)",
    "Продажна цена (без ДДС) (p.price)",
    "Мин. продажна цена (p.price_min)",
    "Продажна цена (с ДДС) (p.price_ttc)",
    "Минимална продажна цена (с ДДС) (p.price_min_ttc)",
    "PriceBaseType (p.price_base_type)",
    "Данъчна ставка (p.tva_tx)",
    "Дата на създаване (p.datec)",
    "CostPrice (p.cost_price)",
    "Склад по подразбиране (p.fk_default_warehouse)",
    "Използване на партиден / сериен № (p.tobatch)",
    "Минимално количество за предупреждение (p.seuil_stock_alerte)",
    "Средно измерена цена (p.pmp)",
    "Желана наличност (p.desiredstock)",
]

FIELD_KEYS = [
    "p.ref", "p.label", "p.fk_product_type", "p.tosell", "p.tobuy",
    "p.description", "p.url", "p.customcode", "p.fk_country",
    "p.accountancy_code_sell", "p.accountancy_code_sell_intra",
    "p.accountancy_code_sell_export", "p.accountancy_code_buy",
    "p.accountancy_code_buy_intra", "p.accountancy_code_buy_export",
    "p.note_public", "p.note", "p.weight", "p.weight_units",
    "p.length", "p.length_units", "p.width", "p.width_units",
    "p.height", "p.height_units", "p.surface", "p.surface_units",
    "p.volume", "p.volume_units", "p.duration", "p.finished",
    "p.price", "p.price_min", "p.price_ttc", "p.price_min_ttc",
    "p.price_base_type", "p.tva_tx", "p.datec", "p.cost_price",
    "p.fk_default_warehouse", "p.tobatch", "p.seuil_stock_alerte",
    "p.pmp", "p.desiredstock",
]


class DolibarrExportError(ValueError):
    pass


def empty_dolibarr_row() -> dict[str, Any]:
    return {key: "" for key in FIELD_KEYS}


class DolibarrProductExporter:

    def __init__(self, project_root: Path | str):
        self.project_root = Path(project_root)

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_product_bundle(self, product_id: str) -> dict[str, Any]:
        folder = self.project_root / "knowledge" / "products" / product_id
        manifest = self._load_json(folder / "product.json")
        identity = self._load_json(folder / manifest["identity"])

        content_bg = None
        bg_file = manifest.get("content", {}).get("bg")
        if bg_file:
            content_bg = self._load_json(folder / bg_file)

        variants = None
        variants_file = manifest.get("variants")
        if variants_file:
            variants = self._load_json(folder / variants_file)

        return {
            "manifest": manifest,
            "identity": identity,
            "content_bg": content_bg,
            "variants": variants,
        }

    def build_rows(
        self,
        product_id: str,
        *,
        to_sell: int = 1,
        to_buy: int = 1,
        product_type: int = 0,
        price_base_type: str = "HT",
        vat_rate: Optional[float] = None,
        country_code: str = "",
    ) -> list[dict[str, Any]]:

        bundle = self.load_product_bundle(product_id)
        identity = bundle["identity"]["identity"]
        variants = (bundle.get("variants") or {}).get("variants", [])

        if not variants:
            raise DolibarrExportError(
                f"{product_id} has no variants for inventory-level export"
            )

        content_data = (bundle.get("content_bg") or {}).get("content", {})
        base_name = (
            content_data.get("name")
            or identity.get("model")
            or product_id
        )
        description = content_data.get("short_description") or ""

        rows: list[dict[str, Any]] = []

        for variant in variants:
            if variant.get("status", "active") != "active":
                continue

            ref = variant.get("sku") or variant.get("variant_id")
            if not ref:
                raise DolibarrExportError("Variant is missing SKU/ref")

            attrs = variant.get("attributes", {})
            size = str(attrs.get("size", "")).strip()
            color = str(attrs.get("color", "")).strip()

            suffix = []
            if color:
                suffix.append(color)
            if size:
                suffix.append(f"размер {size}")

            label = base_name
            if suffix:
                label += " - " + " / ".join(suffix)

            row = empty_dolibarr_row()
            row["p.ref"] = ref
            row["p.label"] = label
            row["p.fk_product_type"] = product_type
            row["p.tosell"] = to_sell
            row["p.tobuy"] = to_buy
            row["p.description"] = description
            row["p.fk_country"] = country_code
            row["p.finished"] = 1
            row["p.price_base_type"] = price_base_type
            row["p.tobatch"] = 0

            if vat_rate is not None:
                row["p.tva_tx"] = vat_rate

            moneywork_code = (
                variant.get("external_ids", {}).get("moneywork")
            )
            if moneywork_code:
                row["p.note"] = (
                    f"M99 external mapping: MoneyWork={moneywork_code}"
                )

            rows.append(row)

        return rows

    def export_csv(
        self,
        rows: Iterable[dict[str, Any]],
        output_path: Path | str,
    ) -> Path:

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(DOLIBARR_PRODUCT_HEADERS)

            for row in rows:
                values = [row.get(key, "") for key in FIELD_KEYS]
                if len(values) != 44:
                    raise DolibarrExportError(
                        "Dolibarr row must have exactly 44 fields"
                    )
                writer.writerow(values)

        return output_path

    @staticmethod
    def validate_required(
        rows: Iterable[dict[str, Any]],
    ) -> list[str]:

        required = [
            "p.ref", "p.label", "p.fk_product_type",
            "p.tosell", "p.tobuy",
        ]
        errors: list[str] = []

        for index, row in enumerate(rows, start=1):
            for key in required:
                if row.get(key, "") == "":
                    errors.append(
                        f"Row {index}: required field {key} is empty"
                    )

        return errors
