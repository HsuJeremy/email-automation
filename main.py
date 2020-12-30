#!/usr/bin/python3
import os
import sys
import json
import pickle
import base64
import email
import requests
import parse_message
from io import StringIO
from email.generator import Generator
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def setup():
    creds = None
    # token.pickle stores access and refresh tokens
    # Created automatically when the authorization flow completes for the first time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_labels(service):
    request = service.users().labels().list(userId='me')
    response = request.execute()
    return response.get('labels', [])

def get_messages(service):
    request = service.users().messages().list(userId='me')
    response = request.execute()
    return response

def get_mime_message(service, user_id, message_id):
    mime_message = None
    try:
        request = service.users().messages().get(userId=user_id, id=message_id, format='raw')
        message = request.execute()
        content = base64.urlsafe_b64decode(message['raw'].encode('utf-8')).decode('utf-8')
        mime_message = email.message_from_string(content)
    except Exception as e:
        print(e)
    return mime_message

def convert_to_str(mime_message):
    print(mime_message)
    fp = StringIO()
    g = Generator(fp, mangle_from_=True, maxheaderlen=60)
    g.flatten(mime_message)
    return fp.getvalue()

def main():
    creds = setup()
    if not creds:
        print('Error setting up credentials')
        sys.exit(0)

    service = build('gmail', 'v1', credentials=creds)

    messages = get_messages(service)['messages']
    for i in range(5):
        # Just print one for now as a test
        result = get_mime_message(service, 'me', messages[i]['id'])
        result_str = convert_to_str(result)
        parse_message.parse_message(result_str)
        return

    return

    labels = get_labels(service)
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

if __name__ == '__main__':
    main()
