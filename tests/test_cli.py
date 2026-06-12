"""Tests for the CLI interface."""

import pytest
from unittest.mock import patch

from crontrans.cli import build_parser, main


class TestBuildParser:
    def test_parser_created(self):
        parser = build_parser()
        assert parser is not None

    def test_explain_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["explain", "*/5 * * * *"])
        assert args.command == "explain"
        assert args.expression == "*/5 * * * *"

    def test_generate_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["generate", "every 5 minutes"])
        assert args.command == "generate"
        assert args.description == "every 5 minutes"

    def test_version(self):
        """Test that --version returns version string."""
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["--version"])
        assert exc.value.code == 0


class TestMainExplain:
    def test_explain_every_5_minutes(self, capsys):
        test_args = ["crontrans", "explain", "*/5 * * * *"]
        with patch("sys.argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "Every 5 minutes" in captured.out

    def test_explain_daily_9am(self, capsys):
        test_args = ["crontrans", "explain", "0 9 * * *"]
        with patch("sys.argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "9:00 AM" in captured.out

    def test_explain_invalid_exits_with_code_1(self, capsys):
        test_args = ["crontrans", "explain", "invalid"]
        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err


class TestMainGenerate:
    def test_generate_every_5_minutes(self, capsys):
        test_args = ["crontrans", "generate", "every 5 minutes"]
        with patch("sys.argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "*/5 * * * *" in captured.out

    def test_generate_daily_9am(self, capsys):
        test_args = ["crontrans", "generate", "daily at 9am"]
        with patch("sys.argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "0 9 * * *" in captured.out

    def test_generate_gibberish_exits_with_code_1(self, capsys):
        test_args = ["crontrans", "generate", "purple monkey dishwasher"]
        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_generate_empty_description_from_stdin_exits_with_code_1(self, capsys):
        """When description is omitted and stdin is empty, should exit with code 1."""
        test_args = ["crontrans", "generate"]
        with patch("sys.argv", test_args), patch("sys.stdin.read", return_value=""):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
