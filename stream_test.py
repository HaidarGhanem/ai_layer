# ============================================================
# Streaming V1 - Integration Test
# ============================================================

from types import SimpleNamespace

from langgraph.checkpoint.memory import InMemorySaver

from services.LLM.manager import LLMManager
from services.loop.loop import Loop
from services.loop.tools.calculator import calculate
from services.loop.tools.current_time import get_current_time
from services.risk.engine import RiskEngine
from services.risk.level import RiskLevel
from services.risk.policy import RiskPolicy
from services.tools.catalog_builder import ToolCatalogBuilder
from services.tools.register import ToolRegistry
from services.tools.selector import ToolSelector
from services.tools.selection import ToolSelectionPolicy
from services.context.builder import ContextBuilder
from services.context.configuration import ContextConfiguration
from services.streaming.content import extract_text
from services.streaming.emitter import StreamEmitter
from services.streaming.event import StreamEvent

try:
    from services.brain import Brain
except ImportError:
    from services.brain.brain import Brain


print("=" * 60)
print("STREAMING V1 INTEGRATION TEST")
print("=" * 60)


print("\n1. STREAMING PRIMITIVES")
emitter = StreamEmitter()

assert isinstance(emitter.token("hello"), StreamEvent)
assert emitter.token("hello").type == "token"
assert emitter.tool_started("calculate").type == "tool_started"
assert emitter.tool_finished("calculate", "7552").type == "tool_finished"
assert emitter.confirmation_required({"x": 1}).type == "confirmation_required"
assert emitter.completed("done").type == "completed"
assert emitter.error("bad").type == "error"

assert extract_text("hello") == "hello"
assert extract_text({"text": "hello"}) == "hello"
assert extract_text({"content": [{"type": "text", "text": "hello"}]}) == "hello"

print("STREAMING PRIMITIVES: PASS")


print("\n2. LOOP TOOL SETUP")
registry = ToolRegistry()
builder = ToolCatalogBuilder()

registry.register(calculate, builder.build(calculate))
registry.register(get_current_time, builder.build(get_current_time))


class FakeRetriever:
    def retrieve(self, query):
        query = query.lower()
        tool_name = "get_current_time" if "time" in query else "calculate"

        return [
            SimpleNamespace(
                node=SimpleNamespace(
                    metadata={"tool_name": tool_name}
                ),
                score=1.0,
            )
        ]


selector = ToolSelector(
    retriever=FakeRetriever(),
    registry=registry,
    policy=ToolSelectionPolicy(max_tools=1),
)

risk_engine = RiskEngine(
    policy=RiskPolicy(
        tool_levels={
            "calculate": RiskLevel.LOW,
            "get_current_time": RiskLevel.LOW,
        }
    )
)

context_builder = ContextBuilder(
    configuration=ContextConfiguration(
        max_tool_tokens=1500
    )
)

checkpointer = InMemorySaver()
llm_manager = LLMManager()

print("LOOP TOOL SETUP: PASS")


print("\n3. LOOP STREAM")
loop = Loop(
    llm=llm_manager.get_adapter("loop"),
    tool_selector=selector,
    tool_registry=registry,
    risk_engine=risk_engine,
    context_builder=context_builder,
    checkpointer=checkpointer,
)

events = list(
    loop.stream(
        question="Calculate 8 multiplied by 944",
        history=[],
        thread_id="stream-test-loop",
    )
)

for event in events:
    print(event)

assert events
assert any(event.type == "token" for event in events)
assert any(event.type == "tool_started" for event in events)
assert any(event.type == "tool_finished" for event in events)
assert any(event.type == "completed" for event in events)

completed = [
    event for event in events
    if event.type == "completed"
][-1]

assert completed.data["content"]

print("LOOP STREAM: PASS")


print("\n4. BRAIN STREAM")
brain = Brain(
    manager=llm_manager,
    retriever=None,
    tool_selector=selector,
    tool_registry=registry,
    risk_engine=risk_engine,
    checkpointer=InMemorySaver(),
)

brain_chat_events = list(
    brain.stream(
        question="What is Python?",
        session_id="brain-stream-chat",
    )
)

for event in brain_chat_events:
    print(event)

assert brain_chat_events
assert brain_chat_events[-1].type == "completed"
assert brain_chat_events[-1].data["content"]

brain_loop_events = list(
    brain.stream(
        question="Calculate 8 multiplied by 944",
        session_id="brain-stream-loop",
    )
)

for event in brain_loop_events:
    print(event)

assert brain_loop_events
assert any(event.type == "tool_finished" for event in brain_loop_events)
assert any(event.type == "completed" for event in brain_loop_events)

print("BRAIN STREAM: PASS")


print("\n" + "=" * 60)
print("ALL STREAMING V1 TESTS PASSED")
print("=" * 60)
