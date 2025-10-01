# git-worktree-cli

A lightweight Python CLI tool to simplify Git worktree management.

## Overview

`wt` makes working with Git worktrees effortless by providing an intuitive command-line interface for creating, listing, and deleting worktrees. It automatically generates consistent paths and can optionally open new worktrees in your IDE or terminal.

## Features

- **Simple Worktree Creation**: Create worktrees with automatic path generation
- **Smart Path Management**: Auto-generates paths as `../<root_folder_name>_<branch_name>`
- **IDE Integration**: Open worktrees directly in your favorite IDE (VS Code, PyCharm, Cursor, etc.)
- **Terminal Integration**: Launch new iTerm2 tabs on macOS pointing to your worktree
- **Easy Management**: List and delete worktrees with simple commands
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

### Create Worktree

Create a new worktree for a branch:

```bash
# Basic usage - creates worktree only
wt create feature-x
# Creates: ../git-worktree-cli_feature-x

# Create and open in terminal (iTerm2 on macOS)
wt create feature-y --mode terminal

# Create and open in VS Code
wt create feature-z --mode ide --ide code

# Create and open in default IDE (auto-detects: code, cursor, pycharm, subl, atom)
wt create feature-w --mode ide
```

**Path Generation**: Worktrees are created at `../<root_folder_name>_<branch_name>`
- If branch exists locally or remotely: checks it out
- If branch doesn't exist: creates a new branch

### List Worktrees

Display all worktrees in the repository:

```bash
wt list
```

Example output:
```
PATH                                               BRANCH                         COMMIT
------------------------------------------------------------------------------------------
/Users/user/projects/myproject                     main                           abc1234
/Users/user/projects/myproject_feature-x           feature-x                      def5678
```

### Delete Worktree

Remove a worktree:

```bash
# Delete a worktree
wt delete /path/to/worktree

# Force delete (even with uncommitted changes)
wt delete /path/to/worktree --force
```

## Modes

The `create` command supports three modes via the `--mode` option:

### `none` (default)
Creates the worktree without any additional action.

```bash
wt create feature-x
```

### `terminal`
Creates the worktree and opens a new terminal tab at that location.

**Supported platforms:**
- macOS: Opens new iTerm2 tab

```bash
ezl create feature-x --mode terminal
```

### `ide`
Creates the worktree and opens it in an IDE.

```bash
# Specify IDE explicitly
wt create feature-x --mode ide --ide code      # VS Code
wt create feature-x --mode ide --ide cursor    # Cursor
wt create feature-x --mode ide --ide pycharm   # PyCharm

# Auto-detect IDE (tries: code, cursor, pycharm, subl, atom)
wt create feature-x --mode ide
```

## Examples

### Working on a new feature

```bash
# Create a new worktree for a feature branch and open in VS Code
wt create feature/auth-system --mode ide --ide code

# Work on the feature...
cd ../myproject_feature/auth-system

# When done, delete the worktree
wt delete /path/to/myproject_feature/auth-system
```

### Quick bug fix

```bash
# Create worktree for hotfix
wt create hotfix/urgent-bug

# Work on the fix in the new location
cd ../myproject_hotfix/urgent-bug

# After merging, clean up
wt delete ../myproject_hotfix/urgent-bug
```

### Review all active worktrees

```bash
wt list
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

[Add your license here]


## Acknowledgments

This project was a way to use Claude Code for a real use-case, which was inspired by [John Lindquists' worktree-cli](https://github.com/johnlindquist/worktree-cli).