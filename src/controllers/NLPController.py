
from controllers.BaseController import BaseController
from models.db_schemes import Project , DataChunk
from stores.llm.LLMEnum import DocumentTypeEnum
from typing import List
import json 



class NLPController(BaseController):
    def __init__(self, generation_client , vector_db_client, embedding_client, template_parser):
        super().__init__()
        self.generation_client = generation_client
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    
    def create_collection_name(self, project_id: str) -> str:
        """there are vector databases dont accept numbers as collection name"""
        # print(f"collection created as collection_{self.vector_db_client.default_vector_size}_{project_id}_collection")
        return f"collection_{self.vector_db_client.default_vector_size}_{project_id}_collection".strip()
    


    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vector_db_client.delete_collection(collection_name=collection_name)


    async def get_vector_db_collection_info(self, project: Project) -> dict:
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = await self.vector_db_client.get_collection_info(collection_name=collection_name)
        return collection_info
    

    async def index_into_vector_db(self, project: Project, chunks_ids: List[int], chunks: List[DataChunk], do_reset: int = 0):
        """
        Step 1: Get Collection Name
        Step 2: Manage Items
        Step 3: Create Collection if not exist 
        Step 4: Insert into vector_db
        """

        # step 1
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step 2
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = self.embedding_client.embed_text(text=texts, document_type=DocumentTypeEnum.DOCUMENT.value)    

        # step 3
        _ = await self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )

        # step 4
        _ = await self.vector_db_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadatas=metadata,
            record_ids=[c.chunk_id for c in chunks]
        )

        return True
    

    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        """
        Step 1: Get Collection Name
        Step 2: Embed Query
        Step 3: Search in Vector DB
        """

        # step 1
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step 2
        query_vector = None
        vectors = self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.QUERY.value)

        if not vectors or len(vectors) == 0:
            return False

        if isinstance(vectors, list) and len(vectors) > 0:
            query_vector = vectors[0]

        if not query_vector:
            return False

        # step 3
        try: 
            search_results = await self.vector_db_client.search_by_vector(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            if not search_results:
                return None

            return search_results
        except Exception as e:
            print("error on getting search results from vector db", e)
            return None
        

    async def answer_rag_question(self,project: Project, text: str, limit: int = 5):
        """
        Step 1: Generate Answer using LLM
        """

        # step 1
        retrieved_docs = await self.search_vector_db_collection(
            project=project, 
            text=text, 
            limit=limit
        )

        if not retrieved_docs or len(retrieved_docs) == 0:
            return None
        
        system_prompt = self.template_parser.get("rag","system_prompt")

        document_prompts = "\n".join([
            self.template_parser.get("rag","document_prompt",{
                    "doc_number" : idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),    
                })
            for idx, doc in enumerate(retrieved_docs)
        ])

        footer_prompt = self.template_parser.get("rag","footer_prompt", {
            "query": text
        })

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            ),
        ]

        full_prompt = "\n\n".join([document_prompts, footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history