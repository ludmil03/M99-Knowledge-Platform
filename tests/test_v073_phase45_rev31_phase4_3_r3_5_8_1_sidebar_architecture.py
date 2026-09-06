from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_sidebar_uses_i18n_and_exact_routes():
 b=(ROOT/"admin-platform/app/templates/base.html").read_text(encoding="utf-8")
 i=(ROOT/"admin-platform/app/services/i18n.py").read_text(encoding="utf-8")
 assert '{{ ui.suppliers }}' in b
 assert '<a href="/suppliers">' in b
 assert '<a href="/imports">' in b
 assert "Suppliers / Browse" in i
def test_add_products_precedes_existing_import_items():
 b=(ROOT/"admin-platform/app/templates/base.html").read_text(encoding="utf-8")
 a=b.find('<a href="/add-products">')
 s=b.find('<a href="/suppliers">')
 j=b.find('<a href="/imports">')
 assert -1 < a < s < j
