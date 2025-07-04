from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    # App Configuration
    app_name: str = "Mikrowisp Integration API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")

    # Mikrowisp API Configuration
    mikrowisp_base_url: str = Field(..., env="MIKROWISP_BASE_URL")
    mikrowisp_token: str = Field(..., env="MIKROWISP_TOKEN")
    mikrowisp_timeout: int = Field(default=30, env="MIKROWISP_TIMEOUT")

    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")

    # N8N Configuration
    n8n_webhook_url: str = Field(..., env="N8N_WEBHOOK_URL")
    n8n_api_key: str = Field(..., env="N8N_API_KEY")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # RabbitMQ Configuration
    rabbitmq_url: str = Field(..., env="RABBITMQ_URL")
    rabbitmq_queue: str = Field(default="mikrowisp_messages", env="RABBITMQ_QUEUE")

    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="JWT_EXPIRATION")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()