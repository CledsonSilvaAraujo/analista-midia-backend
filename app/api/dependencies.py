"""
Injeção de dependências (Dependency Inversion + FastAPI Depends).
Cada dependência tem uma única responsabilidade; a composição é feita aqui.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from config import Settings
from config.exceptions import ConfigurationError
from fastapi import Depends

from app.agent.agent import MediaAnalystOrchestrator
from app.agent.agent_factory import create_media_analyst_orchestrator
from app.domain.interfaces import IAnalyticsRepository
from app.services.analytics_repository import BigQueryAnalyticsRepository
from app.services.bigquery_client import BigQueryClient
from app.services.mock_analytics_repository import MockAnalyticsRepository


@lru_cache
def get_settings() -> Settings:
    """Settings singleton (lê .env uma vez)."""
    return Settings()


def get_bigquery_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> BigQueryClient:
    """Cliente de baixo nível para BigQuery."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and not Path(creds_path).is_file():
        raise ConfigurationError(
            f"Arquivo de credenciais não encontrado: {creds_path}. "
            "No Docker, use GOOGLE_APPLICATION_CREDENTIALS=/app/keys/seu-arquivo.json "
            "e coloque o JSON na pasta keys/ (o docker-compose monta ./keys em /app/keys). "
            "Para testar sem BigQuery, use USE_MOCK_ANALYTICS=true no .env."
        )
    return BigQueryClient(
        project=settings.google_cloud_project,
        dataset=settings.bigquery_dataset,
    )


def get_analytics_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> IAnalyticsRepository:
    """Repositório de analytics: mock (USE_MOCK_ANALYTICS=true) ou BigQuery real."""
    if settings.use_mock_analytics:
        return MockAnalyticsRepository()
    client = get_bigquery_client(settings)
    return BigQueryAnalyticsRepository(client=client)


def get_media_analyst(
    settings: Annotated[Settings, Depends(get_settings)],
    repository: Annotated[IAnalyticsRepository, Depends(get_analytics_repository)],
) -> MediaAnalystOrchestrator:
    """Orquestrador do agente (com LLM e tools já montados)."""
    return create_media_analyst_orchestrator(settings, repository)
