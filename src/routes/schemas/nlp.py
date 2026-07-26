from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    project_id: str = None
    chunk_size : Optional[int] = 100 # default chunk size for processing is 100 if user didnt input anything 
    overlap_size: Optional[int] = 20 
    do_reset: Optional[int] = 0 # reset the process if user want to start over


class SearchRequest(BaseModel):
    # project_id: str = None
    text: str
    limit: Optional[int] = 10
    