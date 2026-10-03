from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """
    Get the current local date and time.

    Use this tool when the user asks for the
    current time or current date and time.
    """

    return datetime.now().astimezone().isoformat()