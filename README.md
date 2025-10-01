# git-worktree-cli

A lightweight Python CLI tool to simplify Git worktree management.

## Overview

`wt` makes working with Git worktrees effortless by providing an intuitive command-line interface for adding, listing, and removing worktrees. It automatically generates consistent paths and can optionally open new worktrees in your IDE or terminal.

## Features

- **Simple Worktree Creation**: Add worktrees with automatic path generation
- **Smart Path Management**: Auto-generates paths as `../<root_folder_name>_<branch_name>`
- **IDE Integration**: Open worktrees directly in your favorite IDE (VS Code, PyCharm, Cursor, etc.)
- **Terminal Integration**: Launch new iTerm2 tabs on macOS pointing to your worktree
- **Easy Management**: List and remove worktrees with simple commands
- **Branch Handling**: Automatically creates new branches or checks out existing ones
- **Cross-Platform**: Works on any system with Python 3.12+ and Git

## Installation

### Prerequisites

Make sure you have [uv](https://docs.astral.sh/uv/) installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/git-worktree-cli.git
cd git-worktree-cli

# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# .venv\Scripts\activate   # On Windows
```

### Global Installation

```bash
# Install globally with uv
uv tool install git-worktree-cli

# Or install from local source
uv tool install .
```

### Verify Installation

```bash
wt --version
```

## Usage

### Add Worktree

Add a new worktree for a branch:

```bash
# Basic usage - adds worktree only
wt add feature-x
# Creates: ../git-worktree-cli_feature-x

# Add and open in VS Code
wt add feature-y --ide code

# Add and start Claude session
wt add feature-z --claude

# Add and open in default IDE (auto-detects: code, cursor, pycharm, subl, atom)
wt add feature-w --ide
```

**Path Generation**: Worktrees are created at `../<root_folder_name>_<branch_name>`
- If branch exists locally or remotely: checks it out
- If branch doesn't exist: creates a new branch

### List Worktrees

Display all worktrees in the repository:

```bash
wt list
# Or use the alias:
wt ls
```

Example output:
```
PATH                                               BRANCH                         COMMIT
------------------------------------------------------------------------------------------
/Users/user/projects/myproject                     main                           abc1234
/Users/user/projects/myproject_feature-x           feature-x                      def5678
```

### Remove Worktree

Remove a worktree:

```bash
# Remove a worktree
wt remove /path/to/worktree

# Or use the alias:
wt rm /path/to/worktree

# Force remove (even with uncommitted changes)
wt remove /path/to/worktree --force
```

## Post-Creation Actions

The `add` command supports optional flags to perform actions after creating the worktree:

### Default (no flags)
Adds the worktree without any additional action.

```bash
wt add feature-x
```

### `--ide`
Adds the worktree and opens it in an IDE.

```bash
# Specify IDE explicitly
wt add feature-x --ide code      # VS Code
wt add feature-x --ide cursor    # Cursor
wt add feature-x --ide pycharm   # PyCharm

# Auto-detect IDE (tries: code, cursor, pycharm, subl, atom)
wt add feature-x --ide
```

### `--claude`
Adds the worktree and starts a Claude Code session.

```bash
wt add feature-x --claude
```

**Note**: `--ide` and `--claude` are mutually exclusive.

## Examples

### Working on a new feature

```bash
# Add a new worktree for a feature branch and open in VS Code
wt add feature/auth-system --ide code

# Work on the feature...
cd ../myproject_feature/auth-system

# When done, remove the worktree
wt rm /path/to/myproject_feature/auth-system
```

### Quick bug fix

```bash
# Add worktree for hotfix
wt add hotfix/urgent-bug

# Work on the fix in the new location
cd ../myproject_hotfix/urgent-bug

# After merging, clean up
wt remove ../myproject_hotfix/urgent-bug
```

### Review all active worktrees

```bash
wt list
# Or use the alias:
wt ls
```

## Requirements

- Python 3.12 or higher
- Git 2.5 or higher (for worktree support)
- iTerm2 (for `--mode terminal` on macOS)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/git-worktree-cli.git
cd git-worktree-cli

# Install all dependencies (including dev)
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_worktree.py -v
```

### Code Quality

```bash
# Format code with black
uv run black wt/ tests/

# Lint with pylint
uv run pylint wt/ tests/ --disable=C0114,C0115,C0116,R0903 --max-line-length=120
```

### Project Structure

```
git-worktree-cli/
├── wt/
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Entry point for python -m wt
│   ├── cli.py             # CLI commands and interface
│   ├── worktree.py        # Core worktree operations
│   └── launchers.py       # IDE and terminal launchers
├── tests/
│   ├── test_cli.py        # CLI tests
│   ├── test_worktree.py   # Worktree operation tests
│   └── test_launchers.py  # Launcher tests
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Troubleshooting

### "Not a git repository" error
Make sure you're running `wt` from within a Git repository.

### IDE not launching
Ensure the IDE executable is in your PATH:
```bash
which code  # VS Code
which pycharm  # PyCharm
```

### Terminal not opening (macOS)
Make sure iTerm2 is installed. Terminal integration currently only supports iTerm2 on macOS.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Acknowledgments

This project was a way to use Claude Code for a real use-case, which was inspired by [John Lindquists' worktree-cli](https://github.com/johnlindquist/worktree-cli).