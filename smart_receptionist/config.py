from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
    LLM_MODEL = os.getenv("LLM_MODEL")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
