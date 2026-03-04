"""
Cliente de baixo nível para BigQuery (Single Responsibility: executar queries).
Não conhece regras de negócio; apenas executa SQL parametrizado e retorna linhas.
"""

import logging
from typing import Any

from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from app.domain.exceptions import DataSourceError

logger = logging.getLogger(__name__)


class BigQueryClient:
    """
    Encapsula a execução de queries no BigQuery.
    Responsabilidade única: executar query e devolver resultados.
    """

    def __init__(self, project: str | None, dataset: str) -> None:
        self._client = bigquery.Client(project=project)
        self._dataset = dataset

    @property
    def dataset(self) -> str:
        """Dataset configurado (ex.: bigquery-public-data.thelook_ecommerce)."""
        return self._dataset

    def run_query(
        self,
        query: str,
        params: list[bigquery.ScalarQueryParameter] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Executa query parametrizada e retorna linhas como lista de dicts.
        Levanta DataSourceError em caso de falha.
        """
        job_config = bigquery.QueryJobConfig()
        if params:
            job_config.query_parameters = params

        try:
            job = self._client.query(query, job_config=job_config)
            rows = job.result()
            return [dict(row) for row in rows]
        except GoogleCloudError as e:
            logger.exception("BigQuery query failed")
            raise DataSourceError(f"Erro no BigQuery: {e}") from e
