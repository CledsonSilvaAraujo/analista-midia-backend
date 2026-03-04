"""Rotas FastAPI do Agente Analista de Mídia (Controller — SRP)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.agent.agent import MediaAnalystOrchestrator
from app.api.dependencies import get_media_analyst, get_settings
from app.domain.exceptions import DataSourceError
from app.domain.schemas import AgentResponse
from config import Settings
from config.exceptions import ConfigurationError

router = APIRouter(prefix="/api", tags=["analyst"])


class AskRequest(BaseModel):
    """Pergunta em linguagem natural."""

    question: str = Field(
        ...,
        min_length=1,
        description="Pergunta sobre tráfego ou performance de canais",
    )


@router.post("/ask", response_model=AgentResponse)
def ask_analyst(
    request: AskRequest,
    agent: Annotated[MediaAnalystOrchestrator, Depends(get_media_analyst)],
) -> AgentResponse:
    """
    Envia uma pergunta em linguagem natural ao Analista de Mídia.
    O agente pode consultar volume de tráfego e performance por canal no BigQuery.
    """
    try:
        answer, sources_used = agent.invoke(request.question)
    except (ConfigurationError, DataSourceError):
        raise  # Tratados pelos exception handlers globais (main.py)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do agente: {e}")

    return AgentResponse(answer=answer, sources_used=sources_used)


@router.get("/health")
def health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str | bool]:
    """Health check: status, versão e indicador de readiness (OpenAI configurada)."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "openai_configured": bool(settings.openai_api_key),
    }
