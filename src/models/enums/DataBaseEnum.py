from enum import Enum 

class DataBaseEnum(Enum):
    """
    Enum class for database-related constants.
    """
    COLLECTION_PROJECT_NAME = "projects"
    COLLECTION_CHUNK_NAME = "chunks"
    COLLECTION_ASSET_NAME = "assets"