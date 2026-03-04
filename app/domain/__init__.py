"""Modelos de domínio, DTOs, exceções e interfaces."""

from app.domain.exceptions import (
    AgentError,
    AppException,
    DataSourceError,
)
from app.domain.interfaces import IAnalyticsRepository
from app.domain.schemas import (
    AgentResponse,
    ChannelPerformance,
    TrafficVolumeResult,
)

__all__ = [
    "AgentError",
    "AgentResponse",
    "AppException",
    "ChannelPerformance",
    "DataSourceError",
    "IAnalyticsRepository",
    "TrafficVolumeResult",
]
