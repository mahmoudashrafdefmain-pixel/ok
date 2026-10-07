"""
player_info.py — collects player name, language, level, and subject choices.
Safe for GUI imports (no interactive terminal input at import time).
"""
import sys
from pathlib import Path
from subs import subject

space = "-_-_-" * 30


class player_info(subject):

    def __init__(self, name, language, lvl, number_of_sub, subject_choosin):
        self.subject_choosin = subject_choosin
        self.name            = name
        self.language        = language
        self.lvl             = lvl
        self.number_of_sub   = number_of_sub


def validation():
    """Terminal interactive validation function — only called if run directly in CLI mode."""
    if not sys.stdin or not sys.stdin.isatty():
        return player_info("Dump Player", "2", "1", 3, ["math", "science", "programming"])

    try:
        from sounds import play_music
        play_music("music")
    except Exception:
        pass

    from terminal import clear_screen

    # ── Name ─────────────────────────────────────────────────────────────────
    clear_screen()
    print(space)
    name = input("do you have a name? ").strip()

    while name.isdigit() or name == "":
        clear_screen()
        print(space)
        print("your name can't be numbers or empty, you dump\n")
        name = input("do you have a name? ").strip()

    # ── Language ─────────────────────────────────────────────────────────────
    clear_screen()
    print(space)
    language = input("arabic[1] or english[2]: ").strip()

    while language not in ("1", "2"):
        clear_screen()
        print(space)
        print("type 1 for arabic and type 2 for english\n")
        language = input("arabic[1] or english[2]: ").strip()

    # ── Level ─────────────────────────────────────────────────────────────────
    clear_screen()
    print(space)
    lvl = input(
        f"{name} how dump are you?\n"
        "  a little [1]  |  above average [2]  |  expert dump [3]  |  random [r]\n"
        "→ "
    ).strip().lower()

    while lvl not in ("1", "2", "3", "r"):
        clear_screen()
        print(space)
        print("brain.exe has stopped working — type 1, 2, 3, or r\n")
        lvl = input(
            f"{name} how dump are you?\n"
            "  a little [1]  |  above average [2]  |  expert dump [3]  |  random [r]\n"
            "→ "
        ).strip().lower()

    # ── Subject count ─────────────────────────────────────────────────────────
    while True:
        clear_screen()
        print(space)
        print("this is how I'm going to test how dump you are:\n")
        print(
            "   m → math          s → science       l → literature\n"
            "   h → history       p → programming   g → general\n"
            "   e → extreme       a → anime         f → football\n"
        )
        number_of_sub = input(
            "how many subjects are you going for? [2 to 9]: "
        ).strip()

        if not number_of_sub.isdigit():
            print("digits only, you baby")
            continue
        number_of_sub = int(number_of_sub)

        if number_of_sub < 2 or number_of_sub > 9:
            print("only 2 to 9 subjects, baby\n")
            continue
        break

    # ── Subject selection ─────────────────────────────────────────────────────
    print(f"\n___--- choose your {number_of_sub} subjects, dump ---___\n")
    clear_screen()
    print(space)

    subject_choosin = []
    for _ in range(number_of_sub):
        while True:
            print(space)
            current_sub = input("Subject: ").strip().lower()

            if len(current_sub) == 1:
                current_sub = player_info.subject_letters.get(current_sub)

            if current_sub not in player_info.subjects:
                clear_screen()
                print(space)
                print("Invalid subject. Try again.")
                continue

            if current_sub in subject_choosin:
                clear_screen()
                print(space)
                print(f"'{current_sub}' already chosen, dump.")
                continue

            subject_choosin.append(current_sub)
            break

    return player_info(name, language, lvl, number_of_sub, subject_choosin)


# Default fallback player object for module imports without running input()
player = player_info("Dump Player", "2", "1", 3, ["math", "science", "programming"])

if __name__ == "__main__":
    player = validation()