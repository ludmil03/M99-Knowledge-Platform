from __future__ import annotations
from html import escape
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services.operator_vat_settings import SHOPS, get_setting, save_setting

router=APIRouter(prefix="/operator/settings/vat",tags=["operator-vat-settings"])

def _actor(request):
    try: s=request.session
    except Exception: return None
    if not any(s.get(k) for k in ("user_id","username","user","authenticated","is_authenticated")):return None
    return str(s.get("username") or s.get("user") or s.get("user_id") or "operator")

def _page(shop,notice=""):
    options="".join(f'<option value="{escape(s)}" {"selected" if s==shop else ""}>{escape(s)}</option>' for s in SHOPS)
    current=get_setting(shop)
    rate=escape(current["vat_percent"] if current else "")
    gid=escape(str(current["tax_group_id"] or "") if current else "")
    last=escape(current["updated_at"] if current else "Never configured")
    note=escape(notice)
    return f"""<!doctype html><html lang="bg"><head><meta charset="utf-8"><title>M99 VAT settings</title><style>body{{font:16px Arial,sans-serif;background:#f4f6fa;margin:40px}}main{{max-width:670px;background:white;padding:30px;border-radius:12px}}label{{display:block;margin:18px 0 6px}}input,select{{padding:12px;width:100%;box-sizing:border-box}}button{{padding:13px 22px;background:#194f9d;color:white;border:0;margin-top:24px;cursor:pointer}}.notice{{color:#17603b}}small{{color:#555}}</style></head><body><main><h1>M99 · Настройки на ДДС</h1><p class="notice">{note}</p><form method="get"><label>Магазин</label><select name="shop" onchange="this.form.submit()">{options}</select></form><form method="post"><input type="hidden" name="shop" value="{escape(shop)}"><label>ДДС (%)</label><input name="vat_percent" inputmode="decimal" required value="{rate}" placeholder="20"><label>PrestaShop ID на данъчна група (по избор)</label><input name="tax_group_id" inputmode="numeric" value="{gid}" placeholder="напр. 1"><small>Процентът се съхранява независимо от API. За реално публикуване към PrestaShop е нужен валиден идентификатор на данъчна група, доказан чрез магазина. Не въвеждайте произволен ID.</small><p><button type="submit">Запази настройката</button></p></form><p><small>Последна промяна: {last}. Промените се записват в одитен журнал.</small></p><p><a href="/operator/add-products">Към добавяне на продукти</a></p></main></body></html>"""

@router.get("",response_class=HTMLResponse)
def show(request:Request,shop:str="m99.eu"):
    if not _actor(request):return RedirectResponse("/login",status_code=303)
    if shop not in SHOPS:shop="m99.eu"
    return HTMLResponse(_page(shop))

@router.post("",response_class=HTMLResponse)
def save(request:Request,shop:str=Form(...),vat_percent:str=Form(...),tax_group_id:str=Form("")):
    actor=_actor(request)
    if not actor:return RedirectResponse("/login",status_code=303)
    try:save_setting(shop,vat_percent,tax_group_id,actor)
    except ValueError as exc:return HTMLResponse(_page(shop if shop in SHOPS else "m99.eu","Грешка: "+str(exc)),status_code=400)
    return HTMLResponse(_page(shop,"Настройката е записана успешно."))
