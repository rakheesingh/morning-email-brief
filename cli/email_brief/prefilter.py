"""
Rule-based pre-filter that classifies ONLY obvious noise WITHOUT using AI.
Only filters things that are definitely not worth AI analysis.
Everything else goes to AI for proper classification.
"""
import re
from .types import RawEmail, EmailSummary

NOREPLY_PATTERNS = {"noreply", "no-reply", "do-not-reply", "donotreply", "mailer-daemon"}

CHARITY_PATTERNS = [
    r"donate\s+(now|today|rs|₹|\$)",
    r"help\s+(him|her|them)\s+survive",
    r"save\s+(his|her|their)\s+life",
    r"baby.*(surgery|hospital|treatment)",
    r"crowdfund",
    r"milaap\.org",
    r"ketto\.org",
    r"gofundme\.com",
]

MASS_MAIL_SIGNALS = {
    "unsubscribe",
    "view in browser",
    "email preferences",
    "manage subscriptions",
    "opt out of",
    "update your preferences",
}


def _get_sender_local(email_addr: str) -> str:
    match = re.search(r"<?([\w.+-]+)@", email_addr)
    return match.group(1).lower() if match else ""


def _is_charity_spam(email: RawEmail) -> bool:
    text = (email.subject + " " + email.snippet).lower()
    matches = sum(1 for p in CHARITY_PATTERNS if re.search(p, text))
    return matches >= 2


def _is_mass_newsletter(email: RawEmail) -> bool:
    sender_local = _get_sender_local(email.sender)
    is_noreply = any(p in sender_local for p in NOREPLY_PATTERNS)

    body_lower = (email.body[:500] + email.snippet).lower()
    mass_signals = sum(1 for kw in MASS_MAIL_SIGNALS if kw in body_lower)

    return is_noreply and mass_signals >= 2


def prefilter(emails: list[RawEmail]) -> tuple[list[EmailSummary], list[RawEmail]]:
    """
    Only filters out:
    - Charity/donation spam (emotional manipulation patterns)
    - Mass newsletters from noreply senders with unsubscribe links

    Everything else goes to AI — we don't assume what's important to the user.

    Returns:
        - already_classified: obvious noise that doesn't need AI
        - needs_ai: everything else
    """
    already_classified: list[EmailSummary] = []
    needs_ai: list[RawEmail] = []

    for email in emails:
        if _is_charity_spam(email):
            already_classified.append(_make_summary(email, "low", "Spam"))
        elif _is_mass_newsletter(email):
            already_classified.append(_make_summary(email, "low", "Newsletter"))
        else:
            needs_ai.append(email)

    return already_classified, needs_ai


def _make_summary(email: RawEmail, priority: str, category: str) -> EmailSummary:
    return EmailSummary(
        email_id=email.id,
        sender=email.sender,
        subject=email.subject,
        date=email.date,
        summary=email.snippet,
        priority=priority,
        needs_reply=False,
        category=category,
    )
