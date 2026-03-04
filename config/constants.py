"""Constantes da aplicação (Open/Closed: alterar comportamento por config)."""

from typing import Final

# Agente
AGENT_MODEL_NAME: Final[str] = "gpt-4o-mini"
AGENT_TEMPERATURE: Final[float] = 0.0
AGENT_MAX_TURNS: Final[int] = 10

# Nomes das tools (para resposta sources_used)
TOOL_NAME_TRAFFIC_VOLUME: Final[str] = "get_traffic_volume_tool"
TOOL_NAME_CHANNEL_PERFORMANCE: Final[str] = "get_channel_performance_tool"
TOOL_NAME_LIST_SOURCES: Final[str] = "list_traffic_sources_tool"
