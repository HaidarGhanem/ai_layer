# from services.LLM.manager import LLMManager
# from services.router.router import Router
# from services.chat.chat import Chat
# from services.prompts.chat import get_chat_prompt
# from services.brain.brain import Brain
# import json

# def main():
#     manager = LLMManager()
#     brain = Brain(manager)
#     result = brain.process("Explain what Node.js is in simple terms.")
#     print(result)
#     print(type(result))

#     print("Content:", result.content)
#     print("Display type:", result.display_type)
#     print("Data:", result.data)
#     print("Metadata:", result.metadata)

# if __name__ == "__main__":
#     main()


# manager = LLMManager()
# chat = manager.get_adapter("chat")
# chat = Chat(manager)
# result = chat.stream("compare node.js and fastapi")
# for chunk in result:
#     print(chunk.content, end="")

# manager = LLMManager()
# chat = Chat(manager)
# result = chat.respond("compare node.js and fastapi")

# print(result)
# print(type(result))
# print(result.content)
# print(result.display_type)

# manager = LLMManager()
# router = Router(manager)
# result = router.route("Show me the products currently in stock")

# print(result)
# print(type(result))
# print(result.route)
# print(result.confidence)
# print(result.needs_clarification)

# manager = LLMManager()
# chat = manager.get_adapter("chat")
# result = chat.invoke("how are you")

# print(json.dumps(result, indent=4))