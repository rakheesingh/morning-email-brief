from datetime import datetime
from .types import Briefing, EmailSummary
from .prioritizer import get_stats

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
GRAY = "\033[90m"

PRIORITY_STYLES = {
    "urgent":    {"icon": "🔴", "label": "REPLY NOW",     "color": RED},
    "important": {"icon": "🟠", "label": "IMPORTANT",     "color": YELLOW},
    "fyi":       {"icon": "🔵", "label": "FYI",           "color": BLUE},
    "low":       {"icon": "⚪", "label": "LOW PRIORITY",  "color": GRAY},
}


def _c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


def _truncate(s: str, max_len: int) -> str:
    return s[:max_len - 1] + "…" if len(s) > max_len else s


def _format_sender(sender: str) -> str:
    import re
    match = re.match(r'^(.+?)\s*<(.+?)>', sender)
    if match:
        return match.group(1).strip('"')
    return sender.split("@")[0]


def done(msg: str):
    print(f"  {_c(GREEN, '✓')} {msg}")


def error(msg: str):
    print(f"  {_c(RED, '✗')} {msg}")


def render_briefing(briefing: Briefing) -> str:
    if not briefing.summaries:
        return "\n  📭 No emails to show.\n"

    stats = get_stats(briefing.summaries)

    try:
        dt = datetime.fromisoformat(briefing.created_at.replace("Z", "+00:00"))
        date_str = dt.strftime("%A, %B %d, %Y at %I:%M %p")
    except Exception:
        date_str = briefing.created_at

    urgent = stats["urgent"]
    important = stats["important"]
    needs_reply = stats["needs_reply"]
    total = stats["total"]

    lines = [
        "",
        f"  {_c(BOLD, '📬 Morning Email Briefing')}",
        f"  {_c(GRAY, date_str)}",
        f"  {_c(GRAY, '━' * 60)}",
        "",
        f"  {_c(BOLD, str(total))} emails  │  "
        f"{_c(RED, f'{urgent} urgent')}  │  "
        f"{_c(YELLOW, f'{important} important')}  │  "
        f"{_c(MAGENTA, f'{needs_reply} need reply')}",
        "",
    ]

    groups = {"urgent": [], "important": [], "fyi": [], "low": []}
    for s in briefing.summaries:
        groups.setdefault(s.priority, []).append(s)

    idx = 1
    for priority in ("urgent", "important", "fyi", "low"):
        emails = groups.get(priority, [])
        if not emails:
            continue

        style = PRIORITY_STYLES[priority]
        label = style["label"]
        count = len(emails)
        lines.append(f"  {style['icon']} {_c(BOLD, _c(style['color'], f'{label} ({count})'))}")
        lines.append(f"  {_c(GRAY, '─' * 60)}")

        for email in emails:
            sender = _format_sender(email.sender)
            reply_tag = _c(MAGENTA, " [↩ REPLY]") if email.needs_reply else ""
            cat_tag = _c(GRAY, f" [{email.category}]")

            lines.append(f"  {_c(BOLD, f'{idx}.')} {_c(BOLD, _truncate(email.subject, 55))}")
            lines.append(f"     {_c(CYAN, sender)}{reply_tag}{cat_tag}")
            if email.summary:
                lines.append(f"     {_c(DIM, '→')} {email.summary}")
            lines.append("")
            idx += 1

    lines.append(_c(GRAY, f"  {'━' * 60}"))
    lines.append(_c(GRAY, f"  Briefing saved. Run {_c(BOLD, 'email-brief history')} to view past briefings."))
    lines.append("")

    return "\n".join(lines)


def render_history(dates: list[str]) -> str:
    if not dates:
        return "\n  No briefings found. Run email-brief to generate one.\n"

    lines = [
        "",
        _c(BOLD, "  📅 Briefing History"),
        f"  {_c(GRAY, '─' * 40)}",
    ]
    for d in dates:
        try:
            dt = datetime.strptime(d, "%Y-%m-%d")
            formatted = dt.strftime("%a, %b %d, %Y")
        except Exception:
            formatted = d
        lines.append(f"  • {formatted}  {_c(GRAY, f'({d})')}")

    lines.append("")
    return "\n".join(lines)
