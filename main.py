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

        # Write to crash_log.txt in multiple safe locations
        try:
            from paths import get_data_path
            crash_file = get_data_path("crash_log.txt")
        except Exception:
            crash_file = BASE_DIR / "crash_log.txt"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"\n{'=' * 60}\nCRASH REPORT — {timestamp}\n{'=' * 60}\n{err_msg}\n"
        try:
            with open(crash_file, "a", encoding="utf-8") as f:
                f.write(report)
        except Exception:
            pass

        # Try Android public storage fallback for easy user retrieval
        for alt_path in ["/sdcard/Download/dumps_test_crash.txt", "/storage/emulated/0/Download/dumps_test_crash.txt"]:
            try:
                with open(alt_path, "a", encoding="utf-8") as f:
                    f.write(report)
                break
            except Exception:
                pass

        # Try Android Toast
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Toast = autoclass('android.widget.Toast')
            String = autoclass('java.lang.String')
            toast_msg = String(f"Dump's Test Error: {e}")
            PythonActivity.mActivity.runOnUiThread(
                lambda: Toast.makeText(PythonActivity.mActivity, toast_msg, Toast.LENGTH_LONG).show()
            )
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
        else:
            # On Android / Linux: render visible on-screen Pygame crash screen
            try:
                import time
                import pygame
                pygame.init()
                try:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                except Exception:
                    screen = pygame.display.set_mode((1280, 720))
                sw, sh = screen.get_size()
                font = pygame.font.Font(None, max(18, int(sh / 32)))
                clock = pygame.time.Clock()

                lines = [
                    "Dump's Test v17.0 — Application Error",
                    f"Error: {e}",
                    f"Crash file: {crash_file}",
                    "----------------------------------------"
                ]
                lines.extend(err_msg.strip().splitlines()[-14:])
                lines.append("Tap screen to exit...")

                start_t = time.time()
                running = True
                while running and (time.time() - start_t < 25):
                    for ev in pygame.event.get():
                        if ev.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, getattr(pygame, 'FINGERDOWN', -1)):
                            running = False
                    screen.fill((30, 10, 18))
                    y = 20
                    for line in lines:
                        surf = font.render(line[:90], True, (255, 230, 230))
                        screen.blit(surf, (20, y))
                        y += font.get_linesize() + 3
                        if y > sh - 25:
                            break
                    pygame.display.flip()
                    clock.tick(30)
                pygame.quit()
            except Exception:
                pass

        sys.exit(1)

if __name__ == "__main__":
    main()
