"""
M537 Voice Gateway Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Server configuration
    PORT: int = 5537
    HOST: str = "0.0.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Project paths
    PROJECTS_BASE_PATH: str = "/data/projects"

    # Security configuration
    MAX_TRANSCRIPT_LENGTH: int = 500
    RATE_LIMIT_PER_MINUTE: int = 60

    # V5.3 Ecosystem information
    ECOSYSTEM_VERSION: str = "V5.3"
    PROJECT_ID: str = "m537"
    PROJECT_NAME: str = "voice_gateway"
    VERSION: str = "1.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
