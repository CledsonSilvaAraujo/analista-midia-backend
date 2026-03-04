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


def create_conversion_by_channel_tool(
    repo: IAnalyticsRepository,
) -> StructuredTool:
    """Cria a tool de taxa de conversão por canal com o repositório injetado."""

    def _invoke(
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        start_d = _parse_date(start_date)
        end_d = _parse_date(end_date)
        if start_d and end_d and start_d > end_d:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_conversion_by_channel(
                start_date=start_d, end_date=end_d
            )
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhum dado de conversão encontrado para o período informado."
        lines = [
            f"- {r.traffic_source}: {r.total_users} usuários, {r.users_with_order} compraram "
            f"({r.conversion_rate_pct:.2f}% de conversão)"
            for r in results
        ]
        return "Taxa de conversão por canal (% usuários que compraram):\n" + "\n".join(
            lines
        )

    return StructuredTool.from_function(
        name="get_conversion_by_channel_tool",
        description=(
            "Consulta a taxa de conversão por canal: quantos usuários de cada canal "
            "fizeram ao menos uma compra (pedido completo). Use para perguntas sobre "
            "qual canal converte melhor, taxa de conversão, ou qual canal traz usuários que mais compram."
        ),
        func=_invoke,
    )


def create_average_order_value_by_channel_tool(
    repo: IAnalyticsRepository,
) -> StructuredTool:
    """Cria a tool de ticket médio por canal."""

    def _invoke(
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        start_d = _parse_date(start_date)
        end_d = _parse_date(end_date)
        if start_d and end_d and start_d > end_d:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_average_order_value_by_channel(
                start_date=start_d, end_date=end_d
            )
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhum dado de ticket médio encontrado para o período."
        lines = [
            f"- {r.traffic_source}: {r.total_orders} pedidos, receita R$ {r.total_revenue:.2f}, "
            f"ticket médio R$ {r.avg_order_value:.2f}"
            for r in results
        ]
        return "Ticket médio por canal:\n" + "\n".join(lines)

    return StructuredTool.from_function(
        name="get_average_order_value_by_channel_tool",
        description=(
            "Consulta o ticket médio (receita total / número de pedidos) por canal. "
            "Use para perguntas sobre valor médio do pedido, ticket médio por canal ou quanto em média cada pedido gera por canal."
        ),
        func=_invoke,
    )


def create_revenue_by_month_by_channel_tool(
    repo: IAnalyticsRepository,
) -> StructuredTool:
    """Cria a tool de receita por mês e por canal (série temporal)."""

    def _invoke(
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        start_d = _parse_date(start_date)
        end_d = _parse_date(end_date)
        if start_d and end_d and start_d > end_d:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_revenue_by_month_by_channel(
                start_date=start_d, end_date=end_d
            )
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhum dado de receita por mês encontrado para o período."
        lines = [
            f"- {r.traffic_source} | {r.year_month}: R$ {r.total_revenue:.2f}"
            for r in results
        ]
        return "Receita por mês e por canal:\n" + "\n".join(lines)

    return StructuredTool.from_function(
        name="get_revenue_by_month_by_channel_tool",
        description=(
            "Consulta a receita por mês e por canal (série temporal). "
            "Use para evolução mensal, tendência de receita por canal ou comparação mês a mês."
        ),
        func=_invoke,
    )


def create_top_categories_by_channel_tool(
    repo: IAnalyticsRepository,
) -> StructuredTool:
    """Cria a tool de categorias mais vendidas por canal."""

    def _invoke(
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 10,
    ) -> str:
        start_d = _parse_date(start_date)
        end_d = _parse_date(end_date)
        if start_d and end_d and start_d > end_d:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_top_categories_by_channel(
                start_date=start_d, end_date=end_d, limit=limit
            )
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhuma categoria encontrada para o período."
        lines = [
            f"- {r.traffic_source} | {r.category}: R$ {r.total_revenue:.2f} ({r.total_units} un.)"
            for r in results
        ]
        return "Categorias mais vendidas por canal:\n" + "\n".join(lines)

    return StructuredTool.from_function(
        name="get_top_categories_by_channel_tool",
        description=(
            "Consulta as categorias (ou produtos) mais vendidas por canal. "
            "Use para perguntas sobre quais categorias vendem mais por canal, produtos mais vendidos por origem de tráfego."
        ),
        func=_invoke,
    )


def create_engagement_by_channel_tool(
    repo: IAnalyticsRepository,
) -> StructuredTool:
    """Cria a tool de engajamento (eventos) por canal."""

    def _invoke(
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        start_d = _parse_date(start_date)
        end_d = _parse_date(end_date)
        if start_d and end_d and start_d > end_d:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_engagement_by_channel(
                start_date=start_d, end_date=end_d
            )
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhum dado de engajamento encontrado para o período."
        lines = [
            f"- {r.traffic_source}: {r.event_count} eventos, {r.unique_users} usuários únicos"
            for r in results
        ]
        return "Engajamento (eventos) por canal:\n" + "\n".join(lines)

    return StructuredTool.from_function(
        name="get_engagement_by_channel_tool",
        description=(
            "Consulta a quantidade de eventos (ex.: page_view) e usuários únicos por canal. "
            "Use para perguntas sobre engajamento, uso do site por canal ou eventos por origem de tráfego."
        ),
        func=_invoke,
    )


def create_distribution_center_performance_tool(
    repo: IAnalyticsRepository,
) -> StructuredTool:
    """Cria a tool de performance por centro de distribuição."""

    def _invoke(
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        start_d = _parse_date(start_date)
        end_d = _parse_date(end_date)
        if start_d and end_d and start_d > end_d:
            return "A data inicial não pode ser maior que a data final."
        try:
            results = repo.get_distribution_center_performance(
                start_date=start_d, end_date=end_d
            )
        except Exception as e:
            return f"Erro ao consultar dados: {e}"
        if not results:
            return "Nenhum dado de centro de distribuição encontrado para o período."
        lines = [
            f"- {r.distribution_center_name}: {r.total_orders} pedidos, R$ {r.total_revenue:.2f}"
            for r in results
        ]
        return "Performance por centro de distribuição:\n" + "\n".join(lines)

    return StructuredTool.from_function(
        name="get_distribution_center_performance_tool",
        description=(
            "Consulta a performance (pedidos e receita) por centro de distribuição. "
            "Use para perguntas sobre qual centro distribui mais, receita por armazém ou análise geográfica de distribuição."
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
    Factory: retorna as nove tools do analista com o repositório injetado.
    Permite testar o agente com repositório injetado (ex.: mock em testes).
    """
    return [
        create_traffic_volume_tool(repo),
        create_channel_performance_tool(repo),
        create_conversion_by_channel_tool(repo),
        create_average_order_value_by_channel_tool(repo),
        create_revenue_by_month_by_channel_tool(repo),
        create_top_categories_by_channel_tool(repo),
        create_engagement_by_channel_tool(repo),
        create_distribution_center_performance_tool(repo),
        create_list_traffic_sources_tool(repo),
    ]
