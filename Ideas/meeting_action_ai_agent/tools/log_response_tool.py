
from langchain.tools import tool

@tool
def log_ticket_response(user_email: str, actions: list, result: dict):
    print(f"Logging: User={user_email}, Actions={actions}, Result={result}")
