# ⏰ crontrans

**Bidirectional cron expression translator — explain cryptic schedules or generate them from plain English.**

```bash
crontrans explain "*/15 * * * 1-5"
# → Every 15 minutes, Monday through Friday

crontrans generate "daily at 3:30 PM"
# → 30 15 * * *
```

---

## 🤖 Fully Vibecoded with Hermes Agent

This project was built entirely through natural language conversations with [Hermes Agent](https://hermes-agent.nousresearch.com) — an autonomous AI coding assistant. From architecture to deployment, every line of code was generated, tested, and shipped via chat prompts.

---

## ✨ Features

- **🔁 Bidirectional** — Both `explain` (cron → English) and `generate` (English → cron)
- **🔍 Precise Human Output** — "Every 5 minutes", "At 9:00 AM, Monday through Friday", "At 4:30 AM, only on Monday, Wednesday, and Friday"
- **🗣️ Natural Language Input** — "daily at 9am", "weekdays at 3:30 PM", "every 30 minutes", "on the 1st of every month"
- **📥 stdin Support** — Pipe descriptions: `echo "every 30 minutes" | crontrans generate`
- **⚠️ Clear Errors** — Invalid expressions get specific field-level error messages on stderr
- **🚦 Proper Exit Codes** — 0 success, 1 user error, 2 crash
- **📦 pip-Installable** — `pip install crontrans`

---

## 🛠️ Tech Stack

| Layer        | Technology      |
|-------------|-----------------|
| Runtime     | Python 3.9+     |
| CLI         | argparse (stdlib)|
| Testing     | pytest          |
| Packaging   | pyproject.toml / pip |

---

## 🚀 Install & Usage

### Install

```bash
pip install crontrans
```

Or from source:

```bash
git clone https://github.com/kvnlnk/crontrans.git
cd crontrans
pip install -e .
```

### Explain mode — turn cron into English

```bash
# Basic
crontrans explain "*/5 * * * *"
# → "Every 5 minutes"

# Specific time on weekdays
crontrans explain "0 9 * * 1-5"
# → "At 9:00 AM, Monday through Friday"

# Multiple specific days
crontrans explain "30 4 * * 1,3,5"
# → "At 4:30 AM, only on Monday, Wednesday, and Friday"

# Monthly with month specified
crontrans explain "0 0 1 1 *"
# → "At 12:00 AM, on day 1 of the month, only in January"
```

### Generate mode — describe a schedule

```bash
# Every N minutes
crontrans generate "every 30 minutes"
# → */30 * * * *

# Daily at a specific time
crontrans generate "daily at 9am"
# → 0 9 * * *

# With minutes
crontrans generate "weekdays at 3:30 PM"
# → 30 15 * * 1-5

# Once a month
crontrans generate "on the 1st at midnight"
# → 0 0 1 * *

# Short form
crontrans generate "every hour"
# → 0 * * * *

# Pipe from another command
echo "every 5 minutes" | crontrans generate
# → */5 * * * *

# Full help
crontrans --help
crontrans explain --help
crontrans generate --help
```

---

## 📁 Project Structure

```
crontrans/
├── crontrans/
│   ├── __init__.py        # Package init, VERSION
│   ├── __main__.py        # python -m crontrans entry
│   ├── cli.py             # argparse subcommands, exit codes
│   ├── constants.py       # Field ranges, day/month names
│   ├── parser.py          # 5-field cron tokenizer
│   ├── explain.py         # Cron → English translation
│   ├── generate.py        # English → Cron translation
│   └── templates.py       # NL keyword → cron component mapping
├── tests/
│   ├── test_parser.py     # Parser tests
│   ├── test_explain.py    # Explain mode tests
│   ├── test_generate.py   # Generate mode tests
│   └── test_cli.py        # CLI integration tests
├── pyproject.toml
└── README.md
```

---

## 🧪 Tests

```bash
python3 -m pytest tests/ -v
```

- **168 tests** across 4 suites
- Parser (all field types: `*`, `*/N`, `N-M`, `N,M`, `N`)
- Explain (every X, specific times, ranges, ordinals, months)
- Generate (all common NL patterns, roundtrip testing)
- CLI (exit codes, stdin piping, --help, --version)

---

## 📄 License

MIT

---

<p align="center">Made with ❤️ by <a href="https://github.com/kvnlnk">kvnlnk</a></p>
