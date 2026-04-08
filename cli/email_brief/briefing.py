from datetime import datetime, timezone

from .config import EMAIL_COUNT
from .gmail_client import fetch_recent_emails
from .summarizer import summarize_emails
from .prioritizer import sort_by_priority
from .storage import save_briefing
from .renderer import done
from .types import Briefing


def run_briefing() -> Briefing:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print("")
    done(f"Starting briefing for {today}")
    done(f"Fetching up to {EMAIL_COUNT} emails...")

    emails = fetch_recent_emails(EMAIL_COUNT)

    if not emails:
        return Briefing(id=None, date=today, created_at=datetime.now(timezone.utc).isoformat(),
                        total_emails=0, summaries=[])

    done(f"Fetched {len(emails)} emails")
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
