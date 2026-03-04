"""
Factory de tools (Factory Pattern + Dependency Inversion).
Cria ferramentas do agente com o repositório injetado — sem acoplamento a Settings/BQ.
"""
from datetime import date

from langchain_core.tools import StructuredTool

from app.domain.interfaces import IAnalyticsRepository


def _parse_date(value: str | None) -> date | None:
    """Parse YYYY-MM-DD ou retorna None."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None  # caller will validate


def create_traffic_volume_tool(repo: IAnalyticsRepository) -> StructuredTool:
    """Cria a tool de volume de tráfego com o repositório injetado."""

    def _invoke(
        start_date: str,
        end_date: str,
        traffic_source: str | None = None,
    ) -> str:
        start = _parse_date(start_date)
        end = _parse_date(end_date)
        if not start or not end:
            return "Datas inválidas. Use formato YYYY-MM-DD."
        if start > end:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_traffic_volume(start, end, traffic_source)
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhum dado encontrado para o período e filtros informados."
        lines = [
            f"- {r.traffic_source}: {r.total_users} usuários (período: {r.period_start} a {r.period_end})"
            for r in results
        ]
        return "Volume de usuários por canal:\n" + "\n".join(lines)

    return StructuredTool.from_function(
        name="get_traffic_volume_tool",
        description=(
            "Consulta o volume de usuários por canal de tráfego em um período. "
            "Use quando a pergunta for sobre quantidade de usuários, volume de tráfego, "
            "ou 'quantos usuários vieram de X no período Y'."
        ),
        func=_invoke,
    )


def create_channel_performance_tool(repo: IAnalyticsRepository) -> StructuredTool:
    """Cria a tool de performance por canal com o repositório injetado."""

    def _invoke(
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        start_d = _parse_date(start_date)
        end_d = _parse_date(end_date)
        if start_d and end_d and start_d > end_d:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_channel_performance(start_date=start_d, end_date=end_d)
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhum dado de performance encontrado para o período informado."
        lines = [
            f"- {r.traffic_source}: {r.total_users} usuários, {r.total_orders} pedidos, "
            f"receita total R$ {r.total_revenue:.2f}, receita/usuário R$ {r.revenue_per_user:.2f}, "
            f"pedidos/usuário {r.orders_per_user:.4f}"
            for r in results
        ]
        return "Performance por canal:\n" + "\n".join(lines)

    return StructuredTool.from_function(
        name="get_channel_performance_tool",
        description=(
            "Consulta a performance de cada canal: usuários, pedidos, receita total, "
            "receita por usuário e pedidos por usuário. Use para perguntas sobre qual canal "
            "performa melhor, ROI, receita por canal ou comparação entre canais."
        ),
        func=_invoke,
    )


def create_list_traffic_sources_tool(repo: IAnalyticsRepository) -> StructuredTool:
    """Cria a tool que lista canais com o repositório injetado."""

    def _invoke() -> str:
        try:
            sources = repo.list_traffic_sources()
        except Exception as e:
            return f"Erro ao consultar canais: {e}"
        if not sources:
            return "Nenhum canal encontrado no dataset."
        return "Canais disponíveis: " + ", ".join(sources)

    return StructuredTool.from_function(
        name="list_traffic_sources_tool",
        description=(
            "Lista todos os canais de tráfego disponíveis no dataset. "
            "Use quando precisar saber quais canais existem (ex.: Search, Organic, Facebook)."
        ),
        func=_invoke,
    )


def create_analyst_tools(repo: IAnalyticsRepository) -> list[StructuredTool]:
    """
    Factory: retorna as três tools do analista com o repositório injetado.
    Permite testar o agente com um repositório mock (Dependency Inversion).
    """
    return [
        create_traffic_volume_tool(repo),
        create_channel_performance_tool(repo),
        create_list_traffic_sources_tool(repo),
    ]
