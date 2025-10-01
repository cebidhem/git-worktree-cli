"""Tests for CLI commands."""

import re
from pathlib import Path

from typer.testing import CliRunner

from wt.cli import app
from wt.worktree import WorktreeError
from wt.launchers import LauncherError


def strip_ansi(text):
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


runner = CliRunner()


class TestCLIVersion:
    """Tests for version command."""

    def test_version_option(self):
        """Test --version option."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "git-worktree-cli version" in result.stdout


class TestCLICreate:
    """Tests for create command."""

    def test_create_worktree_default(self, mocker):
        """Test creating worktree without any flags."""
        mock_create = mocker.patch(
            "wt.cli.create_worktree", return_value=Path("/path/to/worktree")
        )
        mock_print = mocker.patch("builtins.print")

        result = runner.invoke(app, ["create", "feature-x"])

        assert result.exit_code == 0
        mock_create.assert_called_once_with("feature-x")
        mock_print.assert_called_once_with("Worktree created at: /path/to/worktree")

    def test_create_worktree_with_ide(self, mocker):
        """Test creating worktree with --ide flag."""
        mocker.patch("wt.cli.create_worktree", return_value=Path("/path/to/worktree"))
        mock_launch_ide = mocker.patch("wt.cli.launch_ide")

        result = runner.invoke(app, ["create", "feature-x", "--ide", "code"])

        assert result.exit_code == 0
        mock_launch_ide.assert_called_once_with(Path("/path/to/worktree"), "code")

    def test_create_worktree_with_claude(self, mocker):
        """Test creating worktree with --claude flag."""
        mocker.patch("wt.cli.create_worktree", return_value=Path("/path/to/worktree"))
        mock_launch_claude = mocker.patch("wt.cli.launch_claude")

        result = runner.invoke(app, ["create", "feature-x", "--claude"])

        assert result.exit_code == 0
        mock_launch_claude.assert_called_once_with(Path("/path/to/worktree"))

    def test_create_worktree_ide_and_claude_exclusive(self, mocker):
        """Test that --ide and --claude are mutually exclusive."""
        mock_echo = mocker.patch("typer.echo")
        mocker.patch("wt.cli.create_worktree", return_value=Path("/path/to/worktree"))

        result = runner.invoke(
            app, ["create", "feature-x", "--ide", "code", "--claude"]
        )

        assert result.exit_code == 1
        # Verify error message was echoed
        mock_echo.assert_called()
        error_call = [
            call
            for call in mock_echo.call_args_list
            if "mutually exclusive" in str(call)
        ]
        assert len(error_call) > 0

    def test_create_worktree_error(self, mocker):
        """Test creating worktree when WorktreeError occurs."""
        mock_echo = mocker.patch("typer.echo")
        mocker.patch("wt.cli.create_worktree", side_effect=WorktreeError("Test error"))

        result = runner.invoke(app, ["create", "feature-x"])

        assert result.exit_code == 1
        # Verify error message was echoed
        mock_echo.assert_called()
        error_call = [
            call
            for call in mock_echo.call_args_list
            if "Error: Test error" in str(call)
        ]
        assert len(error_call) > 0

    def test_create_worktree_launcher_error(self, mocker):
        """Test creating worktree when LauncherError occurs."""
        mock_echo = mocker.patch("typer.echo")
        mocker.patch("wt.cli.create_worktree", return_value=Path("/path/to/worktree"))
        mocker.patch("wt.cli.launch_ide", side_effect=LauncherError("Launcher error"))

        result = runner.invoke(app, ["create", "feature-x", "--ide", "code"])

        assert result.exit_code == 1
        # Verify error message was echoed
        mock_echo.assert_called()
        error_call = [
            call
            for call in mock_echo.call_args_list
            if "Error: Launcher error" in str(call)
        ]
        assert len(error_call) > 0


class TestCLIList:
    """Tests for list command."""

    def test_list_worktrees_with_results(self, mocker):
        """Test listing worktrees with results."""
        mocker.patch(
            "wt.cli.list_worktrees",
            return_value=[
                {"path": "/path/to/main", "branch": "main", "commit": "abc1234"},
                {
                    "path": "/path/to/feature",
                    "branch": "feature-x",
                    "commit": "def5678",
                },
            ],
        )

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "/path/to/main" in result.stdout
        assert "main" in result.stdout
        assert "abc1234" in result.stdout
        assert "/path/to/feature" in result.stdout
        assert "feature-x" in result.stdout

    def test_list_worktrees_empty(self, mocker):
        """Test listing worktrees when none exist."""
        mocker.patch("wt.cli.list_worktrees", return_value=[])

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No worktrees found" in result.stdout

    def test_list_worktrees_error(self, mocker):
        """Test listing worktrees when error occurs."""
        mock_echo = mocker.patch("typer.echo")
        mocker.patch("wt.cli.list_worktrees", side_effect=WorktreeError("List error"))

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        # Verify error message was echoed
        mock_echo.assert_called()
        error_call = [
            call
            for call in mock_echo.call_args_list
            if "Error: List error" in str(call)
        ]
        assert len(error_call) > 0


class TestCLIDelete:
    """Tests for delete command."""

    def test_delete_worktree(self, mocker):
        """Test deleting worktree."""
        mock_delete = mocker.patch("wt.cli.delete_worktree")

        result = runner.invoke(app, ["delete", "/path/to/worktree"])

        assert result.exit_code == 0
        mock_delete.assert_called_once_with("/path/to/worktree", False)
        assert "Worktree deleted: /path/to/worktree" in result.stdout

    def test_delete_worktree_force(self, mocker):
        """Test deleting worktree with force flag."""
        mock_delete = mocker.patch("wt.cli.delete_worktree")

        result = runner.invoke(app, ["delete", "/path/to/worktree", "--force"])

        assert result.exit_code == 0
        mock_delete.assert_called_once_with("/path/to/worktree", True)

    def test_delete_worktree_error(self, mocker):
        """Test deleting worktree when error occurs."""
        mock_echo = mocker.patch("typer.echo")
        mocker.patch(
            "wt.cli.delete_worktree", side_effect=WorktreeError("Delete error")
        )

        result = runner.invoke(app, ["delete", "/path/to/worktree"])

        assert result.exit_code == 1
        # Verify error message was echoed
        mock_echo.assert_called()
        error_call = [
            call
            for call in mock_echo.call_args_list
            if "Error: Delete error" in str(call)
        ]
        assert len(error_call) > 0


class TestCLIHelp:
    """Tests for help command."""

    def test_main_help(self):
        """Test main help command."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "git-worktree-cli" in result.stdout
        assert "create" in result.stdout
        assert "list" in result.stdout
        assert "delete" in result.stdout

    def test_create_help(self):
        """Test create command help."""
        result = runner.invoke(app, ["create", "--help"])
        output = strip_ansi(result.stdout)

        assert result.exit_code == 0
        assert "Create a new git worktree" in output
        assert "--ide" in output
        assert "--claude" in output

    def test_list_help(self):
        """Test list command help."""
        result = runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "List all git worktrees" in result.stdout

    def test_delete_help(self):
        """Test delete command help."""
        result = runner.invoke(app, ["delete", "--help"])
        output = strip_ansi(result.stdout)

        assert result.exit_code == 0
        assert "Delete a git worktree" in output
        assert "--force" in output
