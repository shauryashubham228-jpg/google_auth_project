import os
from django.shortcuts import render, redirect
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def google_login(request):
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri='http://localhost:8000/google/callback/')
    # Enable PKCE code verifier and save it to the user session
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    request.session['oauth_state'] = state
    request.session['oauth_code_verifier'] = flow.code_verifier  # Fix line 1
    return redirect(authorization_url)

def google_callback(request):
    state = request.session.get('oauth_state')
    verifier = request.session.get('oauth_code_verifier')  # Fix line 2
    
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state, redirect_uri='http://localhost:8000/google/callback/')
    flow.code_verifier = verifier  # Fix line 3
    
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    
    service = build('gmail', 'v1', credentials=flow.credentials)
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    email_list = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        email_list.append({'subject': subject, 'sender': sender, 'snippet': msg_detail.get('snippet', '')})

    return render(request, 'emails.html', {'emails': email_list})
