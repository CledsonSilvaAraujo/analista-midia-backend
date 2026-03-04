"""Testes unitários de configuração e constantes."""
import pytest

from config.constants import (
    AGENT_MAX_TURNS,
    AGENT_MODEL_NAME,
    AGENT_TEMPERATURE,
    TOOL_NAME_CHANNEL_PERFORMANCE,
    TOOL_NAME_LIST_SOURCES,
    TOOL_NAME_TRAFFIC_VOLUME,
)
from config.exceptions import ConfigurationError
from config import Settings


def test_settings_loads_env_defaults() -> None:
    """Settings tem valores padrão para dataset e project."""
    s = Settings()
    assert s.bigquery_dataset == "bigquery-public-data.thelook_ecommerce"
    assert s.google_cloud_project is None


def test_validate_openai_raises_when_key_empty() -> None:
    """validate_openai levanta ConfigurationError quando openai_api_key está vazia."""
    s = Settings(openai_api_key="")
    with pytest.raises(ConfigurationError) as exc_info:
        s.validate_openai()
    assert "OPENAI_API_KEY" in exc_info.value.message


def test_validate_openai_passes_when_key_set() -> None:
    """validate_openai não levanta quando openai_api_key está definida."""
    s = Settings(openai_api_key="sk-any-value")
    s.validate_openai()  # não deve levantar


def test_configuration_error_has_message() -> None:
    """ConfigurationError expõe message."""
    exc = ConfigurationError("Chave inválida")
    assert exc.message == "Chave inválida"


def test_constants_agent_model_name() -> None:
    """Constante AGENT_MODEL_NAME está definida."""
    assert isinstance(AGENT_MODEL_NAME, str)
    assert len(AGENT_MODEL_NAME) > 0


def test_constants_agent_max_turns_positive() -> None:
    """AGENT_MAX_TURNS é positivo."""
    assert AGENT_MAX_TURNS >= 1


def test_constants_agent_temperature_in_range() -> None:
    """AGENT_TEMPERATURE está em intervalo razoável [0, 2]."""
    assert 0 <= AGENT_TEMPERATURE <= 2


def test_constants_tool_names_match_expected() -> None:
    """Nomes das tools são os usados pelo agente."""
    assert TOOL_NAME_TRAFFIC_VOLUME == "get_traffic_volume_tool"
    assert TOOL_NAME_CHANNEL_PERFORMANCE == "get_channel_performance_tool"
    assert TOOL_NAME_LIST_SOURCES == "list_traffic_sources_tool"
