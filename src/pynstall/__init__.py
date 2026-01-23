"""pynstall - Turn your Python scripts into proper Windows apps.

Venv-aware shortcuts with taskbar pinning. Your code runs live from source files,
so `git pull` and reopen = instant update. No rebuild, no redistribution.
"""

from .installer import install_app, uninstall_app

__version__ = "0.1.0"
__all__ = ["install_app", "uninstall_app"]
