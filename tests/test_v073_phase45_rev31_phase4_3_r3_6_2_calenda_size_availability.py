from app.services.v073_phase45 import calenda_public_connector as c

HTML = """
<table id="textile-color-table">
<thead><tr><th>Цвят</th><th>Размер</th></tr></thead>
<tbody>
<tr>
<td><img src="https://calenda.bg/storage/products/93100_20a.jpg"></td>
<td>S</td><td>20.40 &euro; / 39.90 лв.</td>
<td><span class="desktop-title">0 бр.</span><span>Варна: 0 бр. 1-2: 0 бр. 7-10: 207 бр.</span></td>
<td>0 бр.</td><td>207 бр.</td><td>qty</td>
</tr>
<tr>
<td><img src="https://calenda.bg/storage/products/93100_20a.jpg"></td>
<td>M</td><td>20.40 &euro; / 39.90 лв.</td>
<td><span class="desktop-title">2 бр.</span></td>
<td>3 бр.</td><td>320 бр.</td><td>qty</td>
</tr>
<tr>
<td><img src="https://calenda.bg/storage/products/99999_20a.jpg"></td>
<td>WRONG</td><td>1.00 &euro; / 1.96 лв.</td><td>9 бр.</td><td>9 бр.</td><td>9 бр.</td><td>qty</td>
</tr>
</tbody></table>
"""

def test_exact_color_size_rows_and_supplier_buckets():
    rows = c._size_availability_from_html(HTML, "93100", "20")
    assert [r["size"] for r in rows] == ["S", "M"]
    assert rows[0]["price_eur"] == "20.40"
    assert rows[0]["supplier_availability"]["varna_qty"] == 0
    assert rows[0]["supplier_availability"]["delivery_1_2_days_qty"] == 0
    assert rows[0]["supplier_availability"]["delivery_7_10_days_qty"] == 207
    assert rows[0]["supplier_availability"]["total_observed_qty"] == 207

def test_supplier_availability_never_counts_as_m99_stock():
    rows = c._size_availability_from_html(HTML, "93100", "20")
    assert all(r["supplier_availability"]["evidence_scope"] == "SUPPLIER" for r in rows)
    assert all(r["supplier_availability"]["counts_as_m99_owned_stock"] is False for r in rows)

def test_summary_is_exact_sum_of_published_buckets():
    rows = c._size_availability_from_html(HTML, "93100", "20")
    summary = c._summarize_size_availability(rows)
    assert summary["sizes_observed"] == 2
    assert summary["varna_qty"] == 2
    assert summary["delivery_1_2_days_qty"] == 3
    assert summary["delivery_7_10_days_qty"] == 527
    assert summary["total_observed_qty"] == 532
    assert summary["counts_as_m99_owned_stock"] is False
