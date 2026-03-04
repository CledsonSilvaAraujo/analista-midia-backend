"""Testes da API FastAPI."""

from fastapi.testclient import TestClient


def test_health_returns_ok_and_version(app_client: TestClient) -> None:
    """GET /api/health retorna status e versão."""
    r = app_client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_health_indicates_openai_readiness(app_client: TestClient) -> None:
    """Health indica se OpenAI está configurada (sem exigir chave válida)."""
    r = app_client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert "openai_configured" in data
    assert isinstance(data["openai_configured"], bool)


def test_ask_returns_answer_when_agent_mocked(
    client_with_mock_agent: TestClient,
) -> None:
    """POST /api/ask retorna answer e sources_used quando agente está mockado."""
    r = client_with_mock_agent.post(
        "/api/ask",
        json={"question": "Quantos usuários do Search no último mês?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "sources_used" in data
    assert data["answer"] == "Resposta simulada para testes."
    assert "get_traffic_volume_tool" in data["sources_used"]


def test_ask_rejects_empty_question(client_with_mock_agent: TestClient) -> None:
    """POST /api/ask rejeita pergunta vazia (422)."""
    r = client_with_mock_agent.post("/api/ask", json={"question": ""})
    assert r.status_code == 422


def test_ask_rejects_missing_question(client_with_mock_agent: TestClient) -> None:
    """POST /api/ask rejeita body sem question (422)."""
    r = client_with_mock_agent.post("/api/ask", json={})
    assert r.status_code == 422


def test_openapi_schema_available(app_client: TestClient) -> None:
    """Documentação OpenAPI está exposta."""
    r = app_client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "openapi" in schema
    assert "/api/ask" in schema.get("paths", {})


def test_ask_returns_502_when_agent_raises_data_source_error(
    app_client: TestClient,
) -> None:
    """Quando o agente levanta DataSourceError, a API retorna 502."""
    from app.api.dependencies import get_media_analyst
    from app.domain.exceptions import DataSourceError
    from app.main import app

    def failing_agent():
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.invoke.side_effect = DataSourceError("BigQuery timeout")
        return mock

    app.dependency_overrides[get_media_analyst] = failing_agent
    try:
        r = app_client.post(
            "/api/ask",
            json={"question": "Volume do Search?"},
        )
        assert r.status_code == 502
        assert "detail" in r.json()
    finally:
        app.dependency_overrides.clear()


def test_ask_returns_503_when_agent_raises_configuration_error(
    app_client: TestClient,
) -> None:
    """Quando a dependência levanta ConfigurationError (ex.: sem API key), a API retorna 503."""
    from app.api.dependencies import get_media_analyst
    from app.main import app
    from config.exceptions import ConfigurationError

    def failing_agent():
        raise ConfigurationError("OPENAI_API_KEY não configurada.")

    app.dependency_overrides[get_media_analyst] = failing_agent
    try:
        r = app_client.post(
            "/api/ask",
            json={"question": "Qual o melhor canal?"},
        )
        assert r.status_code == 503
        data = r.json()
        assert "detail" in data
        assert "OPENAI" in data["detail"] or "API" in data["detail"]
    finally:
        app.dependency_overrides.clear()


def test_ask_response_schema_has_required_fields(
    client_with_mock_agent: TestClient,
) -> None:
    """Resposta de POST /api/ask contém exatamente answer e sources_used."""
    r = client_with_mock_agent.post(
        "/api/ask",
        json={"question": "Teste?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) == {"answer", "sources_used"}
    assert isinstance(data["answer"], str)
    assert isinstance(data["sources_used"], list)
    assert all(isinstance(s, str) for s in data["sources_used"])
