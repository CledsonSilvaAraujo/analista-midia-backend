"""Testes unitários dos serviços: repositório com cliente mockado."""

from datetime import date
from unittest.mock import MagicMock

import pytest
from app.domain.exceptions import DataSourceError
from app.domain.schemas import (
    AverageOrderValueByChannel,
    ConversionByChannel,
    DistributionCenterPerformance,
    EngagementByChannel,
    RevenueByMonthByChannel,
    TopCategoryByChannel,
)
from app.services.analytics_repository import BigQueryAnalyticsRepository
from app.services.bigquery_client import BigQueryClient


@pytest.fixture
def mock_bq_client() -> MagicMock:
    """Cliente BigQuery mockado (run_query retorna lista controlada)."""
    client = MagicMock(spec=BigQueryClient)
    client.dataset = "bigquery-public-data.thelook_ecommerce"
    return client


def test_repository_get_traffic_volume_maps_rows_to_results(
    mock_bq_client: MagicMock,
) -> None:
    """Repositório mapeia linhas do BQ para list[TrafficVolumeResult]."""
    mock_bq_client.run_query.return_value = [
        {
            "traffic_source": "Search",
            "total_users": 1500,
            "period_start": date(2024, 2, 1),
            "period_end": date(2024, 2, 29),
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_traffic_volume(
        start_date=date(2024, 2, 1),
        end_date=date(2024, 2, 29),
        traffic_source="Search",
    )
    assert len(results) == 1
    assert results[0].traffic_source == "Search"
    assert results[0].total_users == 1500
    assert str(results[0].period_start) == "2024-02-01"
    mock_bq_client.run_query.assert_called_once()
    call_args = mock_bq_client.run_query.call_args
    assert "@start_date" in call_args[0][0] or "start_date" in str(call_args)


def test_repository_get_traffic_volume_passes_traffic_source(
    mock_bq_client: MagicMock,
) -> None:
    """Repositório chama run_query com parâmetros corretos."""
    mock_bq_client.run_query.return_value = []
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    repo.get_traffic_volume(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        traffic_source=None,
    )
    mock_bq_client.run_query.assert_called_once()
    # Segundo argumento são os params
    params = mock_bq_client.run_query.call_args[0][1]
    assert params is not None
    assert len(params) >= 2


def test_repository_get_channel_performance_maps_rows(
    mock_bq_client: MagicMock,
) -> None:
    """Repositório mapeia linhas de performance para list[ChannelPerformance]."""
    mock_bq_client.run_query.return_value = [
        {
            "traffic_source": "Organic",
            "total_users": 800,
            "total_orders": 100,
            "total_revenue": 12000.0,
            "revenue_per_user": 15.0,
            "orders_per_user": 0.125,
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_channel_performance(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )
    assert len(results) == 1
    assert results[0].traffic_source == "Organic"
    assert results[0].total_revenue == 12000.0
    assert results[0].revenue_per_user == 15.0


def test_repository_get_channel_performance_handles_none_revenue(
    mock_bq_client: MagicMock,
) -> None:
    """Repositório trata total_revenue/revenue_per_user None como 0."""
    mock_bq_client.run_query.return_value = [
        {
            "traffic_source": "X",
            "total_users": 10,
            "total_orders": 0,
            "total_revenue": None,
            "revenue_per_user": None,
            "orders_per_user": None,
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_channel_performance()
    assert len(results) == 1
    assert results[0].total_revenue == 0.0
    assert results[0].revenue_per_user == 0.0


def test_repository_get_conversion_by_channel_maps_rows(
    mock_bq_client: MagicMock,
) -> None:
    """get_conversion_by_channel mapeia linhas para list[ConversionByChannel]."""
    mock_bq_client.run_query.return_value = [
        {
            "traffic_source": "Organic",
            "total_users": 1000,
            "users_with_order": 150,
            "conversion_rate_pct": 15.0,
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_conversion_by_channel()
    assert len(results) == 1
    assert results[0].traffic_source == "Organic"
    assert results[0].total_users == 1000
    assert results[0].users_with_order == 150
    assert results[0].conversion_rate_pct == 15.0


def test_repository_list_traffic_sources_returns_string_list(
    mock_bq_client: MagicMock,
) -> None:
    """list_traffic_sources retorna lista de strings."""
    mock_bq_client.run_query.return_value = [
        {"traffic_source": "Search"},
        {"traffic_source": "Organic"},
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    sources = repo.list_traffic_sources()
    assert sources == ["Search", "Organic"]


def test_repository_get_average_order_value_by_channel_maps_rows(
    mock_bq_client: MagicMock,
) -> None:
    """get_average_order_value_by_channel mapeia linhas para list[AverageOrderValueByChannel]."""
    mock_bq_client.run_query.return_value = [
        {
            "traffic_source": "Search",
            "total_orders": 50,
            "total_revenue": 7500.0,
            "avg_order_value": 150.0,
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_average_order_value_by_channel()
    assert len(results) == 1
    assert results[0].traffic_source == "Search"
    assert results[0].avg_order_value == 150.0


def test_repository_get_revenue_by_month_by_channel_maps_rows(
    mock_bq_client: MagicMock,
) -> None:
    """get_revenue_by_month_by_channel mapeia linhas para list[RevenueByMonthByChannel]."""
    mock_bq_client.run_query.return_value = [
        {"traffic_source": "Organic", "year_month": "2024-02", "total_revenue": 4000.0},
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_revenue_by_month_by_channel()
    assert len(results) == 1
    assert results[0].year_month == "2024-02"
    assert results[0].total_revenue == 4000.0


def test_repository_get_top_categories_by_channel_maps_rows(
    mock_bq_client: MagicMock,
) -> None:
    """get_top_categories_by_channel mapeia linhas para list[TopCategoryByChannel]."""
    mock_bq_client.run_query.return_value = [
        {
            "traffic_source": "Search",
            "category": "Vestidos",
            "total_revenue": 2000.0,
            "total_units": 15,
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_top_categories_by_channel(limit=5)
    assert len(results) == 1
    assert results[0].category == "Vestidos"
    assert results[0].total_units == 15


def test_repository_get_engagement_by_channel_maps_rows(
    mock_bq_client: MagicMock,
) -> None:
    """get_engagement_by_channel mapeia linhas para list[EngagementByChannel]."""
    mock_bq_client.run_query.return_value = [
        {
            "traffic_source": "Instagram",
            "event_count": 10000,
            "unique_users": 1200,
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_engagement_by_channel()
    assert len(results) == 1
    assert results[0].event_count == 10000
    assert results[0].unique_users == 1200


def test_repository_get_distribution_center_performance_maps_rows(
    mock_bq_client: MagicMock,
) -> None:
    """get_distribution_center_performance mapeia linhas para list[DistributionCenterPerformance]."""
    mock_bq_client.run_query.return_value = [
        {
            "distribution_center_name": "DC Campinas",
            "total_orders": 150,
            "total_revenue": 22500.0,
        },
    ]
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    results = repo.get_distribution_center_performance()
    assert len(results) == 1
    assert results[0].distribution_center_name == "DC Campinas"
    assert results[0].total_revenue == 22500.0


def test_repository_propagates_data_source_error(mock_bq_client: MagicMock) -> None:
    """Repositório propaga DataSourceError do cliente."""
    mock_bq_client.run_query.side_effect = DataSourceError("Timeout")
    repo = BigQueryAnalyticsRepository(client=mock_bq_client)
    with pytest.raises(DataSourceError) as exc_info:
        repo.get_traffic_volume(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
    assert "Timeout" in str(exc_info.value)
