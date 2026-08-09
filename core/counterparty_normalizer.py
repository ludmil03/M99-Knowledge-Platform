from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import re

from core.moneywork_parser import MoneyWorkCounterparty


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def normalize_legal_name(value: Any) -> str:
    value = clean_text(value).upper()
    value = value.replace('"', "")
    value = re.sub(r"[.,;:()]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_company_id(value: Any) -> str:
    value = clean_text(value).upper()
    return re.sub(r"[^A-Z0-9]", "", value)


def normalize_vat_id(value: Any) -> str:
    return normalize_company_id(value)


def country_code_from_moneywork(value: Any) -> str:
    value = clean_text(value)
    if not value:
        return ""
    match = re.match(r"^\s*([A-Za-z]{2})\s*(?:-|$)", value)
    if match:
        return match.group(1).upper()
    if len(value) == 2 and value.isalpha():
        return value.upper()
    return ""


def normalize_email(value: Any) -> str:
    return clean_text(value).lower()


def normalize_phone(value: Any) -> str:
    value = clean_text(value)
    if not value:
        return ""
    leading_plus = value.startswith("+")
    digits = re.sub(r"\D", "", value)
    if not digits:
        return ""
    return ("+" if leading_plus else "") + digits


@dataclass
class NormalizedCounterparty:
    source_system: str
    source_row_no: int
    legal_name: str
    normalized_name: str
    company_id: str
    vat_id: str
    country_code: str
    city: str
    address: str
    postal_code: str
    email: str
    phone: str
    contact_person: str
    roles: set[str] = field(default_factory=set)
    raw: dict[str, Any] = field(default_factory=dict)

    def fallback_identity_key(self) -> str:
        if self.normalized_name:
            return f"NAME:{self.country_code}:{self.normalized_name}"
        return f"ROW:{self.source_row_no}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_system": self.source_system,
            "source_row_no": self.source_row_no,
            "legal_name": self.legal_name,
            "normalized_name": self.normalized_name,
            "company_id": self.company_id,
            "vat_id": self.vat_id,
            "country_code": self.country_code,
            "city": self.city,
            "address": self.address,
            "postal_code": self.postal_code,
            "email": self.email,
            "phone": self.phone,
            "contact_person": self.contact_person,
            "roles": sorted(self.roles),
            "raw": self.raw,
        }


def normalize_moneywork_counterparty(
    record: MoneyWorkCounterparty,
) -> NormalizedCounterparty:

    role_map = {"K": "CUSTOMER", "S": "SUPPLIER"}
    roles = set()
    if record.role_code in role_map:
        roles.add(role_map[record.role_code])

    fields = record.fields
    legal_name = clean_text(fields.get("Фирма"))

    return NormalizedCounterparty(
        source_system="MONEYWORK",
        source_row_no=record.row_no,
        legal_name=legal_name,
        normalized_name=normalize_legal_name(legal_name),
        company_id=normalize_company_id(fields.get("Булстат")),
        vat_id=normalize_vat_id(fields.get("ДДС-VAT №")),
        country_code=country_code_from_moneywork(fields.get("COUNTRY")),
        city=clean_text(fields.get("Град")),
        address=clean_text(fields.get("Адрес")),
        postal_code=clean_text(fields.get("POST")),
        email=normalize_email(fields.get("E-mail")),
        phone=normalize_phone(fields.get("Телефон")),
        contact_person=clean_text(fields.get("МОЛ")),
        roles=roles,
        raw=dict(fields),
    )
