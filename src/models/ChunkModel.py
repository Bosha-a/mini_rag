from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId 
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]


    @classmethod
    async def create_instance(cls, db_client: object):
        """Factory method to create an instance of ProjectModel and initialize the collection. 
        Declaring init_collection in __init__ is not possible in python so we use create_instance to create instance of class and init collection)"""
        instance = cls(db_client) 
        await instance.init_collection()  # Initialize the collection and create indexes
        return instance

    async def init_collection(self):
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
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude={"id"}))
        chunk.id = str(result.inserted_id)
        return chunk


    async def get_chunk(self, chunk_id: str):
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if record is None:
            return None
        
        return DataChunk(**record) 
    
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            operation = [
                InsertOne(chunk.dict(by_alias=True, exclude={"id"})) for chunk in batch
            ]
            await self.collection.bulk_write(operation)

        return len(chunks) # Return the number of inserted chunks
    

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        
        return result.deleted_count
