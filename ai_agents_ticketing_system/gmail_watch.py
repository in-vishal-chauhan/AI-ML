# gmail_watch.py
import os
import pickle
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

# Update with your full Pub/Sub topic name:
TOPIC_NAME = 'projects/aimeetingnotes/topics/AIMeetingNotesPubSubTopic'

def gmail_authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def watch_gmail():
    service = gmail_authenticate()
    request_body = {
        'labelIds': ['INBOX'],
        'topicName': TOPIC_NAME
    }
    response = service.users().watch(userId='me', body=request_body).execute()
    print("✅ Gmail watch response:", response)

if __name__ == '__main__':
    watch_gmail()
