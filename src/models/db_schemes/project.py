from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  
    project_id: str = Field(..., min_length=1)

    @validator('id', pre=True, always=True)
    def convert_objectid_to_str(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        
        return value
    
    @validator('project_id')
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        
        return value
        
    class Config: 
        arbitrary_types_allowed = False
        allow_population_by_field_name = True