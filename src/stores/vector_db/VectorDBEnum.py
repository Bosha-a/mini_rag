from enum import Enum

class VectorDBEnum(Enum): 
    QDRANT = "QDRANT"


class DistanceMethonEnum(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"
   