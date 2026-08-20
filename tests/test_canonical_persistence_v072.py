from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN_ROOT = REPO_ROOT / "admin-platform"

if str(ADMIN_ROOT) not in sys.path:
    sys.path.insert(0, str(ADMIN_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.db import Base  # noqa: E402
from app.models import entities  # noqa: F401,E402
from app.models.canonical_v072 import (  # noqa: E402
    CanonicalChannel,
    CanonicalInventoryMapping,
    CanonicalMarket,
    CanonicalProduct,
    CanonicalProductGroup,
    CanonicalProductVariant,
)


def test_canonical_metadata_contains_expected_tables():
    expected = {
        "canonical_product_groups",
        "canonical_products",
        "canonical_product_variants",
        "canonical_external_identities",
        "canonical_supplier_offers",
        "canonical_markets",
        "canonical_channels",
        "canonical_channel_product_groups",
        "canonical_channel_presence",
        "canonical_inventory_mappings",
    }
    assert expected.issubset(set(Base.metadata.tables))


def test_persistence_roundtrip_uses_m99_identity():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        group = CanonicalProductGroup(m99_id="M99-PG-1", name="Group")
        session.add(group)
        session.flush()

        product = CanonicalProduct(
            m99_id="M99-P-1",
            product_group_id=group.id,
            name="Product",
        )
        session.add(product)
        session.flush()

        variant = CanonicalProductVariant(
            m99_id="M99-V-1",
            product_id=product.id,
            variant_key="size-42",
        )
        session.add(variant)
        session.commit()

        loaded = session.query(CanonicalProductVariant).filter_by(m99_id="M99-V-1").one()
        assert loaded.variant_key == "size-42"


def test_market_and_channel_are_persisted_separately():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        market = CanonicalMarket(
            code="bg",
            name="Bulgaria",
            country_code="BG",
            default_currency="BGN",
            default_language="bg",
        )
        session.add(market)
        session.flush()

        channel = CanonicalChannel(
            code="mela99",
            name="mela99.com",
            market_id=market.id,
            kind="website",
        )
        session.add(channel)
        session.commit()

        assert channel.market_id == market.id
        assert channel.code != market.code


def test_inventory_mapping_does_not_store_canonical_quantity():
    columns = {c.name for c in CanonicalInventoryMapping.__table__.columns}
    assert "quantity" not in columns
    assert {"variant_id", "system", "warehouse_id", "external_product_id"}.issubset(columns)


def test_alembic_upgrade_creates_canonical_tables(tmp_path):
    db_file = tmp_path / "migration_test.db"
    db_url = "sqlite:///" + db_file.as_posix()

    env = os.environ.copy()
    env["M99_ALEMBIC_DATABASE_URL"] = db_url

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=ADMIN_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    engine = create_engine(db_url, future=True)
    tables = set(inspect(engine).get_table_names())
    assert "alembic_version" in tables
    assert "canonical_product_groups" in tables
    assert "canonical_product_variants" in tables
    assert "canonical_inventory_mappings" in tables
