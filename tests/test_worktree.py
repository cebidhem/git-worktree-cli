"""Tests for worktree operations."""

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from wt.worktree import (
    WorktreeError,
    check_git_repo,
    get_repo_root,
    get_root_folder_name,
    generate_worktree_path,
    branch_exists,
    create_worktree,
    list_worktrees,
    delete_worktree,
)


class TestCheckGitRepo:
    """Tests for check_git_repo function."""

    def test_valid_git_repo(self, mocker):
        """Test checking a valid git repository."""
        mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        check_git_repo()  # Should not raise

    def test_not_git_repo(self, mocker):
        """Test checking when not in a git repository."""
        mocker.patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")
        )
        with pytest.raises(WorktreeError, match="Not a git repository"):
            check_git_repo()


class TestGetRepoRoot:
    """Tests for get_repo_root function."""

    def test_get_repo_root_success(self, mocker):
        """Test getting repository root successfully."""
        mock_result = Mock()
        mock_result.stdout = "/path/to/repo\n"
        mocker.patch("subprocess.run", return_value=mock_result)

        result = get_repo_root()
        assert result == Path("/path/to/repo")

    def test_get_repo_root_failure(self, mocker):
        """Test getting repository root when command fails."""
        mocker.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git", stderr="error"),
        )
        with pytest.raises(WorktreeError, match="Failed to get repository root"):
            get_repo_root()


class TestGetRootFolderName:
    """Tests for get_root_folder_name function."""

    def test_get_root_folder_name(self, mocker):
        """Test getting root folder name."""
        mocker.patch(
            "wt.worktree.get_repo_root", return_value=Path("/path/to/myproject")
        )
        assert get_root_folder_name() == "myproject"


class TestGenerateWorktreePath:
    """Tests for generate_worktree_path function."""

    def test_generate_worktree_path(self, mocker):
        """Test generating worktree path."""
        mocker.patch(
            "wt.worktree.get_repo_root", return_value=Path("/path/to/myproject")
        )

        result = generate_worktree_path("feature-x")
        assert result == Path("/path/to/myproject_feature-x")


class TestBranchExists:
    """Tests for branch_exists function."""

    def test_local_branch_exists(self, mocker):
        """Test when local branch exists."""
        mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        assert branch_exists("main") is True

    def test_remote_branch_exists(self, mocker):
        """Test when only remote branch exists."""
        # First call (local) fails, second call (remote) succeeds
        mocker.patch(
            "subprocess.run",
            side_effect=[subprocess.CalledProcessError(1, "git"), Mock(returncode=0)],
        )
        assert branch_exists("feature-x") is True

    def test_branch_does_not_exist(self, mocker):
        """Test when branch doesn't exist."""
        mocker.patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")
        )
        assert branch_exists("nonexistent") is False


class TestCreateWorktree:
    """Tests for create_worktree function."""

    def test_create_worktree_new_branch(self, mocker):
        """Test creating worktree with a new branch."""
        mock_check_git = mocker.patch("wt.worktree.check_git_repo")
        mocker.patch(
            "wt.worktree.generate_worktree_path",
            return_value=Path("/path/to/myproject_feature-x"),
        )
        mock_branch_exists = mocker.patch(
            "wt.worktree.branch_exists", return_value=False
        )
        mock_run = mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        mock_copy_claude = mocker.patch("wt.worktree.copy_claude_settings")

        result = create_worktree("feature-x")

        assert result == Path("/path/to/myproject_feature-x").absolute()
        mock_check_git.assert_called_once()
        mock_branch_exists.assert_called_once_with("feature-x")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[:3] == ["git", "worktree", "add"]
        assert "-b" in args
        assert "feature-x" in args
        mock_copy_claude.assert_called_once()

    def test_create_worktree_existing_branch(self, mocker):
        """Test creating worktree with an existing branch."""
        mocker.patch("wt.worktree.check_git_repo")
        mocker.patch(
            "wt.worktree.generate_worktree_path",
            return_value=Path("/path/to/myproject_main"),
        )
        mocker.patch("wt.worktree.branch_exists", return_value=True)
        mock_run = mocker.patch("subprocess.run", return_value=Mock(returncode=0))
        mocker.patch("wt.worktree.copy_claude_settings")

        result = create_worktree("main")

        assert result == Path("/path/to/myproject_main").absolute()
        args = mock_run.call_args[0][0]
        assert "-b" not in args

    def test_create_worktree_path_exists(self, mocker, tmp_path):
        """Test creating worktree when path already exists."""
        mocker.patch("wt.worktree.check_git_repo")
        existing_path = tmp_path / "existing"
        existing_path.mkdir()
        mocker.patch("wt.worktree.generate_worktree_path", return_value=existing_path)

        with pytest.raises(WorktreeError, match="Path already exists"):
            create_worktree("feature-x")

    def test_create_worktree_git_failure(self, mocker):
        """Test creating worktree when git command fails."""
        mocker.patch("wt.worktree.check_git_repo")
        mocker.patch(
            "wt.worktree.generate_worktree_path",
            return_value=Path("/path/to/myproject_feature-x"),
        )
        mocker.patch("wt.worktree.branch_exists", return_value=False)
        mocker.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git", stderr="error message"),
        )

        with pytest.raises(WorktreeError, match="Failed to create worktree"):
            create_worktree("feature-x")


class TestListWorktrees:
    """Tests for list_worktrees function."""

    def test_list_worktrees_success(self, mocker):
        """Test listing worktrees successfully."""
        mocker.patch("wt.worktree.check_git_repo")
        mock_result = Mock()
        mock_result.stdout = (
            "worktree /path/to/main\n"
            "HEAD abc1234567890\n"
            "branch refs/heads/main\n"
            "\n"
            "worktree /path/to/feature\n"
            "HEAD def9876543210\n"
            "branch refs/heads/feature-x\n"
            "\n"
        )
        mocker.patch("subprocess.run", return_value=mock_result)

        result = list_worktrees()

        assert len(result) == 2
        assert result[0]["path"] == "/path/to/main"
        assert result[0]["commit"] == "abc1234"
        assert result[0]["branch"] == "main"
        assert result[1]["path"] == "/path/to/feature"
        assert result[1]["commit"] == "def9876"
        assert result[1]["branch"] == "feature-x"

    def test_list_worktrees_empty(self, mocker):
        """Test listing when no worktrees exist."""
        mocker.patch("wt.worktree.check_git_repo")
        mock_result = Mock()
        mock_result.stdout = ""
        mocker.patch("subprocess.run", return_value=mock_result)

        result = list_worktrees()
        assert not result


class TestDeleteWorktree:
    """Tests for delete_worktree function."""

    def test_delete_worktree_success(self, mocker):
        """Test deleting worktree successfully."""
        mocker.patch("wt.worktree.check_git_repo")
        mock_run = mocker.patch("subprocess.run", return_value=Mock(returncode=0))

        delete_worktree("/path/to/worktree")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["git", "worktree", "remove", "/path/to/worktree"]

    def test_delete_worktree_force(self, mocker):
        """Test deleting worktree with force flag."""
        mocker.patch("wt.worktree.check_git_repo")
        mock_run = mocker.patch("subprocess.run", return_value=Mock(returncode=0))

        delete_worktree("/path/to/worktree", force=True)

        args = mock_run.call_args[0][0]
        assert "--force" in args

    def test_delete_worktree_failure(self, mocker):
        """Test deleting worktree when command fails."""
        mocker.patch("wt.worktree.check_git_repo")
        mocker.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git", stderr="error"),
        )

        with pytest.raises(WorktreeError, match="Failed to delete worktree"):
            delete_worktree("/path/to/worktree")
