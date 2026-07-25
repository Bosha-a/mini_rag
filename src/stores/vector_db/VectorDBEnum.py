from enum import Enum

class VectorDBEnum(Enum): 
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"

class DistanceMethonEnum(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"

class PgVectorTableSchemaEnum(Enum):
    ID="id"
    TEXT="text"
    VECTOR="vector"
    CHUNK_ID="chunk_id"
    METADATA="metadata"
    _PREFIX = "pgvector"


class PgVectorDistanceMethonEnum(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PgVectorIndexTypeEnum(Enum):
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"