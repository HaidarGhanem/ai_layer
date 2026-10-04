from abc import ABC, abstractmethod

from services.tools.state import ToolIndexState


class ToolStateStore(ABC):

    @abstractmethod
    def get(
        self,
        tool_id: str,
    ) -> ToolIndexState | None:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        state: ToolIndexState,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        tool_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
    ) -> list[ToolIndexState]:
        raise NotImplementedError