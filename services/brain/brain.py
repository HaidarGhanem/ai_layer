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

        # ====================================================
        # Context / Memory
        # ====================================================

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

        # ====================================================
        # Tool System
        # ====================================================

        self.tool_selector = tool_selector
        self.tool_registry = tool_registry

        # ====================================================
        # Risk
        # ====================================================

        self.risk_engine = risk_engine

        # ====================================================
        # Router
        # ====================================================

        self.router = Router(
            manager
        )

        # ====================================================
        # Chat
        # ====================================================

        self.chat = Chat(
            manager
        )

        # ====================================================
        # RAG
        # ====================================================

        self.rag = Rag(
            retriever=retriever,
            llm=manager.get_adapter(
                "rag"
            ),
        )

        # ====================================================
        # Loop
        # ====================================================

        self.loop = Loop(
            llm=manager.get_adapter(
                "loop"
            ),
            tool_selector=self.tool_selector,
            tool_registry=self.tool_registry,
            risk_engine=self.risk_engine,
            context_builder=self.context_builder,
            checkpointer=checkpointer,
        )

    # ========================================================
    # Process
    # ========================================================

    def process(
        self,
        question: str,
        session_id: str,
    ):

        # ----------------------------------------------------
        # Build Context
        # ----------------------------------------------------

        context = self.context_manager.build(
            session_id=session_id,
            question=question,
        )

        # ----------------------------------------------------
        # Router
        # ----------------------------------------------------

        router_result = self.router.route(
            question=question,
            history=context.messages[:-1],
        )

        print(
            "----------Router Result-----------"
        )

        print(
            router_result.route
        )

        print(
            router_result.confidence
        )

        print(
            router_result.needs_clarification
        )

        print(
            "----------------------------------"
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if router_result.needs_clarification:

            raise ValueError(
                "Clarification is required"
            )

        if router_result.confidence <= 0.5:

            raise ValueError(
                "Router confidence is too low"
            )

        # ----------------------------------------------------
        # Chat
        # ----------------------------------------------------

        if router_result.route == "chat":

            chat_result = self.chat.respond(
                question=question,
                history=context.messages[:-1],
            )

            response = BrainResponse(
                content=chat_result.content,
                display_type=chat_result.display_type,
            )

        # ----------------------------------------------------
        # RAG
        # ----------------------------------------------------

        elif router_result.route == "rag":

            retrieved_results = self.rag.retrieve(
                question
            )

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

        # ----------------------------------------------------
        # Loop
        # ----------------------------------------------------

        elif router_result.route == "loop":

            if self.tool_selector is None:

                raise ValueError(
                    "Tool selector is required for loop route"
                )

            loop_result = self.loop.run(
                question=question,
                history=context.messages[:-1],
                thread_id=session_id,
            )

            response = BrainResponse(
                content=loop_result.content,
                display_type=loop_result.display_type,
                data=loop_result.data,
                metadata=loop_result.metadata,
            )

        # ----------------------------------------------------
        # Unsupported Route
        # ----------------------------------------------------

        else:

            raise ValueError(
                f"Route '{router_result.route}' is not implemented yet"
            )

        # ----------------------------------------------------
        # Save Response
        # ----------------------------------------------------

        self.context_manager.save_response(
            context=context,
            response=response.content,
        )

        return response

    # ========================================================
    # Stream
    # ========================================================

    def stream(
        self,
        question: str,
        session_id: str,
    ):

        context = self.context_manager.build(
            session_id=session_id,
            question=question,
        )

        try:
            router_result = self.router.route(
                question=question,
                history=context.messages[:-1],
            )

            if router_result.needs_clarification:
                yield self.emitter.error(
                    "Clarification is required.",
                    code="CLARIFICATION_REQUIRED",
                )
                return

            if router_result.confidence <= 0.5:
                yield self.emitter.error(
                    "Router confidence is too low.",
                    code="LOW_ROUTER_CONFIDENCE",
                )
                return

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
                )
                return

            if router_result.route == "loop":
                if self.tool_selector is None:
                    yield self.emitter.error(
                        "Tool selector is required for loop route.",
                        code="TOOL_SELECTOR_REQUIRED",
                    )
                    return

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

            yield self.emitter.error(
                f"Route '{router_result.route}' is not implemented yet.",
                code="UNSUPPORTED_ROUTE",
            )

        except Exception as exc:
            yield self.emitter.error(
                str(exc),
                code="BRAIN_STREAM_ERROR",
            )

    def resume_stream(
        self,
        session_id: str,
        approved: bool,
    ):

        try:
            config = {
                "configurable": {
                    "thread_id": session_id,
                }
            }

            state = self.loop.graph.graph.get_state(config)
            question = state.values.get("question", "")

            context = self.context_manager.build(
                session_id=session_id,
                question=question,
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
            yield self.emitter.error(
                str(exc),
                code="BRAIN_RESUME_STREAM_ERROR",
            )
