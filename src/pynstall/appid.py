"""Windows AppUserModelID handling for proper taskbar grouping."""

import sys
from pathlib import Path


def set_appid_on_shortcut(shortcut_path: Path, appid: str) -> bool:
    """Set the AppUserModelID on a shortcut file.

    This ensures the pinned taskbar icon and running application icon
    group together properly.

    Args:
        shortcut_path: Path to the .lnk shortcut file.
        appid: The AppUserModelID string (e.g., 'Company.Product.1.0').

    Returns:
        True if AppUserModelID was set successfully, False otherwise.
    """
    if sys.platform != "win32":
        return False

    try:
        from win32com.propsys import propsys, pscon
        import pythoncom
    except ImportError:
        print("Warning: pywin32 not installed. AppUserModelID not set.")
        print("Install with: pip install pywin32")
        print("Taskbar pinning may show duplicate icons without this.")
        return False

    shortcut_path = Path(shortcut_path).resolve()

    try:
        # Initialize COM
        pythoncom.CoInitialize()

        # Open the shortcut's property store (GPS_READWRITE = 2)
        store = propsys.SHGetPropertyStoreFromParsingName(
            str(shortcut_path),
            None,
            2,  # GPS_READWRITE
            propsys.IID_IPropertyStore,
        )

        # Set the AppUserModelID property
        pv = propsys.PROPVARIANTType(appid, pythoncom.VT_LPWSTR)
        store.SetValue(pscon.PKEY_AppUserModel_ID, pv)

        # Commit changes
        store.Commit()

        return True

    except Exception as e:
        print(f"Warning: Could not set AppUserModelID: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def is_pywin32_available() -> bool:
    """Check if pywin32 is available for AppUserModelID support."""
    try:
        from win32com.propsys import propsys, pscon
        import pythoncom

        return True
    except ImportError:
        return False
