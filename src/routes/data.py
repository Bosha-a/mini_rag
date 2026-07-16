from fastapi import APIRouter , Depends , UploadFile, status, Request 
from fastapi.responses import JSONResponse
import os 
from helpers.config import get_settings , Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseSignal
import logging

from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.ChunkModel import ChunkModel 
from models.enums.AssetTypeEnum import AssetTypeEnum
from models.db_schemes import asset

from .schemas import ProcessRequest
from models.db_schemes import DataChunk, Asset

logger = logging.getLogger('uvicorn_error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1" , "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, 
                      app_settings : Settings = Depends(get_settings)): 
    """
    Upload data to the specified project.

    Validation: 
    Allowed File type 
    Allowed MAX Size 
    """
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    data_controller = DataController()

    is_valid , result_signal = data_controller.validate_uploaded_file(file)
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            # status_code=400 # it is also ok 
            content={
                "signal": result_signal
            }
        )
    
    project_dir_path = ProjectController().get_project_path(project_id=project_id) 
    file_path , file_id = data_controller.generate_unique_filepath(orig_file_name=file.filename, project_id=project_id)
    try:
        async with aiofiles.open(file_path , 'wb') as f: # for memory efficiency and speed 
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        logger.error(f"Failed to upload file {e}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILD.value,
                # "error": str(e) # for sensitivity (don't use error for users put it in logs)
            }
        )
    
    # store the assets into database 
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    asset_resource = Asset(
        asset_project_id = str(project.id),
        asset_type = AssetTypeEnum.FILE.value,
        asset_name = file_id,
        asset_size = os.path.getsize(file_path),
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id" : file_id,
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id : str , process_request : ProcessRequest, request: Request):

    chunk_size = process_request.chunk_size 
    overlap_size= process_request.overlap_size 
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)


    if process_request.file_id is not None:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value
                }
            )
        
        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }

    else: 
        # get all files from the project 
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value
            )
        
        project_files_ids = {
            rec.id: rec.asset_name
            for rec in project_files
            }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value
            }
        )

    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    processed_files = 0

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if do_reset == 1:
        deleted_count = await chunk_model.delete_chunks_by_project_id(project_id=project.id)
        logger.info(f"Deleted {deleted_count} chunks for project {project_id} due to reset request.")


    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.warning(f"File {file_id} not found or could not be loaded for project {project_id}.")
            continue  # Skip to the next file

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )


        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                }
            )
        
        file_chunks_records = [
            DataChunk(
            chunk_text = chunk.page_content,
            chunk_metadata = chunk.metadata, 
            chunk_order = i+1,  
            chunk_project_id = project.id,
            chunk_asset_id = asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]


        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        processed_files += 1

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks" : no_records,
            "processed_files" : processed_files
        }
    ) 


