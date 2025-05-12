# gmail_utils.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

def get_gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.readonly"])
    service = build("gmail", "v1", credentials=creds)
    return service
