from services.loop.graph import LoopGraph
from services.loop.result import LoopResult
from services.loop.state import LoopState

from services.prompts.loop import get_loop_prompt

from services.context.builder import ContextBuilder


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