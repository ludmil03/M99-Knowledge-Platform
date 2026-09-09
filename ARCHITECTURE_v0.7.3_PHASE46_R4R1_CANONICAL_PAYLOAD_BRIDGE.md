# Phase 4.6 R4→R1 Canonical Payload Bridge + Preview Gate

Status: candidate for Windows acceptance; NO channel write.

Identifier contract recovered from README/governance:
- M99 Reference (`M99-` + digits) = permanent canonical/channel identity.
- Supplier reference/SKU = SupplierMapping external identifier.
- Manufacturer reference/MPN = Manufacturer external identifier, accepted only from exact official manufacturer evidence.
- Equal textual values do not merge these roles.
- Supplier source is authoritative for supplier reference/commercial evidence; official manufacturer is authoritative for model/MPN and technical facts.

This revision persists supplier evidence into the R4 durable sidecar so variants/availability survive the R4→R1 handoff, regenerates content with explicit Manufacturer/MPN semantics, renders a read-only m99.eu payload preview, and hard-locks live write until the adapter is separately accepted.
