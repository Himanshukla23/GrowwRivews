"""
Shared Google OAuth 2.0 authentication helper.
Handles the OAuth flow for both Google Docs and Gmail APIs.
Stores tokens in data/google_token.json for reuse.
"""

import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for Docs append + Gmail send
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.send",
]

TOKEN_PATH = os.path.join("data", "google_token.json")
CREDENTIALS_PATH = os.path.join("credentials.json")


def get_google_credentials() -> Credentials:
    """
    Returns valid Google OAuth2 credentials.

    On first run, opens a browser for the OAuth consent flow and saves
    the refresh token to data/google_token.json.
    On subsequent runs, silently refreshes the token.

    Raises:
        FileNotFoundError: If credentials.json is missing.
    """
    creds = None

    # Check for existing token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If no valid creds, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[Auth] Refreshing Google token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Google OAuth credentials file not found at '{CREDENTIALS_PATH}'. "
                    "Download it from Google Cloud Console → APIs & Services → Credentials → "
                    "OAuth 2.0 Client IDs → Download JSON, and save as 'credentials.json' "
                    "in the project root."
                )
                
            # Fail fast if we are running in a headless cloud environment
            if "RENDER" in os.environ or "FLY_APP_NAME" in os.environ or "VERCEL" in os.environ or not os.environ.get("DISPLAY", "true"):
                raise RuntimeError("Cannot perform interactive Google OAuth flow on cloud deployment! Ensure GOOGLE_TOKEN_BASE64 is set with a valid token.")
                
            print("[Auth] Starting Google OAuth flow (browser will open)...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"[Auth] Token saved to {TOKEN_PATH}")

    return creds
