"""Schemas Pydantic para request/response e resultados de dados."""
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Resposta do agente para o cliente."""

    answer: str = Field(..., description="Resposta em linguagem natural")
    sources_used: list[str] = Field(
        default_factory=list,
        description="Ferramentas ou fontes utilizadas na resposta",
    )


class TrafficVolumeResult(BaseModel):
    """Resultado agregado de volume de tráfego por canal/período."""

    traffic_source: str
    total_users: int
    period_start: str
    period_end: str


class ChannelPerformance(BaseModel):
    """Métricas de performance por canal de mídia."""

    traffic_source: str
    total_users: int
    total_orders: int
    total_revenue: float
    revenue_per_user: float
    orders_per_user: float
