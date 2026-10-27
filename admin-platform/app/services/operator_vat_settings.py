"""Durable operator-owned VAT configuration, scoped by channel."""
from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from app.core.db import PROJECT_ROOT

DB = PROJECT_ROOT / "data" / "operator_vat_settings.sqlite3"
SHOPS = ("m99.eu", "mela99.com", "rabotni-drehi.com", "medicinski-drehi.com", "laviro.ro", "alviro.ro", "toplinka.com")

def normalize_rate(value):
    try:
        rate = Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError("INVALID_VAT_PERCENT")
    if not rate.is_finite() or not Decimal("0") <= rate <= Decimal("100"):
        raise ValueError("VAT_PERCENT_OUT_OF_RANGE")
    if rate.as_tuple().exponent < -3:
        raise ValueError("VAT_PERCENT_MAX_THREE_DECIMALS")
    return format(rate.normalize(), "f")

def _connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB), timeout=10)
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("CREATE TABLE IF NOT EXISTS vat_settings (shop TEXT PRIMARY KEY, vat_percent TEXT NOT NULL, tax_group_id INTEGER, updated_at TEXT NOT NULL, updated_by TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS vat_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, shop TEXT NOT NULL, old_percent TEXT, new_percent TEXT NOT NULL, old_group INTEGER, new_group INTEGER, updated_at TEXT NOT NULL, updated_by TEXT NOT NULL)")
    return conn

def get_setting(shop):
    if shop not in SHOPS: raise ValueError("UNKNOWN_SHOP")
    with _connect() as db:
        row=db.execute("SELECT vat_percent,tax_group_id,updated_at,updated_by FROM vat_settings WHERE shop=?", (shop,)).fetchone()
    return None if row is None else {"shop":shop,"vat_percent":row[0],"tax_group_id":row[1],"updated_at":row[2],"updated_by":row[3]}

def save_setting(shop, percent, group_id, actor):
    if shop not in SHOPS: raise ValueError("UNKNOWN_SHOP")
    rate=normalize_rate(percent)
    group=str(group_id or "").strip()
    if group and (not group.isascii() or not group.isdecimal() or int(group)<1): raise ValueError("INVALID_TAX_GROUP_ID")
    gid=int(group) if group else None
    actor=str(actor or "operator")[:120]
    now=datetime.now(timezone.utc).isoformat()
    with _connect() as db:
        db.execute("BEGIN IMMEDIATE")
        old=db.execute("SELECT vat_percent,tax_group_id FROM vat_settings WHERE shop=?", (shop,)).fetchone()
        db.execute("INSERT INTO vat_settings(shop,vat_percent,tax_group_id,updated_at,updated_by) VALUES(?,?,?,?,?) ON CONFLICT(shop) DO UPDATE SET vat_percent=excluded.vat_percent,tax_group_id=excluded.tax_group_id,updated_at=excluded.updated_at,updated_by=excluded.updated_by",(shop,rate,gid,now,actor))
        db.execute("INSERT INTO vat_audit(shop,old_percent,new_percent,old_group,new_group,updated_at,updated_by) VALUES(?,?,?,?,?,?,?)",(shop,old[0] if old else None,rate,old[1] if old else None,gid,now,actor))
    return get_setting(shop)
