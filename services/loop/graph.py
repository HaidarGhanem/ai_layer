from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.prebuilt import ToolNode

from services.loop.nodes import LoopNodes
from services.loop.state import LoopState

from services.risk.engine import RiskEngine
from services.risk.node import RiskNode


class LoopGraph:

    def __init__(
        self,
        llm,
        tool_registry,
        risk_engine: RiskEngine,
        checkpointer=None,
    ):

        self.tool_registry = tool_registry

        self.nodes = LoopNodes(
            llm=llm,
            tool_registry=tool_registry,
        )

        self.risk_node = RiskNode(
            risk_engine=risk_engine
        )

        self.checkpointer = checkpointer

        self.graph = self._build()

    def _build(self):

        graph = StateGraph(
            LoopState
        )

        graph.add_node(
            "llm",
            self.nodes.call_llm,
        )

        graph.add_node(
            "risk",
            self.risk_node.check,
        )

        graph.add_node(
            "tools",
            ToolNode(
                self.tool_registry.get_all()
            ),
        )

        graph.add_edge(
            START,
            "llm",
        )

        graph.add_conditional_edges(
            "llm",
            self.should_check_risk,
            {
                "risk": "risk",
                "end": END,
            },
        )

        graph.add_conditional_edges(
            "risk",
            self.risk_route,
            {
                "tools": "tools",
                "end": END,
            },
        )

        graph.add_edge(
            "tools",
            "llm",
        )

        return graph.compile(
            checkpointer=self.checkpointer
        )

    def should_check_risk(
        self,
        state: LoopState,
    ):

        last_message = state["messages"][-1]

        if getattr(
            last_message,
            "tool_calls",
            None,
        ):

            return "risk"

        return "end"

    def risk_route(
        self,
        state: LoopState,
    ):

        if state.get(
            "risk_action"
        ) == "allow":

            return "tools"

        return "end"

    def invoke(
        self,
        state: LoopState,
        config=None,
    ):

        return self.graph.invoke(
            state,
            config=config,
        )

# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import ToolNode, tools_condition
# from services.loop.nodes import LoopNodes
# from services.loop.state import LoopState

# class LoopGraph:

#     def __init__(self, llm, tools):

#         self.nodes = LoopNodes(
#             llm=llm,
#             tools=tools,
#         )
#         self.tools = tools
#         self.graph = self._build()

#     def _build(self):
#         graph = StateGraph(LoopState)
#         graph.add_node(
#             "llm",
#             self.nodes.call_llm,
#         )
#         graph.add_node(
#             "tools",
#             ToolNode(self.tools),
#         )
#         graph.add_edge(
#             START,
#             "llm",
#         )
#         graph.add_conditional_edges(
#             "llm",
#             tools_condition,
#             {
#                 "tools": "tools",
#                 "__end__": END,
#             },
#         )
#         graph.add_edge(
#             "tools",
#             "llm",
#         )
#         return graph.compile()

#     def invoke(self, state: LoopState):
#         return self.graph.invoke(state)