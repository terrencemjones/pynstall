"""Main installation logic for pynstall."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .appid import set_appid_on_shortcut
from .config import generate_appid, load_config, PynstallConfig
from .shortcut import (
    create_shortcut,
    delete_shortcut,
    get_desktop_path,
    get_start_menu_path,
)
from .venv import find_venv, get_python_exe, is_valid_venv


@dataclass
class InstallResult:
    """Result of an installation operation."""

    success: bool
    desktop_shortcut: Optional[Path] = None
    start_menu_shortcut: Optional[Path] = None
    appid_set: bool = False
    message: str = ""


def install_app(
    name: Optional[str] = None,
    entry: Optional[str] = None,
    venv: Optional[str] = None,
    icon: Optional[str] = None,
    desktop: bool = True,
    start_menu: bool = False,
    appid: Optional[str] = None,
    console: bool = False,
    project_dir: Optional[Path] = None,
) -> InstallResult:
    """Install a Python app as a Windows shortcut.

    Your code runs live from source files - `git pull` and reopen = instant update!

    Args:
        name: Display name for the application. Required if no pyproject.toml config.
        entry: Entry point - module path (e.g., 'myapp.main') or script (e.g., 'main.py').
               Required if no pyproject.toml config.
        venv: Path to virtual environment. Auto-detected if not specified.
        icon: Path to .ico file for custom icon.
        desktop: Create a desktop shortcut (default: True).
        start_menu: Create a Start Menu entry (default: False).
        appid: Windows AppUserModelID for taskbar grouping. Auto-generated if not specified.
        console: Show console window (default: False, suitable for GUI apps).
        project_dir: Project directory. Defaults to current working directory.

    Returns:
        InstallResult with details about the installation.
    """
    if sys.platform != "win32":
        return InstallResult(
            success=False, message="pynstall currently only supports Windows"
        )

    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir).resolve()

    # Try to load config from pyproject.toml
    config = load_config(project_dir)

    # Merge CLI args with config (CLI takes precedence)
    final_name = name or (config.name if config else None)
    final_entry = entry or (config.entry if config else None)
    final_icon = icon or (config.icon if config else None)
    final_venv = venv or (config.venv if config else None)
    final_desktop = desktop if name else (config.desktop if config else True)
    final_start_menu = start_menu if name else (config.start_menu if config else False)
    final_appid = appid or (config.appid if config else None)
    final_console = console if name else (config.console if config else False)

    # Validate required fields
    if not final_name:
        return InstallResult(
            success=False,
            message="App name is required. Use --name or add [tool.pynstall] to pyproject.toml",
        )
    if not final_entry:
        return InstallResult(
            success=False,
            message="Entry point is required. Use --entry or add [tool.pynstall] to pyproject.toml",
        )

    # Find or validate venv
    if final_venv:
        venv_path = project_dir / final_venv
        if not is_valid_venv(venv_path):
            return InstallResult(
                success=False, message=f"Invalid virtual environment: {venv_path}"
            )
    else:
        venv_path = find_venv(project_dir)
        if not venv_path:
            return InstallResult(
                success=False,
                message="No virtual environment found. Create one with: python -m venv venv",
            )

    # Get Python executable
    python_exe = get_python_exe(venv_path, gui=not final_console)
    if not python_exe.exists():
        return InstallResult(
            success=False, message=f"Python executable not found: {python_exe}"
        )

    # Determine entry point type and build arguments
    if final_entry.endswith(".py"):
        # Script file
        script_path = project_dir / final_entry
        if not script_path.exists():
            return InstallResult(
                success=False, message=f"Script not found: {script_path}"
            )
        arguments = f'"{script_path}"'
    else:
        # Module path (e.g., 'myapp.main')
        arguments = f"-m {final_entry}"

    # Resolve icon path
    icon_path = None
    if final_icon:
        icon_path = project_dir / final_icon
        if not icon_path.exists():
            print(f"Warning: Icon not found at {icon_path}, using default")
            icon_path = None

    # Generate AppUserModelID if not specified
    if not final_appid:
        final_appid = generate_appid(final_name)

    result = InstallResult(success=True, appid_set=False)

    # Create desktop shortcut
    if final_desktop:
        desktop_path = get_desktop_path()
        shortcut_path = desktop_path / f"{final_name}.lnk"

        if create_shortcut(
            shortcut_path=shortcut_path,
            target_path=python_exe,
            arguments=arguments,
            working_dir=project_dir,
            icon_path=icon_path,
            description=f"{final_name} - Installed with pynstall",
        ):
            result.desktop_shortcut = shortcut_path
            # Set AppUserModelID
            if set_appid_on_shortcut(shortcut_path, final_appid):
                result.appid_set = True
        else:
            result.success = False
            result.message = "Failed to create desktop shortcut"
            return result

    # Create Start Menu shortcut
    if final_start_menu:
        start_menu_path = get_start_menu_path()
        shortcut_path = start_menu_path / f"{final_name}.lnk"

        if create_shortcut(
            shortcut_path=shortcut_path,
            target_path=python_exe,
            arguments=arguments,
            working_dir=project_dir,
            icon_path=icon_path,
            description=f"{final_name} - Installed with pynstall",
        ):
            result.start_menu_shortcut = shortcut_path
            # Set AppUserModelID
            set_appid_on_shortcut(shortcut_path, final_appid)
        else:
            result.success = False
            result.message = "Failed to create Start Menu shortcut"
            return result

    result.message = f"Successfully installed {final_name}"
    return result


def uninstall_app(
    name: Optional[str] = None,
    project_dir: Optional[Path] = None,
) -> bool:
    """Uninstall an app by removing its shortcuts.

    Args:
        name: Name of the app to uninstall. If not specified, reads from pyproject.toml.
        project_dir: Project directory. Defaults to current working directory.

    Returns:
        True if uninstallation was successful.
    """
    if sys.platform != "win32":
        print("pynstall currently only supports Windows")
        return False

    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir).resolve()

    # Try to load config from pyproject.toml
    if not name:
        config = load_config(project_dir)
        if config:
            name = config.name
        else:
            print(
                "App name is required. Use --name or add [tool.pynstall] to pyproject.toml"
            )
            return False

    success = True

    # Remove desktop shortcut
    desktop_shortcut = get_desktop_path() / f"{name}.lnk"
    if desktop_shortcut.exists():
        if delete_shortcut(desktop_shortcut):
            print(f"Removed desktop shortcut: {desktop_shortcut}")
        else:
            success = False

    # Remove Start Menu shortcut
    start_menu_shortcut = get_start_menu_path() / f"{name}.lnk"
    if start_menu_shortcut.exists():
        if delete_shortcut(start_menu_shortcut):
            print(f"Removed Start Menu shortcut: {start_menu_shortcut}")
        else:
            success = False

    if success:
        print(f"Successfully uninstalled {name}")
    return success
