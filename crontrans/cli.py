"""CLI entry point for crontrans.

Defines argparse with `explain` and `generate` subcommands.
"""

import argparse
import sys

from . import VERSION
from .explain import explain_cron
from .generate import generate_cron


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="crontrans",
        description="Bidirectional cron expression translator — "
                    "explain cron to English or generate cron from English.",
        epilog="Examples:\n"
               "  crontrans explain \"*/5 * * * *\"\n"
               "  crontrans generate \"every 5 minutes\"\n"
               "  crontrans generate \"daily at 9am\"\n"
               "  crontrans generate \"weekdays at 3:30 PM\"",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"crontrans {VERSION}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands",
    )

    # explain subcommand
    explain_parser = subparsers.add_parser(
        "explain",
        help="Translate a cron expression to plain English",
        description="Translate a 5-field cron expression into a human-readable "
                    "English description of the schedule.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    explain_parser.add_argument(
        "expression",
        type=str,
        help="Cron expression (5 fields: minute hour dom month dow)",
    )

    # generate subcommand
    generate_parser = subparsers.add_parser(
        "generate",
        help="Translate plain English to a cron expression",
        description="Convert a natural language schedule description into a "
                    "5-field cron expression.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    generate_parser.add_argument(
        "description",
        type=str,
        nargs="?",
        help="Natural language description (e.g., 'every 5 minutes', 'daily at 9am'). "
             "If omitted, reads from stdin.",
    )

    return parser


def main() -> None:
    """Main entry point. Parses args and dispatches to the appropriate handler."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "explain":
            result = explain_cron(args.expression)
            print(result)

        elif args.command == "generate":
            description = args.description
            if description is None:
                # Read from stdin
                description = sys.stdin.read().strip()
                if not description:
                    print("Error: No description provided (stdin was empty)", file=sys.stderr)
                    sys.exit(1)

            result = generate_cron(description)
            print(result)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
