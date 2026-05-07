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
    ai_mode: str = os.getenv("AI_MODE", "cpu").lower()
    llm_provider: str = os.getenv("LLM_PROVIDER", "local").lower()
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    whisper_provider: str = os.getenv("WHISPER_PROVIDER", "local").lower()
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "llama3.1:8b-instruct-q4_K_M")
    local_embedding_model: str = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    local_whisper_model: str = os.getenv("LOCAL_WHISPER_MODEL", "small")
    cuda_device: str = os.getenv("CUDA_DEVICE", "cuda:0")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    model_mode: str = os.getenv("MODEL_MODE", "dev_rule_based")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///../backend/db.sqlite3")


settings = Settings()
