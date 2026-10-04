import json

from services.streaming.event import StreamEvent


def encode_sse(event: StreamEvent) -> str:
    payload = json.dumps(
        event.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return (
        f"event: {event.type}\n"
        f"data: {payload}\n\n"
    )
