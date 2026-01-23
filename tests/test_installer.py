"""Tests for pynstall installer."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# Skip all tests on non-Windows platforms
pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="pynstall only supports Windows"
)


class TestVenvDetection:
    """Tests for virtual environment detection."""

    def test_find_venv_in_common_locations(self, tmp_path):
        """Should find venv in common directory names."""
        from pynstall.venv import find_venv, VENV_NAMES

        for venv_name in VENV_NAMES:
            # Create a fake venv structure
            venv_dir = tmp_path / venv_name
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "python.exe").touch()

            result = find_venv(tmp_path)
            assert result == venv_dir

            # Clean up for next iteration
            import shutil

            shutil.rmtree(venv_dir)

    def test_find_venv_returns_none_when_missing(self, tmp_path):
        """Should return None when no venv exists."""
        from pynstall.venv import find_venv

        result = find_venv(tmp_path)
        assert result is None

    def test_get_python_exe_gui_mode(self, tmp_path):
        """Should return pythonw.exe for GUI mode."""
        from pynstall.venv import get_python_exe

        venv_path = tmp_path / "venv"
        result = get_python_exe(venv_path, gui=True)
        assert result.name == "pythonw.exe"

    def test_get_python_exe_console_mode(self, tmp_path):
        """Should return python.exe for console mode."""
        from pynstall.venv import get_python_exe

        venv_path = tmp_path / "venv"
        result = get_python_exe(venv_path, gui=False)
        assert result.name == "python.exe"


class TestConfig:
    """Tests for configuration parsing."""

    def test_load_config_from_pyproject(self, tmp_path):
        """Should load config from pyproject.toml."""
        from pynstall.config import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[tool.pynstall]
name = "Test App"
entry = "testapp.main"
icon = "icon.ico"
desktop = true
start_menu = false
"""
        )

        config = load_config(tmp_path)
        assert config is not None
        assert config.name == "Test App"
        assert config.entry == "testapp.main"
        assert config.icon == "icon.ico"
        assert config.desktop is True
        assert config.start_menu is False

    def test_load_config_returns_none_when_missing(self, tmp_path):
        """Should return None when no pyproject.toml exists."""
        from pynstall.config import load_config

        config = load_config(tmp_path)
        assert config is None

    def test_load_config_returns_none_without_pynstall_section(self, tmp_path):
        """Should return None when [tool.pynstall] section is missing."""
        from pynstall.config import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
"""
        )

        config = load_config(tmp_path)
        assert config is None

    def test_generate_appid(self):
        """Should generate a valid AppUserModelID."""
        from pynstall.config import generate_appid

        appid = generate_appid("My Cool App", "2.0")
        assert appid == "Pynstall.MyCoolApp.2.0"

    def test_generate_appid_removes_special_chars(self):
        """Should remove special characters from app name."""
        from pynstall.config import generate_appid

        appid = generate_appid("App (Beta) - Test!", "1.0")
        assert appid == "Pynstall.AppBetaTest.1.0"


class TestInstaller:
    """Tests for the main installer logic."""

    def test_install_fails_without_name(self, tmp_path):
        """Should fail when name is not provided."""
        from pynstall.installer import install_app

        result = install_app(entry="test.main", project_dir=tmp_path)
        assert result.success is False
        assert "name is required" in result.message.lower()

    def test_install_fails_without_entry(self, tmp_path):
        """Should fail when entry is not provided."""
        from pynstall.installer import install_app

        result = install_app(name="Test", project_dir=tmp_path)
        assert result.success is False
        assert "entry point is required" in result.message.lower()

    def test_install_fails_without_venv(self, tmp_path):
        """Should fail when no venv is found."""
        from pynstall.installer import install_app

        result = install_app(name="Test", entry="test.main", project_dir=tmp_path)
        assert result.success is False
        assert "virtual environment" in result.message.lower()
