"""Launchers for opening worktrees in IDEs or terminal."""

import platform
import subprocess
from pathlib import Path
from typing import Optional


class LauncherError(Exception):
    """Base exception for launcher operations."""


def launch_ide(worktree_path: Path, ide_executable: Optional[str] = None) -> None:
    """Launch an IDE in the worktree directory.

    Args:
        worktree_path: The path to the worktree.
        ide_executable: The IDE executable name (e.g., 'code', 'pycharm', 'cursor').
                       If None, attempts to use a default IDE.

    Raises:
        LauncherError: If launching the IDE fails.
    """
    if ide_executable is None:
        # Try to detect common IDEs
        common_ides = ["code", "cursor", "pycharm", "subl", "atom"]
        for ide in common_ides:
            if _command_exists(ide):
                ide_executable = ide
                break

        if ide_executable is None:
            raise LauncherError(
                "No IDE specified and no default IDE found. "
                "Please specify an IDE executable with --ide option."
            )

    if not _command_exists(ide_executable):
        raise LauncherError(
            f"IDE executable '{ide_executable}' not found. "
            f"Please ensure it's installed and available in PATH."
        )

    try:
        subprocess.run(
            [ide_executable, str(worktree_path)], check=True, capture_output=True
        )
        print(f"Opened {worktree_path} in {ide_executable}")
    except subprocess.CalledProcessError as e:
        raise LauncherError(f"Failed to launch IDE: {e}") from e


def launch_terminal(worktree_path: Path) -> None:
    """Launch a terminal in the worktree directory.

    Currently supports iTerm2 on macOS.

    Args:
        worktree_path: The path to the worktree.

    Raises:
        LauncherError: If launching the terminal fails or platform is not supported.
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        _launch_iterm2(worktree_path)
    else:
        raise LauncherError(
            f"Terminal launching is not supported on {system}. "
            f"Currently only macOS (iTerm2) is supported."
        )


def _launch_iterm2(worktree_path: Path) -> None:
    """Launch a new iTerm2 tab in the worktree directory.

    Args:
        worktree_path: The path to the worktree.

    Raises:
        LauncherError: If launching iTerm2 fails.
    """
    # AppleScript to open a new iTerm2 tab and cd to the worktree path
    applescript = f"""
    tell application "iTerm"
        tell current window
            create tab with default profile
            tell current session
                write text "cd {worktree_path}"
            end tell
        end tell
    end tell
    """

    try:
        subprocess.run(
            ["osascript", "-e", applescript], check=True, capture_output=True, text=True
        )
        print(f"Opened new iTerm2 tab at {worktree_path}")
    except subprocess.CalledProcessError as e:
        raise LauncherError(f"Failed to launch iTerm2: {e.stderr}") from e


def _command_exists(command: str) -> bool:
    """Check if a command exists in PATH.

    Args:
        command: The command name to check.

    Returns:
        bool: True if command exists, False otherwise.
    """
    try:
        subprocess.run(["which", command], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def handle_mode(
    mode: str, worktree_path: Path, ide_executable: Optional[str] = None
) -> None:
    """Handle the specified mode after worktree creation.

    Args:
        mode: The mode ('none', 'terminal', or 'ide').
        worktree_path: The path to the created worktree.
        ide_executable: Optional IDE executable name (used when mode='ide').

    Raises:
        LauncherError: If mode handling fails.
    """
    if mode == "none":
        # Do nothing, just print the path
        print(f"Worktree created at: {worktree_path}")
    elif mode == "terminal":
        launch_terminal(worktree_path)
    elif mode == "ide":
        launch_ide(worktree_path, ide_executable)
    else:
        raise LauncherError(f"Unknown mode: {mode}")
