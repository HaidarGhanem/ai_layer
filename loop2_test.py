from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)

from services.context.builder import ContextBuilder
from services.context.configuration import ContextConfiguration


configuration = ContextConfiguration(
    max_history_tokens=100,
    max_retrieved_tokens=100,
    max_tool_tokens=20,
)


builder = ContextBuilder(
    configuration=configuration
)


large_tool_result = (
    "CUSTOMER DATA "
    * 100
)


messages = [

    HumanMessage(
        content="Search for customer"
    ),

    ToolMessage(
        content=large_tool_result,
        tool_call_id="test-call",
    ),

]


bounded_messages = (
    builder.build_tool_messages(
        messages
    )
)


print("ORIGINAL TOOL RESULT LENGTH:")
print(
    len(
        large_tool_result
    )
)


print(
    "\nBOUNDED TOOL RESULT LENGTH:"
)

print(
    len(
        bounded_messages[1].content
    )
)


print(
    "\nBOUNDED TOOL RESULT:"
)

print(
    bounded_messages[1].content
)


print(
    "\nORIGINAL MESSAGE STILL INTACT:"
)

print(
    len(
        messages[1].content
    )
)


assert (
    len(
        bounded_messages[1].content
    )
    <= 20 * 4
)


assert (
    len(
        messages[1].content
    )
    == len(
        large_tool_result
    )
)


assert (
    bounded_messages[0].content
    == messages[0].content
)


print(
    "\nTOOL CONTEXT BUDGET: PASS"
)