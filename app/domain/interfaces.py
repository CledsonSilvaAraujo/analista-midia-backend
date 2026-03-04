"""
Interfaces (Protocols) do domínio — Dependency Inversion (SOLID).
Dependemos de abstrações, não de implementações concretas.
"""
from datetime import date
from typing import Protocol, runtime_checkable

from app.domain.schemas import ChannelPerformance, TrafficVolumeResult


@runtime_checkable
class IAnalyticsRepository(Protocol):
    """
    Contrato para acesso a dados de analytics (tráfego e performance).
    Qualquer implementação (BigQuery, mock, cache) pode ser injetada.
    """

    def get_traffic_volume(
        self,
        start_date: date,
        end_date: date,
        traffic_source: str | None = None,
    ) -> list[TrafficVolumeResult]:
        """Retorna volume de usuários por canal no período."""
        ...

    def get_channel_performance(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ChannelPerformance]:
        """Retorna métricas de performance por canal."""
        ...

    def list_traffic_sources(self) -> list[str]:
        """Retorna lista de canais de tráfego disponíveis."""
        ...
