from langchain_core.messages import BaseMessage
from services.context.configuration import ContextConfiguration

class ContextBuilder:

    def __init__(
        self,
        configuration: ContextConfiguration,
    ):
        self.configuration = configuration

    def build_history(
        self,
        history: list[BaseMessage],
    ) -> list[BaseMessage]:

        max_tokens = (
            self.configuration.max_history_tokens
        )

        selected: list[BaseMessage] = []

        current_tokens = 0

        # Start from the newest message so the
        # most recent conversation is preserved.
        for message in reversed(history):

            message_tokens = self._estimate_tokens(
                message
            )

            if (
                selected
                and current_tokens + message_tokens
                > max_tokens
            ):
                break

            selected.append(message)
            current_tokens += message_tokens

        selected.reverse()

        return selected

    def _estimate_tokens(
        self,
        message: BaseMessage,
    ) -> int:

        content = message.content

        if not isinstance(content, str):
            content = str(content)

        # Rough cross-provider estimation.
        return max(
            1,
            len(content) // 4,
        )