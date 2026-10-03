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


class Brain:

    def __init__(
        self,
        manager,
        retriever,
        tool_selector: ToolSelector | None = None,
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

        # ====================================================
        # Tool Selector
        # ====================================================

        self.tool_selector = tool_selector

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
        )

    # ========================================================
    # Process
    # ========================================================

    def process(
        self,
        question: str,
        session_id: str,
    ):

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

            rag_result = self.rag.answer(
                question
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

        router_result = self.router.route(
            question=question,
            history=context.messages[:-1],
        )

        if (
            router_result.route == "chat"
            and router_result.confidence > 0.5
        ):

            return self.chat.stream(
                question=question,
                history=context.messages[:-1],
            )

        raise ValueError(
            f"Route '{router_result.route}' is not implemented yet"
        )
# from services.chat.chat import Chat
# from services.router.router import Router
# from services.responses.response import BrainResponse

# from services.loop.tools.registry import ToolRegistry
# from services.loop.loop import Loop

# from services.context.manager import ContextManager
# from services.context.in_memory import InMemory
# from services.context.builder import ContextBuilder
# from services.context.configuration import ContextConfiguration

# from services.RAG.rag import Rag

# from services.tools.selector import ToolSelector
# from services.tools.register import ToolRegistry
# from services.tools.retriever import ToolRetriever


# class Brain:

#     def __init__(
#         self,
#         manager,
#         retriever,
#         tool_registry: ToolRegistry | None = None,
#         tool_retriever=None,
#         context_manager: ContextManager | None = None,
#         context_configuration: ContextConfiguration | None = None,
#     ):

#         # ====================================================
#         # Context / Memory
#         # ====================================================

#         if context_manager is not None:

#             self.context_manager = context_manager

#         else:

#             context_configuration = (
#                 context_configuration
#                 or ContextConfiguration()
#             )

#             self.context_manager = ContextManager(
#                 memory=InMemory(),
#                 builder=ContextBuilder(
#                     configuration=context_configuration
#                 ),
#             )

#         # ====================================================
#         # Tool Registry
#         # ====================================================

#         self.tool_registry = (
#             tool_registry
#             or ToolRegistry()
#         )

#         # -----------------------------
#         # Tool Selector
#         # -----------------------------

#         if tool_retriever is not None:

#             self.tool_selector = ToolSelector(
#                 retriever=tool_retriever,
#                 registry=self.tool_registry,
#             )

#         else:

#             self.tool_selector = None

#         # ====================================================
#         # Router
#         # ====================================================

#         self.router = Router(
#             manager
#         )

#         # ====================================================
#         # Chat
#         # ====================================================

#         self.chat = Chat(
#             manager
#         )

#         # ====================================================
#         # RAG
#         # ====================================================

#         self.rag = Rag(
#             retriever=retriever,
#             llm=manager.get_adapter(
#                 "rag"
#             ),
#         )

#         # ====================================================
#         # Loop
#         # ====================================================

#         self.loop = Loop(
#             llm=manager.get_adapter(
#                 "loop"
#             ),
#             tool_selector=self.tool_selector,
#         )

#     # ========================================================
#     # Process
#     # ========================================================

#     def process(
#         self,
#         question: str,
#         session_id: str,
#     ):

#         # ----------------------------------------------------
#         # Build Context
#         # ----------------------------------------------------

#         context = self.context_manager.build(
#             session_id=session_id,
#             question=question,
#         )

#         # ----------------------------------------------------
#         # Router
#         # ----------------------------------------------------

#         router_result = self.router.route(
#             question=question,
#             history=context.messages[:-1],
#         )

#         print(
#             "----------Router Result-----------"
#         )

#         print(
#             router_result.route
#         )

#         print(
#             router_result.confidence
#         )

#         print(
#             router_result.needs_clarification
#         )

#         print(
#             "----------------------------------"
#         )

#         # ----------------------------------------------------
#         # Validation
#         # ----------------------------------------------------

#         if router_result.needs_clarification:

#             raise ValueError(
#                 "Clarification is required"
#             )

#         if router_result.confidence <= 0.5:

#             raise ValueError(
#                 "Router confidence is too low"
#             )

#         # ----------------------------------------------------
#         # Chat
#         # ----------------------------------------------------

#         if router_result.route == "chat":

#             chat_result = self.chat.respond(
#                 question=question,
#                 history=context.messages[:-1],
#             )

#             response = BrainResponse(
#                 content=chat_result.content,
#                 display_type=chat_result.display_type,
#             )

#         # ----------------------------------------------------
#         # RAG
#         # ----------------------------------------------------

#         elif router_result.route == "rag":

#             rag_result = self.rag.answer(
#                 question
#             )

#             response = BrainResponse(
#                 content=rag_result.content,
#                 display_type=rag_result.display_type,
#             )

#         # ----------------------------------------------------
#         # Loop
#         # ----------------------------------------------------

#         elif router_result.route == "loop":

#             loop_result = self.loop.run(
#                 question=question,
#                 history=context.messages[:-1],
#             )

#             response = BrainResponse(
#                 content=loop_result.content,
#                 display_type=loop_result.display_type,
#                 data=loop_result.data,
#                 metadata=loop_result.metadata,
#             )

#         # ----------------------------------------------------
#         # Unknown Route
#         # ----------------------------------------------------

#         else:

#             raise ValueError(
#                 f"Route '{router_result.route}' is not implemented yet"
#             )

#         # ----------------------------------------------------
#         # Save Response
#         # ----------------------------------------------------

#         self.context_manager.save_response(
#             context=context,
#             response=response.content,
#         )

#         return response

#     # ========================================================
#     # Stream
#     # ========================================================

#     def stream(
#         self,
#         question: str,
#         session_id: str,
#     ):

#         context = self.context_manager.build(
#             session_id=session_id,
#             question=question,
#         )

#         router_result = self.router.route(
#             question=question,
#             history=context.messages[:-1],
#         )

#         if (
#             router_result.route == "chat"
#             and router_result.confidence > 0.5
#         ):

#             return self.chat.stream(
#                 question=question,
#                 history=context.messages[:-1],
#             )

#         raise ValueError(
#             f"Route '{router_result.route}' is not implemented yet"
#         )