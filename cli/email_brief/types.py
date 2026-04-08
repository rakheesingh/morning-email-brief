from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional

PriorityLevel = Literal["urgent", "important", "fyi", "low"]


@dataclass
class RawEmail:
    id: str
    thread_id: str
    sender: str
    to: str
    subject: str
    date: str
    snippet: str
    body: str
    labels: list[str] = field(default_factory=list)
    is_unread: bool = False


@dataclass
class EmailSummary:
    email_id: str
    sender: str
    subject: str
    date: str
    summary: str
    priority: PriorityLevel
    needs_reply: bool
    category: str


@dataclass
class Briefing:
    id: Optional[int]
    date: str
    created_at: str
    total_emails: int
    summaries: list[EmailSummary]
