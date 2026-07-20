# Jefferson

**AI-powered voter simulation engine for predicting real-world political reactions.**

Jefferson generates statistically-grounded voter populations, runs them through simulated social interactions and information exposure, and polls them to produce demographically-segmented opinion predictions — all without a single real respondent.

🌐 **Live demo:** [jefferson-one.vercel.app](https://jefferson-one.vercel.app)

> Inspired by [Park et al. (2023) — Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) and [Argyle et al. (2023) — Out of One, Many: Using Language Models to Simulate Human Samples](https://arxiv.org/html/2502.07068v1).

---

## Why this matters

Traditional polling is slow, expensive, and increasingly inaccurate — response rates have collapsed from ~35% in the 1990s to under 6% today. Local campaigns are the hardest hit, priced out of rigorous research entirely.

Jefferson is built for them. LLM-based simulation isn't a replacement for real polling, but it offers a rapid, affordable tool for hypothesis testing, message testing, and scenario planning — grounded in demographic correlations rather than generic LLM prompting.

---

## Project structure

```
Jefferson/
├── backend/              # Production backend: Prefect orchestration, Supabase persistence, CLI, FastAPI
├── web/                  # Next.js frontend (deployed at jefferson-one.vercel.app)
└── docs/archive/         # Earlier prototypes and reference implementations
    ├── voter_simulation_v1/   # In-memory Anthropic Agents SDK prototype
    └── ai-town-reference/     # Stanford Generative Agents reference code
```

The project has two active components:

- **`/backend`** — The production simulation system. Persistent storage, multi-LLM support, batch precinct simulations, news context integration, CLI tooling.
- **`/web`** — Next.js frontend providing the interactive interface and visualizations.

---

## How it works

1. **Generate a population** — Spin up N voter agents per precinct, each with a statistically-correlated demographic profile (age, gender, race, education, income, party ID, ideology, top issues, news sources) drawn from real survey data and demographic distributions.

2. **Inject context** — Optionally scrape local news for the relevant geography so agents respond to current events rather than reasoning in a vacuum.

3. **Poll the population** — Ask any question (open-ended, multiple choice, or scale). Each agent responds in-character based on their demographics, prior opinions, and news exposure. Results are aggregated and cross-tabulated by demographic segment.

The result: a synthetic survey reflecting how a demographically-realistic population might respond — at a fraction of the cost and time of traditional polling.

---

## Tech stack

**Backend** (`/backend`)
- **Python 3.12+** · core language
- **Prefect** · workflow orchestration for batch simulations
- **Supabase (PostgreSQL)** · persistence for personas, survey responses, simulations, news articles
- **FastAPI + Uvicorn** · REST API
- **Click** · CLI interface
- **Pydantic** · data validation
- **Multi-LLM** · ZhipuAI, Google Gemini, Anthropic Claude
- **BeautifulSoup4** · local news scraping
- **uv** · package management

**Frontend** (`/web`)
- **Next.js** · React framework
- **TypeScript**
- **Vercel** · deployment

---

## Quickstart

### Backend

```bash
cd backend
uv sync
cp .env.example .env
# Edit .env with your Supabase URL + at least one LLM API key

# Ingest survey data into a precinct
uv run jefferson ingest survey_data.csv --precincts precinct_001

# Scrape local news context
uv run jefferson scrape-news "San Francisco" --hours 48

# Poll a precinct
uv run jefferson poll precinct_001 "What do you think about housing policy?"

# Run a batch simulation across precincts
uv run jefferson simulate precinct_001 precinct_002 \
  --questions "How will you vote on Prop A?" "What's your top priority?" \
  --iterations 3 \
  --concurrent 50
```

### Frontend

```bash
cd web
npm install
npm run dev
```

See [`/backend/README.md`](./backend/README.md) for full CLI documentation, database schema, and API reference.

---

## Demographic correlation model

Voter attributes are not independently random — they follow weighted distributions reflecting real-world correlations:

- **Age → Political leaning**: Younger agents skew liberal, older agents conservative
- **Location → Political leaning**: Urban agents skew liberal, rural conservative
- **Education → Income**: Higher education correlates with higher income bands
- **Survey-seeded personas**: When real survey data is ingested, personas inherit empirical demographic + opinion patterns rather than synthetic distributions alone

---

## Roadmap

- [ ] **ACS demographic seeding** — Replace synthetic distributions with US Census ACS data for any specified geography
- [ ] **Polymarket integration** — Live prediction market data as an additional signal source for agent opinion formation
- [ ] **Real-time frontend** — Hybrid map visualization + live polling dashboard
- [ ] **Airflow / Prefect Cloud orchestration** — Scheduled simulation runs with automated polling report generation
- [ ] **Longitudinal tracking** — Re-poll the same persona populations over time to model opinion drift

---

## Research basis

- Park, J.S. et al. (2023). [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442). Stanford University.
- Argyle, L.P. et al. (2023). [Out of One, Many: Using Language Models to Simulate Human Samples](https://arxiv.org/html/2502.07068v1).

---

## Archive

`/docs/archive` contains earlier iterations preserved for reference:

- **`voter_simulation_v1/`** — In-memory prototype using the Anthropic Agents SDK. Demonstrates async agent orchestration with persistent opinion memory across multi-turn conversations and Twitter exposure rounds. Superseded by the `/backend` system, which adds persistence and batch processing.
- **`ai-town-reference/`** — Reference implementation from the Stanford Generative Agents project, retained as architectural reference.

---

## Author

**Jose Sirven** · [jose@sirven.xyz](mailto:jose@sirven.xyz) · [sirven.xyz](https://sirven.xyz) · [linkedin.com/in/joesirven](https://linkedin.com/in/joesirven)

## License

MIT — see [LICENSE](./LICENSE).
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
