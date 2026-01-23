"""Windows shortcut creation using PowerShell."""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def create_shortcut(
    shortcut_path: Path,
    target_path: Path,
    arguments: str = "",
    working_dir: Optional[Path] = None,
    icon_path: Optional[Path] = None,
    description: str = "",
) -> bool:
    """Create a Windows shortcut (.lnk) file using PowerShell.

    Args:
        shortcut_path: Where to create the shortcut.
        target_path: Target executable or script.
        arguments: Command-line arguments for the target.
        working_dir: Working directory when launched.
        icon_path: Path to .ico file for custom icon.
        description: Tooltip description.

    Returns:
        True if shortcut was created successfully.
    """
    if sys.platform != "win32":
        raise RuntimeError("Shortcut creation is only supported on Windows")

    # Ensure paths are absolute
    shortcut_path = Path(shortcut_path).resolve()
    target_path = Path(target_path).resolve()

    if working_dir:
        working_dir = Path(working_dir).resolve()
    else:
        working_dir = target_path.parent

    # Build PowerShell command
    ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut_path}')
$s.TargetPath = '{target_path}'
$s.Arguments = '{arguments}'
$s.WorkingDirectory = '{working_dir}'
$s.Description = '{description}'
"""

    if icon_path:
        icon_path = Path(icon_path).resolve()
        ps_script += f"$s.IconLocation = '{icon_path}'\n"

    ps_script += "$s.Save()"

    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            check=True,
        )
        return shortcut_path.exists()
    except subprocess.CalledProcessError as e:
        print(f"Error creating shortcut: {e.stderr}")
        return False


def delete_shortcut(shortcut_path: Path) -> bool:
    """Delete a shortcut file.

    Args:
        shortcut_path: Path to the shortcut to delete.

    Returns:
        True if shortcut was deleted or didn't exist.
    """
    shortcut_path = Path(shortcut_path)
    if shortcut_path.exists():
        try:
            shortcut_path.unlink()
            return True
        except OSError as e:
            print(f"Error deleting shortcut: {e}")
            return False
    return True


def get_desktop_path() -> Path:
    """Get the user's Desktop folder path."""
    if sys.platform == "win32":
        import os

        return Path(os.environ["USERPROFILE"]) / "Desktop"
    else:
        return Path.home() / "Desktop"


def get_start_menu_path() -> Path:
    """Get the user's Start Menu Programs folder path."""
    if sys.platform == "win32":
        import os

        return (
            Path(os.environ["APPDATA"])
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
        )
    else:
        raise RuntimeError("Start Menu is only available on Windows")
