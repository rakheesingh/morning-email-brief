import json
import re
import time

from .config import GROQ_API_KEY, GEMINI_API_KEY
from .types import RawEmail, EmailSummary
from .prompts import build_triage_prompt, build_summarize_prompt
from .prefilter import prefilter
from .renderer import done, error

MAX_RETRIES = 3


def _detect_provider() -> str:
    if GROQ_API_KEY:
        return "groq"
    if GEMINI_API_KEY:
        return "gemini"
    raise RuntimeError("No AI API key configured. Set GROQ_API_KEY or GEMINI_API_KEY.")


def _call_groq(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an email analysis assistant. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "[]"


def _call_gemini(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


def _call_with_retry(provider: str, prompt: str, label: str) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return _call_groq(prompt) if provider == "groq" else _call_gemini(prompt)
        except Exception as err:
            is_rate_limit = "429" in str(err) or "rate" in str(err).lower()

            if is_rate_limit and attempt < MAX_RETRIES:
                wait = attempt * 10
                print(f"  ⏳ Rate limited ({label}). Waiting {wait}s (attempt {attempt}/{MAX_RETRIES})...")
                time.sleep(wait)
                continue

            if is_rate_limit:
                raise RuntimeError(f"Rate limit exceeded after {MAX_RETRIES} retries. Try again in a few minutes.")
            raise
    raise RuntimeError("Exhausted retries")


def _parse_json(text: str) -> list:
    cleaned = re.sub(r"```json\n?", "", text)
    cleaned = re.sub(r"```\n?", "", cleaned).strip()
    parsed = json.loads(cleaned)

    if isinstance(parsed, list):
        return parsed
    for key in ("emails", "summaries", "results"):
        if key in parsed and isinstance(parsed[key], list):
            return parsed[key]
    for val in parsed.values():
        if isinstance(val, list):
            return val
    raise ValueError("Unexpected AI response format")


def summarize_emails(emails: list[RawEmail]) -> list[EmailSummary]:
    if not emails:
        return []

    provider = _detect_provider()
    label = "Groq (Llama 3.3 70B)" if provider == "groq" else "Gemini 2.0 Flash"
    print(f"  Using: {label}\n")

    # Step 1: Pre-filter — mark each email with needs_ai flag
    print("  Step 1: Pre-filtering...")
    filtered = prefilter(emails)

    ai_emails = [item["email"] for item in filtered if item["needs_ai"]]
    skipped = [item for item in filtered if not item["needs_ai"]]
    done(f"Pre-filtered {len(skipped)} obvious emails, {len(ai_emails)} need AI")

    # Build results list — start with pre-filtered ones
    all_summaries: list[EmailSummary] = []

    for item in skipped:
        e = item["email"]
        all_summaries.append(EmailSummary(
            email_id=e.id, sender=e.sender, subject=e.subject,
            date=e.date, summary=e.snippet, priority=item["priority"],
            needs_reply=False, category=item["category"],
        ))

    # Step 2: AI triage — only emails with needs_ai=True
    if ai_emails:
        print(f"\n  Step 2: AI triaging {len(ai_emails)} emails...")
        batch_size = 25

        for i in range(0, len(ai_emails), batch_size):
            batch = ai_emails[i : i + batch_size]
            prompt = build_triage_prompt(batch)

            try:
                text = _call_with_retry(provider, prompt, f"triage {i + 1}-{i + len(batch)}")
                parsed = _parse_json(text)

                email_map = {e.id: e for e in batch}
                for item in parsed:
                    eid = item.get("emailId", "")
                    email = email_map.get(eid)
                    all_summaries.append(EmailSummary(
                        email_id=eid,
                        sender=item.get("from", email.sender if email else ""),
                        subject=item.get("subject", email.subject if email else ""),
                        date=email.date if email else "",
                        summary="",
                        priority=item.get("priority", "low"),
                        needs_reply=item.get("needsReply", False),
                        category=item.get("category", "FY"),
                    ))
            except Exception as err:
                short = str(err)[:80]
                error(f"Triage failed: {short}")
                for email in batch:
                    all_summaries.append(EmailSummary(
                        email_id=email.id, sender=email.sender, subject=email.subject,
                        date=email.date, summary=email.snippet, priority="fyi",
                        needs_reply=False, category="FYI",
                    ))

            if i + batch_size < len(ai_emails):
                time.sleep(1)

        urgent_important = [s for s in all_summaries if s.priority in ("urgent", "important")]
        done(f"AI triaged — {len(urgent_important)} urgent/important found")

        # Step 3: Summarize only urgent + important
        if urgent_important:
            print(f"\n  Step 3: Summarizing {len(urgent_important)} emails...")

            important_ids = {s.email_id for s in urgent_important}
            important_emails = [e for e in ai_emails if e.id in important_ids]
            prompt = build_summarize_prompt(important_emails)

            try:
                text = _call_with_retry(provider, prompt, "summarize")
                results = _parse_json(text)

                summary_map = {r["emailId"]: r["summary"] for r in results if "emailId" in r}
                for s in all_summaries:
                    if s.email_id in summary_map:
                        s.summary = summary_map[s.email_id]

                done(f"Summarized {len(results)} emails")
            except Exception as err:
                short = str(err)[:80]
                error(f"Summary failed: {short}")
                email_map = {e.id: e for e in ai_emails}
                for s in urgent_important:
                    if not s.summary:
                        email = email_map.get(s.email_id)
                        s.summary = email.snippet if email else ""

    # Fill missing summaries with snippets
    email_map = {e.id: e for e in emails}
    for s in all_summaries:
        if not s.summary:
            email = email_map.get(s.email_id)
            s.summary = email.snippet if email else ""

    return all_summaries
