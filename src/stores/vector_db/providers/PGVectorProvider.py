from src.stores.vector_db.VectorDBInterface import VectorDBInterface
from src.stores.vector_db.VectorDBEnum import (
    DistanceMethonEnum, PgVectorDistanceMethonEnum,
    PgVectorTableSchemaEnum, PgVectorIndexTypeEnum)
import logging 
from typing import List
from models.db_schemes import RetrievedDocument
from sqlalchemy import text as sql_text
import json


class PGVectorProvider(VectorDBInterface):
    def __init__(self, db_client, db_path: str, distance_method: str, default_vector_size: int = 3072, index_threshold: int = 100):
        self.db_client=db_client
        self.db_path=db_path
        self.default_vector_size=default_vector_size
        self.distance_method=None 
        self.index_threshold=index_threshold

        self.pgvector_table_prefix=PgVectorTableSchemaEnum._PREFIX.value
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"

        self.logger = logging.getLogger("uvicorn")


    async def connect(self):
        # Test the connection by executing a simple query
        async with self.db_client.acquire() as conn:
            async with conn.begin():
                await conn.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.commit()


    async def disconnect(self):
        pass


    async def is_collection_exists(self, collection_name: str) -> bool:
        async with self.db_client.acquire() as conn:
            async with conn.begin():
                result = await conn.execute(
                    sql_text(
                        "SELECT * FROM pg_tables WHERE tablename = :collection_name"
                    ),
                    {"collection_name": f"{self.pgvector_table_prefix}{collection_name}"}
                )
                records = await result.scalar_one_or_none()
            return records



    async def list_all_collections(self) -> List:
        async with self.db_client.acquire() as conn:
            async with conn.begin():
                result = await conn.execute(
                    sql_text(
                        "SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix"
                    ),
                    {"prefix": f"{self.pgvector_table_prefix}%"}
                )
                records = await result.scalar().all()
            return records


    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as conn:
            async with conn.begin():
                    table_info_sql = sql_text(
                        """
                        SELECT * 
                        FROM pg_tables 
                        WHERE tablename = :collection_name
                        """
                    )

                    count_sql = sql_text(
                        """
                        SELECT COUNT(*) 
                        FROM :collection_name
                        """
                    )

                    table_info_result = await conn.execute(table_info_sql, {"collection_name": collection_name})
                    record_count = await conn.execute(count_sql, {"collection_name": collection_name})  

                    table_data = table_info_result.fetchone()
                    if not table_data:
                        return None  # Collection does not exist

                    return {
                        "table_info": dict(table_data),
                        "record_count": record_count.fetchone()[0]
                    }

    async def delete_collection(self, collection_name: str):
        async with self.db_client() as conn:
            async with conn.begin():
                drop_table_sql = sql_text(
                    f"DROP TABLE IF EXISTS ;collection_name"
                )
                await conn.execute(drop_table_sql, {"collection_name": collection_name})
                await conn.commit() # because there is a change in database

        return True


    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            await self.delete_collection(collection_name=collection_name)
        
        if not await self.is_collection_exists(collection_name=collection_name):
            self.logger.info(f"Creating collection {collection_name} with embedding size {embedding_size}")
            async with self.db_client() as conn:
                async with conn.begin():
                    create_table_sql = sql_text(
                        f"""
                        CREATE TABLE ;collection_name (
                            {PgVectorTableSchemaEnum.ID.value} bigserial PRIMARY KEY,
                            {PgVectorTableSchemaEnum.TEXT.value} TEXT,
                            {PgVectorTableSchemaEnum.VECTOR.value} VECTOR({embedding_size}),
                            {PgVectorTableSchemaEnum.METADATA.value} JSONB DEFAULT \'{{}}\',
                            FOREIGN KEY ({PgVectorTableSchemaEnum.CHUNK_ID.value}) REFERENCES chunks(chunk_id)
                        )
                        """
                    )
                    await conn.execute(create_table_sql)
                    await conn.commit()  # Commit the transaction

            self.logger.info(f"Collection {collection_name} created successfully.")

            return True
        
        return False


    async def is_index_exists(self, collection_name: str) -> bool:
        index_name = await self.default_index_name(collection_name)
        async with self.db_client() as conn:
            async with conn.begin():
                result = await conn.execute(
                    sql_text(
                        "SELECT 1 FROM pg_indexes WHERE tablename = :collection_name AND indexname = :index_name"
                    ),
                    {"collection_name": collection_name, "index_name": index_name}
                )
                records = await result.scalar_one_or_none()
            return bool(records)


    async def create_vector_index(self, collection_name: str, 
                                        index_type: str = PgVectorIndexTypeEnum.HNSW.value):
        
        index_name = await self.default_index_name(collection_name)

        if not await self.is_index_exists(collection_name):
            async with self.db_client() as conn:
                async with conn.begin():
                    count_sql = sql_text(
                        f"SELECT COUNT(*) FROM {collection_name}"
                    )
                    count_result = await conn.execute(count_sql)
                    records_count = await count_result.scalar_one()

                    if records_count is None or records_count < self.index_threshold:
                        self.logger.info(f"Skipping index creation for collection {collection_name} as it has only {records_count} records.")
                        return False

                    else:
                        create_index_sql = sql_text( 
                            f"""
                            CREATE INDEX index_name 
                            ON ;collection_name 
                            USING {index_type} ({PgVectorTableSchemaEnum.VECTOR.value} {self.distance_method})
                            """
                        )
                        await conn.execute(create_index_sql, {"collection_name": collection_name, "index_name": index_name})

            self.logger.info(f"Index {index_name} created successfully on collection {collection_name}.")
            return True
        
        self.logger.info(f"Index {index_name} already exists on collection {collection_name}.")
        return False


    async def reset_vector_index(self, collection_name: str, 
                                       index_type: str = PgVectorIndexTypeEnum.HNSW.value):

        index_name = await self.default_index_name(collection_name)
        async with self.db_client() as conn:
            async with conn.begin():
                drop_index_sql = sql_text(
                    f"DROP INDEX IF EXISTS ;index_name"
                )
                await conn.execute(drop_index_sql, {"index_name": index_name})

            return await self.create_vector_index(collection_name=collection_name, index_type=index_type)



    async def insert_one(self, collection_name: str, text: str, 
                               vector: list, metadata: dict = None, 
                               record_id: str = None):

        is_collection_exists = await self.is_collection_exists(collection_name=collection_name)
        if not is_collection_exists:
            self.logger.error(f"Collection {collection_name} does not exist. Please create it first.")
            return False

        if not record_id:
            self.logger.error("Cannot insert a record without a validchunk_id.")
            return False

        async with self.db_client() as conn:
            async with conn.begin():
                insert_sql = sql_text(
                    f"""
                    INSERT INTO {collection_name} (
                    {PgVectorTableSchemaEnum.TEXT.value}, 
                    {PgVectorTableSchemaEnum.VECTOR.value}, 
                    {PgVectorTableSchemaEnum.METADATA.value},
                    {PgVectorTableSchemaEnum.CHUNK_ID.value}
                    ) 
                    VALUES (:text, :vector, :metadata, :chunk_id)
                    """
                )
                await conn.execute(insert_sql, {
                    "text": text,
                    "vector": f"[" + ",".join([str(v) for v in vector]) + "]",
                    "metadata": metadata,
                    "chunk_id": record_id
                })
                await conn.commit()  # Commit the transaction

        return True


    async def insert_many(self, collection_name: str, texts: list,
                                vectors: list, metadatas: list = None, 
                                record_ids: list = None, batch_size: int = 50):
    
        is_collection_exists = await self.is_collection_exists(collection_name=collection_name)
        if not is_collection_exists:
              self.logger.error(f"Collection {collection_name} does not exist. Please create it first.")
              return False

        if not record_ids or len(record_ids) != len(vectors):
              self.logger.error("Cannot insert records without valid chunk_ids.")
              return False

        async with self.db_client() as conn:
              async with conn.begin():
               for i in range(0, len(vectors), batch_size):
                  batch_texts = texts[i:i + batch_size]
                  batch_vectors = vectors[i:i + batch_size]
                  batch_metadatas = metadatas[i:i + batch_size] if metadatas else [None] * len(batch_vectors)
                  batch_record_ids = record_ids[i:i + batch_size]

                  values = []
                  for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadatas, batch_record_ids):
                          values.append({
                                "text": _text,
                                "vector": f"[" + ",".join([str(v) for v in _vector]) + "]",
                                "metadata": _metadata,
                                "chunk_id": _record_id
                          })

                  batch_insert_sql = sql_text(
                                      f"""
                                      INSERT INTO {collection_name} (
                                      {PgVectorTableSchemaEnum.TEXT.value}, 
                                      {PgVectorTableSchemaEnum.VECTOR.value}, 
                                      {PgVectorTableSchemaEnum.METADATA.value},
                                      {PgVectorTableSchemaEnum.CHUNK_ID.value}
                                      ) 
                                      VALUES (:text, :vector, :metadata, :chunk_id)
                                      """
                                       )
                  await conn.execute(batch_insert_sql, values)

        return True


    async def search_by_vector(self, collection_name: str, query_vector: list, limit: int = 5): 
        
        is_collection_exists = await self.is_collection_exists(collection_name=collection_name)
        if not is_collection_exists:
            self.logger.error(f"Collection {collection_name} does not exist. Please create it first.")
            return []

        query_vector = "[" + ",".join([str(v) for v in query_vector]) + "]"
        async with self.db_client() as conn:
            async with conn.begin():
                search_sql = sql_text(
                    f"""
                    SELECT {PgVectorTableSchemaEnum.TEXT.value} as text, 1 - ({PgVectorTableSchemaEnum.VECTOR.value} <=> :query_vector) AS score
                    FROM {collection_name}
                    ORDER BY score DESC
                    LIMIT :limit
                    """
                )
                result = await conn.execute(search_sql, {
                    "query_vector": query_vector,
                    "limit": limit
                })
                records = await result.fetchall()

        retrieved_documents = []
        for record in records:
            retrieved_documents.append(RetrievedDocument(
                text = record.text,
                score = record.score
            ))

        return retrieved_documents
