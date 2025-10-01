"""Command-line interface for git-worktree-cli."""

from typing import Optional
from enum import Enum

import typer
from typing_extensions import Annotated

from . import __version__
from .worktree import (
    WorktreeError,
    create_worktree,
    list_worktrees,
    delete_worktree,
)
from .launchers import LauncherError, handle_mode


class Mode(str, Enum):
    """Operation modes for worktree creation."""

    NONE = "none"
    TERMINAL = "terminal"
    IDE = "ide"


app = typer.Typer(
    help="git-worktree-cli: A lightweight Python CLI tool to simplify Git worktree management."
)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"git-worktree-cli version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", callback=version_callback, help="Show version and exit."
        ),
    ] = None,
):
    """git-worktree-cli: A lightweight Python CLI tool to simplify Git worktree management."""


@app.command()
def create(
    branch: Annotated[str, typer.Argument(help="Branch name to create worktree for")],
    mode: Annotated[
        Mode, typer.Option(help="Operation mode after creating worktree")
    ] = Mode.NONE,
    ide: Annotated[
        Optional[str],
        typer.Option(
            help="IDE executable name (e.g., code, pycharm, cursor). Used when mode=ide."
        ),
    ] = None,
):
    """Create a new git worktree for BRANCH.

    The worktree will be created at: ../<root_folder_name>_<branch_name>

    Examples:

        \b
        # Create worktree only
        wt create feature-x

        \b
        # Create and open in terminal
        wt create feature-x --mode terminal

        \b
        # Create and open in VS Code
        wt create feature-x --mode ide --ide code

        \b
        # Create and open in default IDE
        wt create feature-x --mode ide
    """
    try:
        worktree_path = create_worktree(branch)
        handle_mode(mode.value, worktree_path, ide)
    except (WorktreeError, LauncherError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command(name="list")
def list_cmd():
    """List all git worktrees in the repository."""
    try:
        worktrees = list_worktrees()

        if not worktrees:
            typer.echo("No worktrees found.")
            return

        # Print header
        typer.echo(f"{'PATH':<50} {'BRANCH':<30} {'COMMIT':<10}")
        typer.echo("-" * 90)

        # Print each worktree
        for wt in worktrees:
            path = wt.get("path", "N/A")
            branch = wt.get("branch", "N/A")
            commit = wt.get("commit", "N/A")
            typer.echo(f"{path:<50} {branch:<30} {commit:<10}")

    except WorktreeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def delete(
    path: Annotated[str, typer.Argument(help="Path to the worktree to delete")],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f", help="Force deletion even with uncommitted changes"
        ),
    ] = False,
):
    """Delete a git worktree at PATH.

    Examples:

        \b
        # Delete a worktree
        wt delete ../myproject_feature-x

        \b
        # Force delete worktree with uncommitted changes
        wt delete ../myproject_feature-x --force
    """
    try:
        delete_worktree(path, force)
        typer.echo(f"Worktree deleted: {path}")
    except WorktreeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
