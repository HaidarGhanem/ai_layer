from enum import Enum

class EmbeddingProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"