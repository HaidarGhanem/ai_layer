from services.streaming.event import StreamEvent


print("=" * 60)
print("STREAM EVENT CONTRACT TEST")
print("=" * 60)


# ------------------------------------------------------------
# 1. Token
# ------------------------------------------------------------

token_event = StreamEvent(
    type="token",
    data={
        "content": "Hello"
    }
)

print("\nTOKEN:")
print(token_event)

assert token_event.type == "token"
assert token_event.data["content"] == "Hello"


# ------------------------------------------------------------
# 2. Tool Started
# ------------------------------------------------------------

tool_started_event = StreamEvent(
    type="tool_started",
    data={
        "tool_name": "calculate"
    }
)

print("\nTOOL STARTED:")
print(tool_started_event)

assert tool_started_event.type == "tool_started"
assert tool_started_event.data["tool_name"] == "calculate"


# ------------------------------------------------------------
# 3. Confirmation Required
# ------------------------------------------------------------

confirmation_event = StreamEvent(
    type="confirmation_required",
    data={
        "message": "Confirmation required",
        "tools": [
            {
                "tool_name": "delete_customer",
                "risk_level": "high",
            }
        ],
    }
)

print("\nCONFIRMATION:")
print(confirmation_event)

assert confirmation_event.type == "confirmation_required"
assert confirmation_event.data["tools"][0]["tool_name"] == "delete_customer"


# ------------------------------------------------------------
# 4. Completed
# ------------------------------------------------------------

completed_event = StreamEvent(
    type="completed",
    data={
        "content": "Operation completed",
        "display_type": "text",
    }
)

print("\nCOMPLETED:")
print(completed_event)

assert completed_event.type == "completed"
assert completed_event.data["content"] == "Operation completed"


# ------------------------------------------------------------
# 5. Error
# ------------------------------------------------------------

error_event = StreamEvent(
    type="error",
    data={
        "message": "Something went wrong",
        "code": "TEST_ERROR",
    }
)

print("\nERROR:")
print(error_event)

assert error_event.type == "error"
assert error_event.data["code"] == "TEST_ERROR"


print("\n" + "=" * 60)
print("STREAM EVENT CONTRACT: PASS")
print("=" * 60)