from langchain_core.messages import BaseMessage

from services.context.configuration import ContextConfiguration


class ContextBuilder:

    def __init__(
        self,
        configuration: ContextConfiguration,
    ):
        self.configuration = configuration

    # ========================================================
    # History
    # ========================================================

    def build_history(
        self,
        history: list[BaseMessage],
    ) -> list[BaseMessage]:

        max_tokens = (
            self.configuration.max_history_tokens
        )

        selected: list[BaseMessage] = []

        current_tokens = 0

        for message in reversed(history):

            message_tokens = (
                self._estimate_message_tokens(
                    message
                )
            )

            if (
                selected
                and current_tokens + message_tokens
                > max_tokens
            ):
                break

            selected.append(
                message
            )

            current_tokens += message_tokens

        selected.reverse()

        return selected

    # ========================================================
    # Retrieved Context
    # ========================================================

    def build_retrieved_context(
        self,
        results: list,
    ) -> list:

        max_tokens = (
            self.configuration.max_retrieved_tokens
        )

        selected = []

        current_tokens = 0

        for result in results:

            text = self._extract_result_text(
                result
            )

            result_tokens = (
                self._estimate_text_tokens(
                    text
                )
            )

            if (
                current_tokens + result_tokens
                > max_tokens
            ):
                continue

            selected.append(
                result
            )

            current_tokens += result_tokens

        return selected

    # ========================================================
    # Tool Results
    # ========================================================

    def build_tool_results(
        self,
        tool_results: list[dict],
    ) -> list[dict]:

        max_tokens = (
            self.configuration.max_tool_tokens
        )

        selected: list[dict] = []

        current_tokens = 0

        for result in tool_results:

            text = str(result)

            result_tokens = (
                self._estimate_text_tokens(
                    text
                )
            )

            if (
                current_tokens + result_tokens
                > max_tokens
            ):
                continue

            selected.append(
                result
            )

            current_tokens += result_tokens

        return selected

    # ========================================================
    # Tool Messages For LLM
    # ========================================================

    def build_tool_messages(
        self,
        messages: list[BaseMessage],
    ) -> list[BaseMessage]:

        max_tokens = (
            self.configuration.max_tool_tokens
        )

        remaining_characters = (
            max_tokens * 4
        )

        result: list[BaseMessage] = []

        for message in messages:

            if message.type != "tool":

                result.append(
                    message
                )

                continue

            content = message.content

            if not isinstance(
                content,
                str,
            ):
                content = str(
                    content
                )

            if remaining_characters <= 0:

                compact_content = (
                    "[Tool result omitted "
                    "because the tool context "
                    "budget was exceeded.]"
                )

            else:

                compact_content = (
                    content[
                        :remaining_characters
                    ]
                )

                remaining_characters -= len(
                    compact_content
                )

            # Keep the original message object
            # unchanged. Create a bounded copy
            # only for the LLM input.
            bounded_message = (
                message.model_copy(
                    update={
                        "content": compact_content
                    }
                )
            )

            result.append(
                bounded_message
            )

        return result

    # ========================================================
    # Token Estimation
    # ========================================================

    def estimate_tokens(
        self,
        text: str,
    ) -> int:

        return self._estimate_text_tokens(
            text
        )

    def _estimate_text_tokens(
        self,
        text: str,
    ) -> int:

        if not text:

            return 0

        return max(
            1,
            len(text) // 4,
        )

    def _estimate_message_tokens(
        self,
        message: BaseMessage,
    ) -> int:

        content = message.content

        if not isinstance(
            content,
            str,
        ):

            content = str(
                content
            )

        return self._estimate_text_tokens(
            content
        )

    # ========================================================
    # Result Text Extraction
    # ========================================================

    def _extract_result_text(
        self,
        result,
    ) -> str:

        node = getattr(
            result,
            "node",
            None,
        )

        if node is not None:

            text = getattr(
                node,
                "text",
                None,
            )

            if text is not None:

                return str(
                    text
                )

        return str(
            result
        )