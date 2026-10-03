# from services.config import get_env
# from services.LLM.configuration import LLMConfiguration
# from services.LLM.profile import LLMProfile
# from services.LLM.provider import LLMProvider


# def get_default_profiles():
#     return {
#         "router": LLMProfile(
#             name="router",
#             configuration=LLMConfiguration(
#                 provider=LLMProvider.GEMINI,
#                 model="gemini-3.5-flash",
#                 temperature=0.0,
#                 api_key=get_env("GEMINI_API_KEY"),
#             ),
#         ),

#         "rag": LLMProfile(
#             name="rag",
#             configuration=LLMConfiguration(
#                 provider=LLMProvider.GEMINI,
#                 model="gemini-3.5-flash",
#                 temperature=0.2,
#                 api_key=get_env("GEMINI_API_KEY"),
#             ),
#         ),

#         "loop": LLMProfile(
#             name="loop",
#             configuration=LLMConfiguration(
#                 provider=LLMProvider.GEMINI,
#                 model="gemini-3.5-flash",
#                 temperature=0.2,
#                 api_key=get_env("GEMINI_API_KEY"),
#             ),
#         ),

#         "chat": LLMProfile(
#             name="chat",
#             configuration=LLMConfiguration(
#                 provider=LLMProvider.GEMINI,
#                 model="gemini-3.5-flash",
#                 temperature=0.7,
#                 api_key=get_env("GEMINI_API_KEY"),
#             ),
#         ),
#     }



from services.config import get_env
from services.LLM.configuration import LLMConfiguration
from services.LLM.profile import LLMProfile
from services.LLM.provider import LLMProvider


def get_default_profiles():
    return {
        "router": LLMProfile(
            name="router",
            configuration=LLMConfiguration(
                provider=LLMProvider.OLLAMA,
                model="qwen2.5:3b",
                temperature=0.0,
            ),
        ),

        "rag": LLMProfile(
            name="rag",
            configuration=LLMConfiguration(
                provider=LLMProvider.OLLAMA,
                model="qwen2.5:3b",
                temperature=0.2,
            ),
        ),

        "loop": LLMProfile(
            name="loop",
            configuration=LLMConfiguration(
                provider=LLMProvider.OLLAMA,
                model="qwen2.5:3b",
                temperature=0.2,
            ),
        ),

        "chat": LLMProfile(
            name="chat",
            configuration=LLMConfiguration(
                provider=LLMProvider.OLLAMA,
                model="qwen2.5:3b",
                temperature=0.7,
            ),
        ),
    }