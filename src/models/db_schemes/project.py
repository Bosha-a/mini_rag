from pydantic import BaseModel , Field, Validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    _id: Optional[ObjectId]
    project_id: str = Field(..., min_length=1)

    @Validator('project_id')
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        
        return value
        
    class Config: 
        arbitrary_types_allowed = False