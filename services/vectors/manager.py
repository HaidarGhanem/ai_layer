from services.vectors.store import VectorStore
from services.vectors.profiles import get_default_profiles

class VectorStoreManager:

    def __init__(self):
        self.profiles = get_default_profiles()

    def get_store(self, name):
        profile = self.profiles.get(name)

        if not profile:
            raise ValueError(
                f"Vector store profile '{name}' not found"
            )

        return VectorStore(profile.configuration)