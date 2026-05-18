from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Interview Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # AI Provider Settings
    # 👇 Changed to Groq to match your .env file!
    GROQ_API_KEY: str 

    # 👇 Added extra="ignore" so it doesn't crash if you have other stuff in your .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instantiate it once to be used across the app
settings = Settings()