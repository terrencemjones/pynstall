"""Windows shortcut creation using PowerShell."""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def _ps_quote(value: object) -> str:
    """Escape a value for use inside a single-quoted PowerShell string.

    PowerShell escapes a single quote by doubling it (``''``).  Without this,
    paths such as ``C:\\Users\\O'Brien\\app.lnk`` break the generated script.

    Args:
        value: Value to escape (converted to ``str``).

    Returns:
        The value with every single quote doubled.
    """
    return str(value).replace("'", "''")


def _build_shortcut_script(
    shortcut_path: Path,
    target_path: Path,
    arguments: str = "",
    working_dir: Optional[Path] = None,
    icon_path: Optional[Path] = None,
    description: str = "",
) -> str:
    """Build the PowerShell script that creates a shortcut.

    Args:
        shortcut_path: Where to create the shortcut.
        target_path: Target executable or script.
        arguments: Command-line arguments for the target.
        working_dir: Working directory when launched.
        icon_path: Path to .ico file for custom icon.
        description: Tooltip description.

    Returns:
        PowerShell script text with all interpolated values escaped.
    """
    if working_dir is None:
        working_dir = target_path.parent

    script = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{_ps_quote(shortcut_path)}')
$s.TargetPath = '{_ps_quote(target_path)}'
$s.Arguments = '{_ps_quote(arguments)}'
$s.WorkingDirectory = '{_ps_quote(working_dir)}'
$s.Description = '{_ps_quote(description)}'
"""

    if icon_path:
        script += f"$s.IconLocation = '{_ps_quote(icon_path)}'\n"

    return script + "$s.Save()"


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

    if icon_path:
        icon_path = Path(icon_path).resolve()

    # Build PowerShell command
    ps_script = _build_shortcut_script(
        shortcut_path=shortcut_path,
        target_path=target_path,
        arguments=arguments,
        working_dir=working_dir,
        icon_path=icon_path,
        description=description,
    )

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
