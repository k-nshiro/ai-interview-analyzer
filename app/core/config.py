from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Interview Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # AI Provider Settings
    OPENAI_API_KEY: str = "" # We'll validate this later when we build the AI layer

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# InRepresent it once to be used across the app
settings = Settings()