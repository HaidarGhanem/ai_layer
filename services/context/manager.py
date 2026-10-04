from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)

from services.context.context import AIContext
from services.context.memory import Memory
from services.context.builder import ContextBuilder


class ContextManager:

    def __init__(
        self,
        memory: Memory,
        builder: ContextBuilder,
    ):
        self.memory = memory
        self.builder = builder

    # ========================================================
    # Build Context
    # ========================================================

    def build(
        self,
        session_id: str,
        question: str,
    ) -> AIContext:

        history = self.memory.get(
            session_id
        )

        selected_history = (
            self.builder.build_history(
                history
            )
        )

        return AIContext(
            session_id=session_id,
            question=question,
            history=history,
            messages=[
                *selected_history,
                HumanMessage(
                    content=question
                ),
            ],
        )

    # ========================================================
    # Retrieved Context
    # ========================================================

    def prepare_retrieved_context(
        self,
        context: AIContext,
        results: list,
    ) -> list:

        selected = (
            self.builder.build_retrieved_context(
                results
            )
        )

        context.retrieved_context = selected

        return selected

    # ========================================================
    # Tool Results
    # ========================================================

    def prepare_tool_results(
        self,
        context: AIContext,
        tool_results: list[dict],
    ) -> list[dict]:

        selected = (
            self.builder.build_tool_results(
                tool_results
            )
        )

        context.tool_results = selected

        return selected

    # ========================================================
    # Save Response
    # ========================================================

    def save_response(
        self,
        context: AIContext,
        response: str,
    ) -> None:

        updated_history = [
            *context.history,
            HumanMessage(
                content=context.question
            ),
            AIMessage(
                content=response
            ),
        ]

        self.memory.save(
            context.session_id,
            updated_history,
        )