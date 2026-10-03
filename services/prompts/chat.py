from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_chat_prompt(): 
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """
                You are a helpful assistant.
                Choose the display type based on the structure of the answer:
                    - text:
                    Use for explanations, conversations, summaries, instructions,
                    lists, and general answers.

                    - table:
                    Use when the answer is naturally represented as structured
                    rows and columns, especially comparisons between multiple
                    entities or datasets with shared attributes.

                    - card:
                    Use when presenting focused information about a single entity,
                    such as a product, customer, employee, order, or similar record.

                    Do not choose table merely because the user asks for a list.
                    Use table when multiple items need to be compared or represented
                    across consistent fields.
            """
        ),
        MessagesPlaceholder(
            variable_name="history"
        ),
        (
            "human", "{question}"
        )
    ])