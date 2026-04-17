import base64
import json
import os
import subprocess
import platform
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Event

import requests as http_requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .config import AUTH_SERVER_URL, DATA_DIR
from .types import RawEmail
from .utils import _extract_body, get_logger, _count_images

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLI_CALLBACK_PORT = 9587
TOKEN_FILE = DATA_DIR / ".credentials"
LOG_FILE = DATA_DIR / "debug.log"

_logger = get_logger("email-brief", LOG_FILE)


def _open_browser(url: str):
    system = platform.system()
    if system == "Darwin":
        subprocess.Popen(["open", url])
    elif system == "Windows":
        subprocess.Popen(["start", url], shell=True)
    else:
        subprocess.Popen(["xdg-open", url])


def _save_tokens(access_token: str, refresh_token: str, expiry_date: int):
    data = json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expiry_date": expiry_date,
    })
    TOKEN_FILE.write_text(data)
    os.chmod(TOKEN_FILE, 0o600)
    has_refresh = bool(refresh_token)
    _logger.info("Tokens saved — has_refresh=%s, expiry=%s", has_refresh, expiry_date)


def _get_tokens() -> dict:
    if not TOKEN_FILE.exists():
        raise FileNotFoundError("Not authenticated. Run: morning-email-brief login")

    data = json.loads(TOKEN_FILE.read_text())
    if not data.get("access_token") or not data.get("refresh_token"):
        raise FileNotFoundError("Invalid credentials. Run: morning-email-brief login")

    return data


def _clear_tokens():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def _refresh_via_server(refresh_token: str) -> dict:
    url = f"{AUTH_SERVER_URL}/api/auth/refresh"
    _logger.info("Refresh request → POST %s", url)

    try:
        resp = http_requests.post(
            url,
            json={"refresh_token": refresh_token},
            timeout=30,
        )
    except http_requests.exceptions.RequestException as net_err:
        _logger.error("Refresh network error: %s", net_err)
        raise RuntimeError(f"Token refresh failed: network error — {net_err}")

    _logger.info("Refresh response: status=%d, content-type=%s, body=%s",
                 resp.status_code,
                 resp.headers.get("content-type", "unknown"),
                 resp.text[:500])

    if resp.status_code != 200:
        try:
            error = resp.json().get("error", "Unknown error")
        except Exception:
            error = f"Server returned {resp.status_code}"
        _logger.error("Refresh failed: %s", error)
        raise RuntimeError(f"Token refresh failed: {error}")

    try:
        data = resp.json()
    except Exception:
        _logger.error("Refresh response not valid JSON: %s", resp.text[:500])
        raise RuntimeError("Token refresh failed: invalid response from server")

    if not data.get("access_token"):
        _logger.error("Refresh response missing access_token: %s", data)
        raise RuntimeError("Token refresh failed: no access_token in response")

    _logger.info("Refresh success — new token expires at %s", data.get("expiry_date"))
    return {
        "access_token": data["access_token"],
        "expiry_date": data.get("expiry_date", 0),
    }


def is_authenticated() -> bool:
    try:
        _get_tokens()
        return True
    except Exception:
        return False


def authenticate() -> Credentials:
    tokens = _get_tokens()

    now_ms = int(time.time() * 1000)
    expiry = tokens["expiry_date"]
    is_expired = expiry and expiry < now_ms

    _logger.info("Auth check — expiry=%s, now=%s, expired=%s", expiry, now_ms, is_expired)

    if is_expired:
        _logger.info("Token expired %ds ago, starting refresh", (now_ms - expiry) // 1000)
        last_error = None
        for attempt in range(1, 4):
            try:
                new_tokens = _refresh_via_server(tokens["refresh_token"])
                tokens["access_token"] = new_tokens["access_token"]
                tokens["expiry_date"] = new_tokens.get("expiry_date", 0)
                _save_tokens(tokens["access_token"], tokens["refresh_token"], tokens["expiry_date"])
                _logger.info("Refresh succeeded on attempt %d", attempt)
                last_error = None
                break
            except Exception as err:
                last_error = err
                _logger.warning("Refresh attempt %d failed: %s", attempt, err)
                if attempt < 3:
                    time.sleep(attempt * 2)

        if last_error:
            _logger.error("All 3 refresh attempts failed. Last error: %s", last_error)
            raise RuntimeError(
                f"Token refresh failed after 3 attempts: {last_error}\n"
                f"  Check logs: {LOG_FILE}\n"
                "  Run: morning-email-brief login"
            )

    return Credentials(token=tokens["access_token"])


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

            token_data = json.loads(base64.urlsafe_b64decode(tokens_encoded + "=="))

            _save_tokens(
                token_data.get("access_token", ""),
                token_data.get("refresh_token", ""),
                token_data.get("expiry_date", 0),
            )

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




def _extract_header(headers: list, name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""



def fetch_recent_emails(count: int, after_epoch: int | None = None) -> list[RawEmail]:
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)

    query = "in:inbox is:unread"
    if after_epoch:
        query += f" after:{after_epoch}"

    results = service.users().messages().list(
        userId="me", maxResults=count, q=query
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

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        body = _extract_body(payload)
        inline_imgs, has_attachment = _count_images(payload)

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
            image_count=inline_imgs,
            has_attachment=has_attachment,
        ))

        if (i + 1) % 10 == 0:
            print(f"\r  Fetched {i + 1}/{len(message_ids)}", end="", flush=True)

    print(f"\n  Fetched {len(emails)} emails successfully.")
    return emails
