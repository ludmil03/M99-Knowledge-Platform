from pathlib import Path
P=Path(__file__).resolve().parents[1]/"admin-platform/app/routers/r7k4_real_operator_publish.py"
def s(): return P.read_text(encoding="utf-8")
def test_current_marker(): assert "R7K.4 R7.2.3.2" in s()
def test_r722_contract():
 x=s(); assert "<select name=item_id required>" in x and "ImportJobItem.import_job_id==int(job_id)" in x
 assert "publish_palltex_controlled" in x and "operator_approved" in x and "HIDDEN" in x
def test_practical_preview():
 x=s(); assert "незадължително за проверката" in x and "Практически gate" in x
