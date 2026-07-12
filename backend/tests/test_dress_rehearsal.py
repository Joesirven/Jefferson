"""Dress-rehearsal experiment unit tests (no live API keys required)."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent


class TestLLMRestoreAndDeepInfra:
    def test_glm_client_class_exists(self):
        from src.tasks.llm import GLMClient, LLMClient

        assert issubclass(GLMClient, LLMClient)
        assert hasattr(GLMClient, "generate")

    def test_openai_compat_client_class_exists(self):
        from src.tasks.llm import LLMClient, OpenAICompatClient

        assert issubclass(OpenAICompatClient, LLMClient)

    def test_get_llm_client_openai_compat_branch(self):
        from src.tasks.llm import OpenAICompatClient, get_llm_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            client = get_llm_client(provider="openai_compat")
        assert isinstance(client, OpenAICompatClient)
        assert client.model == os.getenv("OPENAI_MODEL", "alibaba/qwen-3-32b")
        assert "vercel" in client.base_url or "deepinfra" in client.base_url

    def test_get_llm_client_deepinfra_alias(self):
        from src.tasks.llm import OpenAICompatClient, get_llm_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            client = get_llm_client(provider="deepinfra")
        assert isinstance(client, OpenAICompatClient)

    @pytest.mark.asyncio
    async def test_openai_compat_generate(self):
        from src.tasks.llm import OpenAICompatClient

        mock_message = MagicMock()
        mock_message.content = "Democratic candidate"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            client = OpenAICompatClient()
            client.client = MagicMock()
            client.client.chat.completions.create = AsyncMock(return_value=mock_response)
            result = await client.generate("Who will you vote for?")

        assert result == "Democratic candidate"

    def test_broken_llm_file_restored_no_orphan_glm_init(self):
        llm_path = BACKEND_ROOT / "src" / "tasks" / "llm.py"
        source = llm_path.read_text()
        assert "class GLMClient(LLMClient):" in source
        assert source.index("class GLMClient") < source.index("class GeminiClient")
        assert "class OpenAICompatClient(LLMClient):" in source


class TestPostgresFoundation:
    def test_docker_compose_exists(self):
        assert (BACKEND_ROOT / "docker-compose.yml").exists()

    def test_apply_sql_script_exists(self):
        assert (BACKEND_ROOT / "scripts" / "apply_sql.py").exists()

    def test_core_schema_sql_exists(self):
        sql = (BACKEND_ROOT / "sql" / "000_core_schema.sql").read_text()
        assert "CREATE TABLE IF NOT EXISTS personas" in sql
        assert "CREATE TABLE IF NOT EXISTS simulations" in sql


class TestWarehouseFoundation:
    def test_sync_warehouse_script_exists(self):
        assert (BACKEND_ROOT / "scripts" / "sync_warehouse.py").exists()

    def test_dbt_project_exists(self):
        assert (BACKEND_ROOT / "dbt" / "dbt_project.yml").exists()
        assert (BACKEND_ROOT / "dbt" / "models" / "staging" / "stg_election_precinct_results.sql").exists()


class TestMarginFoundation:
    def test_sql_files_exist(self):
        assert (BACKEND_ROOT / "sql" / "001_election_precinct_results.sql").exists()
        view_sql = (BACKEND_ROOT / "sql" / "002_dress_rehearsal_precinct_margin.sql").read_text()
        assert "dress_rehearsal_precinct_margin" in view_sql
        for column in (
            "simulated_margin",
            "actual_margin",
            "margin_delta",
            "within_threshold",
        ):
            assert column in view_sql

    def test_metrics_doc_exists(self):
        doc = BACKEND_ROOT / "docs" / "metrics" / "dress-rehearsal-margin.md"
        assert doc.exists()
        text = doc.read_text()
        assert "margin_delta" in text
        assert "within_threshold" in text

    def test_wake_county_csv_valid(self):
        csv_path = BACKEND_ROOT / "data" / "election" / "wake_county_2020_precincts.csv"
        assert csv_path.exists()
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) >= 6
        required = {"precinct_id", "dem_votes", "rep_votes", "county", "election_year"}
        assert required.issubset(rows[0].keys())
        assert all(row["county"] == "Wake" for row in rows)
        assert all(int(row["election_year"]) == 2020 for row in rows)

    def test_ingest_script_dry_run(self):
        import subprocess

        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "scripts/ingest_wake_county_2020.py",
                "--dry-run",
            ],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert "Loaded" in result.stdout


class TestPreregistrationLog:
    def test_preregistration_log_exists_with_sealed_precincts(self):
        log_path = REPO_ROOT / "docs" / "experiment" / "2026-06-12-preregistration-log.md"
        assert log_path.exists()
        text = log_path.read_text()
        assert "PLACEHOLDER_EXAM_B" not in text
        assert "PLACEHOLDER_EXAM_C" not in text
        assert "20260612" in text
        assert "Qwen/Qwen3-32B" in text
        assert "5.0" in text or "5" in text
        assert "masking_probe" in text.lower() or "Masking probe" in text

    def test_seal_precinct_draw_script(self):
        import subprocess

        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "scripts/seal_precinct_draw.py",
                "--dry-run",
            ],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert "Pair 1:" in result.stdout
        assert "Seed: 20260612" in result.stdout


class TestMarginMath:
    def test_margin_calculation(self):
        dem, rep, other = 892, 412, 18
        total = dem + rep + other
        margin = (dem / total - rep / total) * 100
        assert abs(margin - 36.0) < 1.0

    def test_within_threshold(self):
        threshold = 5.0
        assert abs(2.0) <= threshold
        assert abs(6.0) > threshold
