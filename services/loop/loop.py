from services.loop.graph import LoopGraph
from services.loop.result import LoopResult
from services.loop.state import LoopState

from services.prompts.loop import get_loop_prompt

from services.context.builder import ContextBuilder
from services.streaming.emitter import StreamEmitter
from services.streaming.content import extract_text


class Loop:

    def __init__(
        self,
        llm,
        tool_selector,
        tool_registry,
        risk_engine,
        context_builder: ContextBuilder,
        checkpointer=None,
    ):

        self.llm = llm

        self.tool_selector = (
            tool_selector
        )

        self.tool_registry = (
            tool_registry
        )

        self.context_builder = (
            context_builder
        )

        self.emitter = StreamEmitter()

        self.prompt = get_loop_prompt()

        self.graph = LoopGraph(
            llm=llm,
            tool_registry=tool_registry,
            risk_engine=risk_engine,
            context_builder=context_builder,
            checkpointer=checkpointer,
        )

    def run(
        self,
        question: str,
        history: list | None = None,
        thread_id: str | None = None,
    ):

        selected_tools = (
            self.tool_selector.select(
                question
            )
        )

        selected_tool_names = [
            tool.name
            for tool in selected_tools
        ]

        prompt_messages = (
            self.prompt.invoke({
                "history": history or [],
                "question": question,
            })
        )

        state: LoopState = {

            "question": question,

            "messages": (
                prompt_messages.messages
            ),

            "tool_results": [],

            "answer": "",

            "selected_tools": (
                selected_tool_names
            ),

            "risk_action": None,

            "risk_decisions": [],
        }

        config = None

        if thread_id is not None:

            config = {
                "configurable": {
                    "thread_id": thread_id,
                }
            }

        result = self.graph.invoke(
            state,
            config=config,
        )

        return self._build_result(
            result
        )

    def resume(
        self,
        thread_id: str,
        approved: bool,
    ):

        from langgraph.types import Command

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        result = self.graph.invoke(
            Command(
                resume=approved
            ),
            config=config,
        )

        return self._build_result(
            result
        )

    def stream(
        self,
        question: str,
        history: list | None = None,
        thread_id: str | None = None,
    ):

        selected_tools = self.tool_selector.select(question)

        selected_tool_names = [
            tool.name
            for tool in selected_tools
        ]

        prompt_messages = self.prompt.invoke({
            "history": history or [],
            "question": question,
        })

        state: LoopState = {
            "question": question,
            "messages": prompt_messages.messages,
            "tool_results": [],
            "answer": "",
            "selected_tools": selected_tool_names,
            "risk_action": None,
            "risk_decisions": [],
        }

        config = None

        if thread_id is not None:
            config = {
                "configurable": {
                    "thread_id": thread_id,
                }
            }

        yield from self._stream_graph(state, config=config)

    def resume_stream(
        self,
        thread_id: str,
        approved: bool,
    ):

        from langgraph.types import Command

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        yield from self._stream_graph(
            Command(resume=approved),
            config=config,
        )

    def _stream_graph(
        self,
        input_data,
        config=None,
    ):

        full_answer = ""
        risk_decisions = []

        try:
            stream = self.graph.graph.stream(
                input_data,
                config=config,
                stream_mode=["messages", "updates"],
                version="v2",
            )

            for part in stream:

                if part["type"] == "messages":
                    message_chunk, metadata = part["data"]

                    if metadata.get("langgraph_node") != "llm":
                        continue

                    content = extract_text(message_chunk)

                    if content:
                        full_answer += content
                        yield self.emitter.token(content)

                elif part["type"] == "updates":

                    for node_name, update in part["data"].items():

                        interrupts = update.get("__interrupt__")

                        if interrupts:
                            interrupt = interrupts[0]
                            payload = getattr(
                                interrupt,
                                "value",
                                interrupt,
                            )

                            if isinstance(payload, dict):
                                yield self.emitter.confirmation_required(payload)
                            else:
                                yield self.emitter.confirmation_required({
                                    "message": str(payload),
                                })

                            return

                        if node_name == "risk":

                            decisions = update.get(
                                "risk_decisions",
                                [],
                            )

                            if decisions:
                                risk_decisions = decisions

                            if update.get("risk_action") == "reject":
                                yield self.emitter.error(
                                    update.get(
                                        "answer",
                                        "The requested action was rejected.",
                                    ),
                                    code="RISK_REJECTED",
                                    details=decisions,
                                )
                                return

                            if update.get("risk_action") == "allow":
                                for decision in decisions:
                                    yield self.emitter.tool_started(
                                        decision.get("tool_name", ""),
                                        decision.get("args"),
                                    )

                        if node_name == "tools":

                            for message in update.get("messages", []):
                                if getattr(message, "type", "") != "tool":
                                    continue

                                yield self.emitter.tool_finished(
                                    tool_name=getattr(message, "name", "unknown"),
                                    result=getattr(message, "content", None),
                                    tool_call_id=getattr(message, "tool_call_id", None),
                                )

                        if node_name == "llm":

                            answer = update.get("answer")
                            if answer:
                                full_answer = extract_text(answer)

        except Exception as exc:
            yield self.emitter.error(
                str(exc),
                code="LOOP_STREAM_ERROR",
            )
            return

        yield self.emitter.completed(
            content=full_answer,
            display_type="text",
            data={
                "risk_decisions": risk_decisions,
            },
            metadata={
                "status": "completed",
            },
        )

    def _build_result(
        self,
        result,
    ):

        interrupts = result.get(
            "__interrupt__"
        )

        if interrupts:

            interrupt_value = (
                interrupts[0].value
            )

            return LoopResult(
                content=(
                    "Confirmation is required "
                    "before executing the action."
                ),
                display_type="card",
                data={
                    "type": "confirmation",
                    **interrupt_value,
                },
                metadata={
                    "status": (
                        "waiting_confirmation"
                    ),
                },
            )

        return LoopResult(
            content=result.get(
                "answer",
                "",
            ),
            display_type="text",
            data={
                "risk_decisions": (
                    result.get(
                        "risk_decisions",
                        [],
                    )
                ),
            },
            metadata={
                "status": "completed",
            },
        )


# ============================================================

# from services.loop.graph import LoopGraph
# from services.loop.result import LoopResult
# from services.loop.state import LoopState

# from services.prompts.loop import get_loop_prompt


# class Loop:

#     def __init__(
#         self,
#         llm,
#         tool_selector,
#     ):
#         self.llm = llm
#         self.tool_selector = tool_selector
#         self.prompt = get_loop_prompt()

#     def run(
#         self,
#         question: str,
#         history: list | None = None,
#     ) -> LoopResult:

#         selected_tools = self.tool_selector.select(
#             question
#         )

#         prompt_messages = self.prompt.invoke({
#             "history": history or [],
#             "question": question,
#         })

#         state: LoopState = {
#             "question": question,
#             "messages": prompt_messages.messages,
#             "tool_results": [],
#             "answer": "",
#         }

#         graph = LoopGraph(
#             llm=self.llm,
#             tools=selected_tools,
#         )

#         result = graph.invoke(
#             state
#         )

#         raw_answer = result["answer"]
        
#         if isinstance(raw_answer, list):
#             final_content = "".join([
#                 block.get("text", "") 
#                 for block in raw_answer 
#                 if isinstance(block, dict) and block.get("type") == "text"
#             ])
#         else:
#             final_content = str(raw_answer)

#         return LoopResult(
#             content=final_content,  
#             display_type="text",
#         )


# ======================================================

# from services.loop.graph import LoopGraph
# from services.loop.result import LoopResult
# from services.loop.state import LoopState
# from services.prompts.loop import get_loop_prompt


# class Loop:

#     def __init__(
#         self,
#         llm,
#         tool_selector,
#     ):
#         self.llm = llm
#         self.tool_selector = tool_selector
#         self.prompt = get_loop_prompt()

#     def run(
#         self,
#         question: str,
#         history: list | None = None,
#     ) -> LoopResult:

#         selected_tools = self.tool_selector.select(
#             question
#         )

#         prompt_messages = self.prompt.invoke({
#             "history": history or [],
#             "question": question,
#         })

#         state: LoopState = {
#             "question": question,
#             "messages": prompt_messages.messages,
#             "tool_results": [],
#             "answer": "",
#         }

#         graph = LoopGraph(
#             llm=self.llm,
#             tools=selected_tools,
#         )

#         result = graph.invoke(state)

#         raw_answer = result["answer"]
        
#         if isinstance(raw_answer, list):
#             final_content = "".join([
#                 block.get("text", "") 
#                 for block in raw_answer 
#                 if isinstance(block, dict) and block.get("type") == "text"
#             ])
#         else:
#             final_content = str(raw_answer)

#         return LoopResult(
#             content=final_content,
#             display_type="text",
#         )