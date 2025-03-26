from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_uri: str
    db_uri_test: str

    api_name: Literal["JIKAN"]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env", case_sensitive=False
    )
