#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
MoneyWork Parser v0.5

Supported legacy exports:
- ARTDATA.txt: CP1251 fixed-width article export.
- Customer/Supplier CSV: CP1251 outer semicolon wrapper with inner comma CSV.

Malformed counterparty rows are quarantined as parse issues instead of
aborting the whole migration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional
import csv
import io

MONEYWORK_ENCODING = "cp1251"

ART_CODE_SLICE = slice(0, 11)
ART_SUPPLIER_SLICE = slice(11, 26)
ART_NAME_SLICE = slice(26, 511)
ART_TAIL_SLICE = slice(511, None)


class MoneyWorkParseError(ValueError):
    pass


@dataclass(frozen=True)
class MoneyWorkParseIssue:
    row_no: int
    issue_type: str
    message: str
    raw: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_no": self.row_no,
            "issue_type": self.issue_type,
            "message": self.message,
            "raw": self.raw,
        }


@dataclass(frozen=True)
class MoneyWorkArticle:
    line_no: int
    legacy_code: str
    supplier_name: str
    name: str
    raw_tail: str
    raw_line: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": "moneywork",
            "source_id": "GENSOFT-MONEYWORK",
            "line_no": self.line_no,
            "legacy_code": self.legacy_code,
            "supplier_name": self.supplier_name,
            "name": self.name,
            "raw_tail": self.raw_tail,
            "raw_line": self.raw_line,
        }


@dataclass(frozen=True)
class MoneyWorkCounterparty:
    row_no: int
    fields: dict[str, str]
    raw_inner_csv: str

    @property
    def role_code(self) -> str:
        return self.fields.get("Тип", "").strip().upper()

    @property
    def legal_name(self) -> str:
        return self.fields.get("Фирма", "").strip()

    @property
    def company_id(self) -> str:
        return self.fields.get("Булстат", "").strip()

    @property
    def vat_id(self) -> str:
        return self.fields.get("ДДС-VAT №", "").strip()

    @property
    def country(self) -> str:
        return self.fields.get("COUNTRY", "").strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_no": self.row_no,
            "role_code": self.role_code,
            "fields": dict(self.fields),
            "raw_inner_csv": self.raw_inner_csv,
        }


class MoneyWorkParser:

    def __init__(self, encoding: str = MONEYWORK_ENCODING):
        self.encoding = encoding
        self.parse_issues: list[MoneyWorkParseIssue] = []

    def reset_issues(self) -> None:
        self.parse_issues = []

    def parse_articles(self, path: Path | str) -> list[MoneyWorkArticle]:
        path = Path(path)
        text = path.read_bytes().decode(self.encoding)

        articles: list[MoneyWorkArticle] = []

        for line_no, raw_line in enumerate(text.splitlines(), start=1):
            if not raw_line.strip():
                continue

            if len(raw_line) < ART_NAME_SLICE.stop:
                self.parse_issues.append(
                    MoneyWorkParseIssue(
                        row_no=line_no,
                        issue_type="ARTDATA_SHORT_LINE",
                        message=f"Line length is {len(raw_line)}",
                        raw=raw_line,
                    )
                )
                continue

            legacy_code = raw_line[ART_CODE_SLICE].strip()
            supplier_name = raw_line[ART_SUPPLIER_SLICE].strip()
            name = raw_line[ART_NAME_SLICE].strip()
            raw_tail = raw_line[ART_TAIL_SLICE]

            if not legacy_code:
                self.parse_issues.append(
                    MoneyWorkParseIssue(
                        row_no=line_no,
                        issue_type="ARTDATA_MISSING_CODE",
                        message="Article code is empty",
                        raw=raw_line,
                    )
                )
                continue

            articles.append(
                MoneyWorkArticle(
                    line_no=line_no,
                    legacy_code=legacy_code,
                    supplier_name=supplier_name,
                    name=name,
                    raw_tail=raw_tail,
                    raw_line=raw_line,
                )
            )

        return articles

    def _parse_outer_rows(self, path: Path | str) -> list[list[str]]:
        path = Path(path)
        text = path.read_bytes().decode(self.encoding)

        return list(
            csv.reader(
                io.StringIO(text),
                delimiter=";",
                quotechar='"',
            )
        )

    def parse_counterparties(
        self,
        path: Path | str,
        expected_role: Optional[str] = None,
    ) -> list[MoneyWorkCounterparty]:

        outer_rows = self._parse_outer_rows(path)
        if not outer_rows:
            return []

        header_inner = outer_rows[0][0]
        headers = next(
            csv.reader(
                [header_inner],
                delimiter=",",
                quotechar='"',
            )
        )

        result: list[MoneyWorkCounterparty] = []
        expected = (
            expected_role.strip().upper()
            if expected_role else None
        )

        for row_no, outer in enumerate(outer_rows[1:], start=2):
            if not outer:
                continue

            inner_csv = outer[0]

            try:
                values = next(
                    csv.reader(
                        [inner_csv],
                        delimiter=",",
                        quotechar='"',
                    )
                )
            except Exception as exc:
                self.parse_issues.append(
                    MoneyWorkParseIssue(
                        row_no=row_no,
                        issue_type="COUNTERPARTY_CSV_ERROR",
                        message=str(exc),
                        raw=inner_csv,
                    )
                )
                continue

            # Normal case: 82 logical columns. If trailing empty columns
            # were omitted, pad them. If extra columns appear because a
            # legacy text field contains unquoted commas, quarantine.
            if len(values) < len(headers):
                values = values + [""] * (len(headers) - len(values))

            if len(values) > len(headers):
                self.parse_issues.append(
                    MoneyWorkParseIssue(
                        row_no=row_no,
                        issue_type="COUNTERPARTY_COLUMN_OVERFLOW",
                        message=(
                            f"Expected {len(headers)} columns, "
                            f"got {len(values)}"
                        ),
                        raw=inner_csv,
                    )
                )
                continue

            fields = dict(zip(headers, values))
            item = MoneyWorkCounterparty(
                row_no=row_no,
                fields=fields,
                raw_inner_csv=inner_csv,
            )

            if expected and item.role_code != expected:
                self.parse_issues.append(
                    MoneyWorkParseIssue(
                        row_no=row_no,
                        issue_type="COUNTERPARTY_ROLE_MISMATCH",
                        message=(
                            f"Expected role {expected}, "
                            f"got {item.role_code or '<empty>'}"
                        ),
                        raw=inner_csv,
                    )
                )
                continue

            result.append(item)

        return result

    @staticmethod
    def summarize_articles(
        articles: Iterable[MoneyWorkArticle],
    ) -> dict[str, Any]:
        items = list(articles)
        suppliers = [a.supplier_name for a in items if a.supplier_name]
        codes = [a.legacy_code for a in items]

        return {
            "records": len(items),
            "unique_legacy_codes": len(set(codes)),
            "duplicate_legacy_codes": len(codes) - len(set(codes)),
            "unique_supplier_names": len(set(suppliers)),
        }

    def issues_summary(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        for issue in self.parse_issues:
            by_type[issue.issue_type] = (
                by_type.get(issue.issue_type, 0) + 1
            )

        return {
            "count": len(self.parse_issues),
            "by_type": by_type,
        }
