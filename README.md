# flatclean

Identify and remove orphaned Flatpak data directories.

When you uninstall a Flatpak application, its data directory in `~/.var/app/` is left behind. This script finds those orphaned directories and offers to delete them.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- flatpak

## Usage

```
uv run flatclean.py
```

The script will list any orphaned directories with their sizes, then prompt for confirmation before deletion.
