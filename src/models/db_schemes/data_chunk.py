from pydantic import BaseModel , Field, validator
from bson.objectid import ObjectId
from typing import Optional

class DataChunk(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # Optional field for MongoDB ObjectId
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict 
    chunk_order : int = Field(..., gt=0)  # Ensure chunk_order is a non-negative integer
    chunk_project_id : str
    chunk_asset_id : str

    @validator('id', pre=True, always=True)
    def convert_objectid_to_str(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        
        return value


    class Config: 
        arbitrary_types_allowed = False # to ignore any type error for ObjectId
        allow_population_by_field_name = True


    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("project_id", 1) # ascending, -1 if descending 
                ],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]
    

class RetrievedDocument(BaseModel):
    text: str 
    score: float