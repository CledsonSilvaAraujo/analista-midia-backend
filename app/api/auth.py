"""
Validação JWT para rotas protegidas (Bearer token).
Se JWT_SECRET não estiver definido no .env, a validação é desativada (útil em dev).
"""

from typing import Annotated, Any

import jwt
from config import Settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import get_settings

security = HTTPBearer(auto_error=False)


def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    """
    Valida o Bearer JWT e retorna o payload.
    Se JWT_SECRET estiver vazio, não exige token (dev/local).
    Se JWT_SECRET estiver definido e token ausente/inválido, retorna 401.
    """
    if not settings.jwt_secret or not settings.jwt_secret.strip():
        return {"sub": "anonymous", "jwt_disabled": True}

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente. Envie o header: Authorization: Bearer <token>",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
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
