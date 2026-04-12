"""
Rule-based pre-filter that adds a needs_ai flag to each email.
Only marks obvious noise as not needing AI analysis.
"""
import re
from .types import RawEmail

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


def prefilter(emails: list[RawEmail]) -> list[dict]:
    """
    Returns a list of dicts, one per email:
    {
        "email": RawEmail,
        "needs_ai": True/False,
        "priority": "low" or None,
        "category": "Spam"/"Newsletter" or None,
    }
    """
    results = []

    for email in emails:
        if _is_charity_spam(email):
            results.append({
                "email": email,
                "needs_ai": False,
                "priority": "low",
                "category": "Spam",
            })
        elif _is_mass_newsletter(email):
            results.append({
                "email": email,
                "needs_ai": False,
                "priority": "low",
                "category": "Newsletter",
            })
        else:
            results.append({
                "email": email,
                "needs_ai": True,
                "priority": None,
                "category": None,
            })

    return results
