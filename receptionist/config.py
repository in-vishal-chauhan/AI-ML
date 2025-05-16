from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    ENDPOINT = os.getenv("ENDPOINT")
    MODEL = os.getenv("MODEL")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
