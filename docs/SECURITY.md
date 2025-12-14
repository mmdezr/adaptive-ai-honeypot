# Security notes

- Do not commit real credentials, API keys, private keys, or tokens.
- Runtime artifacts are excluded from the repository:
  - Cowrie logs / datasets with real IP addresses
  - GeoLite2 databases (.mmdb)
  - Malware samples / binaries
- Secrets must be injected via environment variables (e.g., ELASTIC_PASSWORD).
- If a secret is committed, it must be rotated immediately because Git history is immutable.
