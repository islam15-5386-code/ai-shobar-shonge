import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Service")
    app_env: str = os.getenv("APP_ENV", "development")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    use_openai: bool = os.getenv("USE_OPENAI", "false").lower() == "true"
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "vector_store/faqs.json")
    top_k: int = int(os.getenv("RAG_TOP_K", "3"))


settings = Settings()
