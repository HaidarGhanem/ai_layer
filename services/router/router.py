from services.prompts.router import get_router_prompt
from services.router.result import RouterResult

class Router: 
    def __init__(self, manager):
        self.manager = manager
        self.llm = manager.get_adapter("router")
        self.prompt = get_router_prompt()
        self.structured_llm = self.llm.with_structured_output(RouterResult)

    def route(self, question, history: list | None = None,):
        message = self.prompt.invoke({
            "history": history or [],
            "question": question
        })
        return self.structured_llm.invoke(message)