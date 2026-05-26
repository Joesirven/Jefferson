# Jefferson

**AI-powered synthetic voter simulation engine for predicting real-world political reactions.**

Jefferson generates statistically-grounded voter populations, runs them through simulated social interactions and information exposure, and polls them to produce demographically-segmented opinion predictions — all without a single real respondent.

Live demo: **[jefferson-one.vercel.app](https://jefferson-one.vercel.app)**

> Inspired by [Park et al. (2023) — Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) and [Argyle et al. (2023) — Out of One, Many: Using Language Models to Simulate Human Samples](https://arxiv.org/html/2502.07068v1).

---

## Why this matters

Traditional polling is slow, expensive, and increasingly inaccurate — response rates have collapsed from ~35% in the 1990s to under 6% today. LLM-based simulation offers a complementary approach: not a replacement for real polling, but a tool for rapid hypothesis testing, message testing, and scenario planning.

Jefferson applies this to the political domain with demographically-correlated agent generation, multi-LLM support, persistent Supabase storage, and Prefect-orchestrated batch simulation across real precinct geographies.

---

## Repository structure

```
Jefferson/
├── backend/              ← Python simulation engine (Prefect + Supabase + FastAPI)
├── web/                  ← Next.js frontend (live at jefferson-one.vercel.app)
├── docs/archive/
│   ├── voter_simulation_v1/   ← original Anthropic Agents SDK prototype
│   └── ai-town-reference/     ← generative agent UI reference (Stanford AI Town fork)
├── README.md
└── LICENSE
```

---

## Backend (`/backend`)

The simulation engine powers the full pipeline: ingest survey data, generate synthetic voter personas, run LLM-driven polls, and orchestrate batch simulations across precincts.

### Technology stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Orchestration | Prefect |
| Persistence | Supabase (Postgres) |
| API | FastAPI + Uvicorn |
| CLI | Click |
| LLM providers | Anthropic (Claude), Google Gemini, ZhipuAI |
| Web scraping | BeautifulSoup4 |
| Data | Pydantic, Pandas |
| Package manager | uv |

### Setup

```bash
cd backend
cp .env.example .env   # fill in SUPABASE_URL, SUPABASE_ANON_KEY, and at least one LLM key
uv sync
```

### CLI quick reference

```bash
# Ingest survey data into Supabase
uv run jefferson ingest survey_data.csv --precincts precinct1 precinct2

# Scrape local news for context-aware responses
uv run jefferson scrape-news "San Francisco" --hours 48

# Poll a precinct on a question
uv run jefferson poll precinct_id "What do you think about housing policy?"

# Multiple-choice question
uv run jefferson poll precinct_id "Should we build more affordable housing?" \
  --type choice --options "Yes" "No" "Unsure"

# Run a full batch simulation across precincts
uv run jefferson simulate precinct1 precinct2 \
  --questions "How will you vote on Prop A?" "What's your top priority?" \
  --iterations 3 --concurrent 50

# List recent simulations
uv run jefferson list-sims --limit 10

# Interactive polling session
uv run jefferson interactive-poll precinct_id
```

### Backend structure

```
backend/src/
├── cli.py              # Click commands
├── api/main.py         # FastAPI app
├── flows/
│   ├── ingestion.py    # Prefect ingestion pipelines
│   └── simulation.py   # Prefect simulation workflows
├── models/persona.py   # Pydantic persona model
└── tasks/
    ├── database.py     # Supabase queries
    ├── llm.py          # Multi-LLM client management
    └── news.py         # News scraping
```

---

## Frontend (`/web`)

Next.js app deployed to [jefferson-one.vercel.app](https://jefferson-one.vercel.app).

```bash
cd web
npm install
npm run dev    # http://localhost:3000
```

---

## How the simulation works

1. **Generate a population** — Spin up N voter agents, each with a statistically-correlated demographic profile (age, location, education, income, political leaning) drawn from real precinct survey data or synthetic distributions.

2. **Add news context** — Scrape local news and inject it into agent context so responses reflect current events in the simulated geography.

3. **Run polls** — Ask any question (open-ended, multiple choice, or scale). Each agent responds in-character based on their demographics, prior opinions, and news context. Results are aggregated and cross-tabulated by political leaning, age group, location, and education level.

### Example output

```
=== POLLING RESULTS ===
Question: Should the federal government implement universal healthcare?

By political leaning:
  Very Liberal:      4.6/5 (8 voters)
  Liberal:           3.9/5 (14 voters)
  Moderate:          3.1/5 (12 voters)
  Conservative:      2.2/5 (10 voters)
  Very Conservative: 1.4/5 (6 voters)

By age group:
  18–29:  3.8/5 (18 voters)
  30–44:  3.3/5 (14 voters)
  45–64:  2.9/5 (11 voters)
  65+:    2.4/5 (7 voters)
```

---

## Environment variables

Create `backend/.env` (copy from `backend/.env.example`):

```bash
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# LLM providers (at least one required)
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
ZHIPUAI_API_KEY=your_key

# Optional
PREFECT_SERVER_ANALYTICS_ENABLED=false
DO_NOT_TRACK=1
```

---

## Archive (`/docs/archive`)

| Directory | What it is |
|-----------|-----------|
| `voter_simulation_v1/` | Original prototype using the Anthropic Agents SDK — simple async simulation without persistence or orchestration |
| `ai-town-reference/` | Fork of the Stanford AI Town generative-agent UI (Convex + Vite) — kept as a reference for real-time agent visualization patterns |

---

## Research basis

- Park, J.S. et al. (2023). [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442). Stanford University.
- Argyle, L.P. et al. (2023). [Out of One, Many: Using Language Models to Simulate Human Samples](https://arxiv.org/html/2502.07068v1).

---

## Author

**Jose Sirven** · [jose@sirven.xyz](mailto:jose@sirven.xyz) · [sirven.xyz](https://sirven.xyz)
