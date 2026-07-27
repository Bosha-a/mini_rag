from ..LLMInterface import LLMInterface
from ..LLMEnum import CohereEnum , DocumentTypeEnum
import cohere
import logging 


class CohereProvider(LLMInterface):
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

        self.client = cohere.ClientV2(
            api_key=self.api_key
        )

        self.logger = logging.getLogger(__name__)


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
            self.logger.error("Cohere client is not initialized. Please check your API key.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set. Please set it using set_generation_model method.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        chat_history = chat_history + [self.construct_prompt(prompt, CohereEnum.USER.value)]

        # Construct the prompt for Cohere
        cohere_prompt = "\n".join([f"{entry['role']}: {entry['content']}" for entry in chat_history])

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            temperature=temperature,
            max_tokens=max_output_tokens
        )
        
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message or not response.choices[0].message.content:
            self.logger.error("Failed to generate text from Cohere API. Response is empty or invalid.")
            return None
        
        return response.message.content[0].text.strip()
    

    def embed_text(self, text: str, document_type: str) -> list:
        if not self.client:
            self.logger.error("Cohere client is not initialized. Please check your API key`.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set. Please set it using set_embedding_model method.")
            return None
        
        input_type = CohereEnum.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CohereEnum.QUERY.value


        if isinstance(text, str):
            text = [text]

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=text,
            input_type=input_type,
            embedding_types=['float']

        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Failed to get embedding from Cohere API. Response is empty or invalid.")
            return None

        return response.embeddings.float
    
    
    def construct_prompt(self, prompt: str, role: str) -> str:
        return {
            "role": role,
            "content": prompt
        }
    
