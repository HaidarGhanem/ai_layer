from services.loop.tools.registry import ToolRegistry
from services.loop.tools.calculator import calculate


registry = ToolRegistry()

registry.register(calculate)

print(registry.get("calculate"))
print(registry.get_all())