from services.LLM.manager import LLMManager
from services.loop.loop import Loop
from services.loop.tools.calculator import calculate


llm_manager = LLMManager()

loop = Loop(
    llm=llm_manager.get_adapter("loop"),
    tools=[calculate],
)

result = loop.run(
    "What is 125 multiplied by 8?"
)

print("CONTENT:")
print(result.content)

# from services.loop.loop import Loop
# from services.LLM.manager import LLMManager

# llm_manager = LLMManager()

# loop = Loop(
#     llm=llm_manager.get_adapter("loop")
# )

# result = loop.run(
#     "Explain how an Odoo model works."
# )

# print(result)

# from services.LLM.manager import LLMManager
# from services.loop.graph import Loop


# llm_manager = LLMManager()

# llm = llm_manager.get_adapter("loop")

# loop = Loop(llm)

# result = loop.run(
#     "Explain what an Odoo model is."
# )

# print("========== LOOP RESULT ==========")
# print(result)

# print("\n========== ANSWER ==========")
# print(result["answer"])