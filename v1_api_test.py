from fastapi.testclient import TestClient

from services.api.app import create_app
from services.api.configuration import APIConfiguration
from services.errors.exceptions import ClarificationRequiredError
from services.responses.response import BrainResponse
from services.streaming.event import StreamEvent


class FakeBrain:
    def __init__(self):
        self.raise_process_error = False

    def process(self, question: str, session_id: str):
        if self.raise_process_error:
            raise ClarificationRequiredError(
                details={"field": "question"}
            )

        return BrainResponse(
            content=f"Processed: {question}",
            display_type="text",
        )

    def resume(self, session_id: str, approved: bool):
        return BrainResponse(
            content="Approved" if approved else "Cancelled",
            display_type="text",
        )

    def stream(self, question: str, session_id: str):
        yield StreamEvent(
            type="token",
            data={"content": "Hello"},
        )
        yield StreamEvent(
            type="completed",
            data={
                "content": "Hello",
                "display_type": "text",
            },
            metadata={
                "status": "completed"
            },
        )

    def resume_stream(self, session_id: str, approved: bool):
        yield StreamEvent(
            type="completed",
            data={
                "content": "Approved" if approved else "Cancelled",
                "display_type": "text",
            },
            metadata={
                "status": "completed"
            },
        )


def read_sse_events(response):
    blocks = [
        block
        for block in response.text.split("\n\n")
        if block.strip()
    ]
    return blocks


def main():
    fake_brain = FakeBrain()
    app = create_app(
        fake_brain,
        APIConfiguration(
            service_name="AI Layer Test",
            version="1.0-test",
            debug=True,
        ),
    )

    client = TestClient(app)

    # ------------------------------------------------------------
    # Health
    # ------------------------------------------------------------
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"]

    # ------------------------------------------------------------
    # Process
    # ------------------------------------------------------------
    response = client.post(
        "/v1/process",
        json={
            "question": "hello",
            "session_id": "api-test-1",
        },
        headers={"X-Request-ID": "request-123"},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "request-123"
    assert response.json()["content"] == "Processed: hello"

    # ------------------------------------------------------------
    # Resume
    # ------------------------------------------------------------
    response = client.post(
        "/v1/resume",
        json={
            "session_id": "api-test-1",
            "approved": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Approved"

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------
    response = client.post(
        "/v1/process",
        json={
            "question": "",
            "session_id": "api-test-1",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"
    assert response.json()["request_id"]

    # Extra fields are explicitly forbidden.
    response = client.post(
        "/v1/process",
        json={
            "question": "hello",
            "session_id": "api-test-1",
            "unexpected": True,
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"

    # ------------------------------------------------------------
    # Domain error mapping
    # ------------------------------------------------------------
    fake_brain.raise_process_error = True
    response = client.post(
        "/v1/process",
        json={
            "question": "needs clarification",
            "session_id": "api-test-error",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "CLARIFICATION_REQUIRED"
    assert response.json()["request_id"]
    fake_brain.raise_process_error = False

    # ------------------------------------------------------------
    # SSE stream
    # ------------------------------------------------------------
    with client.stream(
        "POST",
        "/v1/stream",
        json={
            "question": "hello",
            "session_id": "stream-test-1",
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "text/event-stream"
        )
        response.read()
        blocks = read_sse_events(response)

    assert any(block.startswith("event: token") for block in blocks)
    assert any(block.startswith("event: completed") for block in blocks)

    # ------------------------------------------------------------
    # Resume SSE
    # ------------------------------------------------------------
    with client.stream(
        "POST",
        "/v1/resume/stream",
        json={
            "session_id": "stream-test-1",
            "approved": False,
        },
    ) as response:
        assert response.status_code == 200
        response.read()
        blocks = read_sse_events(response)

    assert any(block.startswith("event: completed") for block in blocks)

    print("=" * 60)
    print("V1 API CONTRACT TEST: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()
