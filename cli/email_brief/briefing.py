from datetime import datetime, timezone

from .config import EMAIL_COUNT, LAST_RUN_FILE
from .gmail_client import fetch_recent_emails
from .summarizer import summarize_emails
from .prioritizer import sort_by_priority
from .storage import save_briefing
from .renderer import done
from .types import Briefing
from .utils import get_last_run, save_last_run


def run_briefing() -> Briefing:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    last_run = get_last_run(LAST_RUN_FILE)

    print("")
    done(f"Starting briefing for {today}")

    if last_run:
        from datetime import datetime as dt
        last_time = dt.fromtimestamp(last_run).strftime("%b %d, %I:%M %p")
        done(f"Fetching unread emails since last run ({last_time})...")
    else:
        done(f"First run — fetching up to {EMAIL_COUNT} unread emails...")

    emails = fetch_recent_emails(EMAIL_COUNT, after_epoch=last_run)

    save_last_run(LAST_RUN_FILE)

    if not emails:
        done("No new unread emails since last run.")
        return Briefing(id=None, date=today, created_at=datetime.now(timezone.utc).isoformat(),
                        total_emails=0, summaries=[])

    done(f"Fetched {len(emails)} new emails")
    done("Analyzing with AI...\n")

    summaries = summarize_emails(emails)
    sorted_summaries = sort_by_priority(summaries)

    briefing = Briefing(
        id=None,
        date=today,
        created_at=datetime.now(timezone.utc).isoformat(),
        total_emails=len(emails),
        summaries=sorted_summaries,
    )

    bid = save_briefing(briefing)
    briefing.id = bid
    done(f"Briefing saved (ID: {bid})")

    return briefing
