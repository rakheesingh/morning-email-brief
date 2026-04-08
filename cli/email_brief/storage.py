from __future__ import annotations
import sqlite3
from typing import Optional
from .config import DB_PATH
from .types import Briefing, EmailSummary

_conn: Optional[sqlite3.Connection] = None


def _get_db() -> sqlite3.Connection:
    global _conn
    if _conn:
        return _conn

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _conn = sqlite3.connect(str(DB_PATH))
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA journal_mode=WAL")

    _conn.executescript("""
        CREATE TABLE IF NOT EXISTS briefings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            total_emails INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS email_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            briefing_id INTEGER NOT NULL,
            email_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            subject TEXT NOT NULL,
            date TEXT NOT NULL,
            summary TEXT NOT NULL,
            priority TEXT NOT NULL,
            needs_reply INTEGER NOT NULL DEFAULT 0,
            category TEXT NOT NULL DEFAULT 'Unknown',
            FOREIGN KEY (briefing_id) REFERENCES briefings(id)
        );
        CREATE INDEX IF NOT EXISTS idx_briefings_date ON briefings(date);
    """)

    return _conn


def save_briefing(briefing: Briefing) -> int:
    db = _get_db()
    cursor = db.execute(
        "INSERT INTO briefings (date, created_at, total_emails) VALUES (?, ?, ?)",
        (briefing.date, briefing.created_at, briefing.total_emails),
    )
    briefing_id = cursor.lastrowid

    for s in briefing.summaries:
        db.execute(
            """INSERT INTO email_summaries
               (briefing_id, email_id, sender, subject, date, summary, priority, needs_reply, category)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (briefing_id, s.email_id, s.sender, s.subject, s.date,
             s.summary, s.priority, 1 if s.needs_reply else 0, s.category),
        )

    db.commit()
    return briefing_id


def _rows_to_summaries(rows) -> list[EmailSummary]:
    return [
        EmailSummary(
            email_id=r["email_id"], sender=r["sender"], subject=r["subject"],
            date=r["date"], summary=r["summary"], priority=r["priority"],
            needs_reply=bool(r["needs_reply"]), category=r["category"],
        )
        for r in rows
    ]


def get_latest_briefing() -> Briefing | None:
    db = _get_db()
    row = db.execute("SELECT * FROM briefings ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return None

    summaries = db.execute(
        """SELECT * FROM email_summaries WHERE briefing_id = ?
           ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'important' THEN 1
           WHEN 'fyi' THEN 2 WHEN 'low' THEN 3 END, needs_reply DESC""",
        (row["id"],),
    ).fetchall()

    return Briefing(
        id=row["id"], date=row["date"], created_at=row["created_at"],
        total_emails=row["total_emails"], summaries=_rows_to_summaries(summaries),
    )


def get_briefing_by_date(date: str) -> Briefing | None:
    db = _get_db()
    row = db.execute(
        "SELECT * FROM briefings WHERE date = ? ORDER BY id DESC LIMIT 1", (date,)
    ).fetchone()
    if not row:
        return None

    summaries = db.execute(
        """SELECT * FROM email_summaries WHERE briefing_id = ?
           ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'important' THEN 1
           WHEN 'fyi' THEN 2 WHEN 'low' THEN 3 END, needs_reply DESC""",
        (row["id"],),
    ).fetchall()

    return Briefing(
        id=row["id"], date=row["date"], created_at=row["created_at"],
        total_emails=row["total_emails"], summaries=_rows_to_summaries(summaries),
    )


def get_all_briefing_dates() -> list[str]:
    db = _get_db()
    rows = db.execute("SELECT DISTINCT date FROM briefings ORDER BY date DESC").fetchall()
    return [r["date"] for r in rows]
