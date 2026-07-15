from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")

from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings


app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_connection[settings.MONGODB_DATABASE]


@app.on_event("shutdown") # prefered for any shutdown process in Application 
async def shutdown_db_client():
    app.mongodb_connection.close()


##Each app should be responsed on default route ('/')
app.include_router(base.base_router)
app.include_router(data.data_router)

