from services.prompts.chat import get_chat_prompt
from services.chat.result import ChatResult

class Chat: 
    def __init__(self, manager): 
        self.manager = manager 
        self.llm = manager.get_adapter("chat")
        self.prompt = get_chat_prompt()
        self.structured_llm = self.llm.with_structured_output(ChatResult)

    def respond(self, question: str , history: list | None = None):
        message = self.prompt.invoke({
            "history": history or [],
            "question": question
        })
        return self.structured_llm.invoke(message)

    def stream(self, question: str , history: list | None = None):
        message = self.prompt.invoke({
            "history": history or [],
            "question": question
        })
        return self.llm.stream(message)