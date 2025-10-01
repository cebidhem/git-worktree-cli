"""Command-line interface for git-worktree-cli."""

from typing import Optional

import typer
from typing_extensions import Annotated

from . import __version__
from .worktree import (
    WorktreeError,
    create_worktree,
    list_worktrees,
    delete_worktree,
)
from .launchers import LauncherError, launch_ide, launch_claude


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


@app.command(name="add")
def add(
    branch: Annotated[str, typer.Argument(help="Branch name to add worktree for")],
    ide: Annotated[
        Optional[str],
        typer.Option(
            help="IDE executable name (e.g., code, pycharm, cursor). Opens worktree in IDE."
        ),
    ] = None,
    claude: Annotated[
        bool,
        typer.Option(
            help="Start a Claude session in the new worktree. Mutually exclusive with --ide."
        ),
    ] = False,
):
    """Add a new git worktree for BRANCH.

    The worktree will be created at: ../<root_folder_name>_<branch_name>

    Examples:

        \b
        # Add worktree only
        wt add feature-x

        \b
        # Add and open in VS Code
        wt add feature-x --ide code

        \b
        # Add and start Claude session
        wt add feature-x --claude

        \b
        # Add and open in default IDE
        wt add feature-x --ide
    """
    # Check for mutually exclusive options
    if ide and claude:
        typer.echo("Error: --ide and --claude are mutually exclusive.", err=True)
        raise typer.Exit(code=1)

    try:
        worktree_path = create_worktree(branch)

        # Handle post-creation actions
        if claude:
            launch_claude(worktree_path)
        elif ide:
            launch_ide(worktree_path, ide)
        else:
            print(f"Worktree created at: {worktree_path}")

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


# Alias: ls -> list
@app.command(name="ls", hidden=True)
def ls():
    """Alias for list command."""
    list_cmd()


@app.command(name="remove")
def remove(
    path: Annotated[str, typer.Argument(help="Path to the worktree to remove")],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f", help="Force removal even with uncommitted changes"
        ),
    ] = False,
):
    """Remove a git worktree at PATH.

    Examples:

        \b
        # Remove a worktree
        wt remove ../myproject_feature-x

        \b
        # Force remove worktree with uncommitted changes
        wt remove ../myproject_feature-x --force
    """
    try:
        delete_worktree(path, force)
        typer.echo(f"Worktree removed: {path}")
    except WorktreeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


# Alias: rm -> remove
@app.command(name="rm", hidden=True)
def rm(
    path: Annotated[str, typer.Argument(help="Path to the worktree to remove")],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f", help="Force removal even with uncommitted changes"
        ),
    ] = False,
):
    """Alias for remove command."""
    remove(path, force)


if __name__ == "__main__":
    app()
