# m99.eu Authenticated Read-Only Preflight R2
Base: `baf07f15f33d5ab011c471202951f8c12847b499`.
Replaces failed V1 transport only; existing config remains authoritative (`M99EU_PS_API_KEY`).
Uses the R2-proven one-shot fresh HTTPS connection pattern. Exactly four authenticated API GET operations:
`/api`, `/api/languages`, exact configured `/api/categories/{id}`, `/api/products?schema=blank`.
Discovers language IDs from live ISO codes and requires EN/BG/RU. No assumed IDs. No retry. No write.
