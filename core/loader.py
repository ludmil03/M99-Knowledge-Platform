#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
core.loader

Loads a complete product from the Knowledge Repository.
"""

from pathlib import Path
import json


class LoaderError(Exception):
    """Raised when a knowledge object cannot be loaded."""
    pass


class ProductLoader:

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

    # -------------------------------------------------

    def load_json(self, path: Path):

        if not path.exists():
            raise LoaderError(f"Missing file:\n{path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -------------------------------------------------

    def load(self, product_id: str):

        product_folder = (
            self.project_root
            / "knowledge"
            / "products"
            / product_id
        )

        if not product_folder.exists():
            raise LoaderError(
                f"Unknown product: {product_id}"
            )

        print(f"Loading {product_id}")

        # -----------------------------------------
        # Load Manifest
        # -----------------------------------------

        manifest = self.load_json(
            product_folder / "product.json"
        )

        product = {
            "manifest": manifest
        }

        # -----------------------------------------
        # Load Standard Objects
        # -----------------------------------------

        object_names = [

            "identity",
            "specifications",
            "materials",
            "technologies",
            "standards",
            "applications",
            "certifications",
            "variants"

        ]

        for name in object_names:

            filename = manifest.get(name)

            if filename is None:
                print(f"SKIP {name}")
                continue

            print(f"Loading {filename}")

            product[name] = self.load_json(
                product_folder / filename
            )

        # -----------------------------------------
        # Load Content
        # -----------------------------------------

        content = {}

        for lang, filename in manifest.get(
            "content",
            {}
        ).items():

            if filename is None:
                continue

            print(f"Loading {filename}")

            content[lang] = self.load_json(
                product_folder / filename
            )

        product["content"] = content

        # -----------------------------------------
        # Load Media
        # -----------------------------------------

        media = {}

        media_manifest = manifest.get("media", {})

        if media_manifest.get("images"):

            filename = media_manifest["images"]

            print(f"Loading {filename}")

            media["images"] = self.load_json(
                product_folder / filename
            )

        product["media"] = media

        print()

        print("Knowledge successfully loaded.")

        return product
