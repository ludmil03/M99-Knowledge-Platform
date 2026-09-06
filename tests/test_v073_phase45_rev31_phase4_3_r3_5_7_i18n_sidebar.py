from pathlib import Path
def test_real_base_has_add_products():
 root=Path(__file__).resolve().parents[1]
 t=(root/"admin-platform/app/templates/base.html").read_text(encoding="utf-8")
 assert "/add-products" in t
 assert "Add Products" in t
def test_i18n_supplier_label_preserved():
 root=Path(__file__).resolve().parents[1]
 t=(root/"admin-platform/app/services/i18n.py").read_text(encoding="utf-8")
 assert "Suppliers / Browse" in t
