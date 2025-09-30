# ez-leaf

A lightweight Python CLI tool to simplify Git worktree management.

## Overview

`ez-leaf` makes working with Git worktrees effortless by providing an intuitive command-line interface for creating, listing, and deleting worktrees. It automatically generates consistent paths and can optionally open new worktrees in your IDE or terminal.

## Features

- **Simple Worktree Creation**: Create worktrees with automatic path generation
- **Smart Path Management**: Auto-generates paths as `../<root_folder_name>_<branch_name>`
- **IDE Integration**: Open worktrees directly in your favorite IDE (VS Code, PyCharm, Cursor, etc.)
- **Terminal Integration**: Launch new iTerm2 tabs on macOS pointing to your worktree
- **Easy Management**: List and delete worktrees with simple commands
- **Branch Handling**: Automatically creates new branches or checks out existing ones
- **Cross-Platform**: Works on any system with Python 3.12+ and Git

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/ez-leaf.git
cd ez-leaf

# Install in development mode
pip install -e .

# Or install with dev dependencies (for testing)
pip install -e ".[dev]"
```

### Verify Installation

```bash
ezl --version
```

## Usage

### Create Worktree

Create a new worktree for a branch:

```bash
# Basic usage - creates worktree only
ezl create feature-x
# Creates: ../ez-leaf_feature-x

# Create and open in terminal (iTerm2 on macOS)
ezl create feature-y --mode terminal

# Create and open in VS Code
ezl create feature-z --mode ide --ide code

# Create and open in default IDE (auto-detects: code, cursor, pycharm, subl, atom)
ezl create feature-w --mode ide
```

**Path Generation**: Worktrees are created at `../<root_folder_name>_<branch_name>`
- If branch exists locally or remotely: checks it out
- If branch doesn't exist: creates a new branch

### List Worktrees

Display all worktrees in the repository:

```bash
ezl list
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
ezl delete /path/to/worktree

# Force delete (even with uncommitted changes)
ezl delete /path/to/worktree --force
```

## Modes

The `create` command supports three modes via the `--mode` option:

### `none` (default)
Creates the worktree without any additional action.

```bash
ezl create feature-x
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
ezl create feature-x --mode ide --ide code      # VS Code
ezl create feature-x --mode ide --ide cursor    # Cursor
ezl create feature-x --mode ide --ide pycharm   # PyCharm

# Auto-detect IDE (tries: code, cursor, pycharm, subl, atom)
ezl create feature-x --mode ide
```

## Examples

### Working on a new feature

```bash
# Create a new worktree for a feature branch and open in VS Code
ezl create feature/auth-system --mode ide --ide code

# Work on the feature...
cd ../myproject_feature/auth-system

# When done, delete the worktree
ezl delete /path/to/myproject_feature/auth-system
```

### Quick bug fix

```bash
# Create worktree for hotfix
ezl create hotfix/urgent-bug

# Work on the fix in the new location
cd ../myproject_hotfix/urgent-bug

# After merging, clean up
ezl delete ../myproject_hotfix/urgent-bug
```

### Review all active worktrees

```bash
ezl list
```

## Requirements

- Python 3.12 or higher
- Git 2.5 or higher (for worktree support)
- iTerm2 (for `--mode terminal` on macOS)

## Development

### Running Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_worktree.py -v
```

### Project Structure

```
ez-leaf/
├── ez_leaf/
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Entry point for python -m ez_leaf
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
Make sure you're running `ezl` from within a Git repository.

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

## Author

[Add your name/info here]
