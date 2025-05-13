import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# If modifying these scopes, delete token.json and regenerate it
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        raise Exception("❌ token.json not found. Please run generate_token.py first.")

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_latest_message(service):
    try:
        # Get latest message ID
        results = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
            return None

        message_id = messages[0]['id']
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()

        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')

        # Decode the body
        parts = payload.get('parts', [])
        body = ""
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        else:
            body = base64.urlsafe_b64decode(payload.get('body', {}).get('data', '')).decode('utf-8')

        return {
            "message_id": message_id,
            "subject": subject,
            "from": sender,
            "body": body.strip()
        }

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

if __name__ == '__main__':
    service = get_gmail_service()
    message = get_latest_message(service)
    if message:
        print("📧 Latest Email:")
        print(json.dumps(message, indent=2))
