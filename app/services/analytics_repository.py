"""
Repositório de analytics (Repository Pattern).
Implementa IAnalyticsRepository usando BigQuery — Adapter do BQ para o domínio.
"""

from datetime import date
from typing import TYPE_CHECKING

from google.cloud import bigquery

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
from app.services.bigquery_client import BigQueryClient

if TYPE_CHECKING:
    from app.domain.interfaces import IAnalyticsRepository  # noqa: F401


def _date_params(
    start_date: date | None, end_date: date | None
) -> list[bigquery.ScalarQueryParameter]:
    """Parâmetros de data reutilizados nas queries."""
    return [
        bigquery.ScalarQueryParameter(
            "start_date", "DATE", str(start_date) if start_date else None
        ),
        bigquery.ScalarQueryParameter(
            "end_date", "DATE", str(end_date) if end_date else None
        ),
    ]


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

    def get_conversion_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ConversionByChannel]:
        """Taxa de conversão por canal: % de usuários do período que fizeram ao menos 1 pedido Complete."""
        ds = self._client.dataset
        query = f"""
            WITH users_in_period AS (
                SELECT u.id, u.traffic_source
                FROM `{ds}.users` u
                WHERE (@start_date IS NULL OR u.created_at >= TIMESTAMP(@start_date))
                  AND (@end_date IS NULL OR u.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
            ),
            converters AS (
                SELECT DISTINCT o.user_id
                FROM `{ds}.orders` o
                WHERE o.status = 'Complete'
                  AND (@start_date IS NULL OR o.created_at >= TIMESTAMP(@start_date))
                  AND (@end_date IS NULL OR o.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
            ),
            agg AS (
                SELECT
                    u.traffic_source,
                    COUNT(DISTINCT u.id) AS total_users,
                    COUNT(DISTINCT c.user_id) AS users_with_order
                FROM users_in_period u
                LEFT JOIN converters c ON c.user_id = u.id
                GROUP BY u.traffic_source
            )
            SELECT
                traffic_source,
                total_users,
                users_with_order,
                ROUND(SAFE_DIVIDE(users_with_order, total_users) * 100, 2) AS conversion_rate_pct
            FROM agg
            WHERE total_users > 0
            ORDER BY conversion_rate_pct DESC
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
            ConversionByChannel(
                traffic_source=r["traffic_source"],
                total_users=r["total_users"],
                users_with_order=r["users_with_order"],
                conversion_rate_pct=float(r["conversion_rate_pct"] or 0),
            )
            for r in rows
        ]

    def get_average_order_value_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[AverageOrderValueByChannel]:
        """Ticket médio por canal: receita total / número de pedidos."""
        ds = self._client.dataset
        query = f"""
            WITH base AS (
                SELECT
                    u.traffic_source,
                    o.order_id,
                    SUM(oi.sale_price) AS order_revenue
                FROM `{ds}.users` u
                INNER JOIN `{ds}.orders` o ON o.user_id = u.id AND o.status = 'Complete'
                INNER JOIN `{ds}.order_items` oi ON oi.order_id = o.order_id
                WHERE (@start_date IS NULL OR o.created_at >= TIMESTAMP(@start_date))
                  AND (@end_date IS NULL OR o.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
                GROUP BY u.traffic_source, o.order_id
            )
            SELECT
                traffic_source,
                COUNT(*) AS total_orders,
                ROUND(SUM(order_revenue), 2) AS total_revenue,
                ROUND(SAFE_DIVIDE(SUM(order_revenue), COUNT(*)), 2) AS avg_order_value
            FROM base
            GROUP BY traffic_source
            ORDER BY avg_order_value DESC
        """
        params = _date_params(start_date, end_date)
        rows = self._client.run_query(query, params)
        return [
            AverageOrderValueByChannel(
                traffic_source=r["traffic_source"],
                total_orders=r["total_orders"],
                total_revenue=float(r["total_revenue"] or 0),
                avg_order_value=float(r["avg_order_value"] or 0),
            )
            for r in rows
        ]

    def get_revenue_by_month_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[RevenueByMonthByChannel]:
        """Receita por mês e por canal (série temporal)."""
        ds = self._client.dataset
        query = f"""
            SELECT
                u.traffic_source,
                FORMAT_TIMESTAMP('%Y-%m', o.created_at) AS year_month,
                ROUND(SUM(oi.sale_price), 2) AS total_revenue
            FROM `{ds}.users` u
            INNER JOIN `{ds}.orders` o ON o.user_id = u.id AND o.status = 'Complete'
            INNER JOIN `{ds}.order_items` oi ON oi.order_id = o.order_id
            WHERE (@start_date IS NULL OR o.created_at >= TIMESTAMP(@start_date))
              AND (@end_date IS NULL OR o.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
            GROUP BY u.traffic_source, FORMAT_TIMESTAMP('%Y-%m', o.created_at)
            ORDER BY u.traffic_source, year_month
        """
        params = _date_params(start_date, end_date)
        rows = self._client.run_query(query, params)
        return [
            RevenueByMonthByChannel(
                traffic_source=r["traffic_source"],
                year_month=str(r["year_month"]),
                total_revenue=float(r["total_revenue"] or 0),
            )
            for r in rows
        ]

    def get_top_categories_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 10,
    ) -> list[TopCategoryByChannel]:
        """Categorias mais vendidas por canal (via inventory_items.product_category)."""
        ds = self._client.dataset
        query = f"""
            WITH base AS (
                SELECT
                    u.traffic_source,
                    COALESCE(ii.product_category, 'N/A') AS category,
                    oi.sale_price,
                    1 AS units
                FROM `{ds}.users` u
                INNER JOIN `{ds}.orders` o ON o.user_id = u.id AND o.status = 'Complete'
                INNER JOIN `{ds}.order_items` oi ON oi.order_id = o.order_id
                LEFT JOIN `{ds}.inventory_items` ii ON ii.id = oi.inventory_item_id
                WHERE (@start_date IS NULL OR o.created_at >= TIMESTAMP(@start_date))
                  AND (@end_date IS NULL OR o.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
            )
            SELECT
                traffic_source,
                category,
                ROUND(SUM(sale_price), 2) AS total_revenue,
                SUM(units) AS total_units
            FROM base
            GROUP BY traffic_source, category
            ORDER BY traffic_source, total_revenue DESC
        """
        params = _date_params(start_date, end_date)
        rows = self._client.run_query(query, params)
        # BigQuery LIMIT não aceita parâmetro; limitamos em Python
        rows = rows[: max(1, limit)]
        return [
            TopCategoryByChannel(
                traffic_source=r["traffic_source"],
                category=r["category"],
                total_revenue=float(r["total_revenue"] or 0),
                total_units=int(r["total_units"] or 0),
            )
            for r in rows
        ]

    def get_engagement_by_channel(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EngagementByChannel]:
        """Eventos e usuários únicos por canal (tabela events)."""
        ds = self._client.dataset
        query = f"""
            SELECT
                u.traffic_source,
                COUNT(*) AS event_count,
                COUNT(DISTINCT e.user_id) AS unique_users
            FROM `{ds}.events` e
            INNER JOIN `{ds}.users` u ON u.id = e.user_id
            WHERE (@start_date IS NULL OR e.created_at >= TIMESTAMP(@start_date))
              AND (@end_date IS NULL OR e.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
            GROUP BY u.traffic_source
            ORDER BY event_count DESC
        """
        params = _date_params(start_date, end_date)
        rows = self._client.run_query(query, params)
        return [
            EngagementByChannel(
                traffic_source=r["traffic_source"],
                event_count=int(r["event_count"] or 0),
                unique_users=int(r["unique_users"] or 0),
            )
            for r in rows
        ]

    def get_distribution_center_performance(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DistributionCenterPerformance]:
        """Performance por centro de distribuição (via products → distribution_centers)."""
        ds = self._client.dataset
        query = f"""
            WITH base AS (
                SELECT
                    dc.name AS distribution_center_name,
                    o.order_id,
                    SUM(oi.sale_price) AS order_revenue
                FROM `{ds}.order_items` oi
                INNER JOIN `{ds}.orders` o ON o.order_id = oi.order_id AND o.status = 'Complete'
                INNER JOIN `{ds}.inventory_items` ii ON ii.id = oi.inventory_item_id
                INNER JOIN `{ds}.products` p ON p.id = ii.product_id
                INNER JOIN `{ds}.distribution_centers` dc ON dc.id = p.distribution_center_id
                WHERE (@start_date IS NULL OR o.created_at >= TIMESTAMP(@start_date))
                  AND (@end_date IS NULL OR o.created_at < TIMESTAMP(DATE_ADD(@end_date, INTERVAL 1 DAY)))
                GROUP BY dc.name, o.order_id
            )
            SELECT
                distribution_center_name,
                COUNT(*) AS total_orders,
                ROUND(SUM(order_revenue), 2) AS total_revenue
            FROM base
            GROUP BY distribution_center_name
            ORDER BY total_revenue DESC
        """
        params = _date_params(start_date, end_date)
        rows = self._client.run_query(query, params)
        return [
            DistributionCenterPerformance(
                distribution_center_name=r["distribution_center_name"],
                total_orders=r["total_orders"],
                total_revenue=float(r["total_revenue"] or 0),
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
