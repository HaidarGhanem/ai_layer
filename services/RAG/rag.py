from services.retrieval.retriever import RetrieverService
from services.prompts.rag import get_rag_prompt
from services.RAG.result import RagResult

class Rag:
    def __init__(self, retriever: RetrieverService, llm):
        self.retriever = retriever
        self.llm = llm 
        self.prompt = get_rag_prompt()
        self.structured_llm = self.llm.with_structured_output(RagResult)

    def retrieve(self, question: str):
        return self.retriever.retrieve(question)

    def generate(self, question: str, results):
        context = "\n\n".join(
            result.node.text for result in results
        )
        messages = self.prompt.invoke({
            "context": context, 
            "question": question
        })
        return self.structured_llm.invoke(messages)

    def answer(self, question: str):
        results = self.retrieve(question)
        return self.generate(
            question=question,
            results=results
        )