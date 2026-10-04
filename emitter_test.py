from services.streaming.emitter import StreamEmitter


print("=" * 60)
print("STREAM EMITTER TEST")
print("=" * 60)


emitter = StreamEmitter()


# ------------------------------------------------------------
# 1. Token
# ------------------------------------------------------------

token_event = emitter.emit(
    "token",
    {
        "content": "Hello"
    },
)

print("\nTOKEN:")
print(token_event)

assert token_event.type == "token"
assert token_event.data["content"] == "Hello"


# ------------------------------------------------------------
# 2. Tool Started
# ------------------------------------------------------------

tool_started_event = emitter.emit(
    "tool_started",
    {
        "tool_name": "calculate"
    },
)

print("\nTOOL STARTED:")
print(tool_started_event)

assert tool_started_event.type == "tool_started"
assert tool_started_event.data["tool_name"] == "calculate"


# ------------------------------------------------------------
# 3. Confirmation
# ------------------------------------------------------------

confirmation_event = emitter.emit(
    "confirmation_required",
    {
        "message": "Confirmation required",
        "tools": [
            {
                "tool_name": "delete_customer",
                "risk_level": "high",
            }
        ],
    },
)

print("\nCONFIRMATION:")
print(confirmation_event)

assert confirmation_event.type == "confirmation_required"
assert (
    confirmation_event.data["tools"][0]["tool_name"]
    == "delete_customer"
)


# ------------------------------------------------------------
# 4. Completed
# ------------------------------------------------------------

completed_event = emitter.emit(
    "completed",
    {
        "content": "Operation completed",
        "display_type": "text",
    },
)

print("\nCOMPLETED:")
print(completed_event)

assert completed_event.type == "completed"
assert completed_event.data["content"] == "Operation completed"


# ------------------------------------------------------------
# 5. Empty Data
# ------------------------------------------------------------

empty_event = emitter.emit(
    "completed"
)

print("\nEMPTY DATA:")
print(empty_event)

assert empty_event.type == "completed"
assert empty_event.data == {}


print("\n" + "=" * 60)
print("STREAM EMITTER: PASS")
print("=" * 60)