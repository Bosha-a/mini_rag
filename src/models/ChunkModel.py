from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId 
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    
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
