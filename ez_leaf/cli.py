"""Command-line interface for ez-leaf."""

import sys
import click
from typing import Optional

from . import __version__
from .worktree import (
    WorktreeError,
    create_worktree,
    list_worktrees,
    delete_worktree,
)
from .launchers import LauncherError, handle_mode


@click.group()
@click.version_option(version=__version__, prog_name="ez-leaf")
def main():
    """ez-leaf: A lightweight Python script to simplify Git worktree management."""
    pass


@main.command()
@click.argument("branch")
@click.option(
    "--mode",
    type=click.Choice(["none", "terminal", "ide"], case_sensitive=False),
    default="none",
    help="Operation mode after creating worktree (default: none)."
)
@click.option(
    "--ide",
    type=str,
    default=None,
    help="IDE executable name (e.g., code, pycharm, cursor). Used when mode=ide."
)
def create(branch: str, mode: str, ide: Optional[str]):
    """Create a new git worktree for BRANCH.

    The worktree will be created at: ../<root_folder_name>_<branch_name>

    Examples:

        \b
        # Create worktree only
        ez-leaf create feature-x

        \b
        # Create and open in terminal
        ez-leaf create feature-x --mode terminal

        \b
        # Create and open in VS Code
        ez-leaf create feature-x --mode ide --ide code

        \b
        # Create and open in default IDE
        ez-leaf create feature-x --mode ide
    """
    try:
        worktree_path = create_worktree(branch)
        handle_mode(mode, worktree_path, ide)
    except (WorktreeError, LauncherError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def list():
    """List all git worktrees in the repository."""
    try:
        worktrees = list_worktrees()

        if not worktrees:
            click.echo("No worktrees found.")
            return

        # Print header
        click.echo(f"{'PATH':<50} {'BRANCH':<30} {'COMMIT':<10}")
        click.echo("-" * 90)

        # Print each worktree
        for wt in worktrees:
            path = wt.get('path', 'N/A')
            branch = wt.get('branch', 'N/A')
            commit = wt.get('commit', 'N/A')
            click.echo(f"{path:<50} {branch:<30} {commit:<10}")

    except WorktreeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("path")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force deletion even with uncommitted changes."
)
def delete(path: str, force: bool):
    """Delete a git worktree at PATH.

    Examples:

        \b
        # Delete a worktree
        ez-leaf delete ../myproject_feature-x

        \b
        # Force delete worktree with uncommitted changes
        ez-leaf delete ../myproject_feature-x --force
    """
    try:
        delete_worktree(path, force)
        click.echo(f"Worktree deleted: {path}")
    except WorktreeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
