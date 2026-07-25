from pydantic_settings import BaseSettings, SettingsConfigDict   
from typing import List   

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list[str] 
    FILE_MAX_SIZE: int

    FILE_DEFAULT_CHUNK_SIZE: int 

    # MONGODB_URL: str 
    # MONGODB_DATABASE : str

    # postgres config
    POSTGRES_USERNAME: str 
    POSTGRES_PASSWORD: str 
    POSTGRES_HOST: str 
    POSTGRES_PORT: int 
    POSTGRES_DATABASE: str

    # LLM Config
    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str

    OPENAI_API_BASE_URL: str = None
    OPENAI_TOKEN: str = None
    MODEL_NAME : str = None

    GEMINI_API_KEY : str = None
    
    GENERATION_MODEL_ID : str = None
    EMBEDDING_MODEL_ID : str = None
    EMBEDDING_MODEL_SIZE : int = None

    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    OUTPUT_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None

    # Vector DB Config
    VECTOR_DB_BACKEND_LITERAL : List[str] = None
    VECTOR_DB_BACKEND : str = None
    VECTOR_DB_PATH :  str = None
    VECTOR_DB_DISTANCE_METHOD : str = None
    VECTOR_DB_PGVECTOR_INDEX_THRESHOLD: int = 100

    DEFAULT_LANGUAGE:str = None
    PRIMARY_LANGUAGE:str = None
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()