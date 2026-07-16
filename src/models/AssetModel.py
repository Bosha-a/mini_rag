from models.db_schemes.asset import Asset
from bson.objectid import ObjectId 
from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum

class AssetModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
        
    @classmethod
    async def create_instance(cls, db_client: object):
        """Factory method to create an instance of ProjectModel and initialize the collection. 
        Declaring init_collection in __init__ is not possible in python so we use create_instance to create instance of class and init collection)"""
        instance = cls(db_client) 
        await instance.init_collection()  # Initialize the collection and create indexes
        return instance

    async def init_collection(self):
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
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude={"id"}))
        asset.id = str(result.inserted_id)
        return asset
    

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        records = await self.collection.find(
            {
                "asset_project_id":asset_project_id,
                "asset_type": asset_type
            }
        ).to_list(length=None) # 1 , 3 , 20 any number

        return [
            Asset(**record) 
            for record in records
            ]  # Convert each record to Asset object
    

    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        record = await self.collection.find_one(
            {
                "asset_project_id": asset_project_id,
                "asset_name": asset_name
            }
        )
        
        return Asset(**record) if record else None
