from services.loop.state import LoopState

from services.context.builder import ContextBuilder


class LoopNodes:

    def __init__(
        self,
        llm,
        tool_registry,
        context_builder: ContextBuilder,
    ):
        self.llm = llm
        self.tool_registry = tool_registry
        self.context_builder = context_builder

    def call_llm(
        self,
        state: LoopState,
    ):

        selected_tools = []

        for tool_name in state["selected_tools"]:

            tool = self.tool_registry.get(
                tool_name
            )

            if tool is not None:

                selected_tools.append(
                    tool
                )

        llm = self.llm

        if selected_tools:

            llm = llm.bind_tools(
                selected_tools
            )

        messages = self.context_builder.build_tool_messages(
            state["messages"]
        )

        response = llm.invoke(
            messages
        )

        return {
            "messages": [response],
            "answer": response.content or "",
        }
