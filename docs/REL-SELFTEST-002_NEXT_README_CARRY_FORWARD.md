# Carry-forward decision for next master README

Decision ID: REL-SELFTEST-002
Status: DECIDED
Date: 2026-09-07

Before any user-facing M99 installer, diagnostic or release candidate is delivered, the assistant must proactively search for adjacent failure modes and execute every practical local/static/mocked simulation available for the affected end-to-end path. The operator's Windows/CMD run is the final real-environment acceptance, not first-line debugging. Minor defects discovered internally are consolidated before delivery; tests are not weakened to obtain green status. Fixed architecture and accepted safety contracts are preserved unless explicit superseding evidence/decision exists.

Mandatory carry-forward: include this decision in the next master README and machine-readable decision registry/current state.
