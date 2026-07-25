from fastapi import APIRouter , Depends , UploadFile, status, Request 
from fastapi.responses import JSONResponse
import os 
from helpers.config import get_settings , Settings
from routes.schemas.nlp import PushRequest, SearchRequest
from models import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
import logging


logger = logging.getLogger('uvicorn_error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1" , "nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: int, push_request : PushRequest): 

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )


    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )


    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND.value
                }
        )
    
    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    has_records = True
    page_num = 1
    inerted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.project_id, page_num=page_num)
        if len(page_chunks):
            page_num += 1

        if len(page_chunks) == 0 or not page_chunks:
            has_records = False
            break

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_insterted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            chunks_ids=chunks_ids,
            do_reset=push_request.do_reset,
        )

        if not is_insterted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORD_DB_ERROR.value
                }
            )
        
        inerted_items_count += len(page_chunks)
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORD_DB_SUCCESS.value,
            "inserted_items_count": inerted_items_count
        }
    )

    
@nlp_router.get("/index/info/{project_id}")
async def get_index_info(request: Request, project_id: int):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND.value
            }
        )
    
    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignal.GET_VECTORD_DB_COLLECTION_INFO_SUCCESS.value,
            "collection_info": collection_info
        }
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: int, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND.value
            }
        )

    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    # Implement search logic here
    results = nlp_controller.search_vector_db_collection(
        project=project,
        query=search_request.query,
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.SEARCH_VECTORD_DB_ERROR.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.SEARCH_VECTORD_DB_SUCCESS.value,
            "results": [result.dict() for result in results]
        }
    )



@nlp_router.post("/index/answer/{project_id}")
async def answer_rag_question(request: Request, project_id: int, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND.value
            }
        )

    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.query,
        limit=search_request.limit
    )

    if not answer: 
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.ANSWER_RAG_QUESTION_ERROR.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.ANSWER_RAG_QUESTION_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )