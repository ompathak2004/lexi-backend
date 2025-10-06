from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "Jagriti API Wrapper"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Jagriti API Base URL
    JAGRITI_BASE_URL: str = "https://e-jagriti.gov.in"
    
    # Cache TTL (in seconds)
    CACHE_TTL_STATES: int = 86400  # 24 hours
    CACHE_TTL_CATEGORIES: int = 86400  # 24 hours
    CACHE_TTL_COMMISSIONS: int = 21600  # 6 hours
    CACHE_TTL_JUDGES: int = 21600  # 6 hours
    CACHE_TTL_CASES: int = 300  # 5 minutes
    
    # HTTP Client Settings
    REQUEST_TIMEOUT: int = 300
    MAX_RETRIES: int = 3
    MAX_CONCURRENT_REQUESTS: int = 10
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 30
    MAX_PAGE_SIZE: int = 100
    
    model_config = {
        "case_sensitive": True,
        "extra": "allow"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()