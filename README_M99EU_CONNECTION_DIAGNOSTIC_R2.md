# M99 m99.eu Connection Diagnostic R2
Base stable checkpoint: `77ec326229a723c78b1b3b6ea63b8321c4c09376`.

Purpose: diagnose WinError 10054 observed before any HTTP response from authenticated `/api`.
Stages: DNS, TCP/443, TLS, one GET `/`, one unauthenticated GET `/api`, one authenticated GET `/api`.
No retry. GET only. Credential never printed. Response body not printed. No write.
The failed V1 authenticated preflight remains NOT STABLE and is not used as a base.
