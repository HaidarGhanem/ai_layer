from services.LLM.llm_adapter import LLMAdapter
from services.LLM.profiles import get_default_profiles

class LLMManager:

    def __init__(self):
        self.profiles = get_default_profiles()

    def get_adapter(self, name):
        profile = self.profiles.get(name)

        if not profile:
            raise ValueError(
                f"LLM profile '{name}' not found"
            )

        return LLMAdapter(profile.configuration)