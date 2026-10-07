"""
projector.py — quiz engine for Dump's Test.
"""
import sys
import random
try:
    from rapidfuzz import fuzz
except ImportError:
    class _FuzzFallback:
        @staticmethod
        def ratio(s1, s2):
            import difflib
            return difflib.SequenceMatcher(None, str(s1), str(s2)).ratio() * 100.0
    fuzz = _FuzzFallback()


from settings import settings
from questions_loader import question_loader
from sounds import sounds, voice, stop_music
from language import display, is_open_answer
from terminal import timed_input, clear_screen
from player_info import player

name                   = player.name
num_of_question        = settings.num_of_question
time_for_each_question = settings.time_for_each_question
fuzzy_threshold        = settings.fuzzy_threshold


def _save_recommendation(text: str):
    """Append player suggestion to suggestions.txt next to the game."""
    from pathlib import Path
    suggestions_file = Path(__file__).parent / "suggestions.txt"
    try:
        with open(suggestions_file, "a", encoding="utf-8") as f:
            f.write(f"{name}: {text}\n")
        print("Got it! Your suggestion has been saved. Now back to the quiz…")
    except OSError:
        print("Couldn't save suggestion (file error), but thanks anyway!")


def quiz():
    loader = question_loader()
    selected_questions = loader.loading()

    grade   = 0
    counter = 0

    for i in range(num_of_question):
        counter += 1

        # ── Pick a question ───────────────────────────────────────────────
        question_number = random.choice(list(selected_questions.keys()))
        question        = selected_questions.pop(question_number)

        # ── Display ───────────────────────────────────────────────────────
        print("\n" + "-" * 40)
        print(f"Question {counter}/{num_of_question}")
        print(f"Subject:  {question['subject']}")
        print("-" * 40)
        print(display(question["question"]))

        # ── Choices (only when it's a multiple-choice question) ───────────
        choices_raw = question["choices"]
        if not is_open_answer(choices_raw):
            print()
            for choice in choices_raw.split("|"):
                print(display(choice.strip()))

        print("-" * 40)

        # ── Timed input ───────────────────────────────────────────────────
        answer = timed_input("Your answer: ", time_for_each_question)

        # ── Timeout sound ─────────────────────────────────────────────────
        if answer == "":
            voice("time_out")
            print("No answer — time's up!")

        # ── Quit ──────────────────────────────────────────────────────────
        elif answer.strip().lower() in ("quit", "exit"):
            stop_music()
            sys.exit(f"\nSee you next time, {name}  (((((^_^)))))")

        # ── Recommend ─────────────────────────────────────────────────────
        elif answer.strip().lower() == "recommend":
            suggestion = input("Your suggestion: ").strip()
            if suggestion:
                _save_recommendation(suggestion)
            # Re-ask the current question (don't count it against the player)
            answer = timed_input("Your answer: ", time_for_each_question)
            if answer == "":
                voice("time_out")
                print("No answer — time's up!")

        # ── Empty enter ───────────────────────────────────────────────────
        if answer.strip() == "":
            print("No answer provided.")

        # ── Check answer ──────────────────────────────────────────────────
        answer_clean  = answer.strip().lower()
        correct_clean = question["answer"].strip().lower()

        if len(correct_clean) < 5:
            is_correct = (answer_clean == correct_clean)
        else:
            is_correct = (fuzz.ratio(answer_clean, correct_clean) >= fuzzy_threshold)

        # ── Feedback ──────────────────────────────────────────────────────
        if is_correct:
            grade += 1
            voice("right")
            good = [
                "huh not bad",
                "go go go",
                "so you do have some brain",
                "keep it up dump",
                "you kinda smart",
                "yeah!!",
                "wow even a brainless can answer that",
            ]
            print(random.choice(good))

        else:
            voice("wrong")
            bad = [
                "the same dump I know",
                "do you know something called a brain?",
                "0 > IQ",
                "no no no",
                "wrong again!",
                "did you even think about it?",
            ]
            print(
                f"{random.choice(bad)}: {display(question['answer'])}"
            )

        print("-" * 30)

    return grade, num_of_question
