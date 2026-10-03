from services.loop.state import LoopState


class LoopNodes:

    def __init__(
        self,
        llm,
        tool_registry,
    ):
        self.llm = llm
        self.tool_registry = tool_registry

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

        response = llm.invoke(
            state["messages"]
        )

        return {
            "messages": [response],
            "answer": response.content or "",
        }


# from services.loop.state import LoopState


# class LoopNodes:

#     def __init__(
#         self,
#         llm,
#         tool_registry,
#     ):
#         self.llm = llm
#         self.tool_registry = tool_registry

#     def call_llm(
#         self,
#         state: LoopState,
#     ):

#         selected_tools = []

#         for tool_name in state["selected_tools"]:

#             tool = self.tool_registry.get(
#                 tool_name
#             )

#             if tool is not None:

#                 selected_tools.append(
#                     tool
#                 )

#         llm = self.llm

#         if selected_tools:

#             llm = llm.bind_tools(
#                 selected_tools
#             )

#         response = llm.invoke(
#             state["messages"]
#         )

#         return {
#             "messages": [response],
#             "answer": response.content or "",
#         }



# from services.loop.state import LoopState

# class LoopNodes:

#     def __init__(self, llm, tools):
#         self.llm = llm.bind_tools(tools)

#     def call_llm(self, state: LoopState):

#         response = self.llm.invoke(
#             state["messages"]
#         )

#         return {
#             "messages": [response],
#             "answer": response.content,
#         }