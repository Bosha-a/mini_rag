from enum import Enum

class LLMEnum(Enum): 
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    GEMINI = "GEMINI"

class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class CohereEnum(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = "document" 
    QUERY = "query"


class GeminiEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class DocumentTypeEnum(Enum):
    DOCUMENT = "document" 
    QUERY = "query"
