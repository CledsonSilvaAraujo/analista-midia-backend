"""
Repositório de analytics (Repository Pattern).
Implementa IAnalyticsRepository usando BigQuery — Adapter do BQ para o domínio.
"""

from datetime import date
from typing import TYPE_CHECKING

from google.cloud import bigquery

from app.domain.schemas import ChannelPerformance, TrafficVolumeResult
from app.services.bigquery_client import BigQueryClient

if TYPE_CHECKING:
    from app.domain.interfaces import IAnalyticsRepository  # noqa: F401


class BigQueryAnalyticsRepository:
    """
    Acesso a dados de tráfego e performance no thelook_ecommerce.
    Implementa IAnalyticsRepository; pode ser substituído por mock/cache (Liskov).
    """

    def __init__(self, client: BigQueryClient) -> None:
        self._client = client

    def get_traffic_volume(
        self,
        start_date: date,
        end_date: date,
        traffic_source: str | None = None,
    ) -> list[TrafficVolumeResult]:
        """Volume de usuários por canal no período. Query parametrizada.
        Usa faixa em created_at (sem DATE()) para permitir partition pruning no BigQuery.
        """
        ds = self._client.dataset
        query = f"""
            SELECT
                traffic_source,
                COUNT(DISTINCT id) AS total_users,
                MIN(DATE(created_at)) AS period_start,
                MAX(DATE(created_at)) AS period_end
            FROM `{ds}.users`
            WHERE created_at >= TIMESTAMP(@start_date)
              AND created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY))
              AND (@traffic_source IS NULL OR traffic_source = @traffic_source)
            GROUP BY traffic_source
            ORDER BY total_users DESC
        """
        params = [
            bigquery.ScalarQueryParameter("start_date", "DATE", str(start_date)),
            bigquery.ScalarQueryParameter("end_date", "DATE", str(end_date)),
            bigquery.ScalarQueryParameter("traffic_source", "STRING", traffic_source),
        ]
        rows = self._client.run_query(query, params)
        return [
            TrafficVolumeResult(
                traffic_source=r["traffic_source"],
                total_users=r["total_users"],
                period_start=str(r["period_start"]),
                period_end=str(r["period_end"]),
            )
            for r in rows
        ]

    def get_channel_performance(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ChannelPerformance]:
        """Performance por canal: JOIN users → orders → order_items.
        Filtro em o.created_at sem DATE() para partition pruning.
        """
        ds = self._client.dataset
        query = f"""
            WITH user_orders AS (
                SELECT
                    u.traffic_source,
                    u.id AS user_id,
                    o.order_id AS order_id,
                    oi.sale_price
                FROM `{ds}.users` u
                INNER JOIN `{ds}.orders` o
                    ON o.user_id = u.id AND o.status = 'Complete'
                INNER JOIN `{ds}.order_items` oi ON oi.order_id = o.order_id
                WHERE (@start_date IS NULL OR o.created_at >= TIMESTAMP(@start_date))
                  AND (@end_date IS NULL OR o.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
            ),
            agg AS (
                SELECT
                    traffic_source,
                    COUNT(DISTINCT user_id) AS total_users,
                    COUNT(DISTINCT order_id) AS total_orders,
                    SUM(sale_price) AS total_revenue
                FROM user_orders
                GROUP BY traffic_source
            )
            SELECT
                traffic_source,
                total_users,
                total_orders,
                ROUND(total_revenue, 2) AS total_revenue,
                ROUND(SAFE_DIVIDE(total_revenue, total_users), 2) AS revenue_per_user,
                ROUND(SAFE_DIVIDE(total_orders, total_users), 4) AS orders_per_user
            FROM agg
            ORDER BY total_revenue DESC
        """
        params = [
            bigquery.ScalarQueryParameter(
                "start_date", "DATE", str(start_date) if start_date else None
            ),
            bigquery.ScalarQueryParameter(
                "end_date", "DATE", str(end_date) if end_date else None
            ),
        ]
        rows = self._client.run_query(query, params)
        return [
            ChannelPerformance(
                traffic_source=r["traffic_source"],
                total_users=r["total_users"],
                total_orders=r["total_orders"],
                total_revenue=float(r["total_revenue"] or 0),
                revenue_per_user=float(r["revenue_per_user"] or 0),
                orders_per_user=float(r["orders_per_user"] or 0),
            )
            for r in rows
        ]

    def list_traffic_sources(self) -> list[str]:
        """Lista canais de tráfego distintos."""
        ds = self._client.dataset
        query = f"""
            SELECT DISTINCT traffic_source
            FROM `{ds}.users`
            WHERE traffic_source IS NOT NULL
            ORDER BY traffic_source
        """
        rows = self._client.run_query(query)
        return [r["traffic_source"] for r in rows]
