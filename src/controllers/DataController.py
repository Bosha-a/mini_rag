import re
from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from .ProjectController import ProjectController
import os


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.scaling_size = 1048576 # Convert MB to bytes (1 MB = 1048576 bytes)


    def validate_uploaded_file(self , file : UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False ,  ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
                
        if file.size > self.app_settings.FILE_MAX_SIZE * self.scaling_size: # file.size -> bytes    | FILE_MAX_SIZE -> MB
            return False , ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True , ResponseSignal.FILE_VALIDATION_SUCCESS.value
    


    def generate_unique_filepath(self, orig_file_name: str , project_id: str):
        """
        Generate a unique file name based on the original file name and current timestamp.
        """
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(orig_file_name = orig_file_name)

        new_file_path = os.path.join(project_path , random_key + "_" + cleaned_file_name)

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        return new_file_path , random_key + "_" + cleaned_file_name



    def get_clean_file_name(self , orig_file_name : str):
        cleaned_file_name = re.sub(r'[^\w.]' , '' , orig_file_name.strip())
        cleaned_file_name = orig_file_name.replace(" ", "_").replace(":", "_")

        return cleaned_file_name