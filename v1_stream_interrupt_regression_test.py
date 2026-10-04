"""
Regression test for LangGraph V2 streaming interrupts.

Expected V2 updates shape:

{
    "type": "updates",
    "data": {
        "__interrupt__": (Interrupt(...),)
    }
}

The interrupt is a reserved key directly inside the updates payload.
"""

from services.loop.loop import Loop
from services.streaming.event import StreamEvent


class FakeInterrupt:
    def __init__(self, value):
        self.value = value


class FakeGraph:
    def stream(
        self,
        input_data,
        config=None,
        stream_mode=None,
        version=None,
    ):
        yield {
            "type": "updates",
            "data": {
                "__interrupt__": (
                    FakeInterrupt(
                        {
                            "type": "tool_confirmation",
                            "message": "Confirmation required.",
                            "tools": [
                                {
                                    "tool_name": "delete_customer",
                                    "risk_level": "high",
                                }
                            ],
                        }
                    ),
                ),
            },
        }


class FakeCompiledGraph:
    def __init__(self):
        self.graph = FakeGraph()


class FakeEmitter:
    def confirmation_required(self, payload):
        return StreamEvent(
            type="confirmation_required",
            data=payload,
        )

    def token(self, content):
        return StreamEvent(
            type="token",
            data={"content": content},
        )

    def tool_started(self, tool_name, args=None):
        return StreamEvent(
            type="tool_started",
            data={
                "tool_name": tool_name,
                "args": args,
            },
        )

    def tool_finished(
        self,
        tool_name,
        result=None,
        tool_call_id=None,
    ):
        return StreamEvent(
            type="tool_finished",
            data={
                "tool_name": tool_name,
                "result": result,
                "tool_call_id": tool_call_id,
            },
        )

    def completed(
        self,
        content,
        display_type="text",
        data=None,
        metadata=None,
    ):
        return StreamEvent(
            type="completed",
            data={
                "content": content,
                "display_type": display_type,
                "data": data,
                "metadata": metadata or {},
            },
        )

    def error(self, message, code=None, details=None):
        data = {"message": message}

        if code is not None:
            data["code"] = code

        if details is not None:
            data["details"] = details

        return StreamEvent(
            type="error",
            data=data,
        )


def main():
    loop = Loop.__new__(Loop)

    loop.graph = FakeCompiledGraph()
    loop.emitter = FakeEmitter()

    events = list(
        loop._stream_graph(
            input_data={},
            config={
                "configurable": {
                    "thread_id": "regression-test",
                }
            },
        )
    )

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, StreamEvent)
    assert event.type == "confirmation_required"
    assert event.data["type"] == "tool_confirmation"
    assert (
        event.data["tools"][0]["tool_name"]
        == "delete_customer"
    )

    print("=" * 60)
    print("STREAM INTERRUPT REGRESSION: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()
