"""
Hierarquia de exceções do domínio.
Facilita tratamento diferenciado (ex.: API retorna 502 para DataSourceError).
"""


class AppException(Exception):
    """Exceção base da aplicação. Todas as exceções de negócio herdam dela."""

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


class DataSourceError(AppException):
    """Erro ao acessar fonte de dados (ex.: BigQuery)."""

    pass


class AgentError(AppException):
    """Erro na execução do agente de IA (ex.: LLM indisponível)."""

    pass
