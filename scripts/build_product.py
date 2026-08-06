#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Build Product v0.1

Reads a Gold Master product and generates
the first HTML product page.

Author: M99 Knowledge Platform
"""

import json
from pathlib import Path
print(__file__)

# =====================================================
# CONFIGURATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCT_ID = "M99-PM-000001"

PRODUCT_FILE = (
    PROJECT_ROOT
    / "knowledge"
    / "products"
    / PRODUCT_ID
    / "product.json"
)

OUTPUT_FOLDER = PROJECT_ROOT / "output"
OUTPUT_FOLDER.mkdir(exist_ok=True)

# =====================================================
# LOAD PRODUCT
# =====================================================

print("========================================")
print("M99 Knowledge Platform")
print("Build Product")
print("========================================")
print()

if not PRODUCT_FILE.exists():
    raise FileNotFoundError(f"Missing file:\n{PRODUCT_FILE}")

print("Loading product.json...")

with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
    product = json.load(f)

print("OK")

# =====================================================
# READ DATA
# =====================================================

identity = product.get("identity", {})
classification = product.get("classification", {})
certification = product.get("certification", {})
construction = product.get("construction", {})
knowledge = product.get("knowledge", {})
metadata = product.get("metadata", {})

brand = identity.get("brand", "")
model = identity.get("model", "")
collection = identity.get("collection", "")
sku = identity.get("sku", "")
manufacturer_sku = identity.get("manufacturer_sku", "")

category = classification.get("category", "")
subcategory = classification.get("subcategory", "")

standard = certification.get("standard", "")
protection = certification.get("protection_class", "")
markings = certification.get("additional_markings", [])

toe_cap = construction.get("toe_cap", "")
penetration = construction.get("penetration_protection", "")
sole = construction.get("sole", "")

score = knowledge.get("knowledge_score", "")
confidence = knowledge.get("confidence", "")

version = metadata.get("version", "")

technologies = product.get("technologies", [])

# =====================================================
# BUILD HTML
# =====================================================

print("Generating HTML...")

html = f"""<!DOCTYPE html>
<html lang="bg">
<head>
<meta charset="utf-8">
<title>{brand} {model}</title>

<style>

body {{
    font-family: Arial, Helvetica, sans-serif;
    max-width: 1000px;
    margin: 40px auto;
    padding: 20px;
    line-height: 1.6;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

td, th {{
    border:1px solid #cccccc;
    padding:8px;
}}

h1 {{
    color:#222;
}}

.section {{
    margin-top:40px;
}}

</style>

</head>

<body>

<h1>{brand} {model}</h1>

<p><strong>Collection:</strong> {collection}</p>

<p><strong>SKU:</strong> {sku}</p>

<p><strong>Manufacturer SKU:</strong> {manufacturer_sku}</p>

<div class="section">

<h2>Classification</h2>

<table>

<tr><th>Category</th><td>{category}</td></tr>

<tr><th>Subcategory</th><td>{subcategory}</td></tr>

<tr><th>Protection Class</th><td>{protection}</td></tr>

<tr><th>Standard</th><td>{standard}</td></tr>

<tr><th>Additional Markings</th><td>{", ".join(markings)}</td></tr>

</table>

</div>

<div class="section">

<h2>Construction</h2>

<table>

<tr><th>Toe Cap</th><td>{toe_cap}</td></tr>

<tr><th>Penetration Protection</th><td>{penetration}</td></tr>

<tr><th>Sole</th><td>{sole}</td></tr>

</table>

</div>

<div class="section">

<h2>Technologies</h2>

<ul>
"""

for tech in technologies:
    html += f"<li>{tech.get('name','')}</li>\n"

html += f"""
</ul>

</div>

<div class="section">

<h2>Knowledge Status</h2>

<table>

<tr><th>Knowledge Score</th><td>{score}</td></tr>

<tr><th>Confidence</th><td>{confidence}%</td></tr>

<tr><th>Version</th><td>{version}</td></tr>

</table>

</div>

</body>
</html>
"""

# =====================================================
# SAVE
# =====================================================

OUTPUT_FILE = OUTPUT_FOLDER / f"{PRODUCT_ID}.html"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print()
print("========================================")
print("SUCCESS")
print("========================================")
print()
print(f"HTML generated:")
print(OUTPUT_FILE)
print()
