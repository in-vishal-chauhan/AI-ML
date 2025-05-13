from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import json

# The scope determines what access we need. Readonly is enough for reading emails.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None
    if os.path.exists('token.json'):
        print("Token already exists.")
        return

    # Launches browser for Google login
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the token
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print("✅ token.json has been generated successfully!")

if __name__ == '__main__':
    main()
