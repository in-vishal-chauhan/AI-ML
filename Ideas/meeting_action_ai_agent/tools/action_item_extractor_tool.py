
from langchain.tools import tool
from langchain.chat_models import ChatGroq
from config import settings

llm = ChatGroq(groq_api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL)

@tool
def extract_action_items(email_body: str) -> list:
    prompt = f"Extract all action items from the following meeting notes:\n{email_body}"
    response = llm.predict(prompt)
    return response.split("\n")
