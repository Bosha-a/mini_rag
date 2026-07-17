from pydantic_settings import BaseSettings, SettingsConfigDict      

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list[str] 
    FILE_MAX_SIZE: int

    FILE_DEFAULT_CHUNK_SIZE: int 

    MONGODB_URL: str 
    MONGODB_DATABASE : str


    GENERATION_BACKEND = "OPENAI"
    EMBEDDING_BACKEND = "COHERE"

    OPENAI_API_BASE_URL: str = None
    OPENAI_TOKEN: str = None
    MODEL_NAME : str = None

    COHERE_API_KEY : str = None
    
    GENERATION_MODEL_ID : str = None
    EMBEDDING_MODEL_ID : str = None
    EMBEDDING_MODEL_SIZE : str = None

    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    OUTPUT_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()