from services.tools.resolver import ToolResolver
from services.tools.selection import ToolSelectionPolicy


class ToolSelector:

    def __init__(
        self,
        retriever,
        registry,
        policy: ToolSelectionPolicy | None = None,
    ):

        self.retriever = retriever

        self.resolver = ToolResolver(
            registry=registry
        )

        self.policy = (
            policy
            or ToolSelectionPolicy()
        )

    def select(
        self,
        query: str,
    ):

        results = self.retriever.retrieve(
            query
        )

        selected_results = self.policy.select(
            results
        )

        return self.resolver.resolve(
            selected_results
        )