"""Launchers for opening worktrees in IDEs or terminal."""

import platform
import shlex
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

    Supports iTerm2 on macOS and common terminals on Linux.

    Args:
        worktree_path: The path to the worktree.

    Raises:
        LauncherError: If launching the terminal fails or platform is not supported.
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        _launch_iterm2(worktree_path)
    elif system == "Linux":
        _launch_linux_terminal(worktree_path)
    else:
        raise LauncherError(
            f"Terminal launching is not supported on {system}. "
            f"Currently only macOS and Linux are supported."
        )


def _launch_iterm2(worktree_path: Path, command: Optional[str] = None) -> None:
    """Launch a new iTerm2 tab in the worktree directory.

    Args:
        worktree_path: The path to the worktree.
        command: Optional command to run after cd. If None, just opens terminal.

    Raises:
        LauncherError: If launching iTerm2 fails.
    """
    # Build commands to execute with proper shell escaping
    quoted_path = shlex.quote(str(worktree_path))
    commands = [f"cd {quoted_path}"]
    if command:
        # Don't quote command here - iTerm's "write text" types literally into shell
        # The command value is controlled by our code (e.g., "claude"), not user input
        commands.append(command)

    # Join commands and escape for AppleScript string context
    shell_command = "; ".join(commands)
    # Escape backslashes and quotes for AppleScript string
    escaped_command = shell_command.replace("\\", "\\\\").replace('"', '\\"')

    # AppleScript to open a new iTerm2 tab and execute commands
    applescript = f"""
    tell application "iTerm"
        tell current window
            create tab with default profile
            tell current session
                write text "{escaped_command}"
            end tell
        end tell
    end tell
    """

    try:
        subprocess.run(
            ["osascript", "-e", applescript], check=True, capture_output=True, text=True
        )
        action = "Started Claude session" if command else "Opened new iTerm2 tab"
        print(f"{action} at {worktree_path}")
    except subprocess.CalledProcessError as e:
        raise LauncherError(f"Failed to launch iTerm2: {e.stderr}") from e


def _launch_linux_terminal(worktree_path: Path, command: Optional[str] = None) -> None:
    """Launch a new terminal tab/window in the worktree directory on Linux.

    Args:
        worktree_path: The path to the worktree.
        command: Optional command to run after cd. If None, just opens terminal.

    Raises:
        LauncherError: If launching terminal fails.
    """
    # Properly escape path and command for shell
    quoted_path = shlex.quote(str(worktree_path))

    # Try common Linux terminals in order of preference
    terminals = [
        ("gnome-terminal", ["--tab", "--working-directory", str(worktree_path)]),
        ("konsole", ["--new-tab", "--workdir", str(worktree_path)]),
        ("xfce4-terminal", ["--tab", "--working-directory", str(worktree_path)]),
        ("xterm", ["-e", "bash", "-c", f"cd {quoted_path} && bash"]),
    ]

    if command:
        # If command is provided, we need to execute it after cd
        quoted_command = shlex.quote(command)
        bash_cmd = f"cd {quoted_path} && {quoted_command}"

        terminals = [
            ("gnome-terminal", ["--tab", "--", "bash", "-c", bash_cmd]),
            ("konsole", ["--new-tab", "-e", "bash", "-c", bash_cmd]),
            ("xfce4-terminal", ["--tab", "-e", "bash", "-c", bash_cmd]),
            ("xterm", ["-e", "bash", "-c", bash_cmd]),
        ]

    for terminal, args in terminals:
        if _command_exists(terminal):
            try:
                subprocess.run(
                    [terminal] + args,
                    check=True,
                    capture_output=True,
                )
                action = (
                    "Started Claude session" if command else "Opened new terminal tab"
                )
                print(f"{action} at {worktree_path}")
                return
            except subprocess.CalledProcessError:
                continue

    raise LauncherError(
        "No supported terminal found. "
        "Please install gnome-terminal, konsole, xfce4-terminal, or xterm."
    )


def launch_claude(worktree_path: Path) -> None:
    """Launch a Claude session in the worktree directory.

    Opens a new terminal tab/window and starts a Claude session.
    Supports iTerm2 on macOS and common terminals on Linux.

    Args:
        worktree_path: The path to the worktree.

    Raises:
        LauncherError: If launching Claude fails or platform is not supported.
    """
    # Check if claude command exists
    if not _command_exists("claude"):
        raise LauncherError(
            "Claude CLI not found. "
            "Please install it from https://github.com/anthropics/claude-code"
        )

    system = platform.system()

    if system == "Darwin":  # macOS
        _launch_iterm2(worktree_path, command="claude")
    elif system == "Linux":
        _launch_linux_terminal(worktree_path, command="claude")
    else:
        raise LauncherError(
            f"Claude launching is not supported on {system}. "
            f"Currently only macOS and Linux are supported."
        )


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
