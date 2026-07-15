from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


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