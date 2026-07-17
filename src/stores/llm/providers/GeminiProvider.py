from ..LLMInterface import LLMInterface
from ..LLMEnum import GeminiEnum
from google.genai import types
from google import genai
import logging 


class GeminiProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000, 
                 default_output_max_tokens: int = 1000,
                 default_temperature: float = 0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = genai.Client(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str) -> None:
        self.generation_model_id = model_id



    def set_embedding_model(self, model_id: str, embedding_size: int) -> None:
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip() if len(text) > self.default_input_max_characters else text



    def generate_text(self, prompt: str, chat_history: list = None, max_output_tokens: int = None, temperature: float = None) -> str:
        if chat_history is None:
            chat_history = []

        if not self.client:
            self.logger.error("Gemini client is not initialized. Please check your API key.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set. Please set it using set_generation_model method.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        chat_history.append(
            self.construct_prompt(prompt, role=GeminiEnum.USER.value)
        )

        response = self.client.models.generate_content(
            model=self.generation_model_id,
            contents=chat_history,
            config=types.GenerateContentConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=temperature
                )
        )

        if not response or not response.text or len(response.text) == 0:
            self.logger.error("Failed to generate text from Gemini API. Response is empty or invalid.")
            return None
        
        return response.text
        


    def embd_text(self, text: str, document_type: str) -> list:
        if not self.client:
            self.logger.error("Gemini client is not initialized. Please check your API key.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set. Please set it using set_embedding_model method.")
            return None
        
        response = self.client.models.embed_content(
            model=self.embedding_model_id,
            contents=[text]
        )

        if not response or not response.embeddings or len(response.embeddings) == 0:
            self.logger.error("Failed to get embedding from Gemini API. Response is empty or invalid.")
            return None

        return response.embeddings[0].values


    def construct_prompt(self, prompt: str, role: str) -> str:
        return{
            "role": role,
            "parts": [{"text": self.process_text(prompt)}]
        }