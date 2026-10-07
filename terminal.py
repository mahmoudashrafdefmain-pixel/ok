"""
terminal.py — cross-platform clear screen and timed keyboard input.
"""
import os
import sys
import time
import platform

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    import msvcrt
else:
    import select
    import tty
    import termios


def clear_screen():
    """Clear the terminal — works on Windows, Linux, and macOS."""
    if _IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")


def timed_input(prompt: str, timeout: int) -> str:
    """
    Show a live countdown while waiting for keyboard input.
    Returns the typed string, or '' if time runs out.
    Works on Windows (msvcrt) and Unix (select + termios).
    """
    answer = ""
    start_time = time.time()
    last_second = timeout

    print(prompt, end="", flush=True)

    if _IS_WINDOWS:
        return _timed_input_windows(prompt, timeout, answer, start_time, last_second)
    else:
        return _timed_input_unix(prompt, timeout, answer, start_time, last_second)


def _timed_input_windows(prompt, timeout, answer, start_time, last_second):
    while True:
        elapsed = time.time() - start_time
        remaining = timeout - int(elapsed)

        if remaining <= 0:
            print("\nTIME IS UP!")
            return ""

        if remaining != last_second:
            print(
                f"\rTime remaining: {remaining:2d}s | {prompt}{answer}",
                end="",
                flush=True,
            )
            last_second = remaining

        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == "\r":
                print()
                return answer
            elif key == "\b":
                if answer:
                    answer = answer[:-1]
                    print(
                        f"\rTime remaining: {remaining:2d}s | {prompt}{answer} ",
                        end="",
                        flush=True,
                    )
            elif key.isprintable():
                answer += key
                print(key, end="", flush=True)

        time.sleep(0.05)


def _timed_input_unix(prompt, timeout, answer, start_time, last_second):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            elapsed = time.time() - start_time
            remaining = timeout - int(elapsed)

            if remaining <= 0:
                print("\nTIME IS UP!")
                return ""

            if remaining != last_second:
                print(
                    f"\rTime remaining: {remaining:2d}s | {prompt}{answer}",
                    end="",
                    flush=True,
                )
                last_second = remaining

            rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
            if rlist:
                key = sys.stdin.read(1)
                if key in ("\r", "\n"):
                    print()
                    return answer
                elif key in ("\x7f", "\x08"):  # backspace / delete
                    if answer:
                        answer = answer[:-1]
                        print(
                            f"\rTime remaining: {remaining:2d}s | {prompt}{answer} ",
                            end="",
                            flush=True,
                        )
                elif key == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt
                elif key.isprintable():
                    answer += key
                    print(key, end="", flush=True)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
