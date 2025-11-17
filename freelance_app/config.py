"""
Configuration settings for AI Freelance Search App
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "AI Freelance Search App"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://freelance_user:freelance_pass@localhost:5432/freelance_db"
    )
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "300"))  # 5 minutes

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com"
    ]

    # Subscription Tiers
    FREE_TIER_VETTING_LIMIT: int = 5
    PRO_TIER_VETTING_LIMIT: int = 999999  # Unlimited
    PREMIUM_TIER_VETTING_LIMIT: int = 999999  # Unlimited

    # Rate Limiting
    FREE_TIER_RATE_LIMIT: int = 100  # requests per hour
    PRO_TIER_RATE_LIMIT: int = 1000
    PREMIUM_TIER_RATE_LIMIT: int = 5000

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Trust Score Weights (should sum to 1.0)
    TRUST_SCORE_WEIGHTS: dict = {
        "account_age": 0.20,
        "payment_verified": 0.15,
        "total_spent": 0.15,
        "hire_rate": 0.15,
        "average_rating": 0.20,
        "response_time": 0.10,
        "completion_rate": 0.05
    }

    class Config:
        env_file = ".env"


settings = Settings()
