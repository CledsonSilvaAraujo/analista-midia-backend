"""Configuração central da aplicação (Single Responsibility: carregar config)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from config.exceptions import ConfigurationError

# .env na raiz do projeto (monk/.env), independente do cwd ao subir o servidor
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.is_file() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    bigquery_dataset: str = "bigquery-public-data.thelook_ecommerce"
    google_cloud_project: str | None = None
    jwt_secret: str = ""  # Se preenchido, rotas protegidas exigem Bearer JWT válido
    login_user: str = ""  # Usuário fixo para POST /api/login (só usado se jwt_secret estiver definido)
    login_password: str = ""  # Senha fixa para POST /api/login

    def validate_openai(self) -> None:
        """Valida presença da chave OpenAI. Levanta ConfigurationError se ausente."""
        if not self.openai_api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY não configurada. Defina no .env ou export OPENAI_API_KEY."
            )
