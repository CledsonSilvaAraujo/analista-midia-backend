"""
Repositório mock que retorna dados de exemplo (útil quando BigQuery não está disponível ou sem permissão).
"""

from datetime import date

from app.domain.schemas import ChannelPerformance, TrafficVolumeResult


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

    def list_traffic_sources(self) -> list[str]:
        """Lista canais fictícios."""
        return ["Search", "Organic", "Facebook", "Instagram", "Email"]
