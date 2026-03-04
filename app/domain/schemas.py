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


class ConversionByChannel(BaseModel):
    """Taxa de conversão por canal: % de usuários que fizeram ao menos uma compra."""

    traffic_source: str
    total_users: int
    users_with_order: int
    conversion_rate_pct: float


class AverageOrderValueByChannel(BaseModel):
    """Ticket médio por canal: receita total / número de pedidos."""

    traffic_source: str
    total_orders: int
    total_revenue: float
    avg_order_value: float


class RevenueByMonthByChannel(BaseModel):
    """Receita por mês e por canal (série temporal)."""

    traffic_source: str
    year_month: str
    total_revenue: float


class TopCategoryByChannel(BaseModel):
    """Categoria mais vendida por canal (receita ou volume)."""

    traffic_source: str
    category: str
    total_revenue: float
    total_units: int


class EngagementByChannel(BaseModel):
    """Engajamento (eventos) por canal."""

    traffic_source: str
    event_count: int
    unique_users: int


class DistributionCenterPerformance(BaseModel):
    """Performance por centro de distribuição."""

    distribution_center_name: str
    total_orders: int
    total_revenue: float
