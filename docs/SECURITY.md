# Security notes

## Do not commit
- Credentials, tokens, API keys, private keys.
- Cowrie logs or datasets containing real IP addresses.
- Malware samples or binaries.
- GeoIP databases (.mmdb).

## Secrets handling
- Secrets must be injected via environment variables (e.g., `ELASTIC_PASSWORD`) or local env files not tracked by Git.
- If a secret is ever committed, it must be rotated immediately because Git history is immutable.

## Notes
- This repository includes `.example` configuration files to keep deployments reproducible without exposing sensitive data.
