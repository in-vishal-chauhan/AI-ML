
from langchain.tools import tool

@tool
def create_ticket(user_email: str, actions: list) -> dict:
    # Simulate API call
    return {"status": "created", "user": user_email, "tasks": actions}
