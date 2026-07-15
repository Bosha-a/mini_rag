from fastapi import FastAPI , APIRouter , Depends 
from helpers.config import get_settings , Settings

base_router = APIRouter(
    prefix="/api/v1", # static prefix before each route 
    tags=["api_v1"], # organized routes under a specific_tag - seperate collection of rourtes under specific tag
    # responses={404: {"description": "Not found"}}
)

@base_router.get("/")
async def welcome(app_settings : Settings = Depends(get_settings)): # Depends for more efficiency / won't load function without app settings

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "message": "Hello ",
        "app_name" : app_name ,
        "app_version" : app_version
    }
