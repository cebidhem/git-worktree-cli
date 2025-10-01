"""Core git worktree operations."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional


class WorktreeError(Exception):
    """Base exception for worktree operations."""


def check_git_repo() -> None:
    """Check if the current directory is a git repository.

    Raises:
        WorktreeError: If not in a git repository.
    """
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise WorktreeError(
            "Not a git repository. Please run git-worktree-cli from within a git repository."
        ) from e


def get_repo_root() -> Path:
    """Get the root directory of the git repository.

    Returns:
        Path: The absolute path to the repository root.

    Raises:
        WorktreeError: If not in a git repository.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise WorktreeError(f"Failed to get repository root: {e.stderr}") from e


def get_root_folder_name() -> str:
    """Get the name of the root folder.

    Returns:
        str: The name of the root folder.
    """
    return get_repo_root().name


def generate_worktree_path(branch: str) -> Path:
    """Generate the worktree path based on branch name.

    Path format: ../<root_folder_name>_<branch_name>

    Args:
        branch: The branch name.

    Returns:
        Path: The absolute path for the new worktree.
    """
    root_folder_name = get_root_folder_name()
    repo_root = get_repo_root()
    parent_dir = repo_root.parent

    worktree_name = f"{root_folder_name}_{branch}"
    return parent_dir / worktree_name


def branch_exists(branch: str) -> bool:
    """Check if a branch exists locally or remotely.

    Args:
        branch: The branch name to check.

    Returns:
        bool: True if the branch exists, False otherwise.
    """
    try:
        # Check local branches
        subprocess.run(
            ["git", "rev-parse", "--verify", branch],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        # Check remote branches
        try:
            subprocess.run(
                ["git", "rev-parse", "--verify", f"origin/{branch}"],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False


def copy_claude_settings(worktree_path: Path) -> None:
    """Copy Claude settings from repository root to new worktree.

    Copies .claude/settings.local.json if it exists in the repository root.

    Args:
        worktree_path: The path to the worktree.
    """
    repo_root = get_repo_root()
    source_settings = repo_root / ".claude" / "settings.local.json"

    if source_settings.exists():
        target_claude_dir = worktree_path / ".claude"
        target_claude_dir.mkdir(parents=True, exist_ok=True)

        target_settings = target_claude_dir / "settings.local.json"
        shutil.copy2(source_settings, target_settings)
        print(f"Copied Claude settings to {target_settings}")


def create_worktree(branch: str, path: Optional[Path] = None) -> Path:
    """Create a new git worktree.

    Args:
        branch: The branch name to create/checkout.
        path: Optional custom path for the worktree. If None, generates path automatically.

    Returns:
        Path: The absolute path to the created worktree.

    Raises:
        WorktreeError: If worktree creation fails.
    """
    check_git_repo()

    if path is None:
        path = generate_worktree_path(branch)

    # Check if worktree path already exists
    if path.exists():
        raise WorktreeError(f"Path already exists: {path}")

    try:
        # If branch exists, checkout to it; otherwise create new branch
        if branch_exists(branch):
            subprocess.run(
                ["git", "worktree", "add", str(path), branch],
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            # Create new branch with -b flag
            subprocess.run(
                ["git", "worktree", "add", "-b", branch, str(path)],
                check=True,
                capture_output=True,
                text=True,
            )

        # Copy Claude settings if they exist
        copy_claude_settings(path)

        return path.absolute()
    except subprocess.CalledProcessError as e:
        raise WorktreeError(f"Failed to create worktree: {e.stderr}") from e


def list_worktrees() -> list[dict[str, str]]:
    """List all git worktrees.

    Returns:
        list: A list of dictionaries containing worktree information.
              Each dict has keys: 'path', 'branch', 'commit'.

    Raises:
        WorktreeError: If listing worktrees fails.
    """
    check_git_repo()

    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )

        worktrees = []
        current_worktree = {}

        for line in result.stdout.strip().split("\n"):
            if line.startswith("worktree "):
                current_worktree["path"] = line.split(" ", 1)[1]
            elif line.startswith("HEAD "):
                current_worktree["commit"] = line.split(" ", 1)[1][
                    :7
                ]  # Short commit hash
            elif line.startswith("branch "):
                current_worktree["branch"] = line.split("/")[
                    -1
                ]  # Get branch name from refs/heads/branch
            elif line == "" and current_worktree:
                worktrees.append(current_worktree)
                current_worktree = {}

        # Add the last worktree if exists
        if current_worktree:
            worktrees.append(current_worktree)

        return worktrees
    except subprocess.CalledProcessError as e:
        raise WorktreeError(f"Failed to list worktrees: {e.stderr}") from e


def delete_worktree(path: str, force: bool = False) -> None:
    """Delete a git worktree.

    Args:
        path: The path to the worktree to delete.
        force: If True, force deletion even with uncommitted changes.

    Raises:
        WorktreeError: If worktree deletion fails.
    """
    check_git_repo()

    try:
        cmd = ["git", "worktree", "remove", path]
        if force:
            cmd.append("--force")

        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise WorktreeError(f"Failed to delete worktree: {e.stderr}") from e
