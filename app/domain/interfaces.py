"""
Interfaces (Protocols) do domínio — Dependency Inversion (SOLID).
Dependemos de abstrações, não de implementações concretas.
"""

from datetime import date
from typing import Protocol, runtime_checkable

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

    def get_conversion_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ConversionByChannel]:
        """Retorna taxa de conversão (% usuários que compraram) por canal."""
        ...

    def get_average_order_value_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[AverageOrderValueByChannel]:
        """Retorna ticket médio (receita / pedidos) por canal."""
        ...

    def get_revenue_by_month_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[RevenueByMonthByChannel]:
        """Retorna receita por mês e por canal (série temporal)."""
        ...

    def get_top_categories_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 10,
    ) -> list[TopCategoryByChannel]:
        """Retorna categorias mais vendidas por canal."""
        ...

    def get_engagement_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EngagementByChannel]:
        """Retorna contagem de eventos e usuários únicos por canal."""
        ...

    def get_distribution_center_performance(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DistributionCenterPerformance]:
        """Retorna performance (pedidos, receita) por centro de distribuição."""
        ...

    def list_traffic_sources(self) -> list[str]:
        """Retorna lista de canais de tráfego disponíveis."""
        ...
