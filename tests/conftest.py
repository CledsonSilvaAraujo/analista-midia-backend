"""Fixtures compartilhadas para testes."""
from collections.abc import Generator
from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.agent.agent import MediaAnalystOrchestrator
from app.domain.schemas import ChannelPerformance, TrafficVolumeResult
from app.main import app
from config import Settings


@pytest.fixture
def app_client() -> Generator[TestClient, None, None]:
    """Cliente HTTP para a API (sem override de dependências)."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_settings() -> Settings:
    """Settings com OpenAI key preenchida (evita 503 em testes que chamam get_media_analyst)."""
    return Settings(
        openai_api_key="sk-test-fake-key-for-tests",
        bigquery_dataset="bigquery-public-data.thelook_ecommerce",
        google_cloud_project=None,
    )


@pytest.fixture
def mock_orchestrator() -> MediaAnalystOrchestrator:
    """Orquestrador fake que retorna resposta fixa (sem chamar LLM nem BQ)."""
    fake_llm = MagicMock()
    fake_tools: list = []

    class FakeOrchestrator(MediaAnalystOrchestrator):
        def invoke(self, question: str) -> tuple[str, list[str]]:
            return (
                "Resposta simulada para testes.",
                ["get_traffic_volume_tool"],
            )

    return FakeOrchestrator(llm_with_tools=fake_llm, tools=fake_tools)


@pytest.fixture
def client_with_mock_agent(
    app_client: TestClient,
    mock_orchestrator: MediaAnalystOrchestrator,
) -> Generator[TestClient, None, None]:
    """Cliente HTTP com agente mockado (POST /api/ask não chama LLM nem BigQuery)."""
    from app.api.dependencies import get_media_analyst

    app.dependency_overrides[get_media_analyst] = lambda: mock_orchestrator
    try:
        yield app_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def sample_traffic_results() -> list[TrafficVolumeResult]:
    """Dados de volume de tráfego para testes."""
    return [
        TrafficVolumeResult(
            traffic_source="Search",
            total_users=1500,
            period_start="2024-02-01",
            period_end="2024-02-29",
        ),
        TrafficVolumeResult(
            traffic_source="Organic",
            total_users=800,
            period_start="2024-02-01",
            period_end="2024-02-29",
        ),
    ]


@pytest.fixture
def sample_performance_results() -> list[ChannelPerformance]:
    """Dados de performance por canal para testes."""
    return [
        ChannelPerformance(
            traffic_source="Search",
            total_users=1000,
            total_orders=120,
            total_revenue=15000.0,
            revenue_per_user=15.0,
            orders_per_user=0.12,
        ),
    ]


@pytest.fixture
def mock_analytics_repository(
    sample_traffic_results: list[TrafficVolumeResult],
    sample_performance_results: list[ChannelPerformance],
) -> MagicMock:
    """Repositório mock que retorna dados fixos."""
    repo = MagicMock()
    repo.get_traffic_volume.return_value = sample_traffic_results
    repo.get_channel_performance.return_value = sample_performance_results
    repo.list_traffic_sources.return_value = ["Search", "Organic", "Facebook"]
    return repo
