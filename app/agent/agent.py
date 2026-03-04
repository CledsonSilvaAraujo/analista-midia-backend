"""
Orquestrador do agente (Template Method + Dependency Inversion).
O agente decide quando chamar cada ferramenta; a lógica de execução fica nas tools.
Depende de abstrações (LLM com tools, tool executor) injetadas.
"""
from typing import Protocol, runtime_checkable

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool

from app.agent.prompts import MEDIA_ANALYST_SYSTEM_PROMPT
from config.constants import AGENT_MAX_TURNS


@runtime_checkable
class IAgentOrchestrator(Protocol):
    """Contrato do orquestrador (Interface Segregation)."""

    def invoke(self, question: str) -> tuple[str, list[str]]:
        """Executa a pergunta e retorna (resposta, tools_utilizadas)."""
        ...


class MediaAnalystOrchestrator:
    """
    Orquestra o loop agente: pergunta → LLM → tool_calls? → executa tools → repete.
    Depende de um BaseChatModel com tools vinculadas e de um dicionário tool_name → tool.
    """

    def __init__(
        self,
        llm_with_tools: BaseChatModel,
        tools: list[BaseTool],
        max_turns: int = AGENT_MAX_TURNS,
    ) -> None:
        self._llm = llm_with_tools
        self._tool_by_name = {t.name: t for t in tools}
        self._max_turns = max_turns

    def invoke(self, question: str) -> tuple[str, list[str]]:
        """
        Template Method: loop fixo (pergunta → resposta → tool_calls → tool results → repete).
        Retorna (resposta_final, lista_de_tools_utilizadas).
        """
        messages: list[BaseMessage] = [
            SystemMessage(content=MEDIA_ANALYST_SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
        sources_used: list[str] = []

        for _ in range(self._max_turns):
            response = self._llm.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return (response.content or "").strip(), sources_used

            for tc in response.tool_calls:
                name = tc["name"]
                args = tc.get("args") or {}
                sources_used.append(name)
                tool = self._tool_by_name.get(name)
                result = tool.invoke(args) if tool else "Ferramenta não encontrada."
                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tc["id"],
                    )
                )

        return (
            "Não foi possível concluir a análise no número máximo de passos. Tente reformular a pergunta.",
            sources_used,
        )
