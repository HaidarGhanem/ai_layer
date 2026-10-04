from typing import Any

from services.streaming.event import StreamEvent


class StreamEmitter:

    def emit(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> StreamEvent:
        return StreamEvent(
            type=event_type,
            data=data or {},
        )

    def token(self, content: str) -> StreamEvent:
        return self.emit(
            "token",
            {"content": content},
        )

    def tool_started(
        self,
        tool_name: str,
        args: dict[str, Any] | None = None,
    ) -> StreamEvent:
        data: dict[str, Any] = {"tool_name": tool_name}
        if args is not None:
            data["args"] = args
        return self.emit("tool_started", data)

    def tool_finished(
        self,
        tool_name: str,
        result: Any = None,
        tool_call_id: str | None = None,
    ) -> StreamEvent:
        data: dict[str, Any] = {
            "tool_name": tool_name,
            "result": result,
        }
        if tool_call_id is not None:
            data["tool_call_id"] = tool_call_id
        return self.emit("tool_finished", data)

    def confirmation_required(
        self,
        payload: dict[str, Any] | None = None,
    ) -> StreamEvent:
        return self.emit(
            "confirmation_required",
            payload or {},
        )

    def completed(
        self,
        content: str,
        display_type: str = "text",
        data: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> StreamEvent:
        return self.emit(
            "completed",
            {
                "content": content,
                "display_type": display_type,
                "data": data,
                "metadata": metadata or {},
            },
        )

    def error(
        self,
        message: str,
        code: str | None = None,
        details: Any = None,
    ) -> StreamEvent:
        data: dict[str, Any] = {"message": message}
        if code is not None:
            data["code"] = code
        if details is not None:
            data["details"] = details
        return self.emit("error", data)
