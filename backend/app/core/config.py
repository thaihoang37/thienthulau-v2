import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Thien Thu Lau V2"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/thienthulau"

    # Google AI - individual keys loaded from env
    GOOGLE_API_KEY1: str = ""
    GOOGLE_API_KEY2: str = ""
    GOOGLE_API_KEY3: str = ""
    GOOGLE_API_KEY4: str = ""
    GOOGLE_API_KEY5: str = ""
    GOOGLE_API_KEY6: str = ""
    GOOGLE_API_KEY7: str = ""
    GOOGLE_API_KEY8: str = ""

    @property
    def google_api_keys(self) -> list[str]:
        """Collect all non-empty GOOGLE_API_KEY* values into a list."""
        keys = [
            self.GOOGLE_API_KEY1,
            self.GOOGLE_API_KEY2,
            self.GOOGLE_API_KEY3,
            self.GOOGLE_API_KEY4,
            self.GOOGLE_API_KEY5,
            self.GOOGLE_API_KEY6,
            self.GOOGLE_API_KEY7,
            self.GOOGLE_API_KEY8,
        ]
        return [k.strip() for k in keys if k.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

