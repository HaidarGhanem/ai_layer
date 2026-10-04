from uuid import uuid4

from fastapi.testclient import TestClient

from services.api.app import create_app
from services.api.configuration import APIConfiguration
from services.streaming.event import StreamEvent
from services.risk.level import RiskLevel
from v1_support import build_demo_brain


def consume_events(events):
    return list(events)


def assert_sse_contains(body: str, event_name: str):
    assert f"event: {event_name}" in body, body


def main():
    print("=" * 60)
    print("AI LAYER V1 FINAL E2E")
    print("=" * 60)

    # Normal low-risk brain.
    brain = build_demo_brain()

    # ------------------------------------------------------------
    # 1. Chat process
    # ------------------------------------------------------------
    chat = brain.process(
        question="What is Python? Answer briefly.",
        session_id=f"e2e-chat-{uuid4().hex}",
    )
    assert chat.content.strip()
    assert chat.display_type in {"text", "card", "table"}
    print("CHAT PROCESS: PASS")

    # ------------------------------------------------------------
    # 2. RAG process
    # ------------------------------------------------------------
    rag = brain.process(
        question="What model represents customers in Odoo?",
        session_id=f"e2e-rag-{uuid4().hex}",
    )
    assert "res.partner" in rag.content.lower()
    print("RAG PROCESS: PASS")

    # ------------------------------------------------------------
    # 3. Loop process
    # ------------------------------------------------------------
    loop = brain.process(
        question="Calculate 8 multiplied by 944",
        session_id=f"e2e-loop-{uuid4().hex}",
    )
    assert "7552" in loop.content
    assert loop.metadata.response.get("status") == "completed"
    print("LOOP PROCESS: PASS")

    # ------------------------------------------------------------
    # 4. Brain Chat stream
    # ------------------------------------------------------------
    chat_stream = consume_events(
        brain.stream(
            question="Say hello briefly.",
            session_id=f"e2e-stream-chat-{uuid4().hex}",
        )
    )
    assert all(isinstance(event, StreamEvent) for event in chat_stream)
    assert any(event.type == "token" for event in chat_stream)
    assert chat_stream[-1].type == "completed"
    print("CHAT STREAM: PASS")

    # ------------------------------------------------------------
    # 5. Brain Loop stream
    # ------------------------------------------------------------
    loop_stream = consume_events(
        brain.stream(
            question="Calculate 8 multiplied by 944",
            session_id=f"e2e-stream-loop-{uuid4().hex}",
        )
    )
    assert all(isinstance(event, StreamEvent) for event in loop_stream)
    assert any(event.type == "tool_started" for event in loop_stream)
    assert any(event.type == "tool_finished" for event in loop_stream)
    assert any(event.type == "completed" for event in loop_stream)
    print("LOOP STREAM: PASS")

    # ------------------------------------------------------------
    # 6. Real risk confirmation, approved
    # ------------------------------------------------------------
    high_risk_brain = build_demo_brain(
        calculate_risk=RiskLevel.HIGH,
    )
    approved_session = f"e2e-risk-approved-{uuid4().hex}"

    waiting = high_risk_brain.process(
        question="Calculate 8 multiplied by 944",
        session_id=approved_session,
    )
    assert waiting.metadata.response.get("status") == "waiting_confirmation"
    assert waiting.display_type == "card"
    assert high_risk_brain.context_manager.memory.get(approved_session) == []
    print("RISK WAITING CONFIRMATION: PASS")

    approved = high_risk_brain.resume(
        session_id=approved_session,
        approved=True,
    )
    assert "7552" in approved.content
    assert approved.metadata.response.get("status") == "completed"
    print("RISK APPROVAL RESUME: PASS")

    # ------------------------------------------------------------
    # 7. Real risk confirmation, rejected
    # ------------------------------------------------------------
    rejected_session = f"e2e-risk-rejected-{uuid4().hex}"

    rejected_waiting = high_risk_brain.process(
        question="Calculate 8 multiplied by 944",
        session_id=rejected_session,
    )
    assert rejected_waiting.metadata.response.get("status") == "waiting_confirmation"

    rejected = high_risk_brain.resume(
        session_id=rejected_session,
        approved=False,
    )
    assert rejected.metadata.response.get("status") == "rejected"
    print("RISK REJECTION RESUME: PASS")

    # ------------------------------------------------------------
    # 8. FastAPI process
    # ------------------------------------------------------------
    app = create_app(
        brain,
        APIConfiguration(
            service_name="AI Layer E2E",
            version="1.0-e2e",
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/v1/process",
        json={
            "question": "Calculate 8 multiplied by 944",
            "session_id": f"e2e-api-{uuid4().hex}",
        },
    )
    assert response.status_code == 200
    assert "7552" in response.json()["content"]
    assert response.headers["X-Request-ID"]
    print("API PROCESS: PASS")

    # ------------------------------------------------------------
    # 9. FastAPI streaming
    # ------------------------------------------------------------
    with client.stream(
        "POST",
        "/v1/stream",
        json={
            "question": "Say hello briefly.",
            "session_id": f"e2e-api-stream-{uuid4().hex}",
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "text/event-stream"
        )
        response.read()
        body = response.text

    assert_sse_contains(body, "token")
    assert_sse_contains(body, "completed")
    print("API STREAM: PASS")

    # ------------------------------------------------------------
    # 10. FastAPI confirmation + resume stream
    # ------------------------------------------------------------
    risk_app = create_app(
        high_risk_brain,
        APIConfiguration(
            service_name="AI Layer Risk E2E",
            version="1.0-risk-e2e",
        ),
    )
    risk_client = TestClient(risk_app)
    risk_session = f"e2e-api-risk-{uuid4().hex}"

    with risk_client.stream(
        "POST",
        "/v1/stream",
        json={
            "question": "Calculate 8 multiplied by 944",
            "session_id": risk_session,
        },
    ) as response:
        assert response.status_code == 200
        response.read()
        risk_body = response.text

    assert_sse_contains(risk_body, "confirmation_required")

    with risk_client.stream(
        "POST",
        "/v1/resume/stream",
        json={
            "session_id": risk_session,
            "approved": True,
        },
    ) as response:
        assert response.status_code == 200
        response.read()
        resumed_body = response.text

    assert_sse_contains(resumed_body, "tool_started")
    assert_sse_contains(resumed_body, "tool_finished")
    assert_sse_contains(resumed_body, "completed")
    print("API CONFIRMATION + RESUME STREAM: PASS")

    # ------------------------------------------------------------
    # Final
    # ------------------------------------------------------------
    print("=" * 60)
    print("AI LAYER V1 FINAL E2E: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()
