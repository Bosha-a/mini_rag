from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")

from routes import base , data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vector_db.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


app = FastAPI()

async def startup_span():
    settings = get_settings()

    # app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    # app.db_client = app.mongodb_connection[settings.MONGODB_DATABASE]

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)
    
    app.db_client = sessionmaker(app.db_engine, class_=AsyncSession, expire_on_commit=False)


    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(settings)

    # Generation Client 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # Vector DB Client
    app.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()  # Connect to the vector database

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE
        )  # Initialize TemplateParser with default language


async def shutdown_span():
    # app.mongodb_connection.close()
    app.db_engine.dispose()  # Dispose of the SQLAlchemy engine
    app.vector_db_client.disconnect()  # Disconnect from the vector database


##Each app should be responsed on default route ('/')
# app.router.lifespan.on_startup.append(startup_span)
# app.router.lifespan.on_shutdown.append(shutdown_span)

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)

