from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """
    Calculate a basic mathematical expression.

    Use this tool when the user asks for a mathematical calculation.
    """

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)

    except Exception:
        return "Unable to calculate the expression."