from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "RAG API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    # LLM
    openai_api_key: str | None = None
    llm_provider: str = "local"

    # Vector DB
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Tell Pydantic where to find your .env
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")


settings = Settings()
