from services.context.builder import ContextBuilder
from services.errors.translate import normalize_exception
from services.loop.graph import LoopGraph
from services.loop.result import LoopResult
from services.loop.state import LoopState
from services.prompts.loop import get_loop_prompt
from services.streaming.content import extract_text
from services.streaming.emitter import StreamEmitter


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
        self.tool_selector = tool_selector
        self.tool_registry = tool_registry
        self.context_builder = context_builder
        self.emitter = StreamEmitter()
        self.prompt = get_loop_prompt()

        self.graph = LoopGraph(
            llm=llm,
            tool_registry=tool_registry,
            risk_engine=risk_engine,
            context_builder=context_builder,
            checkpointer=checkpointer,
        )

    def _build_config(self, thread_id: str | None):
        checkpointer = getattr(self.graph, "checkpointer", None)

        if checkpointer is not None and not thread_id:
            raise ValueError(
                "A thread_id is required when the loop uses a checkpointer."
            )

        if not thread_id:
            return None

        return {
            "configurable": {
                "thread_id": thread_id,
            }
        }

    def _build_state(
        self,
        question: str,
        history: list | None,
    ) -> LoopState:
        if self.tool_selector is None:
            raise ValueError(
                "Tool selector is required for loop route."
            )

        selected_tools = self.tool_selector.select(question)
        selected_tool_names = [tool.name for tool in selected_tools]

        prompt_messages = self.prompt.invoke({
            "history": history or [],
            "question": question,
        })

        return {
            "question": question,
            "messages": prompt_messages.messages,
            "tool_results": [],
            "answer": "",
            "selected_tools": selected_tool_names,
            "risk_action": None,
            "risk_decisions": [],
        }

    def run(
        self,
        question: str,
        history: list | None = None,
        thread_id: str | None = None,
    ) -> LoopResult:
        try:
            state = self._build_state(question, history)
            config = self._build_config(thread_id)

            result = self.graph.invoke(
                state,
                config=config,
            )
            return self._build_result(result)
        except Exception as exc:
            raise normalize_exception(exc) from exc

    def resume(
        self,
        thread_id: str,
        approved: bool,
    ) -> LoopResult:
        try:
            if not thread_id:
                raise ValueError(
                    "thread_id is required to resume the loop."
                )

            from langgraph.types import Command

            result = self.graph.invoke(
                Command(resume=approved),
                config=self._build_config(thread_id),
            )
            return self._build_result(result)
        except Exception as exc:
            raise normalize_exception(exc) from exc

    def stream(
        self,
        question: str,
        history: list | None = None,
        thread_id: str | None = None,
    ):
        try:
            state = self._build_state(question, history)
            config = self._build_config(thread_id)
            yield from self._stream_graph(state, config=config)
        except Exception as exc:
            error = normalize_exception(exc)
            yield self.emitter.error(
                error.message,
                code=error.code,
            )

    def resume_stream(
        self,
        thread_id: str,
        approved: bool,
    ):
        try:
            if not thread_id:
                raise ValueError(
                    "thread_id is required to resume the loop."
                )

            from langgraph.types import Command

            yield from self._stream_graph(
                Command(resume=approved),
                config=self._build_config(thread_id),
            )
        except Exception as exc:
            error = normalize_exception(exc)
            yield self.emitter.error(
                error.message,
                code=error.code,
            )

    def _stream_graph(self, input_data, config=None):
        full_answer = ""
        risk_decisions = []

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
                if not content:
                    continue

                full_answer += content
                yield self.emitter.token(content)
                continue

            if part["type"] != "updates":
                continue

            updates = part["data"]

            # LangGraph can expose interrupts directly on the updates
            # payload under the reserved __interrupt__ key.
            # Do not treat that tuple as a normal node update dictionary.
            interrupts = updates.get("__interrupt__")

            if interrupts:
                interrupt = interrupts[0]
                payload = getattr(interrupt, "value", interrupt)

                if isinstance(payload, dict):
                    confirmation_payload = payload
                else:
                    confirmation_payload = {
                        "message": str(payload),
                    }

                yield self.emitter.confirmation_required(
                    confirmation_payload
                )
                return

            for node_name, update in updates.items():
                # Reserved metadata entries are not node update dictionaries.
                if node_name.startswith("__"):
                    continue

                if not isinstance(update, dict):
                    continue

                if node_name == "risk":
                    decisions = update.get("risk_decisions", [])
                    if decisions:
                        risk_decisions = decisions

                    action = update.get("risk_action")

                    if action == "reject":
                        yield self.emitter.error(
                            update.get(
                                "answer",
                                "The requested action was rejected.",
                            ),
                            code="RISK_REJECTED",
                            details=decisions,
                        )
                        return

                    if action == "allow":
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

    def _build_result(self, result) -> LoopResult:
        if result is None:
            raise ValueError("Loop returned no result.")

        interrupts = result.get("__interrupt__")

        if interrupts:
            interrupt_value = interrupts[0].value
            if not isinstance(interrupt_value, dict):
                interrupt_value = {
                    "message": str(interrupt_value),
                }

            return LoopResult(
                content=(
                    "Confirmation is required before executing the action."
                ),
                display_type="card",
                data={
                    "type": "confirmation",
                    **interrupt_value,
                },
                metadata={
                    "status": "waiting_confirmation",
                },
            )

        risk_action = result.get("risk_action")
        status = (
            "rejected"
            if risk_action == "reject"
            else "completed"
        )

        return LoopResult(
            content=extract_text(result.get("answer", "")),
            display_type="text",
            data={
                "risk_decisions": result.get(
                    "risk_decisions",
                    [],
                ),
            },
            metadata={
                "status": status,
            },
        )
