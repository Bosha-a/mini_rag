from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

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

        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], 
                    name=index["name"], 
                    unique=index["unique"]
                )


    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude={"id"}))
        project.id = str(result.inserted_id)
        return project
    

    async def get_project_or_create_one(self,project_id: str):
        record = await self.collection.find_one({"project_id": project_id})

        if record is None: # create new project 
            project = Project(project_id=project_id)
            return await self.create_project(project=project)
        
        return Project(**record) # converting dict that comes from db to Project object
    

    # dont use get all without pagination 
    """
    **Pagination** is a technique used to divide a large dataset into smaller, more manageable chunks or pages. 
    It is commonly used in web applications and APIs to improve performance and user experience when dealing with large amounts of data. 
    Instead of loading all the data at once, pagination allows users to request and view a subset of the data at a time, 
    typically by specifying a page number and the number of items per page.
    
    """
    async def get_all_projects(self, page:int=1 , page_size : int=10):
        total_documents = await self.collection.count_documents({})
        total_pages = (total_documents // page_size) 
        if total_documents % page_size > 0:
            total_pages += 1

        # payload may be crach 
        # for memory effeciency use cursor and async for loop to iterate over the documents in the collection instead of loading all once 
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size) 
        projects = []
        async for document in cursor:
            projects.append(Project(**document))

        return {
            "projects": projects,
            "total_pages": total_pages,
        }