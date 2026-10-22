"""
AgenticBuy Configuration Module.

Loads application settings from environment variables and .env file
using pydantic-settings with safe local fallbacks.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./agenticbuy.db"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "agenticbuy123"
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    JWT_SECRET_KEY: str = "agenticbuy-super-secret-jwt-key-2026-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    GEMMA_MODEL: str = "gemma2:9b"
    GRAPHIFY_OUTPUT_DIR: str = "./graphify_data"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance.

    Uses lru_cache to avoid re-reading the .env file on every call.

    Returns:
        Settings: The application settings singleton.
    """
    return Settings()
