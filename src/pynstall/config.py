"""Configuration parsing from pyproject.toml."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class PynstallConfig:
    """Configuration for pynstall.

    Attributes:
        name: Display name for the application (shown in shortcut).
        entry: Entry point - module path (e.g., 'myapp.main') or script (e.g., 'main.py').
        icon: Path to .ico file for the shortcut.
        venv: Path to virtual environment (auto-detected if not specified).
        desktop: Whether to create a desktop shortcut.
        start_menu: Whether to create a Start Menu entry.
        appid: Windows AppUserModelID for taskbar grouping.
        console: Whether to show a console window (False for GUI apps).
    """

    name: str
    entry: str
    icon: Optional[str] = None
    venv: Optional[str] = None
    desktop: bool = True
    start_menu: bool = False
    appid: Optional[str] = None
    console: bool = False


def load_config(project_dir: Optional[Path] = None) -> Optional[PynstallConfig]:
    """Load pynstall configuration from pyproject.toml.

    Args:
        project_dir: Directory containing pyproject.toml.
                     Defaults to current working directory.

    Returns:
        PynstallConfig if [tool.pynstall] section exists, None otherwise.
    """
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    pyproject_path = project_dir / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    tool_config = data.get("tool", {}).get("pynstall", {})
    if not tool_config:
        return None

    # Validate required fields
    if "name" not in tool_config:
        raise ValueError("[tool.pynstall] requires 'name' field")
    if "entry" not in tool_config:
        raise ValueError("[tool.pynstall] requires 'entry' field")

    return PynstallConfig(
        name=tool_config["name"],
        entry=tool_config["entry"],
        icon=tool_config.get("icon"),
        venv=tool_config.get("venv"),
        desktop=tool_config.get("desktop", True),
        start_menu=tool_config.get("start_menu", False),
        appid=tool_config.get("appid"),
        console=tool_config.get("console", False),
    )


def generate_appid(name: str, version: str = "1.0") -> str:
    """Generate a Windows AppUserModelID from an app name.

    Format: Company.Product.SubProduct.Version
    We use 'Pynstall' as the company prefix.

    Args:
        name: Application name.
        version: Version string.

    Returns:
        A valid AppUserModelID string.
    """
    # Remove spaces and special characters, keep alphanumeric
    clean_name = "".join(c for c in name if c.isalnum())
    return f"Pynstall.{clean_name}.{version}"
