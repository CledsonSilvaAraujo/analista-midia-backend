"""Ponto de entrada para uvicorn."""
# Permite rodar: python -m uvicorn main:app
from app.main import app

__all__ = ["app"]
