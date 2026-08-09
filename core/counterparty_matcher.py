from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from core.counterparty_normalizer import NormalizedCounterparty


@dataclass
class CounterpartyCluster:
    cluster_key: str
    canonical: NormalizedCounterparty
    members: list[NormalizedCounterparty] = field(default_factory=list)
    roles: set[str] = field(default_factory=set)
    conflicts: list[str] = field(default_factory=list)

    def add(self, item: NormalizedCounterparty) -> None:
        self.members.append(item)
        self.roles.update(item.roles)

        if (
            self.canonical.vat_id
            and item.vat_id
            and self.canonical.vat_id != item.vat_id
        ):
            self.conflicts.append(
                f"VAT conflict: {self.canonical.vat_id} vs {item.vat_id}"
            )

        if (
            self.canonical.company_id
            and item.company_id
            and self.canonical.company_id != item.company_id
        ):
            self.conflicts.append(
                f"Company ID conflict: {self.canonical.company_id} "
                f"vs {item.company_id}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_key": self.cluster_key,
            "canonical": self.canonical.to_dict(),
            "roles": sorted(self.roles),
            "member_count": len(self.members),
            "source_rows": [
                {
                    "source_system": item.source_system,
                    "source_row_no": item.source_row_no,
                }
                for item in self.members
            ],
            "conflicts": list(dict.fromkeys(self.conflicts)),
        }


class CounterpartyMatcher:

    @staticmethod
    def identity_key(item: NormalizedCounterparty) -> str:
        if item.vat_id:
            return f"VAT:{item.vat_id}"

        if item.company_id:
            return f"CID:{item.country_code}:{item.company_id}"

        return item.fallback_identity_key()

    def cluster(
        self,
        items: Iterable[NormalizedCounterparty],
    ) -> list[CounterpartyCluster]:

        clusters: dict[str, CounterpartyCluster] = {}

        for item in items:
            key = self.identity_key(item)

            if key not in clusters:
                cluster = CounterpartyCluster(
                    cluster_key=key,
                    canonical=item,
                )
                cluster.add(item)
                clusters[key] = cluster
            else:
                clusters[key].add(item)

        return list(clusters.values())

    def summary(
        self,
        items: Iterable[NormalizedCounterparty],
    ) -> dict[str, Any]:

        data = list(items)
        clusters = self.cluster(data)

        return {
            "source_rows": len(data),
            "unique_counterparty_clusters": len(clusters),
            "duplicate_clusters": sum(
                1 for cluster in clusters
                if len(cluster.members) > 1
            ),
            "multi_role_clusters": sum(
                1 for cluster in clusters
                if {"CUSTOMER", "SUPPLIER"}.issubset(cluster.roles)
            ),
            "conflict_clusters": sum(
                1 for cluster in clusters
                if cluster.conflicts
            ),
        }
