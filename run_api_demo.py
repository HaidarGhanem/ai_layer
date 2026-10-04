from services.observability.langsmith import configure_langsmith
from services.api.app import create_app
from v1_support import build_demo_brain


configure_langsmith()

brain = build_demo_brain()
app = create_app(brain)
