# -*- coding: utf-8 -*-
"""
paths.py — Centralized Resource & Data Path Resolver for Dump's Test v4.0.
Guarantees reliable asset loading whether running from source or packaged via PyInstaller:
  - get_asset_path: Reads bundled read-only assets (from sys._MEIPASS when frozen)
  - get_data_path: Reads/writes mutable data (accounts.db, scores, history) in writable app directory
"""
import sys
import os
from pathlib import Path

# Root directory of the source or the frozen executable
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running inside PyInstaller bundle
    _BUNDLE_DIR = Path(sys._MEIPASS)
    _APP_DIR = Path(sys.executable).parent
else:
    # Running from normal Python script
    _BUNDLE_DIR = Path(__file__).parent.resolve()
    _APP_DIR = _BUNDLE_DIR

# Mobile Environment Detection (Android & iOS Writable Storage)
_IS_ANDROID = "ANDROID_PRIVATE" in os.environ or "ANDROID_ARGUMENT" in os.environ or "PYTHON_SERVICE_ARGUMENT" in os.environ
_IS_IOS = (sys.platform == "darwin") and ("iPhone" in os.uname().machine or "iPad" in os.uname().machine or "KIVY_BUILD" in os.environ or not os.access(str(_BUNDLE_DIR), os.W_OK))

if _IS_ANDROID:
    # Android internal storage: /data/data/<package>/files
    _private_dir = os.environ.get("ANDROID_PRIVATE", "")
    if _private_dir:
        _APP_DIR = Path(_private_dir)
    else:
        _APP_DIR = Path.home() / "dumpstest_data"
elif _IS_IOS:
    # iOS sandbox: App Home / Documents
    _APP_DIR = Path.home() / "Documents"
elif not os.access(str(_APP_DIR), os.W_OK):
    # Any other read-only environment: use user home directory
    _APP_DIR = Path.home() / ".dumpstest"

try:
    _APP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


def get_bundle_dir() -> Path:
    """Returns directory containing bundled read-only game assets."""
    return _BUNDLE_DIR


def get_app_dir() -> Path:
    """Returns writable directory for user saves and databases."""
    return _APP_DIR


def get_asset_path(relative_path: str | Path) -> Path:
    """
    Resolves full path to an asset file (images, audio, videos, qbanks).
    First checks the PyInstaller bundle directory, then falls back to app directory.
    """
    rel = Path(relative_path)
    # Check bundle path
    candidate = _BUNDLE_DIR / rel
    if candidate.exists():
        return candidate

    # Fallback to app directory
    candidate2 = _APP_DIR / rel
    if candidate2.exists():
        return candidate2

    return candidate


def get_data_path(filename: str | Path) -> Path:
    """
    Resolves path for mutable data files (e.g. accounts.db, user_history.json).
    Always returns path in the writable application directory.
    """
    target = _APP_DIR / Path(filename)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    # If the file does not exist yet in writable directory, check if a template exists in bundle
    if not target.exists():
        seed_file = _BUNDLE_DIR / Path(filename)
        if seed_file.exists() and seed_file.is_file():
            try:
                import shutil
                shutil.copy2(str(seed_file), str(target))
            except Exception:
                pass
    return target

