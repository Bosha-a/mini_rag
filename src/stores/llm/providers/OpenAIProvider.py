from ..LLMInterface import LLMInterface
from ..LLMEnum import OpenAIEnum
from openai import OpenAI
import logging 
from typing import List, Union


class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str, base_url: str = None, 
                 default_input_max_characters: int = 1000, 
                 default_output_max_tokens: int = 1000,
                 default_temperature: float = 0.1):
        
        self.api_key = api_key
        self.base_url = base_url

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key, 
            base_url=self.base_url
        ) 

        self.enums = OpenAIEnum

        self.logger = logging.getLogger('__name__')


    def set_generation_model(self, model_id: str) -> str:
        self.generation_model_id = model_id



    def set_embedding_model(self, model_id: str, embedding_size: int) -> str:
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip() if len(text) > self.default_input_max_characters else text


    def generate_text(self, prompt: str, chat_history: list = None, max_output_tokens: int = None, temperature: float = None) -> str:
        if chat_history is None:
            chat_history = []
        
        if not self.client:
            self.logger.error("OpenAI client is not initialized. Please check your API key and base URL.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set. Please set it using set_generation_model method.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        chat_history.append(
            self.construct_prompt(prompt, role=OpenAIEnum.USER.value)
        )

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message or not response.choices[0].message.content:
            self.logger.error("Failed to generate text from OpenAI API. Response is empty or invalid.")
            return None
        
        return response.choices[0].message.content
        


    def embed_text(self, text: Union[str, List[str]], document_type: str) -> list:
        if not self.client:
            self.logger.error("OpenAI client is not initialized. Please check your API key and base URL.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set. Please set it using set_embedding_model method.")
            return None


        if isinstance(text, str):
            text = [text]
        
        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Failed to get embedding from OpenAI API. Response is empty or invalid.")
            return None

        return [d.embedding for d in response.data]


    def construct_prompt(self, prompt: str, role: str) -> str:
        return{
            "role": role,
            "content": prompt
        }