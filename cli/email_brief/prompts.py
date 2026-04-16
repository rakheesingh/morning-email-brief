from .types import RawEmail


def build_triage_prompt(emails: list[RawEmail]) -> str:
    email_list = "\n".join(
        f"--- Email {i + 1} ---\n"
        f"ID: {e.id}\n"
        f"From: {e.sender}\n"
        f"Subject: {e.subject}\n"
        f"Snippet: {e.snippet}\n"
        f"---"
        for i, e in enumerate(emails)
    )

    return f"""You are a strict, no-nonsense email triage assistant. Your job is to help a busy professional decide what actually needs their attention.

Classify each email and return a JSON array.

For EACH email, return an object with:
- "emailId": the email ID exactly as given
- "from": sender name/email
- "subject": the subject line
- "date": ""
- "summary": ""
- "priority": one of "urgent", "important", "fyi", "low"
- "needsReply": true ONLY if a real human (not a bot/system) is directly asking the recipient a question or waiting for their response
- "category": one of "Work", "Finance", "Meeting", "Newsletter", "Personal", "Notification", "HR", "Sales", "Promotion", "Spam"

PRIORITY RULES (be strict):

"urgent" — VERY rare. Only use for:
  - A real colleague/manager/client directly asking you something with a same-day deadline
  - Production outage, P0/P1 incident assigned to you
  - Access/credentials expiring TODAY that block your work
  - A real person you know is blocked and waiting on you
  - your priority got changed or today is your due date for a project or task
  DO NOT mark as urgent: emotional subject lines, charity appeals, clickbait, bank alerts

"important" — Use for:
  - An email from legitimate platforms(example - github, google, aws, azure, vercel, slack, etc.) they are asking for your immediate action or response. figure out if it is a real platform or not.
  - A real person (colleague, recruiter, manager) directly emailing you for a specific question and expecting a response
  - Calendar invites or meeting changes from real people
  - Emails from the comapnies like mynra,flipkart, amazon etc about real coupon or offer codes given to you

"fyi" — Use for:
  - Informational emails worth knowing but no action needed
  - Bank transaction alerts, account statements, UPI alerts, delivery updates
  - Team announcements not requiring your input

"low" — Use for:
  - Newsletters, digests, blog posts, marketing emails
  - Promotions, sales, coupons, offers
  - Automated platform notifications (Naukri alerts, LinkedIn updates, job boards)
  - Charity/donation solicitations
  - Matrimony/dating site notifications
  - Horoscopes, astrology, lifestyle content
  - Any mass-sent email not personally addressed to you

NEEDSREPLY RULES (be very strict):
- true ONLY if a real individual human is personally asking YOU a question or requesting YOUR specific action or imidately expecting your response
- false for: automated emails, no-reply senders, mass emails, newsletters, bank alerts, job platform notifications, charity appeals
- If the sender is a company/platform/bot → needsReply = false, always

COMMON TRAPS TO AVOID:
- Emails with emotional/urgent-sounding subjects from unknown senders → usually spam/charity → "low"
- "Important update" from banks/credit cards → just a notification → "fyi" or "low"
- "You have a new job" from Naukri/Indeed → automated alert → "low"
- "X recruiter expressed interest" → automated platform notification → "low"
- Ignore emails from noreply@ or automated systems
- Ignore emails for bank credentials, OTPs, transactions, any other financial information


Return ONLY valid JSON. No markdown, no explanation. Just the array.

EMAILS:
{email_list}"""


def build_summarize_prompt(emails: list[RawEmail]) -> str:
    email_list = "\n\n".join(
        f"--- Email {i + 1} ---\n"
        f"ID: {e.id}\n"
        f"From: {e.sender}\n"
        f"Subject: {e.subject}\n"
        f"Date: {e.date}\n"
        f"Snippet: {e.snippet}\n"
        f"Body (truncated): {e.body[:800]}\n"
        f"---"
        for i, e in enumerate(emails)
    )

    return f"""You are an email assistant. For each email below, write a concise 1-2 sentence summary focusing on:
- What is this about?
- What action does the recipient need to take?
- What is the deadline or urgency?

Return a JSON array where each object has:
- "emailId": the email ID exactly as given
- "summary": your 1-2 sentence actionable summary

Return ONLY valid JSON. No markdown.

EMAILS:
{email_list}"""
