# pynstall

Turn your Python scripts into proper Windows apps.

**Live source execution** - your code runs from the actual `.py` files, not a frozen bundle. `git pull` and reopen = instant update. No rebuild, no redistribution.

## Features

- **Venv-aware** - Automatically finds and uses your project's virtual environment
- **Taskbar-friendly** - Sets AppUserModelID on both the shortcut and the running process, so pinned icons group correctly
- **Crash visibility** - A generated launcher shows an error dialog and writes a full traceback to `%LOCALAPPDATA%\<AppName>\pynstall.log` instead of dying silently under `pythonw.exe`
- **No bundling** - Unlike PyInstaller, your code stays live and editable
- **Console hiding** - GUI apps launch without a console window (uses `pythonw.exe`)
- **Custom icons** - Use your own `.ico` file for the shortcut

## Installation

```bash
pip install pynstall
```

For full taskbar pinning support (recommended):
```bash
pip install pynstall[appid]
```

## Quick Start

### Option 1: Configure in pyproject.toml

Add to your `pyproject.toml`:

```toml
[tool.pynstall]
name = "My App"
entry = "myapp.main"  # module path or "main.py" for scripts
icon = "assets/icon.ico"  # optional
```

Then run:
```bash
pynstall install
```

### Option 2: Command-line only

```bash
pynstall install --name "My App" --entry myapp.main --icon ./icon.ico
```

## Usage

### Install

```bash
# From pyproject.toml config
pynstall install

# With explicit options
pynstall install --name "My App" --entry myapp.main

# Desktop + Start Menu
pynstall install --start-menu

# For console apps (show terminal window)
pynstall install --console
```

### Uninstall

```bash
# From pyproject.toml config
pynstall uninstall

# With explicit name
pynstall uninstall --name "My App"
```

## Configuration Options

### pyproject.toml

```toml
[tool.pynstall]
name = "My App"              # Required: display name
entry = "myapp.main"         # Required: module path or script.py
icon = "assets/icon.ico"     # Optional: custom icon
venv = "venv"                # Optional: venv path (auto-detected)
desktop = true               # Optional: create desktop shortcut (default: true)
start_menu = false           # Optional: create Start Menu entry (default: false)
appid = "Company.App.1.0"    # Optional: custom AppUserModelID (auto-generated)
console = false              # Optional: show console window (default: false)
```

### Command-line

```
pynstall install [OPTIONS]

Options:
  -n, --name TEXT           Display name for the application
  -e, --entry TEXT          Entry point - module or script
  -i, --icon TEXT           Path to .ico file
  --venv TEXT               Virtual environment path
  --desktop / --no-desktop  Create desktop shortcut (default: yes)
  --start-menu              Create Start Menu entry
  --appid TEXT              Windows AppUserModelID
  --console / --no-console  Show console window (default: no)
  -d, --project-dir PATH    Project directory
```

## Python API

```python
from pynstall import install_app, uninstall_app

# Install
result = install_app(
    name="My App",
    entry="myapp.main",
    icon="assets/icon.ico",
    desktop=True,
    start_menu=True,
)

if result.success:
    print(f"Installed to: {result.desktop_shortcut}")

# Uninstall
uninstall_app(name="My App")
```

## How It Works

pynstall generates a small, dependency-free launcher at
`%LOCALAPPDATA%\<AppName>\launcher.py` and creates a Windows shortcut that:

1. Points to `pythonw.exe` in your venv (no console window for GUI apps)
2. Runs the generated launcher script
3. Sets the process AppUserModelID at startup to match the shortcut's AppUserModelID, keeping pinned and running icons grouped
4. Verifies the venv's Python executable exists, then runs the entry point with `runpy` (module or script)
5. Shows a message box and appends the full traceback to `%LOCALAPPDATA%\<AppName>\pynstall.log` if the app raises

The working directory is your project root. Because the shortcut runs your actual source files:
- Edit code → reopen app → see changes immediately
- `git pull` → reopen app → instant update
- No frozen executables, no rebuild step

## Requirements

- Windows (macOS/Linux support planned)
- Python 3.9+
- A virtual environment in your project

## Optional Dependencies

- `pywin32` - Stamps the AppUserModelID onto the `.lnk` shortcut (needed for proper taskbar pinning)
  - The generated launcher always sets the process AppUserModelID at runtime via `ctypes`
  - Without it, shortcuts still work but pinned icons may show duplicates
  - Install with: `pip install pynstall[appid]`

## License

MIT
