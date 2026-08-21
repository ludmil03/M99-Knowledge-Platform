# ADR-0001 — Anti-loop Project Governance

## Status
ACCEPTED

## Context
M99 Knowledge Platform has accumulated multiple README generations, architecture
documents, test reports and implementation milestones. A human-readable README is
necessary but no longer sufficient to reliably distinguish a decided rule from an
implemented feature, a tested capability, a failed implementation attempt or a
genuinely open question.

Repeatedly reopening already-decided architecture creates circular development.

## Decision
Before proposing architecture or reopening a design question, consult:

1. `governance/DECISION_REGISTRY.yaml`
2. `governance/M99_CURRENT_CONTEXT.yaml`
3. `PROJECT_STATE.md`
4. latest master README
5. relevant ADR
6. relevant tests and implementation history

Rules:
- `DECIDED + NOT_IMPLEMENTED` means implement the decision.
- `IMPLEMENTED + NOT_TESTED` means test it.
- `TESTED` remains current until explicitly superseded.
- `SUPERSEDED` must not be proposed as current design.
- `OPEN/DEFERRED` may be discussed.
- A failed implementation does not reopen a `DECIDED` rule.

## Consequences
The project gains machine-readable context and can distinguish normative design from
implementation progress. New development should update the registries when a
significant decision or implementation state changes.

README remains the master human-readable constitution.
