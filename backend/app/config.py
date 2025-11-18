"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import Literal


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Database configuration
    DATABASE_URL: str = Field(
        default="postgresql://inventory:password@localhost:5432/inventory_db",
        description="PostgreSQL database connection string"
    )
    
    # Redis configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis cache connection string"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="garb-and-glitz-dev-secret-key-change-in-production-please",
        min_length=32,
        description="Secret key for JWT and encryption"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )
    
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Garb & Glitz Inventory API"
    
    # Database pool settings
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=20)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1)
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = Field(default=50, ge=1, le=100)
    MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=1000)
    
    # File upload
    MAX_UPLOAD_SIZE: int = Field(default=10_485_760, description="Max file size in bytes (10MB)")
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validate DATABASE_URL format."""
        if not v.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v
    
    @validator("REDIS_URL")
    def validate_redis_url(cls, v: str) -> str:
        """Validate REDIS_URL format."""
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str, values: dict) -> str:
        """Validate SECRET_KEY in production."""
        if values.get("ENVIRONMENT") == "production":
            if v == "your-secret-key-change-in-production":
                raise ValueError(
                    "SECRET_KEY must be changed in production environment"
                )
        return v


# Create global settings instance
settings = Settings()