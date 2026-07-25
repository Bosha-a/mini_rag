# from models.db_schemes.asset import Asset
from bson.objectid import ObjectId 
from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy import select, delete

class AssetModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        # self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
        self.db_client = db_client
        
    @classmethod
    async def create_instance(cls, db_client: object):
        """Factory method to create an instance of ProjectModel and initialize the collection. 
        Declaring init_collection in __init__ is not possible in python so we use create_instance to create instance of class and init collection)"""
        instance = cls(db_client) 
        # await instance.init_collection()  # Initialize the collection and create indexes
        return instance

    # async def init_collection(self):
        """Initialize the project collection and create necessary indexes."""
        all_collections = await self.db_client.list_collection_names()

        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], 
                    name=index["name"], 
                    unique=index["unique"]
                )


    async def create_asset(self, asset: Asset):
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit() 
            await session.refresh(asset) 

        return asset

    

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        async with self.db_client() as session:
            assets = await session.execute(
                select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_type == asset_type
                )
            )
        return assets.scalars().all()  # Return the list of assets
    

    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        async with self.db_client() as session:
            asset = await session.execute(
                select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_name == asset_name
                )
            )
        return asset.scalar_one_or_none().first()  # Return the first matching asset record
