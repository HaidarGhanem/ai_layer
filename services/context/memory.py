from abc import ABC, abstractmethod
from langchain_core.messages import BaseMessage

class Memory(ABC):

    @abstractmethod
    def get(self, session_id: str) -> list[BaseMessage]:
        raise NotImplementedError

    @abstractmethod
    def save(self, session_id: str, messages: list[BaseMessage]) -> None:
        raise NotImplementedError