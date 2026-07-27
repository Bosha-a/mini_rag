# from pydantic import BaseModel, Field, validator
# from typing import Optional
# from bson.objectid import ObjectId
# from datetime import datetime


# class Asset(BaseModel):
#     id : Optional[str] = Field(None, alias="_id")  # Optional field for MongoDB ObjectId
#     asset_project_id : str
#     asset_type : str = Field(..., min_length=1)
#     asset_name : str = Field(..., min_length=1)
#     asset_size:  Optional[int] = Field(default=None, gt=0)
#     asset_config: Optional[dict] = Field(default=None)
#     asset_created_at: datetime = Field(default_factory=datetime.utcnow)

#     @validator('id', pre=True, always=True)
#     def convert_objectid_to_str(cls, value):
#         if isinstance(value, ObjectId):
#             return str(value)
        
#         return value


#     class Config:
#         arbitrary_types_allowed = False 
#         allow_population_by_field_name = True


#     @classmethod
#     def get_indexes(cls):
#         return [
#             { # for project_id 
#                 "key": [
#                     ("asset_project_id", 1) 
#                 ],
#                 "name": "asset_project_id_index_1",
#                 "unique": False
#             },
#             { # for asset_name 
#                 "key": [
#                     ("asset_project_id", 1) ,
#                     ("asset_name", 1) 
#                 ],
#                 "name": "asset_project_id_name_index_1",
#                 "unique": True # absolutelty project id and name be repeated 
#             }
#         ]