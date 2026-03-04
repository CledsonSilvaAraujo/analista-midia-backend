# Changelog

Todas as mudanças notáveis do projeto são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [0.1.0] - 2025-03-03

### Adicionado

- MVP do Agente Analista de Mídia (Tool Calling + LangChain + BigQuery).
- API FastAPI: `POST /api/ask`, `GET /api/health`.
- Três tools: volume de tráfego, performance por canal, listar canais.
- Integração com dataset `bigquery-public-data.thelook_ecommerce`.
- Arquitetura SOLID: Repository, DI (FastAPI Depends), Factory de tools.
- Health check com `version` e `openai_configured`.
- Testes automatizados (pytest) para API, agente e tools.
- CI com GitHub Actions (Ruff + Pytest).
- Docker e docker-compose para execução em container.
- Documentação: README com setup, arquitetura e padrões; pyproject.toml; LICENSE (MIT).

### Segurança

- Queries BigQuery parametrizadas (evita SQL injection).
- Credenciais via variáveis de ambiente (.env não commitado).
- Dockerfile com usuário não-root.
