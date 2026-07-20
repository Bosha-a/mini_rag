from abc import ABC, abstractmethod
from typing import List


class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        pass


    @abstractmethod
    def disconnect(self):
        pass


    @abstractmethod
    def is_collection_exists(self, collection_name: str) -> bool:
        pass


    @abstractmethod
    def list_all_collections(self) -> List:
        pass


    @abstractmethod
    def get_collection_info(self, collection_name: str):
        pass


    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass


    @abstractmethod
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        pass


    @abstractmethod
    def insert_one(self, collection_name: str, ids: list, vector: list, metadata: dict = None, record_id: str = None):
        pass


    @abstractmethod
    def insert_many(self, collection_name: str, ids: list, vector: list, metadata: dict = None, record_id: str = None, batch_size: int = 50):
        pass


    @abstractmethod
    def search_by_vector(self, collection_name: str, query_vector: list, limit: int = 5):
        pass
    
