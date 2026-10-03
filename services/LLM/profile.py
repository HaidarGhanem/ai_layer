from dataclasses import dataclass
from services.LLM.configuration import LLMConfiguration

@dataclass
class LLMProfile:
    name: str
    configuration: LLMConfiguration

