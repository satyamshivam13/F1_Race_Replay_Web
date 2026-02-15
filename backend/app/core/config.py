"""
Application configuration using Pydantic Settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "F1 Race Replay API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/f1replay"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "https://f1replay.vercel.app"]
    
    # FastF1
    fastf1_cache_dir: str = "/tmp/fastf1_cache"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Replay
    replay_fps: int = 30
    max_concurrent_replays: int = 100
    
    # Sentry
    sentry_dsn: str = ""
    sentry_environment: str = "production"
    sentry_traces_sample_rate: float = 0.1
    sentry_profiles_sample_rate: float = 0.1
    
    # Rate Limiting
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
