"""
Injeção de dependências (Dependency Inversion + FastAPI Depends).
Cada dependência tem uma única responsabilidade; a composição é feita aqui.
"""
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.agent.agent import MediaAnalystOrchestrator
from app.agent.agent_factory import create_media_analyst_orchestrator
from app.domain.interfaces import IAnalyticsRepository
from app.services.analytics_repository import BigQueryAnalyticsRepository
from app.services.bigquery_client import BigQueryClient
from config import Settings


@lru_cache
def get_settings() -> Settings:
    """Settings singleton (lê .env uma vez)."""
    return Settings()


def get_bigquery_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> BigQueryClient:
    """Cliente de baixo nível para BigQuery."""
    return BigQueryClient(
        project=settings.google_cloud_project,
        dataset=settings.bigquery_dataset,
    )


def get_analytics_repository(
    client: Annotated[BigQueryClient, Depends(get_bigquery_client)],
) -> BigQueryAnalyticsRepository:
    """Repositório de analytics (implementação concreta para BQ)."""
    return BigQueryAnalyticsRepository(client=client)


def get_media_analyst(
    settings: Annotated[Settings, Depends(get_settings)],
    repository: Annotated[IAnalyticsRepository, Depends(get_analytics_repository)],
) -> MediaAnalystOrchestrator:
    """Orquestrador do agente (com LLM e tools já montados)."""
    return create_media_analyst_orchestrator(settings, repository)
