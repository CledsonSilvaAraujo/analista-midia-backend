"""
Factory do agente (Builder/Factory Pattern).
Monta o orquestrador com LLM e tools a partir de Settings e repositório injetados.
"""

from config import Settings
from config.constants import AGENT_MAX_TURNS, AGENT_MODEL_NAME, AGENT_TEMPERATURE
from langchain_openai import ChatOpenAI

from app.agent.agent import MediaAnalystOrchestrator
from app.agent.tools_factory import create_analyst_tools
from app.domain.interfaces import IAnalyticsRepository


def create_media_analyst_orchestrator(
    settings: Settings,
    repository: IAnalyticsRepository,
    max_turns: int = AGENT_MAX_TURNS,
) -> MediaAnalystOrchestrator:
    """
    Monta o orquestrador: valida config, cria LLM, cria tools com repo, vincula e retorna.
    Single place to assemble the agent (Open/Closed: trocar LLM ou tools aqui).
    """
    settings.validate_openai()
    llm = ChatOpenAI(
        model=AGENT_MODEL_NAME,
        temperature=AGENT_TEMPERATURE,
        api_key=settings.openai_api_key,
    )
    tools = create_analyst_tools(repository)
    llm_with_tools = llm.bind_tools(tools)
    return MediaAnalystOrchestrator(
        llm_with_tools=llm_with_tools,
        tools=tools,
        max_turns=max_turns,
    )
