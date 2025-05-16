
from langchain.tools import tool

@tool
def identify_note_source(email_body: str) -> bool:
    keywords = ["Fathom", "TickTick", "Fireflies", "Otter"]
    return any(keyword.lower() in email_body.lower() for keyword in keywords)
