#!/usr/bin/env python3
"""
M99 Knowledge Platform
Build Product v0.1

Loads a Gold Master product from the Knowledge Base
and generates the first HTML product page.

Author: M99 Knowledge Platform
"""

import json
from pathlib import Path


# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCT_FOLDER = (
    PROJECT_ROOT /
    "knowledge" /
    "products" /
    "M99-PM-000001"
)

OUTPUT_FOLDER = PROJECT_ROOT / "output"

OUTPUT_FOLDER.mkdir(exist_ok=True)


# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def load_json(file_path):

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------
# LOAD PRODUCT
# ---------------------------------------------------

print("Loading product...")

product = load_json(PRODUCT_FOLDER / "product.json")


# ---------------------------------------------------
# LOAD REFERENCES
# ---------------------------------------------------

references = product["references"]

loaded = {}

for key, value in references.items():

    if isinstance(value, dict):

        loaded[key] = {}

        for lang, filename in value.items():

            if filename is None:
                continue

            loaded[key][lang] = load_json(
                PRODUCT_FOLDER / filename
            )

    else:

        if value is None:
            continue

        loaded[key] = load_json(
            PRODUCT_FOLDER / value
        )

print("Knowledge loaded successfully.")


# ---------------------------------------------------
# BUILD HTML
# ---------------------------------------------------

content = loaded["content"]["bg"]

html = f"""
<!DOCTYPE html>

<html lang="bg">

<head>

<meta charset="utf-8">

<title>{content["content"]["name"]}</title>

</head>

<body>

<h1>

{content["content"]["name"]}

</h1>

<p>

{content["content"]["short_description"]}

</p>

<h2>

Предимства

</h2>

<ul>

"""

for item in content["content"]["key_benefits"]:

    html += f"<li>{item}</li>"

html += """

</ul>

</body>

</html>

"""

output = OUTPUT_FOLDER / "M99-PM-000001.html"

with open(output, "w", encoding="utf-8") as f:
    f.write(html)

print()
print("--------------------------------")
print("HTML generated successfully")
print(output)
print("--------------------------------")
