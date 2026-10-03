from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI 
from langchain_ollama import ChatOllama
from services.LLM.configuration import LLMConfiguration 
from services.LLM.provider import LLMProvider

class LLMAdapter:
    def __init__(self, configuration: LLMConfiguration):
        self.configuration = configuration
        self.llm = self.create_llm()

    def create_llm(self):

        if self.configuration.provider == LLMProvider.GEMINI: 
            return ChatGoogleGenerativeAI(
                model=self.configuration.model,
                temperature=self.configuration.temperature,
                google_api_key=self.configuration.api_key,
            )

        elif self.configuration.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=self.configuration.model,
                temperature=self.configuration.temperature,
                api_key=self.configuration.api_key,
            )

        elif self.configuration.provider == LLMProvider.OLLAMA:
            return ChatOllama(
                model=self.configuration.model,
                temperature=self.configuration.temperature,
                base_url=self.configuration.base_url
            )

        raise ValueError(
            f"Provider {self.configuration.provider} is not supported"
        )

    def invoke(self, prompt):
        return self.llm.invoke(prompt)

    def stream(self, prompt):
        return self.llm.stream(prompt)

    def with_structured_output(self, schema):
        return self.llm.with_structured_output(schema)

    def bind_tools(self, tools):
        return self.llm.bind_tools(tools)