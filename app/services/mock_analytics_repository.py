"""
Repositório mock que retorna dados de exemplo (útil quando BigQuery não está disponível ou sem permissão).
"""

from datetime import date

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


class MockAnalyticsRepository:
    """Implementa IAnalyticsRepository com dados fictícios para demonstração."""

    def get_traffic_volume(
        self,
        start_date: date,
        end_date: date,
        traffic_source: str | None = None,
    ) -> list[TrafficVolumeResult]:
        """Retorna volume fictício por canal no período."""
        all_channels = [
            ("Search", 12_500),
            ("Organic", 8_200),
            ("Facebook", 5_100),
            ("Instagram", 3_800),
            ("Email", 2_400),
        ]
        if traffic_source:
            all_channels = [(s, n) for s, n in all_channels if s == traffic_source]
        return [
            TrafficVolumeResult(
                traffic_source=source,
                total_users=count,
                period_start=str(start_date),
                period_end=str(end_date),
            )
            for source, count in all_channels
        ]

    def get_channel_performance(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ChannelPerformance]:
        """Retorna performance fictícia por canal."""
        return [
            ChannelPerformance(
                traffic_source="Search",
                total_users=12_500,
                total_orders=1_875,
                total_revenue=285_000.0,
                revenue_per_user=22.80,
                orders_per_user=0.15,
            ),
            ChannelPerformance(
                traffic_source="Organic",
                total_users=8_200,
                total_orders=1_148,
                total_revenue=172_200.0,
                revenue_per_user=21.00,
                orders_per_user=0.14,
            ),
            ChannelPerformance(
                traffic_source="Facebook",
                total_users=5_100,
                total_orders=612,
                total_revenue=91_800.0,
                revenue_per_user=18.00,
                orders_per_user=0.12,
            ),
            ChannelPerformance(
                traffic_source="Instagram",
                total_users=3_800,
                total_orders=456,
                total_revenue=68_400.0,
                revenue_per_user=18.00,
                orders_per_user=0.12,
            ),
        ]

    def get_conversion_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ConversionByChannel]:
        """Retorna conversão fictícia por canal."""
        return [
            ConversionByChannel(
                traffic_source="Organic",
                total_users=8_200,
                users_with_order=1_148,
                conversion_rate_pct=14.00,
            ),
            ConversionByChannel(
                traffic_source="Search",
                total_users=12_500,
                users_with_order=1_875,
                conversion_rate_pct=15.00,
            ),
            ConversionByChannel(
                traffic_source="Facebook",
                total_users=5_100,
                users_with_order=612,
                conversion_rate_pct=12.00,
            ),
            ConversionByChannel(
                traffic_source="Instagram",
                total_users=3_800,
                users_with_order=456,
                conversion_rate_pct=12.00,
            ),
        ]

    def get_average_order_value_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[AverageOrderValueByChannel]:
        """Ticket médio fictício por canal."""
        return [
            AverageOrderValueByChannel(
                traffic_source="Organic",
                total_orders=1_148,
                total_revenue=172_200.0,
                avg_order_value=150.0,
            ),
            AverageOrderValueByChannel(
                traffic_source="Search",
                total_orders=1_875,
                total_revenue=285_000.0,
                avg_order_value=152.0,
            ),
        ]

    def get_revenue_by_month_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[RevenueByMonthByChannel]:
        """Receita por mês/canal fictícia."""
        return [
            RevenueByMonthByChannel(
                traffic_source="Search",
                year_month="2024-01",
                total_revenue=95_000.0,
            ),
            RevenueByMonthByChannel(
                traffic_source="Search",
                year_month="2024-02",
                total_revenue=98_000.0,
            ),
            RevenueByMonthByChannel(
                traffic_source="Organic",
                year_month="2024-01",
                total_revenue=58_000.0,
            ),
        ]

    def get_top_categories_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 10,
    ) -> list[TopCategoryByChannel]:
        """Categorias mais vendidas fictícias por canal."""
        return [
            TopCategoryByChannel(
                traffic_source="Search",
                category="Vestidos",
                total_revenue=85_000.0,
                total_units=420,
            ),
            TopCategoryByChannel(
                traffic_source="Organic",
                category="Calçados",
                total_revenue=52_000.0,
                total_units=310,
            ),
        ]

    def get_engagement_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EngagementByChannel]:
        """Engajamento fictício por canal."""
        return [
            EngagementByChannel(
                traffic_source="Instagram",
                event_count=45_000,
                unique_users=3_200,
            ),
            EngagementByChannel(
                traffic_source="Facebook",
                event_count=38_000,
                unique_users=4_100,
            ),
        ]

    def get_distribution_center_performance(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DistributionCenterPerformance]:
        """Performance fictícia por centro de distribuição."""
        return [
            DistributionCenterPerformance(
                distribution_center_name="DC São Paulo",
                total_orders=3_200,
                total_revenue=480_000.0,
            ),
            DistributionCenterPerformance(
                distribution_center_name="DC Campinas",
                total_orders=1_800,
                total_revenue=270_000.0,
            ),
        ]

    def list_traffic_sources(self) -> list[str]:
        """Lista canais fictícios."""
        return ["Search", "Organic", "Facebook", "Instagram", "Email"]
