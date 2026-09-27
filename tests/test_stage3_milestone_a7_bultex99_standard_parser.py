from integrations.bultex99_supplier.public_parser import parse_public_product
def test_iso_colon_standard_real_shape():
 h="<h1>UNO LOW</h1><div>Арт. №: 06100764 € 58.90 с ДДС Стандарт: EN ISO:20345:2022+A1:2024</div>"
 p=parse_public_product(h,"https://bultex99.com/products/5161-uno-low")
 assert p.standard=="EN ISO:20345:2022+A1:2024"
 assert p.supplier_sku=="06100764"
def test_legacy_en_shape_preserved():
 h="<h1>X</h1><div>EN 20345:2022</div>"
 assert parse_public_product(h,"https://bultex99.com/products/9-x").standard=="EN 20345:2022"
