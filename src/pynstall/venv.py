"""Virtual environment detection and utilities."""

import os
import sys
from pathlib import Path
from typing import Optional


# Common venv directory names in order of preference
VENV_NAMES = ["venv", ".venv", "env", ".env"]


def find_venv(project_dir: Optional[Path] = None) -> Optional[Path]:
    """Find a virtual environment in the project directory.

    Args:
        project_dir: Directory to search. Defaults to current working directory.

    Returns:
        Path to venv directory, or None if not found.
    """
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    for name in VENV_NAMES:
        venv_path = project_dir / name
        if is_valid_venv(venv_path):
            return venv_path

    return None


def is_valid_venv(path: Path) -> bool:
    """Check if a path is a valid virtual environment."""
    if not path.is_dir():
        return False

    # Check for Windows venv structure
    if sys.platform == "win32":
        return (path / "Scripts" / "python.exe").exists()
    else:
        # Linux/macOS
        return (path / "bin" / "python").exists()


def get_python_exe(venv_path: Path, gui: bool = False) -> Path:
    """Get the path to the Python executable in a venv.

    Args:
        venv_path: Path to the virtual environment.
        gui: If True, return pythonw.exe on Windows (no console window).

    Returns:
        Path to the Python executable.
    """
    if sys.platform == "win32":
        exe_name = "pythonw.exe" if gui else "python.exe"
        return venv_path / "Scripts" / exe_name
    else:
        return venv_path / "bin" / "python"


def get_activate_script(venv_path: Path) -> Path:
    """Get the path to the activation script for a venv."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "activate.bat"
    else:
        return venv_path / "bin" / "activate"
