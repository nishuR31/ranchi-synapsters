# from pydantic_settings import BaseSettings
# from typing import Optional
# import os

# class Settings(BaseSettings):
#     """Application settings from environment variables"""
    
#     # Neo4j
#     neo4j_uri: str = "bolt://localhost:7687"
#     neo4j_user: str = "neo4j"
#     neo4j_password: str = "password"
#     database_name: str = "neo4j"
    
#     # FastAPI
#     fastapi_host: str = "0.0.0.0"
#     fastapi_port: int = 8000
#     debug: bool = True
    
#     # Upload
#     upload_dir: str = "./data/uploads"
#     max_upload_size: int = 104857600  # 100MB
    
#     # ML
#     num_workers: int = 4
#     batch_size: int = 32
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False

# settings = Settings()

# # Create upload directory if it doesn't exist
# os.makedirs(settings.upload_dir, exist_ok=True)





from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # -------------------------------
    # FastAPI
    # -------------------------------
    FASTAPI_HOST: str = "127.0.0.1"
    FASTAPI_PORT: int = 8000
    DEBUG: bool = True

    # -------------------------------
    # Neo4j Aura
    # -------------------------------
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    DATABASE_NAME: str = "neo4j"

    # -------------------------------
    # Upload & Processing
    # -------------------------------
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 104857600   # 100 MB
    NUM_WORKERS: int = 4
    BATCH_SIZE: int = 32

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",   # Ignore any future env vars instead of crashing
    )


settings = Settings()
