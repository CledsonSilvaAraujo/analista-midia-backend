# Multi-stage: build opcional (apenas runtime por enquanto)
FROM python:3.11-slim as runtime

WORKDIR /app

# Dependências do sistema (BigQuery client pode usar gRPC)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY app/ ./app/
COPY config/ ./config/
COPY main.py .

# Porta padrão uvicorn
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=2 \
    CMD curl -sf http://localhost:8000/api/health || exit 1

# Usuário não-root (segurança)
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
