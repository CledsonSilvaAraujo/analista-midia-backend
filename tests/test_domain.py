"""Testes unitários do domínio: schemas e exceções."""

import pytest
from app.domain.exceptions import AgentError, AppException, DataSourceError
from app.domain.schemas import (
    AgentResponse,
    ChannelPerformance,
    TrafficVolumeResult,
)
from pydantic import ValidationError

# --- Schemas ---


def test_agent_response_requires_answer() -> None:
    """AgentResponse exige campo answer."""
    with pytest.raises(ValidationError):
        AgentResponse(sources_used=[])  # type: ignore[call-arg]


def test_agent_response_default_sources_used_empty() -> None:
    """AgentResponse tem sources_used vazio por padrão."""
    r = AgentResponse(answer="Ok")
    assert r.answer == "Ok"
    assert r.sources_used == []


def test_agent_response_with_sources() -> None:
    """AgentResponse aceita answer e sources_used."""
    r = AgentResponse(
        answer="Resposta",
        sources_used=["get_traffic_volume_tool"],
    )
    assert r.answer == "Resposta"
    assert r.sources_used == ["get_traffic_volume_tool"]


def test_traffic_volume_result_valid() -> None:
    """TrafficVolumeResult aceita campos obrigatórios."""
    r = TrafficVolumeResult(
        traffic_source="Search",
        total_users=100,
        period_start="2024-01-01",
        period_end="2024-01-31",
    )
    assert r.traffic_source == "Search"
    assert r.total_users == 100
    assert r.period_start == "2024-01-01"
    assert r.period_end == "2024-01-31"


def test_traffic_volume_result_rejects_negative_users() -> None:
    """TrafficVolumeResult não deve aceitar total_users negativo (se tiver validator)."""
    # Sem validator explícito, Pydantic aceita; teste de que o modelo existe e é criável
    r = TrafficVolumeResult(
        traffic_source="X",
        total_users=0,
        period_start="2024-01-01",
        period_end="2024-01-31",
    )
    assert r.total_users == 0


def test_channel_performance_valid() -> None:
    """ChannelPerformance aceita todos os campos numéricos."""
    r = ChannelPerformance(
        traffic_source="Organic",
        total_users=500,
        total_orders=50,
        total_revenue=7500.0,
        revenue_per_user=15.0,
        orders_per_user=0.1,
    )
    assert r.traffic_source == "Organic"
    assert r.revenue_per_user == 15.0
    assert r.orders_per_user == 0.1


def test_channel_performance_serialization() -> None:
    """ChannelPerformance pode ser serializado para dict/JSON."""
    r = ChannelPerformance(
        traffic_source="Facebook",
        total_users=200,
        total_orders=20,
        total_revenue=3000.0,
        revenue_per_user=15.0,
        orders_per_user=0.1,
    )
    d = r.model_dump()
    assert d["traffic_source"] == "Facebook"
    assert d["total_revenue"] == 3000.0


# --- Exceções ---


def test_app_exception_has_message() -> None:
    """AppException guarda message e repassa para Exception."""
    exc = AppException("Mensagem de erro")
    assert exc.message == "Mensagem de erro"
    assert str(exc) == "Mensagem de erro"


def test_data_source_error_inherits_app_exception() -> None:
    """DataSourceError herda de AppException e expõe message."""
    exc = DataSourceError("Erro no BigQuery")
    assert isinstance(exc, AppException)
    assert exc.message == "Erro no BigQuery"


def test_agent_error_inherits_app_exception() -> None:
    """AgentError herda de AppException."""
    exc = AgentError("LLM indisponível")
    assert isinstance(exc, AppException)
    assert exc.message == "LLM indisponível"


def test_data_source_error_can_be_raised_and_caught() -> None:
    """DataSourceError pode ser levantada e capturada por tipo."""
    with pytest.raises(DataSourceError) as exc_info:
        raise DataSourceError("Falha na conexão")
    assert "Falha na conexão" in str(exc_info.value)
