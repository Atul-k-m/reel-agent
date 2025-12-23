import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReelAgent"
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GENERATED_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "generated")
    DATA_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "data")
    
    # Models
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_HOST: str = "http://localhost:11434"

    # Optional Free/Freemium APIs (Set in .env)
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    HF_TOKEN: str = ""
    
    # New Image Providers (Optional)
    REPLICATE_API_TOKEN: str = ""
    GETIMG_API_KEY: str = ""
    SEGMIND_API_KEY: str = ""
    DEEPAI_API_KEY: str = ""
    
    # Instagram (Optional for local dev)
    IG_ACCESS_TOKEN: str = ""
    IG_ACCOUNT_ID: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
