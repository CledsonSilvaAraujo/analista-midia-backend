"""Entrada da aplicação FastAPI (composição e tratamento global de exceções)."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # Garante que GOOGLE_APPLICATION_CREDENTIALS e outras variáveis estejam em os.environ

# WSL: se o path da service account estiver no formato Windows, converte para /mnt/c/...
_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if _creds and _creds.startswith("C:"):
    _creds = _creds.replace("\\", "/").replace("C:", "/mnt/c")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _creds

# Docker: se o path do .env não existir no container mas o arquivo existir em /app/keys, usa esse
_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if _creds and not Path(_creds).is_file():
    _docker_keys = Path("/app/keys")
    if _docker_keys.is_dir():
        _name = Path(_creds).name
        _candidate = _docker_keys / _name
        if _candidate.is_file():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(_candidate)

from config import Settings  # noqa: E402
from config.exceptions import ConfigurationError  # noqa: E402
from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from app.api.routes import router  # noqa: E402
from app.domain.exceptions import DataSourceError  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Valida config na subida e avisa se faltar algo no .env."""
    settings = Settings()
    if not settings.openai_api_key or not settings.openai_api_key.strip():
        logger.warning(
            "OPENAI_API_KEY não está definida no .env. "
            "Defina OPENAI_API_KEY no .env para o agente funcionar."
        )
    else:
        try:
            settings.validate_openai()
        except ConfigurationError:
            pass
    if not settings.use_mock_analytics and not os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS"
    ):
        logger.warning(
            "GOOGLE_APPLICATION_CREDENTIALS não está definida no .env. "
            "Para dados reais (BigQuery), defina no .env. Para só testar, use USE_MOCK_ANALYTICS=true."
        )
    if settings.jwt_secret and settings.jwt_secret.strip():
        logger.info(
            "JWT ativado: rotas protegidas exigem Authorization: Bearer <token>"
        )
    else:
        logger.info(
            "JWT desativado (JWT_SECRET vazio): rotas protegidas abertas para desenvolvimento"
        )
    yield


def _register_exception_handlers(app: FastAPI) -> None:
    """Centraliza tratamento de exceções de domínio → HTTP (Open/Closed)."""

    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(
        _request: Request, exc: ConfigurationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": exc.message},
        )

    @app.exception_handler(DataSourceError)
    async def data_source_error_handler(
        _request: Request, exc: DataSourceError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"detail": exc.message},
        )


app = FastAPI(
    title="Analista de Mídia (MVP)",
    description="Agente de IA que analisa tráfego e performance de canais no e-commerce (thelook_ecommerce).",
    version="0.1.0",
    lifespan=lifespan,
)
_register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
