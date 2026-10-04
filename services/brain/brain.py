from services.chat.chat import Chat
from services.router.router import Router
from services.responses.response import BrainResponse

from services.loop.loop import Loop
from services.tools.selector import ToolSelector

from services.context.manager import ContextManager
from services.context.in_memory import InMemory
from services.context.builder import ContextBuilder
from services.context.configuration import ContextConfiguration

from services.RAG.rag import Rag
from services.streaming.emitter import StreamEmitter
from services.streaming.content import extract_text

from services.errors.exceptions import (
    CheckpointNotFoundError,
    ClarificationRequiredError,
    InvalidRequestError,
    LowRouterConfidenceError,
    ToolSelectorRequiredError,
    UnsupportedRouteError,
)
from services.errors.translate import normalize_exception

try:
    from langsmith import traceable
except ImportError:  # pragma: no cover - LangSmith is a V1 dependency.
    def traceable(*args, **kwargs):
        def decorator(function):
            return function
        return decorator


class Brain:
    def __init__(
        self,
        manager,
        retriever,
        tool_selector: ToolSelector | None = None,
        tool_registry=None,
        risk_engine=None,
        checkpointer=None,
        context_manager: ContextManager | None = None,
        context_configuration: ContextConfiguration | None = None,
    ):
        if context_manager is not None:
            self.context_manager = context_manager
        else:
            context_configuration = (
                context_configuration
                or ContextConfiguration()
            )
            self.context_manager = ContextManager(
                memory=InMemory(),
                builder=ContextBuilder(
                    configuration=context_configuration
                ),
            )

        self.context_builder = self.context_manager.builder
        self.emitter = StreamEmitter()

        self.tool_selector = tool_selector
        self.tool_registry = tool_registry
        self.risk_engine = risk_engine

        self.router = Router(manager)
        self.chat = Chat(manager)
        self.rag = Rag(
            retriever=retriever,
            llm=manager.get_adapter("rag"),
        )
        self.loop = Loop(
            llm=manager.get_adapter("loop"),
            tool_selector=self.tool_selector,
            tool_registry=self.tool_registry,
            risk_engine=self.risk_engine,
            context_builder=self.context_builder,
            checkpointer=checkpointer,
        )

    @staticmethod
    def _validate_inputs(question: str, session_id: str) -> None:
        if not isinstance(question, str) or not question.strip():
            raise InvalidRequestError("Question must not be empty.")

        if not isinstance(session_id, str) or not session_id.strip():
            raise InvalidRequestError("Session ID must not be empty.")

    @staticmethod
    def _validate_router_result(router_result) -> None:
        confidence = router_result.confidence

        if router_result.needs_clarification:
            raise ClarificationRequiredError(
                details={
                    "confidence": confidence,
                }
            )

        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise LowRouterConfidenceError(
                message="Router returned an invalid confidence value.",
                details={
                    "confidence": confidence,
                },
            )

        if confidence <= 0.5:
            raise LowRouterConfidenceError(
                details={
                    "confidence": confidence,
                    "route": router_result.route,
                }
            )

    def _build_context(self, question: str, session_id: str):
        return self.context_manager.build(
            session_id=session_id,
            question=question,
        )

    @traceable(
        name="AI Layer / Brain.process",
        run_type="chain",
    )
    def process(
        self,
        question: str,
        session_id: str,
    ):
        try:
            self._validate_inputs(question, session_id)
            context = self._build_context(question, session_id)

            router_result = self.router.route(
                question=question,
                history=context.messages[:-1],
            )
            self._validate_router_result(router_result)

            if router_result.route == "chat":
                chat_result = self.chat.respond(
                    question=question,
                    history=context.messages[:-1],
                )
                response = BrainResponse(
                    content=chat_result.content,
                    display_type=chat_result.display_type,
                )

            elif router_result.route == "rag":
                retrieved_results = self.rag.retrieve(question)
                self.context_manager.prepare_retrieved_context(
                    context=context,
                    results=retrieved_results,
                )
                rag_result = self.rag.generate(
                    question=question,
                    results=context.retrieved_context,
                )
                response = BrainResponse(
                    content=rag_result.content,
                    display_type=rag_result.display_type,
                )

            elif router_result.route == "loop":
                if self.tool_selector is None:
                    raise ToolSelectorRequiredError()

                loop_result = self.loop.run(
                    question=question,
                    history=context.messages[:-1],
                    thread_id=session_id,
                )
                response = BrainResponse(
                    content=loop_result.content,
                    display_type=loop_result.display_type,
                    data=loop_result.data,
                    metadata={
                        "response": loop_result.metadata,
                    },
                )

            else:
                raise UnsupportedRouteError(
                    f"Route '{router_result.route}' is not implemented yet."
                )

            if response.metadata.response.get("status") != "waiting_confirmation":
                self.context_manager.save_response(
                    context=context,
                    response=response.content,
                )

            return response

        except Exception as exc:
            raise normalize_exception(exc) from exc

    def resume(
        self,
        session_id: str,
        approved: bool,
    ):
        try:
            if not isinstance(session_id, str) or not session_id.strip():
                raise InvalidRequestError(
                    "Session ID must not be empty."
                )

            config = {
                "configurable": {
                    "thread_id": session_id,
                }
            }
            state = self.loop.graph.graph.get_state(config)
            values = getattr(state, "values", None)

            if not values or not values.get("question"):
                raise CheckpointNotFoundError(
                    details={"session_id": session_id}
                )

            loop_result = self.loop.resume(
                thread_id=session_id,
                approved=approved,
            )

            context = self._build_context(
                values["question"],
                session_id,
            )

            if loop_result.content:
                self.context_manager.save_response(
                    context=context,
                    response=loop_result.content,
                )

            return BrainResponse(
                content=loop_result.content,
                display_type=loop_result.display_type,
                data=loop_result.data,
                metadata={
                    "response": loop_result.metadata,
                },
            )

        except Exception as exc:
            raise normalize_exception(exc) from exc

    def stream(
        self,
        question: str,
        session_id: str,
    ):
        try:
            self._validate_inputs(question, session_id)
            context = self._build_context(question, session_id)

            router_result = self.router.route(
                question=question,
                history=context.messages[:-1],
            )
            self._validate_router_result(router_result)

            if router_result.route == "chat":
                full_content = ""

                for chunk in self.chat.stream(
                    question=question,
                    history=context.messages[:-1],
                ):
                    content = extract_text(chunk)
                    if not content:
                        continue
                    full_content += content
                    yield self.emitter.token(content)

                self.context_manager.save_response(
                    context=context,
                    response=full_content,
                )
                yield self.emitter.completed(
                    content=full_content,
                    display_type="text",
                    metadata={
                        "status": "completed",
                        "route": "chat",
                    },
                )
                return

            if router_result.route == "rag":
                retrieved_results = self.rag.retrieve(question)
                self.context_manager.prepare_retrieved_context(
                    context=context,
                    results=retrieved_results,
                )

                context_text = "\n\n".join(
                    result.node.text
                    for result in context.retrieved_context
                )
                messages = self.rag.prompt.invoke({
                    "context": context_text,
                    "question": question,
                })

                full_content = ""
                for chunk in self.rag.llm.stream(messages):
                    content = extract_text(chunk)
                    if not content:
                        continue
                    full_content += content
                    yield self.emitter.token(content)

                self.context_manager.save_response(
                    context=context,
                    response=full_content,
                )
                yield self.emitter.completed(
                    content=full_content,
                    display_type="text",
                    metadata={
                        "status": "completed",
                        "route": "rag",
                    },
                )
                return

            if router_result.route == "loop":
                if self.tool_selector is None:
                    raise ToolSelectorRequiredError()

                for event in self.loop.stream(
                    question=question,
                    history=context.messages[:-1],
                    thread_id=session_id,
                ):
                    if event.type == "completed":
                        self.context_manager.save_response(
                            context=context,
                            response=event.data.get("content", ""),
                        )
                    yield event
                return

            raise UnsupportedRouteError(
                f"Route '{router_result.route}' is not implemented yet."
            )

        except Exception as exc:
            error = normalize_exception(exc)
            yield self.emitter.error(
                error.message,
                code=error.code,
                details=error.details,
            )

    def resume_stream(
        self,
        session_id: str,
        approved: bool,
    ):
        try:
            if not isinstance(session_id, str) or not session_id.strip():
                raise InvalidRequestError(
                    "Session ID must not be empty."
                )

            config = {
                "configurable": {
                    "thread_id": session_id,
                }
            }
            state = self.loop.graph.graph.get_state(config)
            values = getattr(state, "values", None)

            if not values or not values.get("question"):
                raise CheckpointNotFoundError(
                    details={"session_id": session_id}
                )

            context = self._build_context(
                values["question"],
                session_id,
            )

            for event in self.loop.resume_stream(
                thread_id=session_id,
                approved=approved,
            ):
                if event.type == "completed":
                    response = event.data.get("content", "")
                    if response:
                        self.context_manager.save_response(
                            context=context,
                            response=response,
                        )
                yield event

        except Exception as exc:
            error = normalize_exception(exc)
            yield self.emitter.error(
                error.message,
                code=error.code,
                details=error.details,
            )
