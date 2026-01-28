"""
Configuración del Backend (SQLite, sin Redis)
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_PATH: str = "/var/fotolibros/fotolibros.db"
    CLAWDBOT_URL: str = "http://127.0.0.1:18789"
    CLAWDBOT_HOOK_TOKEN: str = ""
    OPENROUTER_API_KEY: str = ""
    AGNO_MODEL: str = "openai/gpt-4o-mini"
    TELEGRAM_ADMIN_CHAT: str = ""
    FDF_USER: str = ""
    FDF_PASS: str = ""
    PHOTOS_BASE_DIR: str = "/var/fotolibros/pedidos"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://168.231.98.115:8080"]
    WORKER_MAX_RETRIES: int = 3
    WORKER_TIMEOUT_MINUTES: int = 45
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
