# crontrans — Architecture

## Type
Python CLI tool (pip-installable)

## Target User
Developers, DevOps engineers, and system administrators who work with cron jobs and need to read, write, or audit cron schedules.

## Value Proposition
Bidirectional translation between cron expressions and plain English — explain what a cryptic `*/15 * * * 1-5` does, or generate the correct expression from a natural language description. Reduces errors from manual cron string construction.

## Tech Stack + Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Runtime | Python 3.9+ | Universal; cron-native ecosystem |
| CLI framework | argparse (stdlib) | No dependencies; sufficient for a two-mode tool |
| Parsing | Manual regex + cron formula | No external lib needed; cron format is fixed and small |
| NLP (generate) | Template-based | Cron space is small (~30 common patterns); no need for LLM |
| Testing | pytest | Standard for Python projects |
| Package mgr | pip / PyPI | Standard Python distribution |

## Folder Structure

```
crontrans/
├── crontrans/
│   ├── __init__.py         # Package init, version
│   ├── __main__.py         # python -m crontrans entry
│   ├── cli.py              # argparse definition, mode routing
│   ├── explain.py          # Cron → English translation
│   ├── generate.py         # English → Cron translation
│   ├── parser.py           # Shared cron expression parser / tokenizer
│   ├── templates.py        # NL templates for generate mode
│   └── constants.py        # Field ranges, day names, month names
├── tests/
│   ├── test_explain.py
│   ├── test_generate.py
│   └── test_parser.py
├── setup.py / pyproject.toml
├── .gitignore
├── .env.example
├── README.md
└── ARCHITECTURE.md
```

## Data Flow

```
### Mode 1: Explain (Cron → English)

 cli.py ──►  parser.py ──►  explain.py ──►  stdout
   │            │               │
   │  args      │  tokenized    │  English sentence
   │  "*/5 *    │  {min, hour,  │  "Every 5 minutes"
   │   * * *"   │   dom, mon,   │
   │            │   dow}        │
   ▼            ▼               ▼
 argparse    regex/math     template fill
```

```
### Mode 2: Generate (English → Cron)

 cli.py ──►  generate.py ──►  parser.py ──►  stdout
   │            │                │
   │  args      │  tokenized NL  │  formatted cron
   │  "every    │  {min, hour,   │  "*/5 * * * *"
   │   day at   │   dom, mon,    │
   │   3am"     │   dow}         │
   ▼            ▼                ▼
 argparse    keyword match    field formatter
```

## Key Design Decisions

1. **Bidirectional in one tool** — Single CLI with `explain` and `generate` subcommands via argparse subparsers. Keeps UX simple: `crontrans explain "*/5 * * * *"` or `crontrans generate "every 5 minutes"`.
2. **Template-based NL generation** — Cron's expression space is finite and well-defined (~30 common patterns). A lookup table maps keywords ("every", "at", "daily", "weekdays") to cron components. No NLP library needed.
3. **Cron parsing via field math** — Each of the 5 fields is parsed independently: minute matches `*/N` (every N), `N-M` (range), `N,M` (list), `*` (all). The parser returns a named tuple for clean downstream use.
4. **Explain uses deterministic rules** — No ambiguity: `0 9 * * 1-5` always produces "At 9:00 AM, Monday through Friday". Rules are in order of specificity (exact > range > step > wildcard).
5. **Error-first design** — Invalid cron expressions and unrecognized NL patterns produce specific error messages indicating which field failed and why, rather than a generic parse error.

## Estimated Time Budget

| Area | Estimate |
|------|----------|
| CLI scaffolding (argparse subcommands) | 0.5h |
| Cron parser (5-field tokenizer) | 1.5h |
| Explain mode (cron → English templates) | 2h |
| Generate mode (English → cron matching) | 2h |
| Edge cases / validation / error messages | 1.5h |
| Tests | 1.5h |
| Packaging (pyproject.toml) | 0.5h |
| **Total** | **~9.5h** |
