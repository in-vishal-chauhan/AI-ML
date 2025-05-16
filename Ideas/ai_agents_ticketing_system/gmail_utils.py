import os
import base64
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
import pickle
import time

# If you have token.json already from OAuth flow
creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.readonly'])

# Build the Gmail service
service = build('gmail', 'v1', credentials=creds)

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

def get_last_10_emails():
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

        headers = msg_detail['payload'].get('headers', [])
        subject = sender = date = ''
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From':
                sender = header['value']
            elif header['name'] == 'Date':
                date = header['value']

        # Decode email body
        body = ''
        parts = msg_detail['payload'].get('parts')
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = part['body'].get('data')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            body_data = msg_detail['payload']['body'].get('data')
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')

        emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body
        })

    return emails

EMAILS_FILE = 'emails.json'

def load_emails():
    if not os.path.exists(EMAILS_FILE):
        return []
    with open(EMAILS_FILE, 'rb') as f:
        if os.stat(EMAILS_FILE).st_size == 0:
            return []
        return json.load(f)

def save_emails(emails, mode='w'):
    with open(EMAILS_FILE, mode, encoding='utf-8') as f:
        json.dump(emails, f, ensure_ascii=False, indent=2)


# if __name__ == '__main__':
#     service = get_gmail_service()
#     message = get_latest_message(service)
#     if message:
#         print("📧 Latest Email:")
#         print(json.dumps(message, indent=2))
