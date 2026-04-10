import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")
warnings.filterwarnings("ignore", message=".*urllib3.*")

from .config import GROQ_API_KEY, GEMINI_API_KEY, BRIEFING_TIME, EMAIL_COUNT
from .renderer import done, error, render_briefing, render_history


HELP = f"""
  📬 email-brief — AI email briefing tool

  Usage:
    email-brief              Generate a new briefing
    email-brief login        Sign in with Google (opens browser)
    email-brief last         Show the most recent briefing
    email-brief history      List all past briefing dates
    email-brief date <DATE>  Show briefing for a specific date (YYYY-MM-DD)
    email-brief setup        Configure API keys interactively
    email-brief help         Show this help message

  Config (~/.email-brief/.env):
    BRIEFING_TIME={BRIEFING_TIME}   Daily schedule (24hr format)
    EMAIL_COUNT={EMAIL_COUNT}       Emails to fetch
"""


def _setup():
    from .config import DATA_DIR
    env_path = DATA_DIR / ".env"

    print("\n  📬 Email Brief — Setup\n")

    groq_key = input("  Groq API Key (free from https://console.groq.com): ").strip()

    lines = [
        f"GROQ_API_KEY={groq_key}",
        f"AUTH_SERVER_URL=https://email-brief-eight.vercel.app",
        f"BRIEFING_TIME={BRIEFING_TIME}",
        f"EMAIL_COUNT={EMAIL_COUNT}",
    ]
    env_path.write_text("\n".join(lines) + "\n")

    print("")
    done(f"Config saved to {env_path}")
    print("  Now run: email-brief login\n")


def _login():
    from .gmail_client import wait_for_auth_callback, is_authenticated, _clear_tokens

    print("\n  📬 Email Brief — Gmail Setup\n")

    if is_authenticated():
        done("Already authenticated!")
        print("  To re-authenticate, run: email-brief logout\n")
        return

    try:
        wait_for_auth_callback()
        print("")
        done("Gmail connected! Token saved locally.")
        print("  Run: email-brief\n")
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
        error("No AI API key set. Run: email-brief setup")
        print("  Or set GROQ_API_KEY in ~/.email-brief/.env")
        print("  Get a free key at: https://console.groq.com\n")
        sys.exit(1)

    if command == "logout":
        from .gmail_client import _clear_tokens
        _clear_tokens()
        done("Logged out. Tokens removed from keychain.")
        return

    if command == "run":
        from .gmail_client import is_authenticated
        if not is_authenticated():
            error("Not authenticated. Run: email-brief login")
            sys.exit(1)

        from .briefing import run_briefing
        briefing = run_briefing()
        print(render_briefing(briefing))

    elif command == "last":
        from .storage import get_latest_briefing
        briefing = get_latest_briefing()
        if not briefing:
            error("No briefings found. Run: email-brief")
            sys.exit(1)
        print(render_briefing(briefing))

    elif command == "history":
        from .storage import get_all_briefing_dates
        dates = get_all_briefing_dates()
        print(render_history(dates))

    elif command == "date":
        if len(args) < 2:
            error("Provide a date: email-brief date 2026-04-07")
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
