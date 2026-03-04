"""Testes do orquestrador e da factory de tools."""

from unittest.mock import MagicMock

from app.agent.agent import MediaAnalystOrchestrator
from app.agent.tools_factory import create_analyst_tools, create_traffic_volume_tool
from app.domain.schemas import TrafficVolumeResult
from langchain_core.messages import AIMessage, BaseMessage


def test_orchestrator_returns_final_answer_when_no_tool_calls() -> None:
    """Quando o LLM não chama tools, o orquestrador devolve o content e lista vazia."""
    final_answer = "O canal Search teve 1.500 usuários em fevereiro."

    def fake_invoke(messages: list[BaseMessage]) -> AIMessage:
        return AIMessage(content=final_answer, tool_calls=[])

    llm = MagicMock()
    llm.invoke = fake_invoke
    orchestrator = MediaAnalystOrchestrator(llm_with_tools=llm, tools=[])
    answer, sources = orchestrator.invoke("Quantos usuários do Search?")
    assert answer == final_answer
    assert sources == []


def test_orchestrator_calls_tool_then_returns_llm_answer() -> None:
    """Quando o LLM chama uma tool, ela é executada e o próximo turno devolve a resposta final."""
    tool_result = "Search: 1500 usuários."
    final_answer = "O volume do Search no período foi de 1.500 usuários."

    call_count = 0

    def fake_invoke(messages: list[BaseMessage]) -> AIMessage:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "tc-1",
                        "name": "get_traffic_volume_tool",
                        "args": {
                            "start_date": "2024-02-01",
                            "end_date": "2024-02-29",
                            "traffic_source": "Search",
                        },
                    }
                ],
            )
        return AIMessage(content=final_answer, tool_calls=[])

    fake_tool = MagicMock()
    fake_tool.name = "get_traffic_volume_tool"
    fake_tool.invoke.return_value = tool_result

    llm = MagicMock()
    llm.invoke = fake_invoke
    orchestrator = MediaAnalystOrchestrator(
        llm_with_tools=llm,
        tools=[fake_tool],
    )
    answer, sources = orchestrator.invoke("Volume do Search em fevereiro?")
    assert answer == final_answer
    assert sources == ["get_traffic_volume_tool"]
    fake_tool.invoke.assert_called_once()


def test_traffic_volume_tool_formats_repository_result(
    mock_analytics_repository: MagicMock,
    sample_traffic_results: list[TrafficVolumeResult],
) -> None:
    """A tool de volume formata o retorno do repositório em texto legível."""
    tool = create_traffic_volume_tool(mock_analytics_repository)
    result = tool.invoke(
        {
            "start_date": "2024-02-01",
            "end_date": "2024-02-29",
            "traffic_source": None,
        }
    )
    assert "Search" in result
    assert "1500" in result
    assert "Organic" in result
    assert "800" in result
    mock_analytics_repository.get_traffic_volume.assert_called_once()


def test_traffic_volume_tool_returns_error_on_invalid_date(
    mock_analytics_repository: MagicMock,
) -> None:
    """Datas inválidas retornam mensagem de erro sem chamar o repositório."""
    tool = create_traffic_volume_tool(mock_analytics_repository)
    result = tool.invoke(
        {
            "start_date": "invalid",
            "end_date": "2024-02-29",
            "traffic_source": None,
        }
    )
    assert "inválidas" in result or "YYYY-MM-DD" in result
    mock_analytics_repository.get_traffic_volume.assert_not_called()


def test_create_analyst_tools_returns_three_tools(
    mock_analytics_repository: MagicMock,
) -> None:
    """A factory retorna exatamente três tools."""
    tools = create_analyst_tools(mock_analytics_repository)
    assert len(tools) == 3
    names = {t.name for t in tools}
    assert names == {
        "get_traffic_volume_tool",
        "get_channel_performance_tool",
        "list_traffic_sources_tool",
    }


def test_traffic_volume_tool_rejects_start_after_end(
    mock_analytics_repository: MagicMock,
) -> None:
    """Tool de volume rejeita start_date > end_date sem chamar repositório."""
    tool = create_traffic_volume_tool(mock_analytics_repository)
    result = tool.invoke(
        {
            "start_date": "2024-02-29",
            "end_date": "2024-02-01",
            "traffic_source": None,
        }
    )
    assert "não pode ser maior" in result or "inicial" in result
    mock_analytics_repository.get_traffic_volume.assert_not_called()


def test_channel_performance_tool_formats_repository_result(
    mock_analytics_repository: MagicMock,
    sample_performance_results: list,
) -> None:
    """Tool de performance formata resultado do repositório."""
    from app.agent.tools_factory import create_channel_performance_tool

    tool = create_channel_performance_tool(mock_analytics_repository)
    result = tool.invoke({"start_date": None, "end_date": None})
    assert "Search" in result
    assert "15000" in result or "receita" in result
    mock_analytics_repository.get_channel_performance.assert_called_once()


def test_list_traffic_sources_tool_returns_formatted_string(
    mock_analytics_repository: MagicMock,
) -> None:
    """Tool list_traffic_sources retorna string com canais."""
    from app.agent.tools_factory import create_list_traffic_sources_tool

    tool = create_list_traffic_sources_tool(mock_analytics_repository)
    result = tool.invoke({})
    assert "Search" in result
    assert "Organic" in result
    assert "Facebook" in result
    mock_analytics_repository.list_traffic_sources.assert_called_once()


def test_list_traffic_sources_tool_handles_repository_error(
    mock_analytics_repository: MagicMock,
) -> None:
    """Tool list_traffic_sources retorna mensagem de erro quando repositório falha."""
    from app.agent.tools_factory import create_list_traffic_sources_tool

    mock_analytics_repository.list_traffic_sources.side_effect = Exception("Falha")
    tool = create_list_traffic_sources_tool(mock_analytics_repository)
    result = tool.invoke({})
    assert "Erro" in result or "Falha" in result


def test_orchestrator_uses_unknown_tool_returns_fallback_message() -> None:
    """Quando o LLM chama uma tool que não está na lista, usa mensagem de fallback."""
    call_count = 0

    def fake_invoke(messages: list) -> AIMessage:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "tc-1",
                        "name": "unknown_tool",
                        "args": {},
                    }
                ],
            )
        return AIMessage(content="Pronto.", tool_calls=[])

    fake_tool = MagicMock()
    fake_tool.name = "get_traffic_volume_tool"
    llm = MagicMock()
    llm.invoke = fake_invoke
    orchestrator = MediaAnalystOrchestrator(llm_with_tools=llm, tools=[fake_tool])
    answer, sources = orchestrator.invoke("Pergunta?")
    assert answer == "Pronto."
    assert "unknown_tool" in sources
    fake_tool.invoke.assert_not_called()
