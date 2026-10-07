# -*- coding: utf-8 -*-
"""
ui/investigation_screen.py — Interactive Crime Investigation Mode UI for Dump's Test v15.0.
Features:
  - 20 Classified Detective Cases Selection Hub with pagination & difficulty badges.
  - Interactive Case Briefing with suspect dossiers.
  - Active Investigation Terminal: 10-message narrative branching,
    4 tactical options per turn, hidden score engine, atmospheric sentiment indicators.
  - 5 Advanced Detective Features:
      1. Forensic Lab Evidence Magnifier & Deep Spectral Analysis
      2. Suspect Interrogation & Alibi Contradiction Cross-Examination
      3. Detective Intuition / Sherlock Insight Lifeline ([I] key / button)
      4. Crime Scene Reconstruction Simulation (5-Phase chronological flow)
      5. Career Detective Rank & Badge Progression System (XP & Badges)
  - Interactive Case Dossier Notebook Modal (Clues, Suspects, Timeline, Forensic Lab, Reconstruction).
  - Turn 10 Final Accusation Roster.
  - Multi-Tier Dramatic Verdict Screen (S, A, B, C, D, F) with narrative solution & XP/Coins/Badges.
"""
import math
import time
import pygame
from pathlib import Path

from ui.fonts import render_text
from ui.widgets import (
    Button, draw_rounded_rect, BG_DARK, BG_CARD, CARD_BORDER,
    PRIMARY_GLOW, SECONDARY, ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED,
    TEXT_WHITE, TEXT_MUTED
)
from ui.backgrounds import AnimatedBackground
from game.investigation import (
    get_detective_cases,
    load_case,
    InvestigationCase,
    get_available_cases,
)
from sounds import voice

_BG = AnimatedBackground()

# Custom palette accents for investigation
ACCENT_CYAN = (76, 201, 240)
ACCENT_PURPLE = (131, 56, 236)
ACCENT_ORANGE = (251, 86, 7)
COLOR_CRITICAL = (255, 107, 107)
COLOR_SUPPORTING = (78, 205, 196)
COLOR_HERRING = (160, 160, 160)

CATEGORY_COLORS = {
    "Murder": ACCENT_RED,
    "Theft": ACCENT_GOLD,
    "Kidnapping": ACCENT_CYAN,
    "Robbery": ACCENT_ORANGE,
    "Disappearance": ACCENT_PURPLE,
    "Arson": (255, 75, 75),
    "Blackmail": (255, 140, 0),
    "Smuggling": (0, 180, 216),
    "Corporate Crime": (144, 224, 239),
    "Fraud": ACCENT_GOLD,
    "Poisoning": (106, 76, 147),
    "Cyber Extortion": (0, 245, 212),
    "Conspiracy": (247, 37, 133),
    "Serial Murder": (217, 4, 41),
    "Perfect Crime": (255, 215, 0),
}

AR_PREFIXES = ["أ.", "ب.", "ج.", "د."]


def draw_text(surface: pygame.Surface, text: str, x: int, y: int, size: int = 16, color: tuple = TEXT_WHITE, bold: bool = False, center: bool = False, is_arabic: bool = False):
    """Render and blit text onto surface with optional centering."""
    s = render_text(str(text), size=size, color=color, bold=bold, is_arabic=is_arabic)
    if center:
        rect = s.get_rect(center=(x, y))
        surface.blit(s, rect)
    else:
        surface.blit(s, (x, y))


class InvestigationScreen:
    """
    Complete Investigation Screen:
      Phase 0: Case Selection Hub (all 20 cases, 5 per page)
      Phase 1: Case Briefing
      Phase 2: Active Investigation Gameplay (Turns 1-9)
      Phase 3: Turn 10 Final Accusation Roster
      Phase 4: Case Results & Dramatic Verdict Stamp (S, A, B, C, D, F)
    """

    def __init__(self, app):
        self.app = app
        self.phase = 0  # 0=hub, 1=briefing, 2=gameplay, 3=accusation, 4=results
        self.case: InvestigationCase | None = None

        # Hub pagination
        self.cases_list = []
        self.current_page = 0
        self.cases_per_page = 5
        self.total_pages = 1

        # Interactive Case Dossier modal state (5 Tabs)
        # 0=clues, 1=suspects, 2=timeline, 3=lab, 4=recon
        self.show_dossier = False
        self.dossier_tab = 0
        self.active_interrogation_name = ""

        # Final Accusation selection
        self.selected_suspect_name = ""

        # Feedback banner
        self.feedback_text = ""
        self.feedback_timer = 0.0
        self.feedback_color = ACCENT_GREEN
        self.pending_advance = False

        # Universal Navigation Buttons
        self.btn_back = Button((40, 30, 140, 42), "← BACK", callback=self._go_back, color=BG_CARD, font_size=15)
        # Feature 3: Intuition button
        self.btn_intuition = Button((840, 30, 200, 42), "🧠 INTUITION [I] (2)", callback=self._use_intuition, color=(60, 40, 90), text_color=ACCENT_GOLD, font_size=13, bold=True)
        self.btn_dossier = Button((1060, 30, 180, 42), "📋 CASE DOSSIER", callback=self._toggle_dossier, color=PRIMARY_GLOW, text_color=BG_DARK, font_size=14, bold=True)
        self.btn_close_dossier = Button((1045, 75, 80, 36), "✖ CLOSE", callback=self._toggle_dossier, color=ACCENT_RED, text_color=TEXT_WHITE, font_size=13, bold=True)

        # 5 Dossier Tab Buttons
        self.btn_tab_clues = Button((140, 75, 160, 36), "🔬 Clues", callback=lambda: self._set_dossier_tab(0), color=BG_CARD, font_size=13)
        self.btn_tab_suspects = Button((305, 75, 160, 36), "👥 Suspects", callback=lambda: self._set_dossier_tab(1), color=BG_CARD, font_size=13)
        self.btn_tab_timeline = Button((470, 75, 160, 36), "🕐 Timeline", callback=lambda: self._set_dossier_tab(2), color=BG_CARD, font_size=13)
        self.btn_tab_lab = Button((635, 75, 180, 36), "🧪 Forensic Lab", callback=lambda: self._set_dossier_tab(3), color=BG_CARD, font_size=13)
        self.btn_tab_recon = Button((820, 75, 210, 36), "🕵️ Reconstruction", callback=lambda: self._set_dossier_tab(4), color=BG_CARD, font_size=13)

        self.btn_back_from_interrogation = Button((880, 140, 220, 36), "← Back to Suspects", callback=self._clear_interrogation, color=SECONDARY, text_color=TEXT_WHITE, font_size=13, bold=True)

        # Pagination buttons
        self.btn_prev_page = Button((430, 645, 140, 42), "◀ PREV", callback=self._prev_page, color=BG_CARD, font_size=15)
        self.btn_next_page = Button((710, 645, 140, 42), "NEXT ▶", callback=self._next_page, color=BG_CARD, font_size=15)

        # Briefing launch button
        self.btn_launch_investigation = Button((500, 615, 280, 52), "🔍 BEGIN INVESTIGATION", callback=self._start_gameplay, color=ACCENT_GOLD, text_color=BG_DARK, font_size=17, bold=True)

        # Accusation confirmation button
        self.btn_confirm_accusation = Button((470, 625, 340, 52), "⚡ DECLARE FORMAL ACCUSATION", callback=self._submit_accusation, color=ACCENT_GOLD, text_color=BG_DARK, font_size=16, bold=True)

        # Results navigation buttons
        self.btn_another_case = Button((380, 625, 240, 50), "🔄 Select Another Case", callback=self._reset_to_hub, color=PRIMARY_GLOW, text_color=BG_DARK, font_size=16, bold=True)
        self.btn_return_menu = Button((660, 625, 240, 50), "🏠 Return to Main Menu", callback=lambda: app.change_screen("menu"), color=BG_CARD, font_size=16)

        # Dynamic gameplay and dossier buttons
        self.hub_case_buttons = []
        self.option_buttons = []
        self.suspect_cards_buttons = []
        self.lab_analyze_buttons = []
        self.suspect_interrogate_buttons = []

        self.refresh_labels()
        self._load_cases_data()

    @property
    def is_ar(self) -> bool:
        """True if the active game language is Arabic."""
        return str(getattr(self.app, "language", "2")) == "1"

    def refresh_labels(self):
        """Update button labels and texts based on active application language."""
        charges = getattr(self.case, "intuition_charges", 2) if self.case else 2
        if self.is_ar:
            self.btn_back.text = "← رجوع"
            self.btn_intuition.text = f"🧠 إلهام [{charges}]"
            self.btn_dossier.text = "📋 ملف القضية"
            self.btn_close_dossier.text = "✖ إغلاق"
            self.btn_tab_clues.text = "🔬 الأدلة"
            self.btn_tab_suspects.text = "👥 المشتبه بهم"
            self.btn_tab_timeline.text = "🕐 الخط الزمني"
            self.btn_tab_lab.text = "🧪 فحص الأدلة"
            self.btn_tab_recon.text = "🕵️ إعادة البناء"
            self.btn_back_from_interrogation.text = "← كل المشتبه بهم"
            self.btn_prev_page.text = "◀ السابق"
            self.btn_next_page.text = "التالي ▶"
            self.btn_launch_investigation.text = "🔍 بدء التحقيق الجنائي"
            self.btn_confirm_accusation.text = "⚡ إعلان الاتهام القضائي الرسمي"
            self.btn_another_case.text = "🔄 اختيار قضية أخرى"
            self.btn_return_menu.text = "🏠 العودة للقائمة الرئيسية"
        else:
            self.btn_back.text = "← BACK"
            self.btn_intuition.text = f"🧠 INTUITION [{charges}]"
            self.btn_dossier.text = "📋 CASE DOSSIER"
            self.btn_close_dossier.text = "✖ CLOSE"
            self.btn_tab_clues.text = "🔬 Clues"
            self.btn_tab_suspects.text = "👥 Suspects"
            self.btn_tab_timeline.text = "🕐 Timeline"
            self.btn_tab_lab.text = "🧪 Forensic Lab"
            self.btn_tab_recon.text = "🕵️ Reconstruction"
            self.btn_back_from_interrogation.text = "← All Suspects"
            self.btn_prev_page.text = "◀ PREV"
            self.btn_next_page.text = "NEXT ▶"
            self.btn_launch_investigation.text = "🔍 BEGIN INVESTIGATION"
            self.btn_confirm_accusation.text = "⚡ DECLARE FORMAL ACCUSATION"
            self.btn_another_case.text = "🔄 Select Another Case"
            self.btn_return_menu.text = "🏠 Return to Main Menu"

    def on_enter(self):
        """Lifecycle hook when navigating to Investigation Screen."""
        self._reset_to_hub()
        self.feedback_text = ""
        self.feedback_timer = 0.0

    def _load_cases_data(self):
        """Fetch cases from database and calculate pages."""
        lang = str(getattr(self.app, "language", "2"))
        self.cases_list = get_detective_cases(lang=lang)
        if not self.cases_list:
            self.cases_list = get_available_cases(category="detective", lang=lang)
        self.total_pages = max(1, math.ceil(len(self.cases_list) / self.cases_per_page))
        self._build_hub_buttons()

    def _build_hub_buttons(self):
        """Build clickable case cards for the active hub page."""
        self.hub_case_buttons = []
        start_idx = self.current_page * self.cases_per_page
        end_idx = min(len(self.cases_list), start_idx + self.cases_per_page)
        page_cases = self.cases_list[start_idx:end_idx]

        for i, c in enumerate(page_cases):
            y = 140 + i * 96

            def make_cb(cid=c["id"]):
                return lambda: self._select_case(cid)

            btn = Button((240, y, 800, 84), "", callback=make_cb(), color=BG_CARD)
            self.hub_case_buttons.append((btn, c))

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._build_hub_buttons()
            voice("click")

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._build_hub_buttons()
            voice("click")

    def _select_case(self, case_id: str):
        """Load selected case into active session and go to Briefing (Phase 1)."""
        lang = str(getattr(self.app, "language", "2"))
        self.case = load_case(case_id, lang=lang)
        if self.case:
            self.phase = 1
            self.show_dossier = False
            self.active_interrogation_name = ""
            self.selected_suspect_name = ""
            self.refresh_labels()
            voice("select")

    def _start_gameplay(self):
        """Transition from Briefing into Active Investigation (Phase 2)."""
        if self.case:
            self.phase = 2
            self.feedback_text = ""
            self.feedback_timer = 0.0
            self.pending_advance = False
            self.show_dossier = False
            self.active_interrogation_name = ""
            self.refresh_labels()
            if getattr(self.case, "questions", None) and not getattr(self.case, "messages", None):
                self.case.start_question()
                self._build_legacy_question_buttons()
            else:
                self._build_gameplay_options()
            voice("start")

    # ── FEATURE 3: INTUITION ACTION ──
    def _use_intuition(self):
        """Trigger Sherlock Intuition lifeline."""
        if not self.case:
            return
        res = self.case.use_detective_intuition()
        self.refresh_labels()
        if res.get("success"):
            self.feedback_text = res.get("whisper", "")
            self.feedback_color = ACCENT_GOLD
            self.feedback_timer = 5.0
            voice("right")
            e_idx = res.get("eliminated_idx")
            r_idx = res.get("recommended_idx")
            if e_idx is not None and 0 <= e_idx < len(self.option_buttons):
                btn_e = self.option_buttons[e_idx]
                btn_e.color = (45, 30, 45)
                btn_e.is_disabled = True
                if not btn_e.text.startswith("✖ "):
                    btn_e.text = f"✖ {btn_e.text}"
            if r_idx is not None and 0 <= r_idx < len(self.option_buttons):
                btn_r = self.option_buttons[r_idx]
                btn_r.color = (30, 65, 50)
        else:
            self.feedback_text = res.get("reason", "No intuition charges remaining!")
            self.feedback_color = ACCENT_RED
            self.feedback_timer = 2.5
            voice("wrong")

    def _build_legacy_question_buttons(self):
        """Build clickable choices for legacy question-based cases."""
        self.option_buttons = []
        if not self.case or self.case.is_complete:
            return
        q = self.case.current_question
        if not q:
            return
        raw = q.get("choices", [])
        if isinstance(raw, str):
            choices = [c.strip() for c in raw.split("|")]
        else:
            choices = list(raw)
        is_arabic = self.is_ar
        for i, opt_text in enumerate(choices[:4]):
            y = 350 + i * 66
            def make_cb(text=opt_text):
                return lambda: self._submit_answer(text)
            prefix = f"{AR_PREFIXES[i]}" if is_arabic else f"{chr(65+i)}."
            btn = Button((180, y, 920, 58), f"{prefix}  {opt_text}", callback=make_cb(), color=BG_CARD, font_size=15, align="left")
            self.option_buttons.append(btn)

    def _submit_answer(self, chosen: str):
        """Submit answer for legacy question cases."""
        if not self.case:
            return
        q = self.case.current_question
        if not q or self.case.is_complete:
            return

        time_taken = time.time() - self.case.q_start_time
        correct_answer = q.get("answer", "").strip().lower()
        chosen_clean = chosen.strip().lower()
        is_correct = chosen_clean == correct_answer

        if is_correct:
            self.case.correct_count += 1
            self.case.evidence_score = min(100, self.case.evidence_score + 20)
            self.feedback_text = "✨ استنتاج دقيق! تم إثبات الرابط الجنائي." if self.is_ar else "✨ ACCURATE DEDUCTION! Forensic connection confirmed."
            self.feedback_color = ACCENT_GREEN
            voice("right")
        else:
            self.case.wrong_count += 1
            expected = q.get('answer', '')
            self.feedback_text = f"❌ استنتاج خاطئ! الإجابة الصحيحة: {expected}" if self.is_ar else f"❌ FLAWED CONCLUSION! Expected: {expected}"
            self.feedback_color = ACCENT_RED
            voice("wrong")

        self.case.total_time += min(time_taken, self.case.q_time_limit)
        self.case.answers_log.append({
            "question": q["question"],
            "chosen": chosen,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "time_taken": round(time_taken, 2),
        })

        self.feedback_timer = 1.7
        self.pending_advance = True

    def _build_gameplay_options(self):
        """Construct the 4 tactical decision buttons for the active message."""
        self.option_buttons = []
        if not self.case or self.case.is_complete:
            return

        if self.case.is_final_accusation_step:
            self.phase = 3
            self._build_accusation_roster()
            return

        msg = self.case.current_message
        if not msg:
            return

        opts = msg.get("options", [])
        is_arabic = self.is_ar
        for i, opt in enumerate(opts[:4]):
            y = 350 + i * 66

            def make_cb(idx=i):
                return lambda: self._on_choose_option(idx)

            prefix = f"{AR_PREFIXES[i]}" if is_arabic else f"{chr(65+i)}."
            btn = Button((180, y, 920, 58), f"{prefix}  {opt.get('text', '')}", callback=make_cb(), color=BG_CARD, font_size=15, align="left")
            self.option_buttons.append(btn)

    def _on_choose_option(self, option_idx: int):
        """Execute chosen option, update feedback, and advance to next turn."""
        if not self.case:
            return

        res = self.case.choose_turn_option(option_idx)
        if not res.get("accepted"):
            return

        self.feedback_text = res.get("feedback", "")
        self.feedback_color = ACCENT_GREEN if res.get("clue_unlocked") else ACCENT_CYAN
        self.feedback_timer = 2.4
        voice("right" if res.get("clue_unlocked") else "click")

        if res.get("is_accusation") or self.case.is_final_accusation_step:
            self.phase = 3
            self._build_accusation_roster()
        else:
            self._build_gameplay_options()

    def _build_accusation_roster(self):
        """Build suspect selection cards for Message 10 Final Accusation."""
        self.suspect_cards_buttons = []
        if not self.case:
            return

        suspects = self.case.get_suspect_profiles()
        card_w = 340
        card_h = 90

        for i, s in enumerate(suspects):
            col = i % 2
            row = i // 2
            x = 280 + col * 370
            y = 210 + row * 100

            def make_cb(name=s["name"]):
                return lambda: self._select_suspect_accusation(name)

            btn = Button((x, y, card_w, card_h), "", callback=make_cb(), color=BG_CARD)
            self.suspect_cards_buttons.append((btn, s))

        if suspects and not self.selected_suspect_name:
            self.selected_suspect_name = suspects[0]["name"]

    def _select_suspect_accusation(self, name: str):
        self.selected_suspect_name = name
        voice("click")

    def _submit_accusation(self):
        """Submit final accusation and transition to dramatic results screen."""
        if not self.case or not self.selected_suspect_name:
            return

        username = getattr(self.app, "player_name", None)
        eval_res = self.case.make_final_accusation(self.selected_suspect_name, username=username)
        self.phase = 4

        if eval_res.get("is_won"):
            voice("win")
        else:
            voice("game_over")

    def _toggle_dossier(self):
        """Toggle Case Dossier modal."""
        self.show_dossier = not self.show_dossier
        if self.show_dossier:
            self._build_dossier_tab_buttons()
        voice("select")

    def _set_dossier_tab(self, tab_idx: int):
        self.dossier_tab = tab_idx
        self.active_interrogation_name = ""
        self._build_dossier_tab_buttons()
        voice("click")

    def _clear_interrogation(self):
        self.active_interrogation_name = ""
        self._build_dossier_tab_buttons()
        voice("click")

    # ── BUILD DOSSIER INTERACTIVE BUTTONS ──
    def _build_dossier_tab_buttons(self):
        self.lab_analyze_buttons = []
        self.suspect_interrogate_buttons = []
        if not self.case:
            return

        # Tab 1: Suspect Interrogation Buttons
        if self.dossier_tab == 1 and not self.active_interrogation_name:
            suspects = self.case.get_suspect_profiles()
            for i, s in enumerate(suspects[:4]):
                sy = 175 + i * 110
                btn_txt = "⚖️ استجواب" if self.is_ar else "⚖️ INTERROGATE"
                def make_interrogate_cb(s_name=s["name"]):
                    return lambda: self._trigger_interrogation(s_name)
                btn = Button((950, sy + 30, 150, 36), btn_txt, callback=make_interrogate_cb(), color=ACCENT_GOLD, text_color=BG_DARK, font_size=12, bold=True)
                self.suspect_interrogate_buttons.append(btn)

        # Tab 3: Forensic Lab Analyze Buttons
        elif self.dossier_tab == 3:
            clues = self.case.get_unlocked_clues()
            for i, c in enumerate(clues[:5]):
                cid = c.get("id", f"clue_{i+1}")
                is_analyzed = cid in self.case.analyzed_clues
                cy = 175 + i * 88
                if not is_analyzed:
                    btn_txt = "🔬 فحص (+15)" if self.is_ar else "🔬 ANALYZE (+15)"
                    def make_analyze_cb(target_id=cid):
                        return lambda: self._trigger_lab_analysis(target_id)
                    btn = Button((960, cy + 22, 140, 36), btn_txt, callback=make_analyze_cb(), color=PRIMARY_GLOW, text_color=BG_DARK, font_size=12, bold=True)
                    self.lab_analyze_buttons.append(btn)

    # ── FEATURE 1 ACTION: FORENSIC LAB ──
    def _trigger_lab_analysis(self, clue_id: str):
        if not self.case:
            return
        res = self.case.analyze_clue(clue_id)
        if res.get("success"):
            voice("right")
            self.feedback_text = res.get("finding", "")
            self.feedback_color = ACCENT_GREEN
            self.feedback_timer = 4.0
            self._build_dossier_tab_buttons()

    # ── FEATURE 2 ACTION: INTERROGATION ──
    def _trigger_interrogation(self, suspect_name: str):
        if not self.case:
            return
        self.active_interrogation_name = suspect_name
        self.case.interrogate_suspect(suspect_name)
        voice("select")

    def _go_back(self):
        """Navigation back handler."""
        if self.show_dossier:
            if self.active_interrogation_name:
                self.active_interrogation_name = ""
                self._build_dossier_tab_buttons()
            else:
                self.show_dossier = False
            return
        if self.phase == 0:
            self.app.change_screen("menu")
        elif self.phase == 1:
            self.phase = 0
            self._load_cases_data()
        elif self.phase in (2, 3):
            self.phase = 1
        elif self.phase == 4:
            self._reset_to_hub()

    def _reset_to_hub(self):
        self.phase = 0
        self.case = None
        self.show_dossier = False
        self.active_interrogation_name = ""
        self.selected_suspect_name = ""
        self.feedback_text = ""
        self.refresh_labels()
        self._load_cases_data()

    def update(self):
        dt = 1.0 / 60.0
        mp = pygame.mouse.get_pos()

        # Update universal navigation buttons
        self.btn_back.update(mp)
        if self.phase in (1, 2, 3):
            self.btn_intuition.update(mp)
        self.btn_dossier.update(mp)

        if self.show_dossier:
            self.btn_close_dossier.update(mp)
            self.btn_tab_clues.update(mp)
            self.btn_tab_suspects.update(mp)
            self.btn_tab_timeline.update(mp)
            self.btn_tab_lab.update(mp)
            self.btn_tab_recon.update(mp)

            if self.dossier_tab == 1:
                if self.active_interrogation_name:
                    self.btn_back_from_interrogation.update(mp)
                else:
                    for btn in self.suspect_interrogate_buttons:
                        btn.update(mp)
            elif self.dossier_tab == 3:
                for btn in self.lab_analyze_buttons:
                    btn.update(mp)

        if self.phase == 0:
            self.btn_prev_page.update(mp)
            self.btn_next_page.update(mp)
            for btn, _ in self.hub_case_buttons:
                btn.update(mp)
        elif self.phase == 1:
            self.btn_launch_investigation.update(mp)
        elif self.phase == 2:
            for btn in self.option_buttons:
                btn.update(mp)
        elif self.phase == 3:
            self.btn_confirm_accusation.update(mp)
            for btn, _ in self.suspect_cards_buttons:
                btn.update(mp)
        elif self.phase == 4:
            self.btn_another_case.update(mp)
            self.btn_return_menu.update(mp)

        if self.feedback_timer > 0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)
            if self.feedback_timer <= 0.0 and self.pending_advance:
                self.pending_advance = False
                if self.case and getattr(self.case, "questions", None) and not getattr(self.case, "messages", None):
                    self.case.current_q_idx += 1
                    if self.case.current_q_idx >= len(self.case.questions):
                        self.case._finalize_legacy()
                        self.phase = 4
                    else:
                        self.case.start_question()
                        self._build_legacy_question_buttons()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if self.phase in (1, 2, 3):
                    self._toggle_dossier()
                    return True
            elif event.key == pygame.K_i:
                if self.phase in (1, 2, 3):
                    self._use_intuition()
                    return True
            elif event.key == pygame.K_ESCAPE:
                if self.show_dossier:
                    if self.active_interrogation_name:
                        self.active_interrogation_name = ""
                        self._build_dossier_tab_buttons()
                    else:
                        self.show_dossier = False
                    return True
                else:
                    if self.phase == 0 or self.phase == 4:
                        self.app.change_screen("menu")
                        return True
                    elif self.phase in (1, 2, 3):
                        self.phase = 0
                        return True

        if self.show_dossier:
            if self.btn_close_dossier.handle_event(event): return True
            if self.btn_tab_clues.handle_event(event): return True
            if self.btn_tab_suspects.handle_event(event): return True
            if self.btn_tab_timeline.handle_event(event): return True
            if self.btn_tab_lab.handle_event(event): return True
            if self.btn_tab_recon.handle_event(event): return True

            if self.dossier_tab == 1:
                if self.active_interrogation_name:
                    if self.btn_back_from_interrogation.handle_event(event): return True
                else:
                    for btn in self.suspect_interrogate_buttons:
                        if btn.handle_event(event): return True
            elif self.dossier_tab == 3:
                for btn in self.lab_analyze_buttons:
                    if btn.handle_event(event): return True
            return True

        if self.btn_back.handle_event(event):
            return True

        if self.phase in (1, 2, 3):
            if self.btn_intuition.handle_event(event):
                return True

        if self.phase == 0:
            if self.btn_prev_page.handle_event(event): return True
            if self.btn_next_page.handle_event(event): return True
            for btn, _ in self.hub_case_buttons:
                if btn.handle_event(event):
                    return True

        elif self.phase == 1:
            if self.btn_dossier.handle_event(event): return True
            if self.btn_launch_investigation.handle_event(event): return True

        elif self.phase == 2:
            if self.btn_dossier.handle_event(event): return True
            for btn in self.option_buttons:
                if btn.handle_event(event):
                    return True

        elif self.phase == 3:
            if self.btn_dossier.handle_event(event): return True
            if self.btn_confirm_accusation.handle_event(event): return True
            for btn, _ in self.suspect_cards_buttons:
                if btn.handle_event(event):
                    return True

        elif self.phase == 4:
            if self.btn_another_case.handle_event(event): return True
            if self.btn_return_menu.handle_event(event): return True

        return False

    def draw(self, surface: pygame.Surface):
        _BG.draw(surface)

        if self.phase == 0:
            self._draw_hub(surface)
        elif self.phase == 1:
            self._draw_briefing(surface)
        elif self.phase == 2:
            self._draw_gameplay(surface)
        elif self.phase == 3:
            self._draw_accusation(surface)
        elif self.phase == 4:
            self._draw_results(surface)

        if self.show_dossier:
            self._draw_dossier_modal(surface)

    # ── DRAW PHASE 0: CASE SELECTION HUB ──
    def _draw_hub(self, surface: pygame.Surface):
        self.btn_back.draw(surface)

        career = {"rank": "Rookie Sleuth", "icon": "🔰", "xp": 0, "next_rank_xp": 200, "badges": [], "solved_count": 0}
        try:
            from game.accounts import get_detective_career
            p_name = getattr(self.app, "player_name", "Player")
            career = get_detective_career(p_name, is_arabic=self.is_ar)
        except Exception:
            pass

        rank_title = f"{career.get('icon', '🎖️')} {career.get('rank', 'Rookie Sleuth')}"
        xp_txt = f"XP: {career.get('xp', 0)} / {career.get('next_rank_xp', 200)}"
        solved_txt = f"{career.get('solved_count', 0)}/20 Solved" if not self.is_ar else f"{career.get('solved_count', 0)}/20 قضية محلولة"
        badges_cnt = len(career.get("badges", []))
        badges_txt = f"🏅 {badges_cnt} Badges" if not self.is_ar else f"🏅 {badges_cnt} أوسمة جنائية"

        if self.is_ar:
            draw_text(surface, "مكتب التحقيقات الجنائية والمباحث", 640, 32, size=26, color=ACCENT_GOLD, center=True, bold=True, is_arabic=True)
            draw_text(surface, f"{rank_title}   •   {xp_txt}   •   {solved_txt}   •   {badges_txt}", 640, 68, size=14, color=ACCENT_CYAN, center=True, bold=True, is_arabic=True)
        else:
            draw_text(surface, "CRIME INVESTIGATION BUREAU", 640, 32, size=26, color=ACCENT_GOLD, center=True, bold=True)
            draw_text(surface, f"{rank_title}   •   {xp_txt}   •   {solved_txt}   •   {badges_txt}", 640, 68, size=14, color=ACCENT_CYAN, center=True, bold=True)

        for btn, c in self.hub_case_buttons:
            rect = btn.rect
            btn.draw(surface)

            cat = c.get("category", "Mystery")
            cat_col = CATEGORY_COLORS.get(cat, ACCENT_GOLD)
            pygame.draw.rect(surface, cat_col, (rect.x, rect.y, 6, rect.height), border_top_left_radius=6, border_bottom_left_radius=6)

            title_str = f"📁 {c['id'].upper().replace('_', ' ')}: {c['title']}"
            draw_text(surface, title_str, rect.x + 20, rect.y + 14, size=16, color=TEXT_WHITE, bold=True, is_arabic=self.is_ar)

            diff_colors = {"Easy": ACCENT_GREEN, "Medium": ACCENT_GOLD, "Hard": ACCENT_ORANGE, "Expert": ACCENT_RED, "سهل": ACCENT_GREEN, "متوسط": ACCENT_GOLD, "صعب": ACCENT_ORANGE, "خبير": ACCENT_RED}
            diff_col = diff_colors.get(c.get("difficulty"), ACCENT_GOLD)
            badge_x = rect.right - 140
            draw_rounded_rect(surface, (30, 25, 45), (badge_x, rect.y + 12, 120, 26), border_color=diff_col, radius=4)
            draw_text(surface, f"★ {c.get('difficulty', 'Medium')}", badge_x + 60, rect.y + 25, size=12, color=diff_col, center=True, bold=True, is_arabic=self.is_ar)

            turns_lbl = f"10 مسارات تحقيق  •  {cat}" if self.is_ar else f"10 Tactical Turns  •  {cat}"
            draw_text(surface, turns_lbl, rect.x + 20, rect.y + 44, size=13, color=ACCENT_CYAN, is_arabic=self.is_ar)

        page_str = f"صفحة {self.current_page + 1} من {self.total_pages}" if self.is_ar else f"Page {self.current_page + 1} of {self.total_pages}"
        draw_text(surface, page_str, 640, 666, size=15, color=TEXT_MUTED, center=True, bold=True, is_arabic=self.is_ar)
        self.btn_prev_page.draw(surface)
        self.btn_next_page.draw(surface)

    # ── DRAW PHASE 1: BRIEFING ──
    def _draw_briefing(self, surface: pygame.Surface):
        self.btn_back.draw(surface)
        self.btn_intuition.draw(surface)
        self.btn_dossier.draw(surface)

        if not self.case:
            return

        draw_rounded_rect(surface, BG_CARD, (140, 90, 1000, 510), border_color=PRIMARY_GLOW, radius=12)

        cat = getattr(self.case, "category", "Crime")
        cat_col = CATEGORY_COLORS.get(cat, ACCENT_GOLD)
        diff_str = getattr(self.case, "difficulty", "Medium")

        draw_text(surface, f"CLASSIFIED DOSSIER // {cat.upper()}", 170, 110, size=14, color=cat_col, bold=True, is_arabic=self.is_ar)
        draw_text(surface, self.case.title, 170, 135, size=24, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)
        draw_text(surface, f"Difficulty: {diff_str}   |   Suspects: {len(self.case.suspects)}   |   Evidence Clues: {len(self.case.clues)}", 170, 172, size=13, color=TEXT_MUTED, is_arabic=self.is_ar)

        draw_rounded_rect(surface, BG_DARK, (170, 205, 940, 170), border_color=CARD_BORDER, radius=8)
        briefing_hdr = "بيان الواقعة الجنائية وملابسات القضية:" if self.is_ar else "INCIDENT REPORT & DETECTIVE BRIEFING:"
        draw_text(surface, briefing_hdr, 190, 218, size=13, color=PRIMARY_GLOW, bold=True, is_arabic=self.is_ar)
        self._draw_wrapped_text(surface, self.case.briefing, 190, 245, max_w=900, size=14, color=TEXT_WHITE, line_h=22)

        suspects_hdr = "المشتبه بهم الرئيسيون:" if self.is_ar else "PERSONS OF INTEREST / SUSPECTS:"
        draw_text(surface, suspects_hdr, 170, 395, size=14, color=ACCENT_CYAN, bold=True, is_arabic=self.is_ar)

        for i, s in enumerate(self.case.get_suspect_profiles()[:4]):
            sx = 170 + i * 238
            draw_rounded_rect(surface, BG_DARK, (sx, 425, 226, 75), border_color=CARD_BORDER, radius=6)
            draw_text(surface, f"👤 {s['name']}", sx + 12, 436, size=13, color=TEXT_WHITE, bold=True, is_arabic=self.is_ar)
            draw_text(surface, s.get('role', 'Suspect'), sx + 12, 458, size=11, color=TEXT_MUTED, is_arabic=self.is_ar)
            draw_text(surface, f"Motive: {s.get('motive', 'Unknown')[:18]}...", sx + 12, 476, size=10, color=ACCENT_GOLD, is_arabic=self.is_ar)

        self.btn_launch_investigation.draw(surface)

    # ── DRAW PHASE 2: GAMEPLAY ──
    def _draw_gameplay(self, surface: pygame.Surface):
        self.btn_back.draw(surface)
        self.btn_intuition.draw(surface)
        self.btn_dossier.draw(surface)

        if not self.case:
            return

        step_num = self.case.current_step_idx + 1
        total_steps = self.case.total_steps
        hdr_txt = f"الجولة {step_num} من {total_steps}: استجواب مسرح الجريمة" if self.is_ar else f"INVESTIGATION TURN {step_num} / {total_steps}: CRIME SCENE"
        draw_text(surface, hdr_txt, 640, 42, size=18, color=ACCENT_GOLD, center=True, bold=True, is_arabic=self.is_ar)

        # Narrative Terminal Box
        draw_rounded_rect(surface, BG_CARD, (140, 88, 1000, 240), border_color=PRIMARY_GLOW, radius=12)

        msg = self.case.current_message
        if msg:
            speaker_str = f"🎙️ {msg.get('speaker', 'Detective Inspector')}"
            draw_text(surface, speaker_str, 170, 102, size=14, color=ACCENT_CYAN, bold=True, is_arabic=self.is_ar)
            self._draw_wrapped_text(surface, msg.get("text", ""), 170, 130, max_w=940, size=15, color=TEXT_WHITE, line_h=23)

        # Atmospheric sentiment guidance
        sentiment = self.case.get_atmospheric_sentiment(lang=str(getattr(self.app, "language", "2")))
        draw_rounded_rect(surface, (20, 25, 42), (160, 260, 960, 52), border_color=CARD_BORDER, radius=8)
        draw_text(surface, sentiment, 640, 286, size=13, color=ACCENT_GOLD, center=True, bold=True, is_arabic=self.is_ar)

        # Draw 4 Tactical Choice Buttons
        for btn in self.option_buttons:
            btn.draw(surface)

        # Feedback Toast Banner
        if self.feedback_timer > 0 and self.feedback_text:
            f_surf = pygame.Surface((1000, 42), pygame.SRCALPHA)
            f_surf.fill((15, 20, 35, 235))
            surface.blit(f_surf, (140, 620))
            draw_rounded_rect(surface, (15, 20, 35), (140, 620, 1000, 42), border_color=self.feedback_color, radius=6)
            draw_text(surface, self.feedback_text, 640, 641, size=13, color=self.feedback_color, center=True, bold=True, is_arabic=self.is_ar)

    # ── DRAW PHASE 3: ACCUSATION ──
    def _draw_accusation(self, surface: pygame.Surface):
        self.btn_back.draw(surface)
        self.btn_dossier.draw(surface)

        if not self.case:
            return

        hdr_str = "الجولة 10: المحكمة والاتهام القضائي النهائي" if self.is_ar else "FINAL TURN 10: OFFICIAL JUDICIAL ACCUSATION"
        draw_text(surface, hdr_str, 640, 42, size=22, color=ACCENT_GOLD, center=True, bold=True, is_arabic=self.is_ar)

        sub_str = "اختر المشتبه به الذي تعتقد أنه الجاني الحقيقي بناءً على الأدلة والتحقيقات:" if self.is_ar else "Select the prime suspect you formally accuse based on collected clues and alibis:"
        draw_text(surface, sub_str, 640, 78, size=14, color=TEXT_MUTED, center=True, is_arabic=self.is_ar)

        for btn, s in self.suspect_cards_buttons:
            rect = btn.rect
            is_selected = (s["name"] == self.selected_suspect_name)
            border_col = ACCENT_GOLD if is_selected else CARD_BORDER
            bg_col = (45, 38, 70) if is_selected else BG_CARD

            draw_rounded_rect(surface, bg_col, (rect.x, rect.y, rect.w, rect.h), border_color=border_col, radius=8)

            draw_text(surface, f"👤 {s['name']}", rect.x + 16, rect.y + 12, size=15, color=TEXT_WHITE, bold=True, is_arabic=self.is_ar)
            draw_text(surface, s.get("role", "Suspect"), rect.x + 16, rect.y + 34, size=12, color=ACCENT_CYAN, is_arabic=self.is_ar)
            draw_text(surface, f"Alibi: {s.get('alibi', 'Unknown')[:32]}...", rect.x + 16, rect.y + 54, size=11, color=TEXT_MUTED, is_arabic=self.is_ar)

            if is_selected:
                draw_rounded_rect(surface, ACCENT_GOLD, (rect.right - 90, rect.y + 12, 76, 24), radius=4)
                draw_text(surface, "ACCUSED", rect.right - 52, rect.y + 24, size=10, color=BG_DARK, center=True, bold=True)

        self.btn_confirm_accusation.draw(surface)

    # ── DRAW PHASE 4: CASE RESULTS & DRAMATIC VERDICT ──
    def _draw_results(self, surface: pygame.Surface):
        if not self.case:
            return

        res = self.case.get_final_evaluation(username=getattr(self.app, "player_name", None))
        rank = res.get("rank", "F")
        rank_title = res.get("rank_title", "Unsolved")

        rank_colors = {
            "S": ACCENT_GOLD,
            "A": ACCENT_GREEN,
            "B": ACCENT_CYAN,
            "C": (255, 215, 0),
            "D": ACCENT_ORANGE,
            "F": ACCENT_RED,
        }
        accent = rank_colors.get(rank, TEXT_WHITE)

        draw_rounded_rect(surface, BG_CARD, (140, 50, 1000, 560), border_color=accent, radius=12)

        if self.is_ar:
            header = f"الحكم القضائي: {self.case.title} // حسم القضية"
            rank_banner = f"★ المرتبة {rank}: {rank_title} ★"
            accused_line = f"المتهم من طرفك: {res.get('accused_suspect')}     |     الجاني الحقيقي: {res.get('true_culprit')}"
            debrief_hdr = "التقرير الختامي الرسمي وكشف ملابسات الجريمة:"
            metrics_line = f"الأدلة الجنائية: {res.get('evidence_score')}/100   •   الفحص المخبري: {res.get('analyzed_clues_count', 0)}   •   الاستجوابات: {res.get('interrogated_suspects_count', 0)}"
            rewards_line = f"المكافآت الممنوحة:  +{res.get('xp_awarded')} نقطة خبرة   •   +{res.get('coins_awarded')} عملة ذهبية"
        else:
            header = f"VERDICT: {self.case.title.upper()} // RESOLUTION"
            rank_banner = f"★ RANK {rank}: {rank_title.upper()} ★"
            accused_line = f"Your Accusation: {res.get('accused_suspect')}     |     True Culprit: {res.get('true_culprit')}"
            debrief_hdr = "OFFICIAL CASE DEBRIEF & TRUTH REVEALED:"
            metrics_line = f"Evidence Score: {res.get('evidence_score')}/100   •   Forensic Lab: {res.get('analyzed_clues_count', 0)} Analyzed   •   Interrogated: {res.get('interrogated_suspects_count', 0)}"
            rewards_line = f"REWARDS GRANTED:  +{res.get('xp_awarded')} Avatar XP   •   +{res.get('coins_awarded')} Gold Coins"

        draw_text(surface, header, 640, 72, size=18, color=TEXT_MUTED, center=True, bold=True, is_arabic=self.is_ar)
        draw_text(surface, rank_banner, 640, 112, size=28, color=accent, center=True, bold=True, is_arabic=self.is_ar)
        draw_text(surface, accused_line, 640, 155, size=15, color=TEXT_WHITE, center=True, bold=True, is_arabic=self.is_ar)

        draw_rounded_rect(surface, BG_DARK, (180, 185, 920, 220), border_color=CARD_BORDER, radius=8)
        draw_text(surface, debrief_hdr, 205, 198, size=13, color=PRIMARY_GLOW, bold=True, is_arabic=self.is_ar)
        self._draw_wrapped_text(surface, res.get("true_solution", ""), 205, 226, max_w=870, size=13, color=TEXT_WHITE, line_h=21)

        draw_text(surface, metrics_line, 640, 425, size=14, color=ACCENT_CYAN, center=True, is_arabic=self.is_ar)

        badges = res.get("badges_earned", [])
        if badges:
            b_str = " | ".join([f"🏅 {b}" for b in badges])
            draw_text(surface, f"New Badges Earned: {b_str}", 640, 455, size=13, color=ACCENT_GOLD, center=True, bold=True)

        draw_text(surface, rewards_line, 640, 490, size=15, color=ACCENT_GREEN, center=True, bold=True, is_arabic=self.is_ar)

        self.btn_another_case.draw(surface)
        self.btn_return_menu.draw(surface)

    # ── DRAW CASE DOSSIER / NOTEBOOK MODAL OVERLAY (5 TABS) ──
    def _draw_dossier_modal(self, surface: pygame.Surface):
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        surface.blit(overlay, (0, 0))

        draw_rounded_rect(surface, (20, 25, 38), (120, 45, 1040, 630), border_color=PRIMARY_GLOW, radius=12)

        modal_title = "📁 ملف القضية ومفكرة المحقق الجنائي" if self.is_ar else "📁 CASE DOSSIER & INVESTIGATOR NOTEBOOK"
        draw_text(surface, modal_title, 140, 52, size=16, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)
        self.btn_close_dossier.draw(surface)

        self.btn_tab_clues.draw(surface)
        self.btn_tab_suspects.draw(surface)
        self.btn_tab_timeline.draw(surface)
        self.btn_tab_lab.draw(surface)
        self.btn_tab_recon.draw(surface)

        tab_xs = [140, 305, 470, 635, 820]
        tab_ws = [160, 160, 160, 180, 210]
        active_x = tab_xs[self.dossier_tab]
        active_w = tab_ws[self.dossier_tab]
        pygame.draw.rect(surface, ACCENT_GOLD, (active_x, 112, active_w, 3))

        draw_rounded_rect(surface, BG_DARK, (140, 125, 1000, 530), border_color=CARD_BORDER, radius=8)

        if not self.case:
            return

        # TAB 0: CLUES
        if self.dossier_tab == 0:
            clues = self.case.get_unlocked_clues()
            if not clues:
                empty_msg = "لم يتم كشف أي أدلة بعد. اتخذ قراراتك خلال جولات التحقيق لجمع الأدلة!" if self.is_ar else "No evidence unlocked yet. Make choices during investigation turns to uncover clues!"
                draw_text(surface, empty_msg, 640, 350, size=15, color=TEXT_MUTED, center=True, is_arabic=self.is_ar)
            else:
                hdr = f"الأدلة الجنائية المكتشفة ({len(clues)} / {len(self.case.clues)}):" if self.is_ar else f"DISCOVERED CLUES & EVIDENCE ({len(clues)} / {len(self.case.clues)}):"
                draw_text(surface, hdr, 160, 140, size=14, color=ACCENT_CYAN, bold=True, is_arabic=self.is_ar)
                for i, c in enumerate(clues[:5]):
                    cy = 170 + i * 92
                    draw_rounded_rect(surface, BG_CARD, (160, cy, 960, 84), border_color=CARD_BORDER, radius=6)
                    role_col = {"Critical": COLOR_CRITICAL, "Supporting": COLOR_SUPPORTING, "Red Herring": COLOR_HERRING}.get(c.get("role"), TEXT_WHITE)
                    title_str = f"[{c.get('category', 'Evidence')}]  {c.get('title')}   ({c.get('role', '')})"
                    draw_text(surface, title_str, 175, cy + 10, size=14, color=role_col, bold=True, is_arabic=self.is_ar)
                    self._draw_wrapped_text(surface, c.get("description", ""), 175, cy + 32, max_w=930, size=12, color=TEXT_WHITE, line_h=18)

        # TAB 1: SUSPECTS & INTERROGATION
        elif self.dossier_tab == 1:
            if self.active_interrogation_name and self.active_interrogation_name in self.case.interrogated_suspects:
                # Active Interrogation View
                rec = self.case.interrogated_suspects[self.active_interrogation_name]
                self.btn_back_from_interrogation.draw(surface)

                s_title = f"⚖️ جلسة استجواب رسمية: {rec['name']} ({rec['role']})" if self.is_ar else f"⚖️ OFFICIAL INTERROGATION: {rec['name']} ({rec['role']})"
                draw_text(surface, s_title, 160, 145, size=16, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)

                # Suspicion Meter
                susp = rec.get("suspicion", 50)
                meter_col = ACCENT_GREEN if susp < 40 else (ACCENT_GOLD if susp < 65 else ACCENT_RED)
                draw_text(surface, f"Suspicion Meter: {susp}%" if not self.is_ar else f"مؤشر الشبهة الجنائية: {susp}%", 160, 185, size=13, color=meter_col, bold=True, is_arabic=self.is_ar)
                draw_rounded_rect(surface, (35, 30, 50), (160, 205, 340, 14), radius=4)
                fill_w = int(340 * (susp / 100.0))
                draw_rounded_rect(surface, meter_col, (160, 205, fill_w, 14), radius=4)

                draw_text(surface, f"Psychological Stress: {rec.get('stress', 'Normal')}" if not self.is_ar else f"الحالة النفسية: {rec.get('stress', 'طبيعي')}", 540, 185, size=13, color=ACCENT_ORANGE, bold=True, is_arabic=self.is_ar)

                # Dialogue Exchange
                draw_rounded_rect(surface, BG_CARD, (160, 235, 960, 140), border_color=CARD_BORDER, radius=8)
                q_lbl = "🔍 سؤال المحقق الجنائي:" if self.is_ar else "🔍 DETECTIVE QUESTION:"
                draw_text(surface, q_lbl, 180, 245, size=12, color=PRIMARY_GLOW, bold=True, is_arabic=self.is_ar)
                self._draw_wrapped_text(surface, rec.get("question", ""), 180, 268, max_w=920, size=13, color=TEXT_WHITE, line_h=19)

                a_lbl = f"👤 إجابة المشتبه به ({rec['name']}):" if self.is_ar else f"👤 SUSPECT RESPONSE ({rec['name']}):"
                draw_text(surface, a_lbl, 180, 310, size=12, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)
                self._draw_wrapped_text(surface, rec.get("answer", ""), 180, 332, max_w=920, size=13, color=TEXT_WHITE, line_h=19)

                # Contradictions Detected
                draw_rounded_rect(surface, (25, 22, 40), (160, 390, 960, 230), border_color=CARD_BORDER, radius=8)
                c_lbl = "⚠️ التناقضات المكتشفة مع الأدلة الجنائية:" if self.is_ar else "⚠️ FORENSIC CONTRADICTIONS & DISCREPANCIES DETECTED:"
                draw_text(surface, c_lbl, 180, 405, size=13, color=ACCENT_RED, bold=True, is_arabic=self.is_ar)
                for ci, contra in enumerate(rec.get("contradictions", [])):
                    draw_text(surface, f"• {contra}", 190, 435 + ci * 28, size=13, color=TEXT_WHITE, is_arabic=self.is_ar)

            else:
                # Suspect Roster with Interrogate Buttons
                suspects = self.case.get_suspect_profiles()
                hdr = f"سجلات المشتبه بهم والشهود ({len(suspects)}):" if self.is_ar else f"PERSONS OF INTEREST & SUSPECT PROFILES ({len(suspects)}):"
                draw_text(surface, hdr, 160, 140, size=14, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)
                for i, s in enumerate(suspects[:4]):
                    sy = 175 + i * 110
                    draw_rounded_rect(surface, BG_CARD, (160, sy, 960, 102), border_color=CARD_BORDER, radius=6)
                    draw_text(surface, f"👤 {s['name']} — {s['role']}", 175, sy + 8, size=15, color=TEXT_WHITE, bold=True, is_arabic=self.is_ar)
                    p_story = f"الرواية: {s['public_story']}" if self.is_ar else f"Public Story: {s['public_story']}"
                    p_secret = f"السر الخفي: {s['private_secret']}" if self.is_ar else f"Private Secret: {s['private_secret']}"
                    alibi_txt = f"العذر: {s['alibi']}" if self.is_ar else f"Stated Alibi: {s['alibi']}"
                    draw_text(surface, p_story, 175, sy + 30, size=12, color=ACCENT_CYAN, is_arabic=self.is_ar)
                    draw_text(surface, p_secret, 175, sy + 48, size=12, color=ACCENT_RED, is_arabic=self.is_ar)
                    draw_text(surface, alibi_txt, 175, sy + 68, size=12, color=TEXT_MUTED, is_arabic=self.is_ar)

                for btn in self.suspect_interrogate_buttons:
                    btn.draw(surface)

        # TAB 2: TIMELINE
        elif self.dossier_tab == 2:
            hdr = "الخط الزمني المتسلسل للأحداث:" if self.is_ar else "CHRONOLOGICAL CASE TIMELINE:"
            draw_text(surface, hdr, 160, 140, size=14, color=PRIMARY_GLOW, bold=True, is_arabic=self.is_ar)
            timeline_items = getattr(self.case, "timeline", [])
            for i, t in enumerate(timeline_items[:7]):
                ty = 175 + i * 62
                draw_rounded_rect(surface, BG_CARD, (160, ty, 960, 54), border_color=CARD_BORDER, radius=6)
                draw_text(surface, f"🕐 {t.get('time', 'Time')}", 180, ty + 16, size=15, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)
                draw_text(surface, t.get("event", ""), 310, ty + 17, size=13, color=TEXT_WHITE, is_arabic=self.is_ar)

        # TAB 3: FEATURE 1 - FORENSIC LAB
        elif self.dossier_tab == 3:
            hdr = "معمل الأدلة الجنائية والتحليل الطيفي المجهري (+15 نقطة لكل فحص):" if self.is_ar else "FORENSIC LAB: SPECTRAL & MICROSCOPIC EVIDENCE ANALYSIS (+15 PTS EACH):"
            draw_text(surface, hdr, 160, 140, size=14, color=ACCENT_CYAN, bold=True, is_arabic=self.is_ar)
            clues = self.case.get_unlocked_clues()
            if not clues:
                empty_msg = "لا توجد أدلة جاهزة للفحص المخبري حالياً. اجمع الأدلة أولاً!" if self.is_ar else "No evidence available for lab analysis yet. Discover clues first!"
                draw_text(surface, empty_msg, 640, 350, size=15, color=TEXT_MUTED, center=True, is_arabic=self.is_ar)
            else:
                for i, c in enumerate(clues[:5]):
                    cid = c.get("id", f"clue_{i+1}")
                    is_analyzed = cid in self.case.analyzed_clues
                    cy = 170 + i * 92
                    border_c = ACCENT_GREEN if is_analyzed else CARD_BORDER
                    draw_rounded_rect(surface, BG_CARD, (160, cy, 960, 84), border_color=border_c, radius=6)

                    title_str = f"🔬 {c.get('title', 'Evidence')} [{c.get('category', 'Clue')}]"
                    draw_text(surface, title_str, 175, cy + 10, size=14, color=PRIMARY_GLOW, bold=True, is_arabic=self.is_ar)

                    if is_analyzed:
                        finding_txt = self.case.forensic_findings.get(cid, "تم الفحص بنجاح.")
                        self._draw_wrapped_text(surface, finding_txt, 175, cy + 32, max_w=760, size=12, color=ACCENT_GREEN, line_h=18)
                        draw_rounded_rect(surface, (25, 50, 40), (950, cy + 22, 150, 34), radius=4)
                        draw_text(surface, "✔ ANALYZED", 1025, cy + 39, size=11, color=ACCENT_GREEN, center=True, bold=True)
                    else:
                        self._draw_wrapped_text(surface, c.get("description", ""), 175, cy + 32, max_w=760, size=12, color=TEXT_WHITE, line_h=18)

                for btn in self.lab_analyze_buttons:
                    btn.draw(surface)

        # TAB 4: FEATURE 4 - CRIME SCENE RECONSTRUCTION
        elif self.dossier_tab == 4:
            recon = self.case.get_crime_scene_reconstruction()
            hdr = f"محاكاة إعادة بناء مسرح الجريمة // نسبة التطابق: {recon.get('confidence_percent', 0)}%" if self.is_ar else f"CRIME SCENE RECONSTRUCTION SIMULATION // CONFIDENCE: {recon.get('confidence_percent', 0)}%"
            draw_text(surface, hdr, 160, 140, size=15, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)

            # Confidence bar
            conf = recon.get("confidence_percent", 0)
            bar_col = ACCENT_GREEN if conf >= 80 else (ACCENT_GOLD if conf >= 50 else ACCENT_RED)
            draw_rounded_rect(surface, (35, 30, 50), (160, 165, 400, 12), radius=3)
            fill_w = int(400 * (conf / 100.0))
            draw_rounded_rect(surface, bar_col, (160, 165, fill_w, 12), radius=3)

            for i, p in enumerate(recon.get("phases", [])[:5]):
                py_pos = 190 + i * 88
                is_ver = p.get("verified", False)
                border_c = ACCENT_GREEN if is_ver else CARD_BORDER
                draw_rounded_rect(surface, BG_CARD, (160, py_pos, 960, 80), border_color=border_c, radius=6)

                icon = p.get("icon", "📍")
                p_num = p.get("phase", i + 1)
                p_title = f"{icon} المرحلة {p_num}: {p.get('name')}" if self.is_ar else f"{icon} PHASE {p_num}: {p.get('name')}"
                draw_text(surface, p_title, 175, py_pos + 8, size=14, color=PRIMARY_GLOW, bold=True, is_arabic=self.is_ar)
                self._draw_wrapped_text(surface, p.get("desc", ""), 175, py_pos + 30, max_w=780, size=12, color=TEXT_WHITE, line_h=18)

                tag_bg = (25, 55, 35) if is_ver else (45, 35, 45)
                tag_col = ACCENT_GREEN if is_ver else TEXT_MUTED
                tag_lbl = "✔ VERIFIED" if is_ver else "⏳ PENDING"
                draw_rounded_rect(surface, tag_bg, (960, py_pos + 22, 140, 32), radius=4)
                draw_text(surface, tag_lbl, 1030, py_pos + 38, size=11, color=tag_col, center=True, bold=True)

    def _draw_wrapped_text(self, surface, text: str, x: int, y: int, max_w: int, size: int = 14, color: tuple = TEXT_WHITE, line_h: int = 22):
        """Utility for multi-line wrapped text rendering with pixel measurement and RTL support."""
        words = str(text).split(" ")
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_str = " ".join(current_line)
            test_surf = render_text(test_str, size=size)
            if test_surf.get_width() > max_w:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(" ".join(current_line))
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        for idx, line in enumerate(lines):
            line_s = render_text(line, size=size, color=color, is_arabic=self.is_ar)
            if self.is_ar:
                line_x = x + max_w - line_s.get_width()
            else:
                line_x = x
            surface.blit(line_s, (line_x, y + idx * line_h))
