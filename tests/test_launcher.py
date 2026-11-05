"""Tests for generated launcher scripts."""

import sys
from pathlib import Path

import pytest

from pynstall.launcher import (
    build_launcher_source,
    create_launcher,
    get_launcher_dir,
    get_launcher_path,
    get_log_path,
    remove_launcher,
)


# Launcher paths and AUMID handling are Windows-specific.
pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="pynstall only supports Windows"
)


class TestLauncherPaths:
    """Tests for per-app launcher and log locations."""

    def test_paths_use_localappdata(self, tmp_path, monkeypatch):
        """Should place the launcher and log under LOCALAPPDATA."""
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

        assert get_launcher_path("My App") == tmp_path / "My App" / "launcher.py"
        assert get_log_path("My App") == tmp_path / "My App" / "pynstall.log"

    def test_directory_name_is_sanitized(self, tmp_path, monkeypatch):
        """Should replace characters that are invalid in Windows paths."""
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

        assert get_launcher_dir("Bad:Name?") == tmp_path / "Bad_Name_"


class TestLauncherGeneration:
    """Tests for launcher source generation and file cleanup."""

    def test_source_bakes_appid_and_module_entry(self, tmp_path):
        """Generated source should contain the AUMID, entry, and Python path."""
        python_exe = tmp_path / "venv" / "Scripts" / "pythonw.exe"
        log_path = tmp_path / "logs" / "pynstall.log"

        source = build_launcher_source(
            app_name="Quote App",
            entry="myapp.main",
            appid="Company.QuoteApp.1.0",
            python_exe=python_exe,
            log_path=log_path,
            project_dir=tmp_path,
        )

        assert "APP_ID = 'Company.QuoteApp.1.0'" in source
        assert "ENTRY = 'myapp.main'" in source
        assert "ENTRY_IS_SCRIPT = False" in source
        assert f"PROJECT_DIR = {str(tmp_path)!r}" in source
        assert repr(str(python_exe)) in source
        assert repr(str(log_path)) in source
        assert "SetCurrentProcessExplicitAppUserModelID" in source
        assert "MessageBoxW" in source
        assert "runpy" in source

        # The generated script must be syntactically valid Python.
        compile(source, "launcher.py", "exec")

    def test_source_bakes_script_entry(self, tmp_path):
        """Script entries should be stored as an absolute path."""
        script = tmp_path / "main.py"
        source = build_launcher_source(
            app_name="Script App",
            entry=str(script),
            appid="Pynstall.ScriptApp.1.0",
            python_exe=tmp_path / "pythonw.exe",
            entry_is_script=True,
            log_path=tmp_path / "pynstall.log",
        )

        assert "ENTRY_IS_SCRIPT = True" in source
        assert f"ENTRY = {str(script)!r}" in source
        compile(source, "launcher.py", "exec")

    def test_create_launcher_writes_file(self, tmp_path):
        """Should create parent directories and write the launcher."""
        launcher_path = tmp_path / "localappdata" / "My App" / "launcher.py"

        assert create_launcher(
            launcher_path=launcher_path,
            app_name="My App",
            entry="myapp.main",
            appid="Pynstall.MyApp.1.0",
            python_exe=tmp_path / "venv" / "Scripts" / "pythonw.exe",
        )

        assert launcher_path.exists()
        content = launcher_path.read_text(encoding="utf-8")
        assert "Pynstall.MyApp.1.0" in content
        assert "myapp.main" in content

    def test_remove_launcher_deletes_file(self, tmp_path):
        """Should delete a generated launcher."""
        launcher_path = tmp_path / "launcher.py"
        launcher_path.write_text("# generated", encoding="utf-8")

        assert remove_launcher(launcher_path) is True
        assert not launcher_path.exists()

    def test_remove_launcher_missing_file_is_ok(self, tmp_path):
        """Removing a missing launcher should succeed."""
        assert remove_launcher(tmp_path / "missing.py") is True
