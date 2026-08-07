#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Build Product v0.2

Loads a complete Gold Master product through
M99 ProductLoader and generates an HTML page.

Usage:

    python scripts/build_product.py

or:

    python scripts/build_product.py M99-PM-000001
"""

import sys
from pathlib import Path
from html import escape

# =====================================================
# PROJECT PATH
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Make project root available for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.loader import ProductLoader, LoaderError


# =====================================================
# CONFIGURATION
# =====================================================

DEFAULT_PRODUCT_ID = "M99-PM-000001"

OUTPUT_FOLDER = PROJECT_ROOT / "output"
OUTPUT_FOLDER.mkdir(exist_ok=True)


# =====================================================
# HELPERS
# =====================================================

def safe(value):
    """
    Safely convert a value to HTML text.
    """

    if value is None:
        return ""

    return escape(str(value))


def get_value(data, key, default=""):
    """
    Safely get a value from a dictionary.
    """

    if not isinstance(data, dict):
        return default

    return data.get(key, default)


def render_list(items):
    """
    Convert a list into HTML list items.
    """

    if not items:
        return "<li>Няма налични данни</li>"

    html = ""

    for item in items:

        if isinstance(item, dict):

            name = item.get("name", "")

            if name:
                html += f"<li>{safe(name)}</li>"

            else:
                html += f"<li>{safe(item)}</li>"

        else:

            html += f"<li>{safe(item)}</li>"

    return html


def render_dict_table(data):
    """
    Convert a dictionary into a simple HTML table.
    """

    if not isinstance(data, dict) or not data:
        return "<p>Няма налични данни.</p>"

    rows = ""

    for key, value in data.items():

        if isinstance(value, list):

            if value and isinstance(value[0], dict):
                display_value = ", ".join(
                    str(
                        item.get("name", item)
                    )
                    for item in value
                )
            else:
                display_value = ", ".join(
                    str(item)
                    for item in value
                )

        elif isinstance(value, dict):

            display_value = ", ".join(
                f"{k}: {v}"
                for k, v in value.items()
            )

        else:

            display_value = value

        rows += f"""
        <tr>
            <th>{safe(key)}</th>
            <td>{safe(display_value)}</td>
        </tr>
        """

    return f"""
    <table>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


# =====================================================
# HTML GENERATOR
# =====================================================

def generate_html(product, product_id):
    """
    Generate complete HTML product page.
    """

    manifest = product.get("manifest", {})

    identity = product.get("identity", {})
    specifications = product.get("specifications", {})
    materials = product.get("materials", {})
    technologies = product.get("technologies", {})
    standards = product.get("standards", {})
    applications = product.get("applications", {})
    certifications = product.get("certifications", {})

    content = product.get("content", {})
    content_bg = content.get("bg", {})

    media = product.get("media", {})
    images = media.get("images", {})

    # -------------------------------------------------
    # Identity
    # -------------------------------------------------

    brand = get_value(identity, "brand")
    model = get_value(identity, "model")
    collection = get_value(identity, "collection")
    sku = get_value(identity, "sku")
    manufacturer_sku = get_value(
        identity,
        "manufacturer_sku"
    )

    product_type = get_value(
        identity,
        "product_type"
    )

    gender = get_value(
        identity,
        "gender"
    )

    # -------------------------------------------------
    # Content
    # -------------------------------------------------

    title = (
        get_value(content_bg, "title")
        or f"{brand} {model}"
    )

    short_description = (
        get_value(
            content_bg,
            "short_description"
        )
    )

    description = (
        get_value(
            content_bg,
            "description"
        )
    )

    # -------------------------------------------------
    # Build HTML
    # -------------------------------------------------

    html = f"""<!DOCTYPE html>

<html lang="bg">

<head>

<meta charset="utf-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>{safe(title)}</title>

<meta name="generator"
      content="M99 Knowledge Platform">

<meta name="product-id"
      content="{safe(product_id)}">

<style>

body {{
    font-family:
        Arial,
        Helvetica,
        sans-serif;

    max-width: 1100px;

    margin: 0 auto;

    padding: 40px;

    line-height: 1.6;

    color: #222;

    background: #fff;
}}

header {{
    margin-bottom: 40px;
}}

h1 {{
    font-size: 36px;

    margin-bottom: 10px;
}}

h2 {{
    margin-top: 45px;

    border-bottom:
        2px solid #222;

    padding-bottom: 8px;
}}

table {{
    border-collapse: collapse;

    width: 100%;

    margin-top: 15px;
}}

th,
td {{
    border:
        1px solid #ddd;

    padding: 10px;

    text-align: left;

    vertical-align: top;
}}

th {{
    width: 30%;

    background: #f5f5f5;
}}

ul {{
    padding-left: 25px;
}}

.product-meta {{
    color: #666;

    margin-bottom: 25px;
}}

.description {{
    font-size: 18px;

    margin-top: 25px;
}}

.footer {{
    margin-top: 60px;

    padding-top: 20px;

    border-top:
        1px solid #ddd;

    color: #777;

    font-size: 13px;
}}

</style>

</head>

<body>

<header>

<h1>{safe(title)}</h1>

<div class="product-meta">

<strong>Brand:</strong>
{safe(brand)}
<br>

<strong>Model:</strong>
{safe(model)}
<br>

<strong>Product ID:</strong>
{safe(product_id)}

</div>

"""

    if short_description:

        html += f"""
<div class="description">

{safe(short_description)}

</div>
"""

    if description:

        html += f"""
<div class="description">

{safe(description)}

</div>
"""

    # -------------------------------------------------
    # Identity
    # -------------------------------------------------

    html += f"""

<h2>Product Identity</h2>

<table>

<tr>
<th>SKU</th>
<td>{safe(sku)}</td>
</tr>

<tr>
<th>Manufacturer SKU</th>
<td>{safe(manufacturer_sku)}</td>
</tr>

<tr>
<th>Brand</th>
<td>{safe(brand)}</td>
</tr>

<tr>
<th>Collection</th>
<td>{safe(collection)}</td>
</tr>

<tr>
<th>Model</th>
<td>{safe(model)}</td>
</tr>

<tr>
<th>Product Type</th>
<td>{safe(product_type)}</td>
</tr>

<tr>
<th>Gender</th>
<td>{safe(gender)}</td>
</tr>

</table>
"""

    # -------------------------------------------------
    # Specifications
    # -------------------------------------------------

    if specifications:

        html += """

<h2>Specifications</h2>

"""

        html += render_dict_table(
            specifications
        )

    # -------------------------------------------------
    # Materials
    # -------------------------------------------------

    if materials:

        html += """

<h2>Materials</h2>

"""

        html += render_dict_table(
            materials
        )

    # -------------------------------------------------
    # Technologies
    # -------------------------------------------------

    if technologies:

        html += """

<h2>Technologies</h2>

"""

        if isinstance(
            technologies,
            list
        ):

            html += f"""
<ul>

{render_list(technologies)}

</ul>
"""

        else:

            html += render_dict_table(
                technologies
            )

    # -------------------------------------------------
    # Standards
    # -------------------------------------------------

    if standards:

        html += """

<h2>Standards</h2>

"""

        html += render_dict_table(
            standards
        )

    # -------------------------------------------------
    # Applications
    # -------------------------------------------------

    if applications:

        html += """

<h2>Applications</h2>

"""

        if isinstance(
            applications,
            list
        ):

            html += f"""
<ul>

{render_list(applications)}

</ul>
"""

        else:

            html += render_dict_table(
                applications
            )

    # -------------------------------------------------
    # Certifications
    # -------------------------------------------------

    if certifications:

        html += """

<h2>Certifications</h2>

"""

        html += render_dict_table(
            certifications
        )

    # -------------------------------------------------
    # Media
    # -------------------------------------------------

    if images:

        html += """

<h2>Images</h2>

"""

        if isinstance(
            images,
            list
        ):

            html += "<ul>"

            for image in images:

                if isinstance(
                    image,
                    dict
                ):

                    image_url = (
                        image.get("url")
                        or image.get("src")
                        or ""
                    )

                    if image_url:

                        html += f"""
<li>
<a href="{safe(image_url)}">
{safe(image_url)}
</a>
</li>
"""

                else:

                    html += (
                        f"<li>{safe(image)}</li>"
                    )

            html += "</ul>"

        else:

            html += render_dict_table(
                images
            )

    # -------------------------------------------------
    # Manifest
    # -------------------------------------------------

    html += f"""

<h2>Knowledge Metadata</h2>

<table>

<tr>
<th>Knowledge ID</th>
<td>{safe(
    get_value(
        manifest,
        "knowledge_id"
    )
)}</td>
</tr>

<tr>
<th>Product ID</th>
<td>{safe(
    get_value(
        manifest,
        "product_id"
    )
    or product_id
)}</td>
</tr>

<tr>
<th>Knowledge Version</th>
<td>{safe(
    get_value(
        manifest,
        "version"
    )
)}</td>
</tr>

<tr>
<th>Schema Version</th>
<td>{safe(
    get_value(
        manifest.get(
            "metadata",
            {}
        ),
        "schema_version"
    )
)}</td>
</tr>

</table>

<div class="footer">

Generated by
<strong>M99 Knowledge Platform</strong>

<br>

Product:
{safe(product_id)}

</div>

</body>

</html>
"""

    return html


# =====================================================
# MAIN
# =====================================================

def main():

    print()
    print("========================================")
    print("M99 Knowledge Platform")
    print("Build Product v0.2")
    print("========================================")
    print()

    # -------------------------------------------------
    # Product ID
    # -------------------------------------------------

    if len(sys.argv) > 1:

        product_id = sys.argv[1]

    else:

        product_id = DEFAULT_PRODUCT_ID

    print(
        f"Product: {product_id}"
    )

    print()

    # -------------------------------------------------
    # Loader
    # -------------------------------------------------

    try:

        loader = ProductLoader(
            PROJECT_ROOT
        )

        product = loader.load(
            product_id
        )

    except LoaderError as error:

        print()
        print("ERROR")
        print("----------------------------------------")
        print(error)
        print()

        sys.exit(1)

    except Exception as error:

        print()
        print("UNEXPECTED ERROR")
        print("----------------------------------------")
        print(error)
        print()

        raise

    # -------------------------------------------------
    # Generate
    # -------------------------------------------------

    print(
        "Generating HTML..."
    )

    html = generate_html(
        product,
        product_id
    )

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    output_file = (
        OUTPUT_FOLDER
        / f"{product_id}.html"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    # -------------------------------------------------
    # Success
    # -------------------------------------------------

    print()

    print("========================================")
    print("SUCCESS")
    print("========================================")

    print()

    print(
        "Knowledge loaded:"
        " YES"
    )

    print(
        "HTML generated:"
        " YES"
    )

    print()

    print(
        f"Output:"
    )

    print(
        output_file
    )

    print()


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    main()
