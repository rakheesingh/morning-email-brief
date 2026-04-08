import base64
import json
import re
import subprocess
import sys
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Event

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .config import TOKEN_PATH, AUTH_SERVER_URL, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET
from .types import RawEmail

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLI_CALLBACK_PORT = 9587


def _open_browser(url: str):
    system = platform.system()
    if system == "Darwin":
        subprocess.Popen(["open", url])
    elif system == "Windows":
        subprocess.Popen(["start", url], shell=True)
    else:
        subprocess.Popen(["xdg-open", url])


def authenticate() -> Credentials:
    if not TOKEN_PATH.exists():
        raise FileNotFoundError("Not authenticated. Run: email-brief login")

    token_data = json.loads(TOKEN_PATH.read_text())
    creds = Credentials(
        token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data.get("client_id", "") or GMAIL_CLIENT_ID,
        client_secret=token_data.get("client_secret", "") or GMAIL_CLIENT_SECRET,
        expiry=None,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data["access_token"] = creds.token
        TOKEN_PATH.write_text(json.dumps(token_data, indent=2))

    return creds


def wait_for_auth_callback():
    done = Event()
    error_msg = [None]

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if not parsed.path.startswith("/callback"):
                return

            params = parse_qs(parsed.query)
            tokens_encoded = params.get("tokens", [None])[0]
            err = params.get("error", [None])[0]

            if err:
                self.send_response(302)
                self.send_header("Location", f"{AUTH_SERVER_URL}/auth/error")
                self.end_headers()
                error_msg[0] = f"Authorization denied: {err}"
                done.set()
                return

            if not tokens_encoded:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing tokens")
                error_msg[0] = "No tokens received"
                done.set()
                return

            tokens = json.loads(base64.urlsafe_b64decode(tokens_encoded + "=="))
            TOKEN_PATH.write_text(json.dumps(tokens, indent=2))

            self.send_response(302)
            self.send_header("Location", f"{AUTH_SERVER_URL}/auth/success")
            self.end_headers()
            done.set()

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("localhost", CLI_CALLBACK_PORT), CallbackHandler)
    server.timeout = 120

    login_url = f"{AUTH_SERVER_URL}/api/auth/login"
    print(f"\n  Opening browser for Gmail sign-in...\n")
    print(f"  If the browser doesn't open, visit:")
    print(f"  {login_url}\n")
    _open_browser(login_url)

    while not done.is_set():
        server.handle_request()

    server.server_close()

    if error_msg[0]:
        raise RuntimeError(error_msg[0])


def _decode_base64(data: str) -> str:
    padded = data.replace("-", "+").replace("_", "/")
    return base64.b64decode(padded + "==").decode("utf-8", errors="replace")


def _extract_header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _extract_body(payload: dict) -> str:
    if payload.get("body", {}).get("data"):
        return _decode_base64(payload["body"]["data"])

    parts = payload.get("parts", [])
    for mime in ["text/plain", "text/html"]:
        for part in parts:
            if part.get("mimeType") == mime and part.get("body", {}).get("data"):
                text = _decode_base64(part["body"]["data"])
                if mime == "text/html":
                    text = re.sub(r"<[^>]*>", " ", text)
                    text = re.sub(r"\s+", " ", text).strip()
                return text

    for part in parts:
        nested = _extract_body(part)
        if nested:
            return nested

    return ""


def fetch_recent_emails(count: int) -> list[RawEmail]:
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me", maxResults=count, q="in:inbox is:unread"
    ).execute()

    message_ids = results.get("messages", [])
    if not message_ids:
        print("  No unread emails found.")
        return []

    print(f"  Fetching {len(message_ids)} emails...")

    emails = []
    for i, msg_ref in enumerate(message_ids):
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])
        body = _extract_body(msg.get("payload", {}))

        emails.append(RawEmail(
            id=msg.get("id", ""),
            thread_id=msg.get("threadId", ""),
            sender=_extract_header(headers, "From"),
            to=_extract_header(headers, "To"),
            subject=_extract_header(headers, "Subject"),
            date=_extract_header(headers, "Date"),
            snippet=msg.get("snippet", ""),
            body=body[:2000],
            labels=msg.get("labelIds", []),
            is_unread="UNREAD" in msg.get("labelIds", []),
        ))

        if (i + 1) % 10 == 0:
            print(f"\r  Fetched {i + 1}/{len(message_ids)}", end="", flush=True)

    print(f"\n  Fetched {len(emails)} emails successfully.")
    return emails
