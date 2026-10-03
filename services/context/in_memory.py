from langchain_core.messages import BaseMessage
from services.context.memory import Memory

class InMemory(Memory):

    def __init__(self):
        self._sessions: dict[str, list[BaseMessage]] = {}

    def get(self, session_id: str) -> list[BaseMessage]:
        return self._sessions.get(
            session_id,
            [],
        )

    def save(
        self,
        session_id: str,
        messages: list[BaseMessage],
    ) -> None:
        self._sessions[session_id] = messages