"""
game/pro_features.py — Pro gameplay lifelines and power systems for Dump's Test.
"""
import time
from sounds import voice


class ProSystems:
    def __init__(self):
        self.overdrive_meter = 0
        self.is_overdrive_active = False
        self.overdrive_duration = 0.0
        self.has_shield = True
        self.shield_active = False
        self.gamble_mode = False

    def reset_round(self):
        self.overdrive_meter = 0
        self.is_overdrive_active = False
        self.has_shield = True
        self.shield_active = False
        self.gamble_mode = False

    def on_correct_answer(self) -> int:
        base_points = 1
        if not self.is_overdrive_active:
            self.overdrive_meter = min(100, self.overdrive_meter + 34)
            if self.overdrive_meter >= 100:
                self.is_overdrive_active = True
                self.overdrive_duration = time.time() + 12.0
                voice("win")

        multiplier = 1
        if self.is_overdrive_active:
            if time.time() < self.overdrive_duration:
                multiplier = 3
            else:
                self.is_overdrive_active = False
                self.overdrive_meter = 0

        if self.gamble_mode:
            multiplier *= 3
            self.gamble_mode = False

        # Cap total multiplier to maximum 3x to prevent leaderboard corruption
        multiplier = min(multiplier, 3)

        return base_points * multiplier

    def on_wrong_answer(self) -> bool:
        if self.shield_active:
            self.shield_active = False
            self.has_shield = False
            voice("shield")
            return True
        self.overdrive_meter = max(0, self.overdrive_meter - 40)
        self.is_overdrive_active = False
        self.gamble_mode = False
        return False


class ProFeaturesManager:
    def __init__(self):
        self.used_5050 = False
        self.used_freeze = False
        self.used_swap = False
        self.used_poll = False
        self.systems = ProSystems()

    def reset(self):
        self.used_5050 = False
        self.used_freeze = False
        self.used_swap = False
        self.used_poll = False
        self.systems.reset_round()

    def use_50_50(self) -> bool:
        if not self.used_5050:
            self.used_5050 = True
            return True
        return False

    def use_5050(self) -> bool:
        return self.use_50_50()

    def use_freeze_time(self) -> bool:
        if not self.used_freeze:
            self.used_freeze = True
            return True
        return False

    def use_freeze(self) -> bool:
        return self.use_freeze_time()

    def use_swap_question(self) -> bool:
        if not self.used_swap:
            self.used_swap = True
            return True
        return False

    def use_swap(self) -> bool:
        return self.use_swap_question()

    def use_poll(self) -> bool:
        if not self.used_poll:
            self.used_poll = True
            return True
        return False

    def use_curse(self) -> bool:
        return self.use_poll()
