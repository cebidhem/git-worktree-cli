"""git-worktree-cli: A lightweight Python CLI tool to simplify Git worktree management."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("git-worktree-cli")
except PackageNotFoundError:
    # Package not installed, running from source
    __version__ = "dev"
