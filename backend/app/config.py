from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "MeetingMind"
    debug: bool = False
    secret_key: str = "change-this-to-a-random-secret-key"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Database
    database_url: str = "sqlite+aiosqlite:///./meetingmind.db"

    # OpenAI
    openai_api_key: Optional[str] = None

    # Otter.ai
    otter_email: Optional[str] = None
    otter_password: Optional[str] = None

    # Notion
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None

    # Zapier Webhooks
    zapier_webhook_summary: Optional[str] = None
    zapier_webhook_action_items: Optional[str] = None
    zapier_webhook_followup: Optional[str] = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
