# 📬 Email Brief

**AI-powered CLI tool that reads your Gmail inbox, summarizes every email in one sentence, and tells you what to reply to first.**

Built for developers and busy professionals who get 50-100+ emails a day and miss the important ones.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AI: Groq](https://img.shields.io/badge/AI-Groq%20(free)-orange.svg)](https://console.groq.com)

---

## What It Does

```
$ email-brief

  📬 Morning Email Briefing
  Wednesday, April 8, 2026 at 10:00 AM
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  50 emails  │  1 urgent  │  5 important  │  3 need reply

  🔴 REPLY NOW (1)
  ─────────────────────────────────────────────────────
  1. Production DB migration failing — need your help
     Alex Chen [↩ REPLY] [Work]
     → Migration script throws FK constraint error on users table.
       Alex is blocked and needs your fix before 2 PM deploy.

  🟠 IMPORTANT (5)
  ─────────────────────────────────────────────────────
  2. Offer Letter — Senior Engineer at Acme Corp
     Sarah from HR [↩ REPLY] [HR]
     → Offer letter attached. Needs your signature by Friday.

  3. Sprint retro moved to 4 PM
     David Park [Meeting]
     → Calendar updated. New agenda includes Q2 planning.

  🔵 FYI (15)
  ─────────────────────────────────────────────────────
  4. UPI transaction alert — Rs.2,500 debited
     HDFC Bank [Finance]

  ⚪ LOW PRIORITY (29)
  ─────────────────────────────────────────────────────
  5. Your weekly newsletter from dev.to
     DEV Community [Newsletter]
  ...
```

### Key Features

- **Smart triage** — AI classifies each email as Urgent, Important, FYI, or Low Priority
- **AI summaries only where it matters** — urgent and important emails get detailed summaries, the rest just show subject lines (saves tokens)
- **Detects what needs a reply** — highlights emails where a real person is waiting for your response
- **Filters out noise** — charity spam, newsletters, promotions, automated alerts correctly classified as low priority
- **Works with any Gmail account** — uses Google OAuth2 (read-only access)
- **100% free** — uses Groq free tier (14,400 requests/day) + Gmail API (free)
- **Privacy-first** — emails are processed locally, never stored on any server
- **Briefing history** — past briefings saved locally in SQLite

---

## Quick Start

### Install

```bash
pip install email-brief
```

### Setup (2 minutes, one time)

```bash
# 1. Configure your free Groq API key
email-brief setup

# 2. Sign in with Google (opens browser)
email-brief login
```

### Use

```bash
email-brief              # Generate today's briefing
email-brief last         # Re-print the last briefing
email-brief history      # List past briefing dates
email-brief date 2026-04-08  # View a specific day's briefing
```

---

## How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Gmail API   │────▶│  Groq AI     │────▶│  Terminal     │
│  (read-only) │     │  (Llama 3.3) │     │  Output       │
│              │     │              │     │              │
│ Fetch 50     │     │ Step 1:      │     │ Sorted by    │
│ unread       │     │ Triage ALL   │     │ priority     │
│ emails       │     │ (cheap)      │     │              │
│              │     │              │     │ AI summaries │
│              │     │ Step 2:      │     │ only for     │
│              │     │ Summarize    │     │ urgent +     │
│              │     │ important    │     │ important    │
│              │     │ only (smart) │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 2-Step AI Processing (saves 70% tokens)

1. **Triage** — classifies all 50 emails using only subject + snippet (cheap, fast)
2. **Summarize** — writes detailed summaries only for urgent + important emails (5-10 emails, not 50)

FYI and Low Priority emails just show the original snippet — no AI call needed.

---

## Getting API Keys (free)

### Groq API Key (required)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (Google or GitHub)
3. API Keys → Create API Key → copy it
4. Free tier: 14,400 requests/day — more than enough

### Gmail Access

Run `email-brief login` — opens your browser for Google sign-in. Read-only access, we never send or modify emails.

---

## Configuration

All config is stored in `~/.email-brief/.env`:

```bash
GROQ_API_KEY=gsk_xxxxx        # Required: free from console.groq.com
GMAIL_CLIENT_ID=xxxxx          # Set by auth server
GMAIL_CLIENT_SECRET=xxxxx      # Set by auth server
AUTH_SERVER_URL=https://...    # Auth server for Google sign-in
BRIEFING_TIME=10:00            # Daily schedule (for watch mode)
EMAIL_COUNT=50                 # Number of emails to fetch
```

---

## Project Structure

```
email-brief/
├── cli/                       # Python CLI tool (pip installable)
│   ├── email_brief/
│   │   ├── main.py            # CLI entry point
│   │   ├── gmail_client.py    # Gmail API + OAuth
│   │   ├── summarizer.py      # Groq/Gemini AI engine
│   │   ├── prompts.py         # AI prompt templates
│   │   ├── prioritizer.py     # Priority sorting
│   │   ├── renderer.py        # Terminal output (colors, formatting)
│   │   ├── storage.py         # SQLite briefing history
│   │   ├── config.py          # Environment config
│   │   └── types.py           # Data models
│   └── pyproject.toml
│
└── auth-server/               # Next.js server for Google OAuth
    ├── src/app/
    │   ├── page.tsx            # Landing page
    │   ├── privacy/page.tsx    # Privacy policy
    │   ├── terms/page.tsx      # Terms of service
    │   └── api/auth/           # OAuth routes
    └── package.json
```

---

## Privacy & Security

- **Read-only access** — we only use the `gmail.readonly` scope. We cannot send, delete, or modify your emails.
- **Local processing** — your emails are processed on your machine. Email content is sent to Groq/Gemini API for summarization but never stored on any server.
- **Local storage** — OAuth tokens and briefing history are stored locally in `~/.email-brief/`. Nothing is uploaded.
- **Open source** — review every line of code to verify exactly how your data is handled.

---

## Supported AI Providers

| Provider | Model | Cost | Setup |
|---|---|---|---|
| **Groq** (default) | Llama 3.3 70B | Free (14,400 req/day) | [console.groq.com](https://console.groq.com) |
| Google Gemini | Gemini 2.0 Flash | Free (1,500 req/day) | [aistudio.google.com](https://aistudio.google.com) |

Set `GROQ_API_KEY` or `GEMINI_API_KEY` in your config. Groq is recommended (faster, higher limits).

---

## Tech Stack

- **Python 3.9+**
- **Groq** — Llama 3.3 70B for email triage and summarization
- **Gmail API** — OAuth2 read-only access
- **SQLite** — local briefing history
- **Next.js** — auth server for Google sign-in (hosted on Vercel)

---

## Roadmap

- [x] CLI tool with `pip install`
- [x] Gmail integration (OAuth2)
- [x] AI-powered triage + summarization
- [x] Smart priority scoring (Urgent → Important → FYI → Low)
- [x] 2-step AI processing (70% token savings)
- [x] Briefing history (SQLite)
- [ ] Outlook / Microsoft 365 support
- [ ] Daily email digest (get briefing in your inbox)
- [ ] Chrome extension
- [ ] Web dashboard
- [ ] Slack/Discord notifications
- [ ] Custom priority rules per user

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Clone and setup for development
git clone https://github.com/yourusername/email-brief.git
cd email-brief/cli
pip install -e .
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

**If this tool saves you time, give it a star!** ⭐
