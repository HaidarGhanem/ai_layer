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