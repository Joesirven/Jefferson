# Jefferson

**AI-powered voter simulation engine for predicting real-world political reactions.**

Jefferson generates statistically-grounded voter populations, runs them through simulated social interactions and information exposure, and polls them to produce demographically-segmented opinion predictions — all without a single real respondent.

> Inspired by [Park et al. (2023) — Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) and [Argyle et al. (2023) — Out of One, Many: Using Language Models to Simulate Human Samples](https://arxiv.org/html/2502.07068v1).

---

## What it does

1. **Generate a population** — Spin up N voter agents, each with a statistically-correlated demographic profile (age, location, education, income, political leaning, interests) drawn from real demographic distributions.

2. **Run social simulation** — Agents are exposed to topic-relevant social media content and paired for multi-turn conversations. After each interaction, agents update their opinions based on how persuasive they found the exchange.

3. **Poll the population** — Ask any question. Each agent responds in-character based on their demographics, prior opinions, and interaction history. Results are aggregated and cross-tabulated by political leaning, age group, location, and education level.

The result: a synthetic survey that reflects how a demographically-realistic population might respond to a political question — at a fraction of the cost and time of traditional polling.

---

## Why this matters

Traditional polling is slow, expensive, and increasingly inaccurate (response rates have collapsed from ~35% in the 1990s to under 6% today). LLM-based simulation offers a complementary approach — not a replacement for real polling, but a tool for rapid hypothesis testing, message testing, and scenario planning.

Jefferson applies this to the political domain with demographically-correlated agent generation, making it more rigorous than generic LLM prompting.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Jefferson                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │ master_agent │    │ voter_agent  │                  │
│  │              │    │              │                  │
│  │ - Population │───▶│ - Demographics│                  │
│  │   generation │    │ - Opinion     │                  │
│  │ - Demographic│    │   memory      │                  │
│  │   correlations    │ - Interaction │                  │
│  └──────────────┘    │   tools       │                  │
│                      └──────────────┘                  │
│                             │                           │
│               ┌─────────────┴─────────────┐            │
│               ▼                           ▼            │
│      ┌──────────────┐           ┌──────────────┐       │
│      │  simulation  │           │   polling    │       │
│      │              │           │              │       │
│      │ - Twitter     │           │ - Per-agent  │       │
│      │   exposure    │           │   responses  │       │
│      │ - Peer        │           │ - Cross-tab  │       │
│      │   conversations          │   by demo-   │       │
│      │ - Opinion     │           │   graphics   │       │
│      │   dynamics    │           │ - Aggregate  │       │
│      └──────────────┘           │   results    │       │
│                                 └──────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### Core modules

| File | Responsibility |
|------|---------------|
| `master_agent.py` | Population generation with demographic correlations (age→political leaning, location→political leaning, education→income) |
| `voter_agent.py` | Individual voter agent with opinion tools (`remember_interaction`, `get_opinion`) |
| `simulation.py` | Async simulation engine — Twitter exposure and peer conversation rounds |
| `polling.py` | Interactive polling with demographic cross-tabulation |
| `twitter_mock.py` | Topic-relevant social content feed across 16 political topics |
| `main.py` | Entry point |

### Demographic correlation model

Voter attributes are not independently random — they follow weighted distributions that reflect real-world correlations:

- **Age → Political leaning**: Younger agents skew liberal, older agents skew conservative, matching known generational patterns
- **Location → Political leaning**: Urban agents skew liberal, rural agents skew conservative
- **Education → Income**: Higher education levels correlate with higher income bands
- **Combined**: Political leaning is a weighted average of age-based and location-based distributions, producing more nuanced profiles

### Opinion dynamics

Each agent maintains a persistent opinion store (topic → score, 1–5 scale). Opinions shift through two mechanisms:

1. **Twitter exposure**: Agent reads topic-relevant posts weighted by engagement metrics (likes, retweets), then records an opinion delta (-4 to +4)
2. **Peer conversation**: Two agents with overlapping interests hold a 3-turn dialogue. Each records how persuasive they found the exchange and updates their opinion accordingly

---

## Quickstart

```bash
# Clone and install dependencies
git clone https://github.com/joesirven/jefferson
cd jefferson/voter_simulation
pip install -r requirements.txt

# Run a simulation with 50 voters, 3 rounds
python main.py

# You'll be prompted to ask polling questions:
# > Should the federal minimum wage be raised to $20/hour?
# > How do you feel about the current state of immigration policy?
```

### Example output

```
=== POLLING RESULTS ===
Question: Should the federal government implement universal healthcare?

Voter: James (67, Male, Conservative)
  Education: High School | Income: Middle | Location: Rural
  Score: 2/5 — "Government healthcare would reduce my choices..."

Voter: Jennifer (28, Female, Very Liberal)
  Education: Graduate Degree | Income: Upper Middle | Location: Urban
  Score: 5/5 — "Healthcare is a fundamental right..."

Average score: 3.12/5

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

## Roadmap

- [ ] **FastAPI web layer** — REST API exposing simulation runs and polling endpoints
- [ ] **PostgreSQL persistence** — Store agent populations, conversation logs, and poll results
- [ ] **Real-time frontend** — Hybrid map visualization + live polling dashboard (inspired by Stanford Generative Agents UI)
- [ ] **ACS demographic seeding** — Replace synthetic demographics with distributions derived from real Census data for a specified geography
- [ ] **Polymarket integration** — Live prediction market data as an additional signal source for agent opinion formation
- [ ] **Airflow orchestration** — Scheduled simulation runs with automated polling report generation

---

## Tech stack

**Simulation**: Python · Anthropic Agents SDK · Pydantic · asyncio

**Coming**: FastAPI · PostgreSQL · Redis · Next.js · Docker

---

## Research basis

- Park, J.S. et al. (2023). [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442). Stanford University.
- Argyle, L.P. et al. (2023). [Out of One, Many: Using Language Models to Simulate Human Samples](https://arxiv.org/html/2502.07068v1).

---

## Author

**Jose Sirven** · [jose@sirven.xyz](mailto:jose@sirven.xyz) · [sirven.xyz](https://sirven.xyz)
