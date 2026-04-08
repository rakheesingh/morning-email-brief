from .types import EmailSummary, PriorityLevel

PRIORITY_ORDER = {"urgent": 0, "important": 1, "fyi": 2, "low": 3}


def sort_by_priority(summaries: list[EmailSummary]) -> list[EmailSummary]:
    def sort_key(s: EmailSummary):
        return (
            PRIORITY_ORDER.get(s.priority, 3),
            0 if s.needs_reply else 1,
        )
    return sorted(summaries, key=sort_key)


def group_by_priority(summaries: list[EmailSummary]) -> dict[str, list[EmailSummary]]:
    groups: dict[str, list[EmailSummary]] = {
        "urgent": [], "important": [], "fyi": [], "low": [],
    }
    for s in summaries:
        groups.setdefault(s.priority, []).append(s)
    return groups


def get_stats(summaries: list[EmailSummary]) -> dict:
    groups = group_by_priority(summaries)
    return {
        "total": len(summaries),
        "urgent": len(groups["urgent"]),
        "important": len(groups["important"]),
        "fyi": len(groups["fyi"]),
        "low": len(groups["low"]),
        "needs_reply": sum(1 for s in summaries if s.needs_reply),
    }
