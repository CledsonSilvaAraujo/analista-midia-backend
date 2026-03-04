"""Exceções de configuração (camada config não depende de app)."""


class ConfigurationError(Exception):
    """Configuração inválida ou ausente (ex.: API key não definida)."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
