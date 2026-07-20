
from controllers.BaseController import BaseController
from models.db_schemes import Project , DataChunk
from stores.llm.LLMEnum import DocumentTypeEnum
from typing import List
import json 



class NLPController(BaseController):
    def __init__(self, generation_client , vector_db_client, embedding_client):
        super().__init__()
        self.generation_client = generation_client
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client

    
    def create_collection_name(self, project_id: str) -> str:
        """there are vector databases dont accept numbers as collection name"""
        print(f"collection created as project_{project_id}_collection")
        return f"project_{project_id}_collection"
    


    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.id)
        return self.vector_db_client.delete_collection(collection_name=collection_name)


    def get_vector_db_collection_info(self, project: Project) -> dict:
        collection_name = self.create_collection_name(project_id=project.id)
        collection_info = self.vector_db_client.get_collection_info(collection_name=collection_name)
        return collection_info
    

    def index_into_vector_db(self, project: Project, chunks_ids: List[int], chunks: List[DataChunk], do_reset: int = 0):
        """
        Step 1: Get Collection Name
        Step 2: Manage Items
        Step 3: Create Collection if not exist 
        Step 4: Insert into vector_db
        """

        # step 1
        collection_name = self.create_collection_name(project_id=project.id)

        # step 2
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]

        vectors = [
            self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        # step 3
        _ = self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )

        # step 4
        _ = self.vector_db_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunks_ids
        )

        return True
    

    def search_vector_db_collection(self, project: Project, query: str, limit: int = 10):
        """
        Step 1: Get Collection Name
        Step 2: Embed Query
        Step 3: Search in Vector DB
        """

        # step 1
        collection_name = self.create_collection_name(project_id=project.id)

        # step 2
        query_vector = self.embedding_client.embed_text(text=query, document_type=DocumentTypeEnum.QUERY.value)

        # step 3
        try: 
            search_results = self.vector_db_client.search_by_vector(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            if not search_results:
                return None

            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text"),
                    "metadata": result.payload.get("metadata")
                }
                for result in search_results
            ]
        except Exception as e:
            print("error on getting search results from vector db", e)
            return None