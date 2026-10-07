"""
main.py — Entry point for Dump's Test v11.0 Online Master Edition.
"""
import sys
from pathlib import Path

# Ensure project directory is in sys.path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from ui.engine import GameApp

def main():
    """Launch Dump's Test v11.0 Online Master Edition Pygame Graphical Interface."""
    try:
        app = GameApp()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting Dump's Test...")
        sys.exit(0)
    except Exception as e:
        import traceback
        import datetime
        err_msg = traceback.format_exc()
        print(f"\n[CRASH] Game encountered an error: {e}")
        print(err_msg)

        # Write to crash_log.txt
        try:
            from paths import get_data_path
            crash_file = get_data_path("crash_log.txt")
        except Exception:
            crash_file = BASE_DIR / "crash_log.txt"
        try:
            with open(crash_file, "a", encoding="utf-8") as f:

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'=' * 60}\nCRASH REPORT — {timestamp}\n{'=' * 60}\n")
                f.write(err_msg)
        except Exception:
            pass

        # Display native Windows error dialog
        if sys.platform == "win32":
            try:
                import ctypes
                dialog_text = (
                    f"Dump's Test encountered an unexpected error:\n\n"
                    f"{e}\n\n"
                    f"A detailed crash report has been saved to:\n"
                    f"{crash_file}"
                )
                ctypes.windll.user32.MessageBoxW(0, dialog_text, "Dump's Test — Application Error", 0x10)
            except Exception:
                pass

        sys.exit(1)

if __name__ == "__main__":
    main()
