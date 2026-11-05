"""Command-line interface for pynstall."""

import sys
from pathlib import Path

import click

from . import __version__
from .installer import install_app, uninstall_app


@click.group()
@click.version_option(version=__version__)
def main():
    """pynstall - Turn your Python scripts into proper Windows apps.

    Your code runs live from source files - `git pull` and reopen = instant update!
    No bundling, no rebuilding.

    \b
    Quick start:
      1. Add [tool.pynstall] to pyproject.toml
      2. Run: pynstall install

    Or use command-line options:
      pynstall install --name "My App" --entry myapp.main
    """
    pass


@main.command()
@click.option("--name", "-n", help="Display name for the application")
@click.option(
    "--entry",
    "-e",
    help="Entry point - module path (e.g., 'myapp.main') or script (e.g., 'main.py')",
)
@click.option("--icon", "-i", help="Path to .ico file for custom icon")
@click.option("--venv", help="Path to virtual environment (auto-detected if not specified)")
@click.option("--desktop/--no-desktop", default=True, help="Create desktop shortcut")
@click.option("--start-menu/--no-start-menu", default=False, help="Create Start Menu entry")
@click.option("--appid", help="Windows AppUserModelID for taskbar grouping")
@click.option("--console/--no-console", default=False, help="Show console window")
@click.option(
    "--project-dir",
    "-d",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Project directory (defaults to current directory)",
)
def install(
    name,
    entry,
    icon,
    venv,
    desktop,
    start_menu,
    appid,
    console,
    project_dir,
):
    """Install the app as a Windows shortcut.

    \b
    Examples:
      # From pyproject.toml config
      pynstall install

      # With explicit options
      pynstall install --name "My App" --entry myapp.main --icon ./icon.ico

      # GUI app without console
      pynstall install --name "My GUI" --entry myapp.gui --no-console

    The shortcut runs your live source code - `git pull` and reopen = instant update!
    """
    if sys.platform != "win32":
        click.echo("Error: pynstall currently only supports Windows", err=True)
        sys.exit(1)

    result = install_app(
        name=name,
        entry=entry,
        venv=venv,
        icon=icon,
        desktop=desktop,
        start_menu=start_menu,
        appid=appid,
        console=console,
        project_dir=project_dir,
    )

    if result.success:
        click.echo()
        click.echo("=" * 40)
        click.echo("  Installation Complete!")
        click.echo("=" * 40)
        click.echo()
        click.echo(result.message)
        click.echo()

        if result.desktop_shortcut:
            click.echo(f"  Desktop: {result.desktop_shortcut}")
        if result.start_menu_shortcut:
            click.echo(f"  Start Menu: {result.start_menu_shortcut}")
        if result.launcher_path:
            click.echo(f"  Launcher: {result.launcher_path}")

        click.echo()
        if result.appid_set:
            click.echo("  AppUserModelID set for proper taskbar grouping")
        else:
            click.echo("  Note: Install pywin32 for better taskbar pinning:")
            click.echo("        pip install pywin32")

        click.echo()
        click.echo("  Your code runs live - git pull and reopen = instant update!")
        click.echo()
    else:
        click.echo(f"Error: {result.message}", err=True)
        sys.exit(1)


@main.command()
@click.option("--name", "-n", help="Name of the app to uninstall")
@click.option(
    "--project-dir",
    "-d",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Project directory (defaults to current directory)",
)
def uninstall(name, project_dir):
    """Remove app shortcuts.

    \b
    Examples:
      # From pyproject.toml config
      pynstall uninstall

      # With explicit name
      pynstall uninstall --name "My App"
    """
    if sys.platform != "win32":
        click.echo("Error: pynstall currently only supports Windows", err=True)
        sys.exit(1)

    success = uninstall_app(name=name, project_dir=project_dir)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
