"""
Validação JWT para rotas protegidas (Bearer token).
Se JWT_SECRET não estiver definido no .env, a validação é desativada (útil em dev/local).
"""

import os
from typing import Annotated, Any

import jwt
from config import Settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import get_settings

security = HTTPBearer(auto_error=False)


def _effective_jwt_secret(settings: Settings) -> str:
    """Secret usado para validar JWT (Settings ou os.environ)."""
    return (settings.jwt_secret or os.environ.get("JWT_SECRET") or "").strip()

def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    """
    Valida o Bearer JWT e retorna o payload.
    Se JWT_SECRET estiver vazio, não exige token (dev/local).
    Se JWT_SECRET estiver definido e token ausente/inválido, retorna 401.
    """
    secret = _effective_jwt_secret(settings)
    if not secret:
        return {"sub": "anonymous", "jwt_disabled": True}

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente. Envie o header: Authorization: Bearer <token>",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
