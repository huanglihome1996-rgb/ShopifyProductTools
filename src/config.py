"""
ShopifyProductTools 配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = "ShopifyProductTools"
    app_version: str = "0.1.0"
    debug: bool = False

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/shopify_tools.db"

    # AI 配置
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_api_key: Optional[str] = None  # 通用 AI API Key
    ai_base_url: Optional[str] = None  # AI API Base URL (for proxies)
    ai_model: str = "gpt-4-turbo-preview"

    # Shopify 配置
    shopify_api_version: str = "2024-01"

    # 导入配置
    max_import_batch: int = 100
    max_retry_attempts: int = 3

    # 图片处理配置
    image_max_width: int = 1200
    image_max_height: int = 1200
    image_quality: int = 85

    # 安全配置
    secret_key: str = "change-this-in-production"
    token_encryption_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
