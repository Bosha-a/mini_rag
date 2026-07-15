from pydantic import BaseModel , Field, Validator
from bson.objectid import ObjectId
from typing import Optional

class DataChunk(BaseModel):
    _id: Optional[ObjectId]
    chenk_text: str = Field(..., min_length=1)
    chunk_metadata: dict 
    chunk_order : int = Field(..., gt=0)  # Ensure chunk_order is a non-negative integer
    chunk_project_id : ObjectId


    class Config: 
        arbitrary_types_allowed = False # to ignore any type error for ObjectId
        