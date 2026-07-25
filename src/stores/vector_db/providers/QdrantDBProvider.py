from ..VectorDBInterface import VectorDBInterface
from qdrant_client import models, QdrantClient
from ..VectorDBEnum import DistanceMethonEnum
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_client: str, distance_method: str, default_vector_size: int = 3072, index_threshold: int = 100):
        self.client = None
        self.db_client = db_client
        self.distance_method = None 


        if distance_method == DistanceMethonEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethonEnum.DOT.value:
            self.distance_method = models.Distance.DOT
        
        self.logger = logging.getLogger("uvicorn")


    async def connect(self):
        try:
            self.client = QdrantClient(path=self.db_client)
            self.logger.info(f"Connected to Qdrant database at {self.db_client}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant database: {e}")
            raise e


    async def disconnect(self):
        self.client = None


    async def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)


    async def list_all_collections(self) -> List:
        return self.client.get_collections()


    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name).model_dump()


    async def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name=collection_name)


    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
            if do_reset:
                _ = self.delete_collection(collection_name=collection_name)
            
            if not self.is_collection_exists(collection_name):
                self.logger.info(f"Creating collection {collection_name}")
                _ = self.client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=embedding_size,
                        distance=self.distance_method
                    )
                )

                return True
            return False
        

    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist. Please create it first.")
            return False
        
        try:
            _ = self.client.upload_points(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to insert record into collection {collection_name}: {e}")
            return False    

    async def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: list = None, record_ids: list = None, batch_size: int = 50):
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist. Please create it first.")
            return False
        
        if metadata is None:
            metadata = [None] * len(texts)
        
        if record_ids is None:
            record_ids = list(range(len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_points = [
                models.PointStruct(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]
            
            try: 
                _ = self.client.upload_points(
                    collection_name=collection_name,
                    points=batch_points
                )
            except Exception as e:
                self.logger.error(f"Failed to insert batch records into collection {collection_name}: {e}")
                return False
            
        return True


    async def search_by_vector(self, collection_name: str, query_vector: list, limit: int = 5):
        results = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit
        ).points
    
        if not results or len(results) == 0:
            return None
        
        return [
            RetrievedDocument(
                text=result.payload.get("text"),
                score=result.score
            )
            for result in results
        ]
    


