from .LLMEnum import LLMEnum
from .providers import CohereProvider, OpenAIProvider, GeminiProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str): 
        if provider == LLMEnum.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_TOKEN,
                base_url=self.config.OPENAI_API_BASE_URL,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.OUTPUT_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        
        # if provider == LLMEnum.COHERE.value:
        #     return CohereProvider(
        #         api_key=self.config.COHERE_API_KEY,
        #         default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
        #         default_output_max_tokens=self.config.OUTPUT_DEFAULT_MAX_TOKENS,
        #         default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
        #     )
        
        if provider == LLMEnum.GEMINI.value:
            return GeminiProvider(
                api_key=self.config.GEMINI_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.OUTPUT_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None