import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")
warnings.filterwarnings("ignore", message=".*urllib3.*")

from .config import GROQ_API_KEY, GEMINI_API_KEY, AI_PROVIDER, BRIEFING_TIME, EMAIL_COUNT
from .renderer import done, error, render_briefing, render_history
from .utils import select


CMD = "morning-email-brief"

HELP = f"""
  📬 morning-email-brief — AI email briefing tool

  Install:
    pip install morning-email-brief

  Usage:
    {CMD}              Generate a new briefing
    {CMD} login        Sign in with Google (opens browser)
    {CMD} last         Show the most recent briefing
    {CMD} history      List all past briefing dates
    {CMD} date <DATE>  Show briefing for a specific date (YYYY-MM-DD)
    {CMD} setup        Choose AI provider (Groq / Gemini) & configure
    {CMD} help         Show this help message

  AI Providers:
    Groq    Free — Llama 3.3 70B  (https://console.groq.com)
    Gemini  Free — Gemini 2.0 Flash (https://aistudio.google.com/apikey)

  Config (~/.email-brief/.env):
    AI_PROVIDER               groq or gemini
    BRIEFING_TIME={BRIEFING_TIME}        Daily schedule (24hr format)
    EMAIL_COUNT={EMAIL_COUNT}          Emails to fetch
"""


def _setup():
    from .config import DATA_DIR
    env_path = DATA_DIR / ".env"

    print("\n  📬 Email Brief — Setup\n")

    providers = [
        "Groq   — Free, fast (Llama 3.3 70B)",
        "Gemini — Free tier (Gemini 2.0 Flash)",
    ]
    choice = select("Choose your AI provider  (↑↓ to move, Enter to select):", providers)

    lines = [f"AUTH_SERVER_URL=https://email-brief-eight.vercel.app"]

    if choice == 0:
        api_key = input("  Groq API Key (free from https://console.groq.com): ").strip()
        lines.append(f"AI_PROVIDER=groq")
        lines.append(f"GROQ_API_KEY={api_key}")
        provider_name = "Groq (Llama 3.3 70B)"
    else:
        api_key = input("  Gemini API Key (free from https://aistudio.google.com/apikey): ").strip()
        lines.append(f"AI_PROVIDER=gemini")
        lines.append(f"GEMINI_API_KEY={api_key}")
        provider_name = "Gemini 2.0 Flash"

    lines.extend([
        f"BRIEFING_TIME={BRIEFING_TIME}",
        f"EMAIL_COUNT={EMAIL_COUNT}",
    ])
    env_path.write_text("\n".join(lines) + "\n")

    print("")
    done(f"Config saved to {env_path}")
    done(f"AI provider: {provider_name}")
    print(f"  Now run: {CMD} login\n")


def _login():
    from .gmail_client import wait_for_auth_callback

    print("\n  📬 Email Brief — Gmail Setup\n")

    try:
        wait_for_auth_callback()
        print("")
        done("Gmail connected! Token saved locally.")
        print(f"  Run: {CMD}\n")
    except Exception as err:
        error(str(err))
        sys.exit(1)


def main():
    args = sys.argv[1:]
    command = args[0] if args else "run"

    if command in ("help", "--help", "-h"):
        print(HELP)
        return

    if command == "setup":
        _setup()
        return

    if command == "login":
        _login()
        return

    if not GROQ_API_KEY and not GEMINI_API_KEY:
        error(f"No AI API key set. Run: {CMD} setup")
        print("  This will let you choose between Groq and Gemini.\n")
        sys.exit(1)

    if command == "logout":
        from .gmail_client import _clear_tokens
        _clear_tokens()
        done("Logged out. Credentials removed.")
        return

    if command == "run":
        from .gmail_client import is_authenticated
        if not is_authenticated():
            error(f"Not authenticated. Run: {CMD} login")
            sys.exit(1)

        from .briefing import run_briefing
        briefing = run_briefing()
        print(render_briefing(briefing))

    elif command == "last":
        from .storage import get_latest_briefing
        briefing = get_latest_briefing()
        if not briefing:
            error(f"No briefings found. Run: {CMD}")
            sys.exit(1)
        print(render_briefing(briefing))

    elif command == "history":
        from .storage import get_all_briefing_dates
        dates = get_all_briefing_dates()
        print(render_history(dates))

    elif command == "date":
        if len(args) < 2:
            error(f"Provide a date: {CMD} date 2026-04-07")
            sys.exit(1)
        from .storage import get_briefing_by_date
        briefing = get_briefing_by_date(args[1])
        if not briefing:
            error(f"No briefing found for {args[1]}")
            sys.exit(1)
        print(render_briefing(briefing))

    else:
        print(f"  Unknown command: {command}")
        print(HELP)
        sys.exit(1)


if __name__ == "__main__":
    main()
