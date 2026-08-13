# M99 v0.6.7.4.5.1 — Central Secrets Architecture

Central provider: HashiCorp Vault KV v2 over HTTPS.

Goals:
- Enter channel credentials once.
- Reuse them from any authorized computer.
- Keep secrets out of Git, JSON output and normal logs.
- Support central rotation and revocation.
- Avoid local plaintext secret files.

Runtime access:
- M99_VAULT_ADDR identifies the central Vault.
- M99_VAULT_TOKEN authenticates the current machine/session.
- Optional M99_VAULT_NAMESPACE is supported.

Channel secrets are stored under secret/m99/channels/<site>.
M99 scripts only read the fields required by each channel.

Security note:
No system is impossible to compromise. A new computer must authenticate to the
central vault before it can use the stored channel credentials. The design avoids
re-entering six channel API keys, while still preserving an authorization boundary.
