"""Fixtures compartilhadas para testes."""

from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from app.agent.agent import MediaAnalystOrchestrator
from app.domain.schemas import (
    AverageOrderValueByChannel,
    ChannelPerformance,
    ConversionByChannel,
    DistributionCenterPerformance,
    EngagementByChannel,
    RevenueByMonthByChannel,
    TopCategoryByChannel,
    TrafficVolumeResult,
)
from app.main import app
from config import Settings
from fastapi.testclient import TestClient


@pytest.fixture
def app_client(mock_settings: Settings) -> Generator[TestClient, None, None]:
    """Cliente HTTP para a API. get_settings é sobrescrito para desativar JWT nos testes."""
    from app.api.dependencies import get_settings

    app.dependency_overrides[get_settings] = lambda: mock_settings
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_settings() -> Settings:
    """Settings para testes: OpenAI fake, JWT desativado (jwt_secret vazio)."""
    return Settings(
        openai_api_key="sk-test-fake-key-for-tests",
        bigquery_dataset="bigquery-public-data.thelook_ecommerce",
        google_cloud_project=None,
        jwt_secret="",
        login_user="",
        login_password="",
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
def sample_conversion_results() -> list[ConversionByChannel]:
    """Dados de conversão por canal para testes."""
    return [
        ConversionByChannel(
            traffic_source="Organic",
            total_users=800,
            users_with_order=120,
            conversion_rate_pct=15.0,
        ),
    ]


@pytest.fixture
def sample_avg_order_value_results() -> list[AverageOrderValueByChannel]:
    """Dados de ticket médio por canal para testes."""
    return [
        AverageOrderValueByChannel(
            traffic_source="Search",
            total_orders=100,
            total_revenue=15000.0,
            avg_order_value=150.0,
        ),
    ]


@pytest.fixture
def sample_revenue_by_month_results() -> list[RevenueByMonthByChannel]:
    """Dados de receita por mês/canal para testes."""
    return [
        RevenueByMonthByChannel(
            traffic_source="Search",
            year_month="2024-01",
            total_revenue=5000.0,
        ),
    ]


@pytest.fixture
def sample_top_categories_results() -> list[TopCategoryByChannel]:
    """Dados de categorias por canal para testes."""
    return [
        TopCategoryByChannel(
            traffic_source="Search",
            category="Vestidos",
            total_revenue=3000.0,
            total_units=20,
        ),
    ]


@pytest.fixture
def sample_engagement_results() -> list[EngagementByChannel]:
    """Dados de engajamento por canal para testes."""
    return [
        EngagementByChannel(
            traffic_source="Instagram",
            event_count=5000,
            unique_users=800,
        ),
    ]


@pytest.fixture
def sample_distribution_center_results() -> list[DistributionCenterPerformance]:
    """Dados de performance por DC para testes."""
    return [
        DistributionCenterPerformance(
            distribution_center_name="DC SP",
            total_orders=200,
            total_revenue=30000.0,
        ),
    ]


@pytest.fixture
def mock_analytics_repository(
    sample_traffic_results: list[TrafficVolumeResult],
    sample_performance_results: list[ChannelPerformance],
    sample_conversion_results: list[ConversionByChannel],
    sample_avg_order_value_results: list[AverageOrderValueByChannel],
    sample_revenue_by_month_results: list[RevenueByMonthByChannel],
    sample_top_categories_results: list[TopCategoryByChannel],
    sample_engagement_results: list[EngagementByChannel],
    sample_distribution_center_results: list[DistributionCenterPerformance],
) -> MagicMock:
    """Repositório mock que retorna dados fixos."""
    repo = MagicMock()
    repo.get_traffic_volume.return_value = sample_traffic_results
    repo.get_channel_performance.return_value = sample_performance_results
    repo.get_conversion_by_channel.return_value = sample_conversion_results
    repo.get_average_order_value_by_channel.return_value = sample_avg_order_value_results
    repo.get_revenue_by_month_by_channel.return_value = sample_revenue_by_month_results
    repo.get_top_categories_by_channel.return_value = sample_top_categories_results
    repo.get_engagement_by_channel.return_value = sample_engagement_results
    repo.get_distribution_center_performance.return_value = (
        sample_distribution_center_results
    )
    repo.list_traffic_sources.return_value = ["Search", "Organic", "Facebook"]
    return repo
