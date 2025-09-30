"""Tests for launcher operations."""

import subprocess
from unittest.mock import Mock

import pytest

from wt.launchers import (
    LauncherError,
    launch_ide,
    launch_terminal,
    _launch_iterm2,
    _command_exists,
    handle_mode,
)


class TestCommandExists:
    """Tests for _command_exists helper function."""

    def test_command_exists(self, mocker):
        """Test when command exists."""
        mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        assert _command_exists("ls") is True

    def test_command_does_not_exist(self, mocker):
        """Test when command doesn't exist."""
        mocker.patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "which")
        )
        assert _command_exists("nonexistent") is False


class TestLaunchIDE:
    """Tests for launch_ide function."""

    def test_launch_ide_with_executable(self, mocker, tmp_path):
        """Test launching IDE with specified executable."""
        mock_exists = mocker.patch("wt.launchers._command_exists", return_value=True)
        mock_run = mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        mock_print = mocker.patch("builtins.print")

        launch_ide(tmp_path, "code")

        mock_exists.assert_called_once_with("code")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["code", str(tmp_path)]
        mock_print.assert_called_once()

    def test_launch_ide_auto_detect(self, mocker, tmp_path):
        """Test launching IDE with auto-detection."""

        def command_exists_side_effect(cmd):
            return cmd == "cursor"

        mocker.patch(
            "wt.launchers._command_exists", side_effect=command_exists_side_effect
        )
        mock_run = mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        mocker.patch("builtins.print")

        launch_ide(tmp_path, None)

        # Should have found and used 'cursor'
        args = mock_run.call_args[0][0]
        assert args[0] == "cursor"

    def test_launch_ide_no_default_found(self, mocker, tmp_path):
        """Test launching IDE when no default is found."""
        mocker.patch("wt.launchers._command_exists", return_value=False)

        with pytest.raises(LauncherError, match="No IDE specified"):
            launch_ide(tmp_path, None)

    def test_launch_ide_not_found(self, mocker, tmp_path):
        """Test launching IDE when executable doesn't exist."""
        mocker.patch("wt.launchers._command_exists", return_value=False)

        with pytest.raises(LauncherError, match="not found"):
            launch_ide(tmp_path, "nonexistent")

    def test_launch_ide_failure(self, mocker, tmp_path):
        """Test launching IDE when command fails."""
        mocker.patch("wt.launchers._command_exists", return_value=True)
        mocker.patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "code")
        )

        with pytest.raises(LauncherError, match="Failed to launch IDE"):
            launch_ide(tmp_path, "code")


class TestLaunchTerminal:
    """Tests for launch_terminal function."""

    def test_launch_terminal_macos(self, mocker, tmp_path):
        """Test launching terminal on macOS."""
        mocker.patch("platform.system", return_value="Darwin")
        mock_launch_iterm2 = mocker.patch("wt.launchers._launch_iterm2")

        launch_terminal(tmp_path)

        mock_launch_iterm2.assert_called_once_with(tmp_path)

    def test_launch_terminal_unsupported_platform(self, mocker, tmp_path):
        """Test launching terminal on unsupported platform."""
        mocker.patch("platform.system", return_value="Windows")

        with pytest.raises(LauncherError, match="not supported on Windows"):
            launch_terminal(tmp_path)


class TestLaunchITerm2:
    """Tests for _launch_iterm2 function."""

    def test_launch_iterm2_success(self, mocker, tmp_path):
        """Test launching iTerm2 successfully."""
        mock_run = mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        mock_print = mocker.patch("builtins.print")

        _launch_iterm2(tmp_path)

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "osascript"
        assert str(tmp_path) in args[2]
        mock_print.assert_called_once()

    def test_launch_iterm2_failure(self, mocker, tmp_path):
        """Test launching iTerm2 when command fails."""
        mocker.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "osascript", stderr="error"),
        )

        with pytest.raises(LauncherError, match="Failed to launch iTerm2"):
            _launch_iterm2(tmp_path)


class TestHandleMode:
    """Tests for handle_mode function."""

    def test_handle_mode_none(self, mocker, tmp_path):
        """Test handle_mode with mode='none'."""
        mock_print = mocker.patch("builtins.print")

        handle_mode("none", tmp_path)

        mock_print.assert_called_once()
        assert "Worktree created at" in mock_print.call_args[0][0]

    def test_handle_mode_terminal(self, mocker, tmp_path):
        """Test handle_mode with mode='terminal'."""
        mock_launch_terminal = mocker.patch("wt.launchers.launch_terminal")

        handle_mode("terminal", tmp_path)

        mock_launch_terminal.assert_called_once_with(tmp_path)

    def test_handle_mode_ide(self, mocker, tmp_path):
        """Test handle_mode with mode='ide'."""
        mock_launch_ide = mocker.patch("wt.launchers.launch_ide")

        handle_mode("ide", tmp_path, "code")

        mock_launch_ide.assert_called_once_with(tmp_path, "code")

    def test_handle_mode_unknown(self, tmp_path):
        """Test handle_mode with unknown mode."""
        with pytest.raises(LauncherError, match="Unknown mode"):
            handle_mode("invalid", tmp_path)
