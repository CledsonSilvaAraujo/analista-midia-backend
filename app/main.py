"""Entrada da aplicação FastAPI (composição e tratamento global de exceções)."""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.domain.exceptions import DataSourceError
from config.exceptions import ConfigurationError
from config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Valida config na subida (opcional)."""
    settings = Settings()
    try:
        settings.validate_openai()
    except ConfigurationError:
        pass  # API key pode ser injetada depois
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
