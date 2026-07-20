from enum import Enum 

## Add each constants here 
class ResponseSignal(Enum):
    FILE_VALIDATION_SUCCESS = "file_validate_successfully"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_uploaded_successfully"
    FILE_UPLOAD_FAILD = "file_uploaded_faild"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    
    PROCESSING_FAILED = "processing_failed"
    PROCESSING_SUCCESS = "processing_successed"

    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_files_found_with_this_id"

    PROJECT_NOT_FOUND = "project_not_found"

    INSERT_INTO_VECTORD_DB_ERROR = "insert_into_vectordb_failed"
    INSERT_INTO_VECTORD_DB_SUCCESS = "insert_into_vectordb_success"

    GET_VECTORD_DB_COLLECTION_INFO_SUCCESS = "get_vectordb_collection_info_success"
    SEARCH_VECTORD_DB_SUCCESS = "search_vectordb_success"
    SEARCH_VECTORD_DB_ERROR = "search_vectordb_error"