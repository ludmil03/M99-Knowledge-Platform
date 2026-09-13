
from __future__ import annotations

import re
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.models.entities import Product, ImportJobItem

M99_RE = re.compile(r"^M99-([0-9]+)$")

class CanonicalIdentityAllocationError(RuntimeError):
    pass

def _text(v) -> str:
    return str(v or "").strip()

def _valid(v: str) -> bool:
    return bool(M99_RE.fullmatch(_text(v)))

def _next_reference(db: Session) -> str:
    values = db.query(Product.m99_reference).all()
    high = 0
    for row in values:
        raw = row[0] if isinstance(row, tuple) else getattr(row, "m99_reference", row)
        m = M99_RE.fullmatch(_text(raw))
        if m:
            high = max(high, int(m.group(1)))
    return f"M99-{high+1}"

def _required_unhandled_columns() -> list[str]:
    known = {"id","m99_reference","supplier_reference","name","lifecycle"}
    bad=[]
    mapper=sa_inspect(Product)
    for col in mapper.columns:
        if col.key in known:
            continue
        if col.nullable or col.default is not None or col.server_default is not None:
            continue
        # SQLAlchemy-managed PK/autoincrement columns are safe.
        if col.primary_key or bool(getattr(col,"autoincrement",False)):
            continue
        bad.append(col.key)
    return bad

def allocate_or_reuse_for_item(db: Session, *, item: ImportJobItem) -> dict:
    """Create/reuse permanent canonical M99 identity for exactly one DRAFT item.

    Supplier reference and Manufacturer MPN are never used as the M99 identity.
    If item.matched_product_id already points to a Product with M99-N, reuse it.
    Otherwise create a canonical Product in lifecycle=draft, link matched_product_id,
    commit, then read back.
    """
    matched_id = getattr(item, "matched_product_id", None)
    if matched_id:
        existing = db.get(Product, int(matched_id))
        if existing and _valid(getattr(existing, "m99_reference", "")):
            return {
                "created": False,
                "product_id": int(existing.id),
                "m99_reference": _text(existing.m99_reference),
                "status": "REUSED_EXISTING_MATCH",
            }

    bad=_required_unhandled_columns()
    if bad:
        raise CanonicalIdentityAllocationError(
            "Product model has required columns not covered by governed R7E allocator: "
            + ", ".join(sorted(bad))
        )

    supplier_ref=_text(getattr(item,"supplier_reference",""))
    title=_text(getattr(item,"source_title","")) or "Canonical product"
    ref=_next_reference(db)

    kwargs={}
    mapper=sa_inspect(Product)
    cols={c.key for c in mapper.columns}
    if "m99_reference" not in cols:
        raise CanonicalIdentityAllocationError("Product.m99_reference column is missing.")
    kwargs["m99_reference"]=ref
    if "supplier_reference" in cols:
        kwargs["supplier_reference"]=supplier_ref
    if "name" in cols:
        kwargs["name"]=title
    if "lifecycle" in cols:
        kwargs["lifecycle"]="draft"

    product=Product(**kwargs)
    db.add(product)
    db.flush()
    if not getattr(product,"id",None):
        raise CanonicalIdentityAllocationError("Canonical Product flush did not return an id.")

    if not hasattr(item,"matched_product_id"):
        raise CanonicalIdentityAllocationError("ImportJobItem.matched_product_id is unavailable.")
    item.matched_product_id=int(product.id)
    db.add(item)
    db.commit()

    readback=db.get(Product,int(product.id))
    if not readback or _text(getattr(readback,"m99_reference",""))!=ref:
        raise CanonicalIdentityAllocationError("Canonical identity readback mismatch.")
    return {
        "created": True,
        "product_id": int(readback.id),
        "m99_reference": ref,
        "status": "CREATED_PERMANENT_M99_ID",
    }
