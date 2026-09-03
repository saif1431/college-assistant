"""Centralized application configuration.

All environment-driven values are defined here and nowhere else. Settings are
read from the repository-root `.env` file (shared by backend and frontend),
regardless of which directory the backend process is started from.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] == college-assistant/ (repo root)
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- LLM ---
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"
    groq_temperature: float = 0.3

    # --- Embeddings ---
    hf_token: str | None = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # --- RAG ---
    documents_dir: str = "backend/data/documents"
    vector_store_dir: str = "backend/data/vector_store"
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_k: int = 3

    # --- App ---
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def documents_path(self) -> Path:
        return (BASE_DIR / self.documents_dir).resolve()

    @property
    def vector_store_path(self) -> Path:
        return (BASE_DIR / self.vector_store_dir).resolve()


@lru_cache
def get_settings() -> Settings:
    """Settings are cached: env is read once per process, not per call."""
    return Settings()
