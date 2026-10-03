from langchain_core.tools import tool


@tool
def delete_demo_record(record_id: str) -> str:
    """
    Delete a demo record.

    Use this tool only when the user explicitly
    asks to delete a demo record.
    """

    return (
        f"Demo record {record_id} "
        "was deleted."
    )