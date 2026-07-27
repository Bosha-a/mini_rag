from .VectorDBEnum import VectorDBEnum
from .providers import QdrantDBProvider, PGVectorProvider
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker

class VectorDBProviderFactory:
    def __init__(self, config: dict, db_client: sessionmaker=None):
        self.config = config
        self.base_controller = BaseController()  # Initialize BaseController to access its methods
        self.db_client = db_client

    def create(self, provider: str): 
        if provider == VectorDBEnum.QDRANT.value:
            qdrant_db_client=self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            
            return QdrantDBProvider(
                db_path=qdrant_db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVECTOR_INDEX_THRESHOLD
            )

        if provider == VectorDBEnum.PGVECTOR.value:
            return PGVectorProvider(
                db_client=self.db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVECTOR_INDEX_THRESHOLD
            )
        
        return None