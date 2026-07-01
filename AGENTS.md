# AGENTS.md

## Cursor Cloud specific instructions

Jefferson is a monorepo with two active components. Standard commands live in
`README.md`, `backend/README.md`, and `web/package.json`; this section only
captures non-obvious setup/run caveats for cloud agents.

### Services overview

| Service | Path | Runnable without secrets? | How to run (dev) |
|---------|------|---------------------------|------------------|
| Web frontend (Next.js) | `web/` | Yes | `pnpm -C web run dev` (serves http://localhost:3000) |
| Backend CLI/API (FastAPI + Prefect) | `backend/` | No (needs Supabase + an LLM key) | `uv run --directory backend uvicorn src.api.main:app --reload` |

The update script already installs deps for both (`pnpm` for `web`, `uv sync`
for `backend`). `uv` is installed to `~/.local/bin` and is on PATH for
interactive shells via `~/.bashrc`.

### Web (`web/`)

- Package manager is `pnpm` (see `web/pnpm-lock.yaml`); do not use npm/yarn there.
- Lint: `pnpm -C web run lint`. Build: `pnpm -C web run build`. Dev: `pnpm -C web run dev`.
- The `sharp` build script is intentionally left unapproved; it is only needed
  for production image optimization and does not affect dev.
- `web/public/videos/*.mp4|*.mov` are Git LFS pointer stubs (~130 bytes), not
  real media, so the `/about` and `/demo` video players show a black frame in
  this environment. The pages and their interactive controls still render/work.

### Backend (`backend/`)

- Package manager is `uv`. From repo root use `uv run --directory backend ...`,
  or `cd backend && uv run ...`.
- Runtime imports use a `src`-rooted layout (`from src.flows...`). The standalone
  test scripts in `backend/` instead prepend `backend/src` to `sys.path` and
  import as `from models...` / `from utils...`; run them from the `backend/`
  directory.
- Tests that need NO external services or API keys:
  `uv run --directory backend pytest test_survey_parser.py test_precinct_configs.py`
  and `uv run --directory backend python test_persona_generation.py`.
- Lint/format/typecheck: `uv run --directory backend ruff check src/`,
  `ruff format src/`, `mypy src/` (ruff currently reports pre-existing findings).
- Actually running polls/simulations requires `SUPABASE_URL`, `SUPABASE_ANON_KEY`
  and at least one LLM key (`ZHIPUAI_API_KEY` / `GEMINI_API_KEY` /
  `ANTHROPIC_API_KEY`); copy `backend/.env.example` to `backend/.env`.
- Known pre-existing code defects (not environment issues; do not "fix" as part
  of setup): `backend/src/flows/ingestion.py` has a `SyntaxError` (unclosed paren
  near line 525) that blocks importing the CLI and the FastAPI app, and
  `backend/src/tasks/llm.py` is a corrupted variant that imports `zai` (the
  correct/full version is `backend/src/tasks/llm.py.backup`).
