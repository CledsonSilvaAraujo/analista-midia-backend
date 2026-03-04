"""Constantes da aplicação (Open/Closed: alterar comportamento por config)."""

from typing import Final

# Agente
AGENT_MODEL_NAME: Final[str] = "gpt-4o-mini"
AGENT_TEMPERATURE: Final[float] = 0.0
AGENT_MAX_TURNS: Final[int] = 10

# Nomes das tools (para resposta sources_used)
TOOL_NAME_TRAFFIC_VOLUME: Final[str] = "get_traffic_volume_tool"
TOOL_NAME_CHANNEL_PERFORMANCE: Final[str] = "get_channel_performance_tool"
TOOL_NAME_CONVERSION: Final[str] = "get_conversion_by_channel_tool"
TOOL_NAME_LIST_SOURCES: Final[str] = "list_traffic_sources_tool"
TOOL_NAME_AVG_ORDER_VALUE: Final[str] = "get_average_order_value_by_channel_tool"
TOOL_NAME_REVENUE_BY_MONTH: Final[str] = "get_revenue_by_month_by_channel_tool"
TOOL_NAME_TOP_CATEGORIES: Final[str] = "get_top_categories_by_channel_tool"
TOOL_NAME_ENGAGEMENT: Final[str] = "get_engagement_by_channel_tool"
TOOL_NAME_DISTRIBUTION_CENTER: Final[str] = "get_distribution_center_performance_tool"
