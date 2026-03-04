# Analista de Mídia — MVP Agente de IA

[![CI](https://github.com/SEU_USUARIO/monk/actions/workflows/ci.yml/badge.svg)](https://github.com/SEU_USUARIO/monk/actions/workflows/ci.yml)  
> **Repositório:** [Link do repositório público no GitHub](https://github.com/SEU_USUARIO/monk) *(substitua SEU_USUARIO pela URL real após criar o repositório)*

MVP de um **Agente de IA Autônomo** que atua como **Analista Júnior de Mídia**: entende perguntas em linguagem natural, consulta o dataset **thelook_ecommerce** no Google BigQuery e devolve **insights acionáveis** — não apenas números brutos.

---

## Entregáveis

| Entregável | Descrição |
|------------|-----------|
| **1. Link do repositório** | Repositório público no GitHub (atualize o link no topo deste README). |
| **2. README.md** | Este arquivo: instruções de setup, credenciais e arquitetura do agente (abaixo). |

---

## Pré-requisitos

- **Python 3.10+**
- Conta **OpenAI** (para a API do modelo)
- Conta **Google Cloud** (free tier; apenas para acessar o BigQuery com dataset público)

---

## Setup — Instruções claras

### Passo 1: Clonar e entrar no projeto

```bash
git clone https://github.com/SEU_USUARIO/monk.git
cd monk
```

*(Se você criou o projeto localmente, use apenas `cd monk` na pasta do projeto.)*

### Passo 2: Instalar dependências

Sempre use um ambiente virtual:

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (escolha o comando do seu sistema)
.venv\Scripts\activate          # Windows (cmd/PowerShell)
# source .venv/bin/activate     # Linux / macOS

# Instalar dependências
pip install -r requirements.txt
```

### Passo 3: Onde colocar as chaves de API e credenciais

Todas as credenciais ficam em um arquivo **`.env`** na **raiz do projeto** (mesma pasta do `README.md`). O arquivo `.env` **não** é commitado (está no `.gitignore`).

**3.1 — Criar o arquivo `.env`**

Na raiz do projeto, crie o arquivo `.env`. Você pode copiar o modelo:

```bash
# Windows (PowerShell)
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

**3.2 — Chave da OpenAI**

1. Acesse [OpenAI → API Keys](https://platform.openai.com/api-keys).
2. Crie uma chave (Create new secret key).
3. No `.env`, preencha:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

**3.3 — Credenciais do Google Cloud (BigQuery)**

O projeto usa o dataset público `bigquery-public-data.thelook_ecommerce`. Você precisa de credenciais GCP válidas.

**Opção A — Application Default Credentials (recomendado para desenvolvimento)**

1. Instale o [Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
2. No terminal, execute:

```bash
gcloud auth application-default login
```

3. Não é obrigatório definir nada no `.env` para essa opção; o cliente BigQuery usa as credenciais padrão.

**Opção B — Service Account (útil para CI/deploy)**

1. No [Google Cloud Console](https://console.cloud.google.com/), crie um projeto (ou use um existente).
2. IAM & Admin → Service Accounts → Create Service Account.
3. Crie uma chave JSON e baixe o arquivo.
4. Coloque o arquivo em um local seguro (ex.: `monk/keys/gcp-service-account.json`) e **não** faça commit dele.
5. No `.env`, adicione o **caminho absoluto** do arquivo:

```env
# Exemplo Windows
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\seu_usuario\monk\keys\gcp-service-account.json

# Exemplo Linux/macOS
# GOOGLE_APPLICATION_CREDENTIALS=/home/seu_usuario/monk/keys/gcp-service-account.json
```

*(Opcional)* Se quiser fixar o projeto GCP nas queries:

```env
GOOGLE_CLOUD_PROJECT=seu-projeto-id
```

### Passo 4: Rodar a API

Na raiz do projeto (com o ambiente virtual ativado):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Documentação interativa:** http://localhost:8000/docs  
- **Health check:** http://localhost:8000/api/health  

### Passo 5: Testar o agente

Exemplo via terminal:

```bash
curl -X POST http://localhost:8000/api/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"Como foi o volume de usuários vindos de Search no último mês?\"}"
```

*(No Linux/macOS use `\` no lugar de `^`.)*

Ou use a interface em http://localhost:8000/docs → **POST /api/ask** → Try it out.

### Frontend (repositório separado)

A interface em **React + Tailwind** que consome esta API está em outro repositório:

- **Frontend:** [analista-midia-frontend](https://github.com/SEU_USUARIO/analista-midia-frontend) *(substitua pela URL real do repo do frontend)*

Lá você encontra instruções para rodar o frontend em desenvolvimento (com proxy para esta API) e para build de produção usando `VITE_API_URL` se a API estiver em outro domínio.

---

## Arquitetura do agente — Diagrama e explicação

O agente **não** é um único prompt que envia todos os dados para a LLM. Ele usa **Tool Calling (Function Calling)**: o modelo **decide** quando chamar cada ferramenta; as ferramentas executam código (consultas ao BigQuery) e devolvem resultados para o modelo formular a resposta em linguagem natural.

### Diagrama de fluxo

```
┌─────────────┐     POST /api/ask      ┌──────────────┐
│   Cliente   │ ────────────────────► │   FastAPI    │
└─────────────┘   { "question": "..." } └──────┬───────┘
                                              │
              ┌───────────────────────────────▼───────────────────────────────┐
              │                    Agente (LangChain)                         │
              │  ┌─────────────┐     Tool Calling      ┌──────────────────┐   │
              │  │ System      │ ◄──────────────────►  │ LLM (OpenAI)     │   │
              │  │ Prompt      │   (modelo decide      │ gpt-4o-mini      │   │
              │  │ (Analista   │    quais tools usar)  └────────┬─────────┘   │
              │  │  Júnior)    │                                 │             │
              │  └─────────────┘                    ┌───────────▼───────────┐ │
              │                                     │ Tools (ferramentas)   │ │
              │                                     │ • get_traffic_volume  │ │
              │                                     │ • get_channel_        │ │
              │                                     │   performance         │ │
              │                                     │ • list_traffic_sources│ │
              │                                     └───────────┬───────────┘ │
              └─────────────────────────────────────────────────│─────────────┘
                                                                 │
              ┌──────────────────────────────────────────────────▼────────────┐
              │   BigQueryClient + BigQueryAnalyticsRepository (Repository)   │
              │   Queries parametrizadas → thelook_ecommerce                   │
              │   (users, orders, order_items)                                 │
              └───────────────────────────────────────────────────────────────┘
```

### Quais tools foram criadas e por quê

| Tool | Propósito | Quando o agente usa |
|------|-----------|----------------------|
| **`get_traffic_volume_tool`** | Consultar **volume de usuários** por canal de tráfego em um período. | Perguntas como *"Como foi o volume de usuários vindos de Search no último mês?"* ou *"Quantos usuários vieram do Organic em janeiro?"*. Filtra a tabela `users` por `traffic_source` e intervalo de datas. |
| **`get_channel_performance_tool`** | Consultar **performance por canal**: usuários, pedidos, receita total, receita por usuário, pedidos por usuário. | Perguntas como *"Qual canal tem a melhor performance?"*, *"Qual o ROI por canal?"*, *"Qual canal gera mais receita por usuário?"*. Usa JOIN entre `users`, `orders` e `order_items` (receita via `sale_price`). |
| **`list_traffic_sources_tool`** | Listar os **canais de tráfego** existentes no dataset (ex.: Search, Organic, Facebook). | Quando o agente precisa saber quais canais existem antes de responder ou quando o usuário pergunta "quais canais temos?". |

A **lógica de execução** (SQL, chamada ao BigQuery) fica nas **tools**; a **lógica de interpretação e redação** (entender a pergunta, escolher a tool, resumir em texto útil) fica no **LLM**. Assim atendemos ao requisito de separar prompt da execução de código e de usar Tool Calling corretamente.

---

## Estrutura do projeto

```
monk/
├── app/
│   ├── agent/                  # Orquestrador + factory de tools + prompts
│   │   ├── agent.py            # MediaAnalystOrchestrator (Template Method)
│   │   ├── agent_factory.py   # create_media_analyst_orchestrator (DI)
│   │   ├── prompts.py         # System prompt do Analista Júnior
│   │   └── tools_factory.py   # create_analyst_tools(repo) — Factory + DI
│   ├── api/
│   │   ├── dependencies.py    # Injeção de dependências (FastAPI Depends)
│   │   └── routes.py          # POST /api/ask, GET /api/health (Controller)
│   ├── domain/
│   │   ├── exceptions.py     # Hierarquia de exceções (AppException → DataSourceError, etc.)
│   │   ├── interfaces.py    # IAnalyticsRepository (Protocol — Dependency Inversion)
│   │   └── schemas.py        # Pydantic: AgentResponse, TrafficVolumeResult, ChannelPerformance
│   ├── services/
│   │   ├── analytics_repository.py   # BigQueryAnalyticsRepository (Repository Pattern)
│   │   └── bigquery_client.py        # BigQueryClient (SRP: executar queries)
│   └── main.py               # App FastAPI + exception handlers globais
├── config/
│   ├── constants.py         # Constantes (model name, max_turns)
│   └── settings.py          # Settings (Pydantic Settings, .env)
├── main.py                  # Entrypoint uvicorn (main:app)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Padrões e boas práticas

- **SOLID:** SRP (cliente BQ vs repositório; controller vs orquestrador), DIP (dependência em `IAnalyticsRepository`), ISP (protocolos enxutos).
- **Design patterns:** Repository (acesso a dados abstraído), Factory (tools e orquestrador), Dependency Injection (FastAPI Depends), Template Method (loop do agente), hierarquia de exceções (tratamento centralizado).
- **Hábitos:** tipagem (type hints e Pydantic), logging em falhas, constantes centralizadas.

---

## Stack

- **Backend:** Python 3.10+, FastAPI  
- **IA:** LangChain + Tool Calling (OpenAI)  
- **Dados:** Google BigQuery (cliente oficial Python), dataset `bigquery-public-data.thelook_ecommerce`  
- **Frontend:** em [repositório separado](https://github.com/SEU_USUARIO/analista-midia-frontend) (React 18, Vite, TypeScript, Tailwind CSS)  

---

## Exemplos de perguntas

- *"Como foi o volume de usuários vindos de Search no último mês?"*  
- *"Qual dos canais tem a melhor performance? E por quê?"*  
- *"Quais canais de tráfego existem?"*  
- *"Qual canal gera mais receita por usuário?"*  

A resposta da API vem em JSON: `answer` (texto em linguagem natural) e `sources_used` (lista das ferramentas utilizadas).

---

## Testes, CI e Docker

### Testes

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Os testes cobrem: health (versão e `openai_configured`), POST `/api/ask` (com agente mockado), validação de body, orquestrador com/sem tool calls e factory de tools. Não é necessário OpenAI nem BigQuery para rodar os testes.

### Lint (Ruff)

```bash
ruff check app config tests
```

### CI (GitHub Actions)

O workflow `.github/workflows/ci.yml` roda em todo push/PR em `main`/`master`: instala dependências, executa Ruff e Pytest. Coloque `OPENAI_API_KEY=sk-test-fake-for-ci` no CI (os testes usam mocks e não consomem a API).

### Docker

```bash
# Build e run
docker-compose up --build
# API em http://localhost:8000
```

O `Dockerfile` usa imagem slim, usuário não-root e `HEALTHCHECK` em `/api/health`. Credenciais via `.env` ou variáveis de ambiente no `docker-compose`.

---

## Como publicar no GitHub (entregável 1)

Este repositório contém **apenas o backend (API)**. O frontend está em um repositório separado (pasta `monk-frontend` na mesma raiz que este projeto, ou outro repo de sua escolha).

**Backend (este projeto):**

1. Crie um repositório **público** no GitHub (ex.: `analista-midia-backend` ou `monk`).
2. Na raiz do projeto (backend), execute (substitua `SEU_USUARIO` e o nome do repo):

```bash
git init
git add .
git commit -m "MVP Analista de Mídia - Backend (API + Agente IA + BigQuery)"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/analista-midia-backend.git
git push -u origin main
```

3. Atualize o link do repositório no topo deste README e na seção "Frontend (repositório separado)" (com a URL do repo do **frontend** quando ele existir).

**Frontend (repositório separado):**

1. Crie outro repositório no GitHub (ex.: `analista-midia-frontend`).
2. Na pasta do frontend (ex.: `monk-frontend`, criada ao lado desta):

```bash
cd monk-frontend
git init
git add .
git commit -m "Frontend React + Tailwind para Analista de Mídia"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/analista-midia-frontend.git
git push -u origin main
```

3. No README do frontend, atualize o link do backend. No README do backend, atualize o link do frontend.
# analista-midia-backend
