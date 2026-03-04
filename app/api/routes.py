"""Rotas FastAPI do Agente Analista de Mídia (Controller — SRP)."""

import time
from typing import Annotated, Any

import jwt
from config import Settings
from config.exceptions import ConfigurationError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.agent.agent import MediaAnalystOrchestrator
from app.api.auth import get_jwt_payload
from app.api.dependencies import get_media_analyst, get_settings
from app.domain.exceptions import DataSourceError
from app.domain.schemas import AgentResponse

router = APIRouter(prefix="/api", tags=["analyst"])


class LoginRequest(BaseModel):
    """Credenciais para obter um JWT."""

    username: str = Field(..., description="Usuário (definido em LOGIN_USER no .env)")
    password: str = Field(..., description="Senha (definida em LOGIN_PASSWORD no .env)")


class LoginResponse(BaseModel):
    """Resposta do login com o token de acesso."""

    access_token: str = Field(
        ..., description="Token JWT para usar em Authorization: Bearer <token>"
    )
    token_type: str = Field(default="bearer", description="Tipo do token")


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
    _auth: Annotated[dict[str, Any], Depends(get_jwt_payload)],
) -> AgentResponse:
    """
    Envia uma pergunta em linguagem natural ao Analista de Mídia.
    O agente pode consultar volume de tráfego e performance por canal no BigQuery.
    Exige Bearer JWT válido se JWT_SECRET estiver definido no .env.
    """
    try:
        answer, sources_used = agent.invoke(request.question)
    except (ConfigurationError, DataSourceError):
        raise  # Tratados pelos exception handlers globais (main.py)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do agente: {e}")

    return AgentResponse(answer=answer, sources_used=sources_used)


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponse:
    """
    Autenticação com usuário e senha fixos (definidos no .env).
    Retorna um JWT para usar no header: Authorization: Bearer <access_token>.
    Só funciona se JWT_SECRET, LOGIN_USER e LOGIN_PASSWORD estiverem definidos no .env.
    """
    if not settings.jwt_secret or not settings.jwt_secret.strip():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Login desativado: defina JWT_SECRET no .env para usar autenticação.",
        )
    if not settings.login_user or not settings.login_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login não configurado: defina LOGIN_USER e LOGIN_PASSWORD no .env.",
        )
    if (
        request.username != settings.login_user
        or request.password != settings.login_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
        )
    payload = {
        "sub": settings.login_user,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400,  # 24 horas
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return LoginResponse(access_token=token)


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
