from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId 
from pymongo import InsertOne
from sqlalchemy import select, delete


class ChunkModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        # self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
        self.db_client = db_client


    @classmethod
    async def create_instance(cls, db_client: object):
        """Factory method to create an instance of ProjectModel and initialize the collection. 
        Declaring init_collection in __init__ is not possible in python so we use create_instance to create instance of class and init collection)"""
        instance = cls(db_client) 
        # await instance.init_collection()  # Initialize the collection and create indexes
        return instance

    # async def init_collection(self):
        """Initialize the project collection and create necessary indexes."""
        all_collections = await self.db_client.list_collection_names()

        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], 
                    name=index["name"], 
                    unique=index["unique"]
                )
    
    async def create_chunk(self, chunk: DataChunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
                await session.commit() 
                await session.refresh(chunk) 

            return chunk


    async def get_chunk(self, chunk_id: str):
        async with self.db_client() as session:
            async with session.begin():
                chunk = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
                return chunk

    
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i + batch_size]
                    session.add_all(batch)
            await session.commit()

        return len(chunks) # Return the number of inserted chunks
    

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        async with self.db_client() as session:
            result = await session.execute(delete(DataChunk).where(DataChunk.chunk_project_id == project_id))
            await session.commit()
        return result.rowcount  # Return the number of deleted chunks

        

    async def get_project_chunks(self, project_id: str, page_num: int=0, page_size: int=50):
        """Retrieve all chunks associated with a specific project ID."""
        async with self.db_client() as session:
            chunks = await session.execute(
                select(DataChunk)
                .where(DataChunk.chunk_project_id == project_id)
                .offset((page_num - 1) * page_size)
                .limit(page_size)
            )
            return chunks.scalars().all()  # Return the list of chunks
            
        