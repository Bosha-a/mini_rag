from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__ (self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.PROJECT_COLLECTION_NAME.value]


    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.dict())
        project._id = result.inserted_id
        return project
    

    async def get_project_ot_create_one(self,project_id: str):
        record = await self.collection.find_one({"project_id": project_id})

        if record is None: # create new project 
            project = Project(project_id=project_id)
            return await self.create_project(project=project)
        
        return Project(**record)
    

    # dont use get all without pagination
    async def get_all_projects(self, page:int=1 , page_size : int=1):
        total_documents = await self.collection.count_documents({})
        total_pages = (total_documents // page_size) 
        if total_documents % page_size > 0:
            total_pages += 1

        # payload may be crach 
        # for memory effeciency 
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size) 
        projects = []
        async for document in cursor:
            projects.append(Project(**document))

        return {
            "projects": projects,
            "total_pages": total_pages,
        }