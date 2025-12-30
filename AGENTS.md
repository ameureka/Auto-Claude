# Repository Guidelines

## Project Structure & Module Organization
- `apps/backend/` houses the Python backend/CLI and agent logic.
  - Key modules: `core/` (client/auth/security), `agents/`, `spec_agents/`, `integrations/`, `prompts/`.
- `apps/frontend/` contains the Electron desktop UI (React/TypeScript); shared UI primitives live in `apps/frontend/src/renderer/components/ui/`.
- `tests/` holds the pytest suite; `scripts/` has build utilities; `guides/` and `docs/` are reference material.

## Build, Test, and Development Commands
- `npm run install:all` installs backend + frontend dependencies.
- `npm run dev` starts the Electron dev server with hot reload.
- `npm start` builds and runs the desktop app.
- `npm run build` builds the frontend; `npm run package` creates a distributable.
- CLI workflow (backend): `cd apps/backend && python spec_runner.py --interactive`, then `python run.py --spec 001`.

## Coding Style & Naming Conventions
- Python: PEP 8, type hints, docstrings for public APIs; 4-space indent; `ruff` + `ruff-format`.
- TypeScript/React: 2-space indent, functional components with hooks, prefer named exports; `eslint` + `npm run typecheck`.
- General: no trailing whitespace, newline at EOF, keep lines under 100 chars when practical.

## Testing Guidelines
- Backend: pytest in `tests/` (files `tests/test_*.py`); run `npm run test:backend` or `apps/backend/.venv/bin/pytest tests/ -v`.
- Frontend: vitest via `npm test`, coverage via `npm run test:coverage`, E2E via `npm run test:e2e` (requires `npm run build`).
- Requirements: new features include tests; bug fixes add regression tests; avoid coverage regressions.

## Commit & Pull Request Guidelines
- Commit format: `<type>: <subject>` with optional body/footer; types: feat, fix, docs, style, refactor, test, chore.
- Branch from `develop` and target `develop` for PRs; use prefixes like `feature/`, `fix/`, `docs/`.
- PRs must pass CI (tests, lint, typecheck); include a clear description, linked issues, and screenshots for UI changes; list breaking changes.

## Configuration Notes
- Create `apps/backend/.env` from `apps/backend/.env.example`; set `CLAUDE_CODE_OAUTH_TOKEN`.
- AI integrations use the Claude Agent SDK (see `apps/backend/core/client.py`).
