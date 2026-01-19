# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Identify and optionally remove orphaned Flatpak data directories."""

import shutil
import subprocess
import sys
from pathlib import Path


def get_installed_flatpaks() -> set[str]:
    """Return set of installed Flatpak application IDs."""
    try:
        result = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application"],
            capture_output=True,
            text=True,
            check=True,
        )
        return set(result.stdout.strip().splitlines())
    except FileNotFoundError:
        print("Error: flatpak command not found", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running flatpak: {e}", file=sys.stderr)
        sys.exit(1)


def get_directory_size(path: Path) -> int:
    """Return total size of directory in bytes."""
    total = 0
    for entry in path.rglob("*"):
        if entry.is_file() and not entry.is_symlink():
            try:
                total += entry.stat().st_size
            except OSError:
                pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def find_orphaned_dirs(app_dir: Path, installed: set[str]) -> list[tuple[Path, int]]:
    """Find directories not matching any installed Flatpak."""
    orphaned = []
    for entry in sorted(app_dir.iterdir()):
        if entry.is_dir() and entry.name not in installed:
            size = get_directory_size(entry)
            orphaned.append((entry, size))
    return orphaned


def main() -> None:
    app_dir = Path.home() / ".var" / "app"

    if not app_dir.exists():
        print(f"{app_dir} does not exist")
        sys.exit(0)

    installed = get_installed_flatpaks()
    orphaned = find_orphaned_dirs(app_dir, installed)

    if not orphaned:
        print("No orphaned Flatpak data directories found")
        sys.exit(0)

    total_size = sum(size for _, size in orphaned)
    print(f"Found {len(orphaned)} orphaned directories ({format_size(total_size)} total):\n")

    for i, (path, size) in enumerate(orphaned, 1):
        print(f"  {i}. {path.name} ({format_size(size)})")

    print()
    response = input("Delete all orphaned directories? [y/N] ").strip().lower()

    if response == "y":
        for path, _ in orphaned:
            print(f"Removing {path.name}...")
            if path.is_symlink():
                path.unlink()
            else:
                shutil.rmtree(path)
        print("Done")
    else:
        print("No changes made")


if __name__ == "__main__":
    main()
