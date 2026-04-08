# Contributing to Email Brief

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

### CLI (Python)

```bash
cd cli
pip install -e .        # Install in editable mode
email-brief help        # Verify it works
```

### Auth Server (Next.js)

```bash
cd auth-server
npm install
cp .env.example .env.local    # Add your Google OAuth credentials
npm run dev                    # Runs on localhost:3001
```

## Project Structure

- `cli/` — Python CLI tool (the main product)
- `auth-server/` — Next.js server that handles Google OAuth sign-in

## How to Contribute

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Make your changes** and test them
4. **Submit a pull request** with a clear description

## Ideas for Contributions

- **Outlook/Microsoft 365 support** — add a new email provider
- **Better AI prompts** — improve email classification accuracy
- **Slack/Discord notifications** — send briefing to messaging apps
- **Chrome extension** — browser-based interface
- **Web dashboard** — visual briefing interface
- **Tests** — add unit and integration tests
- **Docs** — improve documentation, add examples

## Code Style

- Python: follow PEP 8
- TypeScript (auth-server): follow existing style
- No unnecessary comments — code should be self-explanatory

## Reporting Issues

- Use GitHub Issues
- Include your Python version, OS, and the full error message
- Describe what you expected vs. what happened

## Questions?

Open an issue or start a discussion. We're happy to help!
