from pathlib import Path
def text():
 return (Path(__file__).resolve().parents[1]/"admin-platform/app/templates/base.html").read_text(encoding="utf-8")
def test_exact_add_products_item():
 t=text(); assert t.count('<a href="/add-products">⊕ Add Products</a>')==1
def test_existing_items_preserved():
 t=text(); assert '<a href="/suppliers">◉ {{ ui.suppliers }}</a>' in t; assert '<a href="/imports">⇩ {{ ui.imports }}</a>' in t
def test_imports_order():
 t=text(); a=t.find('<a href="/add-products">'); s=t.find('<a href="/suppliers">'); i=t.find('<a href="/imports">'); assert -1<a<s<i
