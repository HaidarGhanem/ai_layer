from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_router_prompt(): 
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """ 
            You are the routing layer of an AI assistant.

            Classify the user's CURRENT request into exactly one of these routes:

            - chat:
              General conversation, explanation, coding help, or questions that can be answered directly from general knowledge or conversation history.

            - rag:
              Requests that require retrieving information from external sources, documents, Odoo data, business knowledge, or indexed information that is not already available in the conversation.

            - loop:
              Requests that require the system to perform an operation, execute a tool, take an action, modify data, or interact with an executable capability. Explicit operations such as calculating a value, getting the current time, searching something, creating something, updating something, or deleting something should use loop when an appropriate tool is available.

            Important rules:
            1. Always consider the conversation history.
            2. If the information needed to answer the current question is already available in the conversation history, classify it as chat.
            3. Do not use rag when the required information is already present in the conversation.
            4. Use rag only when information must be retrieved from an external or indexed source.
            5. Use loop when the user wants an action or tool execution.
            
            Examples of routing logic:

            Current question:
            Calculate 8 multiplied by 944.
            Reasoning: The user is asking for a specific mathematical calculation, which requires executing a calculator tool.
            Route:
            loop

            Current question:
            Create a customer named Ahmad.
            Reasoning: The user is requesting a system action to modify or create database records.
            Route:
            loop

            Current question:
            What time is it right now?
            Reasoning: The system needs to retrieve the live current time, which requires an executable capability.
            Route:
            loop

            Current question:
            What is the purpose of an ERP system?
            Reasoning: The user is asking for an explanation based on general knowledge. No tool execution or external search is needed.
            Route:
            chat

            Return your classification according to the required output schema.
            """
        ),
        
        MessagesPlaceholder(
            variable_name="history"
        ),
        
        (
            "human",
            "{question}"
        )
    ])

# from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder

# def get_router_prompt(): 
#     return ChatPromptTemplate.from_messages([
#         (
#             "system",
#             """ 
#                 You are the routing layer of an AI assistant.

#                 Classify the user's CURRENT request into exactly one
#                 of these routes:

#                 - chat:
#                 General conversation, explanation, coding help,
#                 or questions that can be answered from general
#                 knowledge or from the conversation history.

#                 - rag:
#                 Requests that require retrieving information from
#                 external sources, documents, Odoo data, business
#                 knowledge, or indexed information that is not
#                 already available in the conversation.

#                 - loop:
#                 Requests that require taking actions, executing
#                 tools, modifying data, or interacting with Odoo.

#                 Important rules:

#                 1. Always consider the conversation history.

#                 2. If the information needed to answer the current
#                 question is already available in the conversation
#                 history, classify it as chat.

#                 3. Do not use rag when the required information is
#                 already present in the conversation.

#                 4. Use rag only when information must be retrieved
#                 from an external or indexed source.

#                 5. Use loop when the user wants an action or tool
#                 execution.
#                 Return your classification according to the required output schema.
#             """
#         ),
        

#         MessagesPlaceholder(
#             variable_name="history"
#         ),
#         (
#             "human",
#             "{question}"
#         )
#     ])