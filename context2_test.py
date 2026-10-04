from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)

from services.context.in_memory import InMemory
from services.context.manager import ContextManager
from services.context.builder import ContextBuilder
from services.context.configuration import ContextConfiguration


# ============================================================
# Configuration
# ============================================================

configuration = ContextConfiguration(
    max_history_tokens=30,
    max_retrieved_tokens=30,
    max_tool_tokens=20,
)


# ============================================================
# Builder
# ============================================================

builder = ContextBuilder(
    configuration=configuration
)


# ============================================================
# Memory
# ============================================================

memory = InMemory()


# ============================================================
# Manager
# ============================================================

context_manager = ContextManager(
    memory=memory,
    builder=builder,
)


# ============================================================
# 1. History Budget
# ============================================================

print(
    "\n================ HISTORY BUDGET ================"
)


history = [

    HumanMessage(
        content="Old message " * 10
    ),

    AIMessage(
        content="Old answer " * 10
    ),

    HumanMessage(
        content="Recent message " * 10
    ),

]


selected_history = builder.build_history(
    history
)


print(
    "FULL HISTORY:",
    len(history)
)

print(
    "SELECTED HISTORY:",
    len(selected_history)
)

for message in selected_history:

    print(
        message
    )


assert len(
    selected_history
) < len(
    history
)


# ============================================================
# 2. Retrieved Context Budget
# ============================================================

print(
    "\n================ RETRIEVED CONTEXT ================"
)


class FakeResult:

    def __init__(self, text):
        self.node = type(
            "FakeNode",
            (),
            {
                "text": text
            }
        )()


retrieved_results = [

    FakeResult(
        "First result " * 10
    ),

    FakeResult(
        "Second result " * 10
    ),

    FakeResult(
        "Third result"
    ),

]


selected_results = (
    builder.build_retrieved_context(
        retrieved_results
    )
)


print(
    "FULL RESULTS:",
    len(
        retrieved_results
    )
)

print(
    "SELECTED RESULTS:",
    len(
        selected_results
    )
)


assert len(
    selected_results
) < len(
    retrieved_results
)


# ============================================================
# 3. Tool Results Budget
# ============================================================

print(
    "\n================ TOOL RESULTS ================"
)


tool_results = [

    {
        "tool": "search_customer",
        "result": "Customer information " * 10,
    },

    {
        "tool": "search_order",
        "result": "Order information " * 10,
    },

    {
        "tool": "calculate",
        "result": "7552",
    },

]


selected_tool_results = (
    builder.build_tool_results(
        tool_results
    )
)


print(
    "FULL TOOL RESULTS:",
    len(
        tool_results
    )
)

print(
    "SELECTED TOOL RESULTS:",
    len(
        selected_tool_results
    )
)

print(
    selected_tool_results
)


assert len(
    selected_tool_results
) < len(
    tool_results
)


# ============================================================
# 4. Context Manager Integration
# ============================================================

print(
    "\n================ CONTEXT MANAGER ================"
)


context = context_manager.build(
    session_id="context-v2-test",
    question="What happened?",
)


context_manager.prepare_retrieved_context(
    context=context,
    results=retrieved_results,
)


context_manager.prepare_tool_results(
    context=context,
    tool_results=tool_results,
)


print(
    "HISTORY:",
    context.history
)

print(
    "\nMESSAGES:",
    context.messages
)

print(
    "\nRETRIEVED CONTEXT:",
    context.retrieved_context
)

print(
    "\nTOOL RESULTS:",
    context.tool_results
)


assert context.retrieved_context

assert context.tool_results


# ============================================================
# Final
# ============================================================

print(
    "\n=================================================="
)

print(
    "ALL CONTEXT V2 TESTS PASSED"
)

print(
    "=================================================="
)