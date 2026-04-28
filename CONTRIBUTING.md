
---
# Contributing to AIVP

Thanks for your interest! We welcome issues, discussions, and PRs.

## Quick Start
1. Fork the repo and create a feature branch: `git checkout -b feat/short-name`.
2. Run locally (Windows): `dev.ps1` — or see README for manual steps.
3. Follow code style: React/TS on frontend, FastAPI/Python on backend.

## Branching & PRs
- `main` is protected — open PRs from branches.
- Keep PRs focused; include screenshots for UI changes.
- Link related issues (e.g., `Closes #123`).

## DCO (Developer Certificate of Origin)
All commits must be signed off:
```
Signed-off-by: Your Name <email@example.com>
```
Use `git commit -s` to add it automatically. By signing-off you certify your contribution under the project license.

## Commit style
- Conventional-ish: `feat: …`, `fix: …`, `docs: …`, `refactor: …`.
- Keep messages concise; body explains the why.

## Adding a new Lab
- Place UI under `apps/web/src/` and backend logic under `apps/api/`.
- Include a short scenario and objective; wire a dynamic secret.
- Add tests or a demo prompt that proves the lab works.

## Security issues
Please **do not** open public issues for vulnerabilities. Email the maintainers or use the security policy contact.

## License
Unless noted otherwise, contributions are under the repository’s license.