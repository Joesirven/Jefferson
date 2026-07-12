# src/tasks/database.py
"""Database connection and queries using asyncpg (Postgres)."""

from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Optional

import asyncpg

from src.models.persona import Persona

_pool: Optional[asyncpg.Pool] = None


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL must be set in environment. "
            "Example: postgresql://jefferson:jefferson@localhost:5432/jefferson"
        )
    return url


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(get_database_url(), min_size=1, max_size=10)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def _json(value: Any) -> Optional[str]:
    if value is None:
        return None
    return json.dumps(value)


def _persona_row(persona: Persona) -> Dict[str, Any]:
    data = persona.model_dump(mode="json")
    data.pop("id", None)
    return data


# ============================================================================
# PERSONA QUERIES
# ============================================================================


async def get_personas_by_precinct(precinct_id: str) -> List[Persona]:
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM personas WHERE precinct_id = $1", precinct_id)
    return [Persona(**dict(row)) for row in rows]


async def save_persona(persona: Persona) -> Dict[str, Any]:
    pool = await get_pool()
    row = _persona_row(persona)
    columns = list(row.keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    col_names = ", ".join(columns)
    values = [row[c] for c in columns]

    record = await pool.fetchrow(
        f"INSERT INTO personas ({col_names}) VALUES ({placeholders}) RETURNING *",
        *values,
    )
    return dict(record)


async def save_personas_batch(personas: List[Persona]) -> List[Dict[str, Any]]:
    if not personas:
        return []

    pool = await get_pool()
    rows = [_persona_row(p) for p in personas]
    columns = list(rows[0].keys())
    col_names = ", ".join(columns)

    inserted: List[Dict[str, Any]] = []
    async with pool.acquire() as conn:
        async with conn.transaction():
            for row in rows:
                placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
                values = [row[c] for c in columns]
                record = await conn.fetchrow(
                    f"INSERT INTO personas ({col_names}) VALUES ({placeholders}) RETURNING *",
                    *values,
                )
                inserted.append(dict(record))
    return inserted


async def get_persona_count(precinct_id: Optional[str] = None) -> int:
    pool = await get_pool()
    if precinct_id:
        return await pool.fetchval(
            "SELECT COUNT(*) FROM personas WHERE precinct_id = $1", precinct_id
        )
    return await pool.fetchval("SELECT COUNT(*) FROM personas")


# ============================================================================
# SIMULATION RESULTS
# ============================================================================


async def save_simulation_results(simulation_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
    pool = await get_pool()
    record = await pool.fetchrow(
        """
        INSERT INTO simulations (simulation_id, results, status, completed_at)
        VALUES ($1, $2::jsonb, 'completed', NOW())
        ON CONFLICT (simulation_id) DO UPDATE SET
            results = EXCLUDED.results,
            status = EXCLUDED.status,
            completed_at = NOW()
        RETURNING *
        """,
        simulation_id,
        json.dumps(results),
    )
    return dict(record)


async def save_results(
    all_results: Dict[str, Any], simulation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Save multi-precinct simulation output (used by simulation flows)."""
    sim_id = simulation_id or str(uuid.uuid4())
    return await save_simulation_results(sim_id, all_results)


async def get_simulation_results(simulation_id: str) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    record = await pool.fetchrow(
        "SELECT * FROM simulations WHERE simulation_id = $1", simulation_id
    )
    return dict(record) if record else None


async def list_simulations(limit: int = 50) -> List[Dict[str, Any]]:
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM simulations ORDER BY created_at DESC LIMIT $1", limit
    )
    return [dict(row) for row in rows]


# ============================================================================
# NEWS CONTEXT
# ============================================================================


async def get_latest_news_context(county: str, hours: int = 24) -> str:
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT title, summary FROM news_articles
        WHERE county = $1
        ORDER BY published_at DESC NULLS LAST
        LIMIT 10
        """,
        county,
    )

    if not rows:
        return ""

    context = f"Recent news from {county}:\n"
    for row in rows:
        summary = (row["summary"] or "")[:100]
        context += f"- {row['title']}: {summary}...\n"
    return context


async def upsert_news_article(article: Dict[str, Any]) -> None:
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO news_articles (title, url, summary, content, source, county, published_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (url) DO UPDATE SET
            title = EXCLUDED.title,
            summary = EXCLUDED.summary,
            content = EXCLUDED.content,
            source = EXCLUDED.source,
            scraped_at = NOW()
        """,
        article.get("title"),
        article.get("url"),
        article.get("summary"),
        article.get("content"),
        article.get("source"),
        article.get("county"),
        article.get("published_at"),
    )


# ============================================================================
# SURVEY DATA
# ============================================================================


async def get_matching_survey_respondents(
    age_range: tuple, education: str, race: str, county: Optional[str] = None
) -> List[Dict[str, Any]]:
    pool = await get_pool()
    if county:
        rows = await pool.fetch(
            "SELECT * FROM survey_responses WHERE county = $1 LIMIT 100", county
        )
    else:
        rows = await pool.fetch("SELECT * FROM survey_responses LIMIT 100")
    return [dict(row) for row in rows]


async def insert_survey_batch(batch: List[Dict[str, Any]], table: str = "survey_responses") -> int:
    if not batch:
        return 0
    if table != "survey_responses":
        raise ValueError(f"Unsupported table: {table}")

    pool = await get_pool()
    inserted = 0
    async with pool.acquire() as conn:
        async with conn.transaction():
            for record in batch:
                await conn.execute(
                    """
                    INSERT INTO survey_responses (
                        age_group, education, gender, race, income, party_id, ideology,
                        vote_history, issue_positions, top_issues, news_sources, raw_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10, $11, $12::jsonb)
                    """,
                    record.get("age_group"),
                    record.get("education"),
                    record.get("gender"),
                    record.get("race"),
                    record.get("income"),
                    record.get("party_id"),
                    record.get("ideology"),
                    _json(record.get("vote_history")),
                    _json(record.get("issue_positions")),
                    record.get("top_issues"),
                    record.get("news_sources"),
                    _json(record),
                )
                inserted += 1
    return inserted
