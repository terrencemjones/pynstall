"""Tests for PowerShell shortcut generation."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pynstall.shortcut import _build_shortcut_script, _ps_quote, create_shortcut


pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="pynstall only supports Windows"
)


class TestPowerShellQuoting:
    """Tests for single-quote escaping in generated PowerShell."""

    def test_ps_quote_doubles_single_quotes(self):
        """PowerShell escapes apostrophes by doubling them."""
        assert _ps_quote("O'Brien") == "O''Brien"
        assert _ps_quote("no quotes") == "no quotes"
        assert _ps_quote(123) == "123"

    def test_build_script_escapes_every_interpolated_value(self):
        """Paths and descriptions containing apostrophes must be escaped."""
        script = _build_shortcut_script(
            shortcut_path=Path("C:/Users/O'Brien/Desktop/My App.lnk"),
            target_path=Path("C:/Users/O'Brien/venv/Scripts/pythonw.exe"),
            arguments='"C:\\Users\\O\'Brien\\AppData\\Local\\My App\\launcher.py"',
            working_dir=Path("C:/Users/O'Brien/project"),
            icon_path=Path("C:/Users/O'Brien/icon.ico"),
            description="Terrence's app",
        )

        assert "O'Brien" not in script
        assert "O''Brien" in script
        assert "Terrence''s app" in script
        assert script.count("O''Brien") == 5

    def test_create_shortcut_uses_escaped_script(self, tmp_path, monkeypatch):
        """create_shortcut should pass the escaped script to PowerShell."""
        import pynstall.shortcut as shortcut_module

        captured = {}

        def fake_run(command, **kwargs):
            captured["command"] = command
            return MagicMock()

        monkeypatch.setattr(shortcut_module.subprocess, "run", fake_run)

        app_dir = tmp_path / "O'Brien"
        app_dir.mkdir()
        python_exe = app_dir / "pythonw.exe"
        python_exe.touch()

        shortcut_path = tmp_path / "Desktop O'Brien" / "My App.lnk"
        shortcut_path.parent.mkdir()
        shortcut_path.touch()

        assert create_shortcut(
            shortcut_path=shortcut_path,
            target_path=python_exe,
            arguments=f'"{app_dir / "launcher.py"}"',
            description="Terrence's app",
        )

        script = captured["command"][-1]
        assert "O''Brien" in script
        assert "O'Brien" not in script
        assert "Terrence''s app" in script
