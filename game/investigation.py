# -*- coding: utf-8 -*-
"""
game/investigation.py — Advanced Crime Investigation System for Dump's Test v4.0.
Supports 20 rich detective crime cases, hidden investigation scoring,
Case Dossier clue notebook, 10-message interactive branching, suspect lie-detection,
and multi-tier final accusation rankings (S, A, B, C, D, F).
Maintains 100% backward compatibility for legacy test suites.
"""
import time
import random
import json
from pathlib import Path

# Import 20-case master database
from game.investigation_cases_db import (
    ALL_INVESTIGATION_CASES,
    CASES_BY_ID,
    get_all_detective_cases,
    get_detective_case_by_id,
)

# Optional accounts rewards
try:
    from game.accounts import (
        award_avatar_win_xp, add_user_coins,
        award_detective_career_xp, get_detective_career
    )
except ImportError:
    award_avatar_win_xp = None
    add_user_coins = None
    award_detective_career_xp = None
    get_detective_career = None


# ── SAMPLE STARTER CASES (Legacy backward compatibility) ──────────────────────
BUILTIN_CASES = [
    {
        "id": "case_001",
        "title": "The Alchemist's Stolen Formula",
        "difficulty": "Medium",
        "briefing": "A renowned alchemist reports that their legendary transmutation formula has vanished from a locked laboratory. Three apprentices had access. Examine the evidence, question the suspects, and identify the thief.",
        "suspects": ["Marcus the Ambitious", "Elena the Quiet", "Viktor the Newcomer"],
        "clues": [
            "A broken window latch was found, but dust suggests it hasn't been opened in weeks.",
            "Marcus was seen near the lab at midnight, but claims he was returning a borrowed book.",
            "Elena's notebook contains copied fragments of the formula.",
            "Viktor's quarters were searched — nothing was found.",
            "The lab door's lock shows no signs of tampering."
        ],
        "questions": [
            {"question": "Based on the broken window latch and dust evidence, was the window used as an entry point?", "choices": "Yes, the thief entered through the window|No, the window was not used recently|The dust was planted as a false clue|Cannot be determined", "answer": "No, the window was not used recently", "time_limit": 20},
            {"question": "Marcus was near the lab at midnight. Does this make him the prime suspect?", "choices": "Yes, his presence is suspicious|No, returning a book is plausible|He should be arrested immediately|More evidence is needed", "answer": "More evidence is needed", "time_limit": 15},
            {"question": "Elena's notebook contains formula fragments. What does this suggest?", "choices": "She copied the formula and stole the original|She was studying the formula as an apprentice|She is definitively the thief|The fragments are unrelated", "answer": "She copied the formula and stole the original", "time_limit": 30},
            {"question": "The lab door lock shows no tampering. What does this mean?", "choices": "The thief had a key|The formula was never stolen|The lock is irrelevant|Someone broke in through the roof", "answer": "The thief had a key", "time_limit": 20},
            {"question": "FINAL DEDUCTION: Who stole the Alchemist's Formula?", "choices": "Marcus the Ambitious|Elena the Quiet|Viktor the Newcomer|The Alchemist staged it", "answer": "Elena the Quiet", "time_limit": 60}
        ]
    },
    {
        "id": "case_002",
        "title": "The Haunted Clocktower Mystery",
        "difficulty": "Hard",
        "briefing": "The ancient clocktower stopped at exactly 3:33 AM, and the clockmaker was found unconscious at the base. Strange symbols were carved into the gears. Was this sabotage, an accident, or something else entirely?",
        "suspects": ["The Mayor", "Old Gertrude", "The Rival Clockmaker", "The Night Guard"],
        "clues": [
            "The symbols carved into the gears match an ancient protection ward.",
            "The Mayor recently proposed demolishing the clocktower for a new town hall.",
            "Old Gertrude was seen leaving the tower at 2:45 AM with a lantern.",
            "The rival clockmaker had publicly threatened to 'silence that infernal tower'.",
            "The night guard's logbook has a missing page for that night.",
            "Tool marks on the gears are consistent with the clockmaker's own tools."
        ],
        "questions": [
            {"question": "The symbols on the gears are protection wards. Who would carve protective symbols?", "choices": "Someone trying to protect the tower|Someone cursing the tower|A random vandal|The clockmaker testing new designs", "answer": "Someone trying to protect the tower", "time_limit": 25},
            {"question": "The Mayor wants to demolish the tower. Does this give motive for sabotage?", "choices": "Yes, stopping the clock supports the demolition argument|No, the Mayor would use legal channels|The Mayor has no connection to the incident|The Mayor is the victim", "answer": "Yes, stopping the clock supports the demolition argument", "time_limit": 30},
            {"question": "Old Gertrude left at 2:45 AM. The clock stopped at 3:33 AM. What does this tell us?", "choices": "She could have set a delayed mechanism|She left before the incident|She is clearly guilty|The times are unrelated", "answer": "She left before the incident", "time_limit": 20},
            {"question": "The night guard's logbook has a missing page. What does this imply?", "choices": "The guard is hiding something|The page fell out naturally|The guard is the saboteur|Someone else removed the page", "answer": "The guard is hiding something", "time_limit": 25},
            {"question": "Tool marks match the clockmaker's own tools. Combined with Old Gertrude's ward symbols, what happened?", "choices": "Gertrude carved wards to protect; someone else sabotaged|The clockmaker sabotaged his own tower|Gertrude and the clockmaker conspired|The rival clockmaker used stolen tools", "answer": "Gertrude carved wards to protect; someone else sabotaged", "time_limit": 45},
            {"question": "FINAL DEDUCTION: Who sabotaged the clocktower?", "choices": "The Mayor orchestrated it|Old Gertrude did it accidentally|The Rival Clockmaker committed sabotage|The Night Guard is responsible", "answer": "The Rival Clockmaker committed sabotage", "time_limit": 60}
        ]
    },
    {
        "id": "case_003",
        "title": "The Royal Treasury Heist",
        "difficulty": "Expert",
        "briefing": "Three priceless artifacts have vanished from the Royal Treasury overnight. The vault was sealed, the guards saw nothing, and the King demands answers. Unravel the impossible heist.",
        "suspects": ["Captain of the Guard", "The Royal Advisor", "The Court Jester", "The Foreign Ambassador"],
        "clues": [
            "The vault has only one key, held personally by the King.",
            "A secret passage was discovered behind a bookshelf in the advisor's quarters.",
            "The jester was performing at a banquet during the estimated theft window.",
            "The ambassador's ship departed unusually early the next morning.",
            "Guard rotation records show a 15-minute gap at 2 AM — the Captain authorized it.",
            "Traces of a rare foreign spice were found near the vault entrance.",
            "The advisor recently purchased a large estate despite modest salary."
        ],
        "questions": [
            {"question": "The vault key is held only by the King. How was the vault opened?", "choices": "The key was copied|A secret passage bypassed the door|The lock was picked by an expert|The King is involved", "answer": "A secret passage bypassed the door", "time_limit": 20},
            {"question": "A secret passage connects to the advisor's quarters. Is the advisor involved?", "choices": "Definitely — the passage proves guilt|Possibly — but the passage might predate the advisor|No — anyone could have used it|The passage is unrelated", "answer": "Possibly — but the passage might predate the advisor", "time_limit": 30},
            {"question": "The Captain authorized a 15-minute guard gap. Why?", "choices": "He was bribed to create an opportunity|Standard rotation procedure|He was negligent but not complicit|He personally committed the theft", "answer": "He was bribed to create an opportunity", "time_limit": 25},
            {"question": "Foreign spice near the vault and the ambassador's early departure. Connection?", "choices": "The ambassador is the mastermind|The ambassador transported the stolen goods|The spice is from the ambassador's gift|Coincidence", "answer": "The ambassador transported the stolen goods", "time_limit": 35},
            {"question": "The advisor has unexplained wealth. The Captain created a guard gap. The ambassador left early. What's the full picture?", "choices": "All three conspired together|The advisor planned it alone using the others|The Captain and ambassador conspired without the advisor|Only one person is guilty", "answer": "All three conspired together", "time_limit": 45},
            {"question": "FINAL DEDUCTION: Who is the MASTERMIND of the Royal Treasury Heist?", "choices": "Captain of the Guard|The Royal Advisor|The Court Jester|The Foreign Ambassador", "answer": "The Royal Advisor", "time_limit": 60}
        ]
    }
]

BUILTIN_CASES_AR = [
    {
        "id": "case_001",
        "title": "معادلة الخيميائي المسروقة",
        "difficulty": "متوسط",
        "briefing": "يُبلّغ خيميائي شهير أن صيغته الأسطورية للتحويل قد اختفت من معمله المغلق. ثلاثة متدربين فقط كان بإمكانهم الدخول. افحص الأدلة، واستجوب المشتبه بهم، وحدد السارق.",
        "suspects": ["ماركوس الطموح", "إيلينا الهادئة", "فيكتور الوافد الجديد"],
        "clues": [
            "عُثر على مزلاج نافذة مكسور، لكن الغبار المتراكم يشير إلى أنها لم تُفتح منذ أسابيع.",
            "شوهد ماركوس بالقرب من المختبر عند منتصف الليل، لكنه يدعي أنه كان يعيد كتاباً مستعاراً.",
            "دفتر إيلينا يحتوي على أجزاء منسوخة من صيغة التحويل.",
            "تم تفتيش غرفة فيكتور ولم يُعثر على أي شيء مريب.",
            "قفل باب المختبر لا يُظهر أي علامات عبث أو كسر."
        ],
        "questions": [
            {"question": "بناءً على مزلاج النافذة المكسور والغبار، هل استُخدمت النافذة كنقطة دخول؟", "choices": "نعم، دخل السارق عبر النافذة|لا، لم تُستخدم النافذة مؤخراً|الغبار وُضع كدليل مضلل|لا يمكن التحديد", "answer": "لا، لم تُستخدم النافذة مؤخراً", "time_limit": 20},
            {"question": "كان ماركوس قرب المختبر عند منتصف الليل. هل يجعله هذا المشتبه به الرئيسي؟", "choices": "نعم، وجوده مريب للغاية|لا، إعادة كتاب سبب معقول|يجب القبض عليه فوراً|هناك حاجة لمزيد من الأدلة", "answer": "هناك حاجة لمزيد من الأدلة", "time_limit": 15},
            {"question": "دفتر إيلينا يحتوي على أجزاء منسوخة. ماذا يوحي ذلك؟", "choices": "نسخت الصيغة وسرقت الأصل|كانت تدرس الصيغة كمتدربة|إنها السارقة بشكل قاطع|الملاحظات لا علاقة لها بالسرقة", "answer": "نسخت الصيغة وسرقت الأصل", "time_limit": 30},
            {"question": "قفل باب المختبر سليم دون عبث. ماذا يعني ذلك؟", "choices": "السارق يمتلك مفتاحاً|الصيغة لم تُسرق أبداً|القفل ليس دليلاً مهماً|شخص ما دخل عبر السقف", "answer": "السارق يمتلك مفتاحاً", "time_limit": 20},
            {"question": "الاستنتاج النهائي: من الذي سرق صيغة الخيميائي؟", "choices": "ماركوس الطموح|إيلينا الهادئة|فيكتور الوافد الجديد|الخيميائي نفسه لفّق السرقة", "answer": "إيلينا الهادئة", "time_limit": 60}
        ]
    },
    {
        "id": "case_002",
        "title": "لغز برج الساعة المسكون",
        "difficulty": "صعب",
        "briefing": "توقف برج الساعة القديم عند الساعة 3:33 صباحاً تماماً، وعُثر على صانع الساعات فاقداً للوعي عند القاعدة مع نقوش غريبة على التروس. هل هذا تخريب أم حادث؟",
        "suspects": ["العمدة", "العجوز غيرترود", "صانع الساعات المنافس", "حارس الليل"],
        "clues": [
            "الرموز المنقوشة على التروس تطابق تعويذة حماية قديمة.",
            "اقترح العمدة مؤخراً هدم برج الساعة لبناء مبنى بلدية جديد.",
            "شوهدت العجوز غيرترود تغادر البرج في 2:45 صباحاً وبيدها فانوس.",
            "هدد صانع الساعات المنافس علناً بـ 'إسكات ذلك البرج الملعون'.",
            "سجل دفتر حارس الليل يحتوي على صفحة مفقودة لتلك الليلة.",
            "علامات الأدوات على التروس تطابق أدوات صانع الساعات نفسه."
        ],
        "questions": [
            {"question": "الرموز على التروس هي تعاويذ حماية. من سينقش رموز حماية؟", "choices": "شخص يحاول حماية البرج|شخص يلقي لعنة على البرج|مخرّب عشوائي|صانع الساعات يجرب تصاميم جديدة", "answer": "شخص يحاول حماية البرج", "time_limit": 25},
            {"question": "العمدة يريد هدم البرج. هل يمنحه هذا دافعاً للتخريب؟", "choices": "نعم، توقف الساعة يدعم حجة الهدم|لا، العمدة سيستخدم الطرق القانونية|العمدة ليس له صلة بالحادث|العمدة هو الضحية", "answer": "نعم، توقف الساعة يدعم حجة الهدم", "time_limit": 30},
            {"question": "غادرت غيرترود في 2:45 وتوقفت الساعة في 3:33. ماذا يخبرنا ذلك؟", "choices": "ربما ضبطت آلية مؤقتة|غادرت قبل وقوع الحادث|إنها مذنبة بوضوح|الأوقات غير مرتبطة", "answer": "غادرت قبل وقوع الحادث", "time_limit": 20},
            {"question": "دفتر حارس الليل يفتقد صفحة. ماذا يستنتج من ذلك؟", "choices": "الحارس يخفي شيئاً ما|الصفحة سقطت تلقائياً|الحارس هو المخرب|شخص آخر مزق الصفحة", "answer": "الحارس يخفي شيئاً ما", "time_limit": 25},
            {"question": "علامات الأدوات تطابق أدوات صانع الساعات، مع تعاويذ غيرترود. ما الذي حدث؟", "choices": "غيرترود نقشت حماية؛ وشخص آخر خرّب الساعة|صانع الساعات خرب برجه بنفسه|غيرترود وصانع الساعات تآمرا|صانع الساعات المنافس استخدم أدوات مسروقة", "answer": "غيرترود نقشت حماية؛ وشخص آخر خرّب الساعة", "time_limit": 45},
            {"question": "الاستنتاج النهائي: من قام بتخريب برج الساعة؟", "choices": "العمدة دبّر الأمر|العجوز غيرترود فعلتها بالخطأ|صانع الساعات المنافس ارتكب التخريب|حارس الليل هو المسؤول", "answer": "صانع الساعات المنافس ارتكب التخريب", "time_limit": 60}
        ]
    },
    {
        "id": "case_003",
        "title": "سرقة الخزانة الملكية",
        "difficulty": "خبير",
        "briefing": "اختفت ثلاث قطع أثرية لا تقدر بثمن من الخزانة الملكية ليلاً. كانت الخزانة محكمة الإغلاق، والحراس لم يشاهدوا شيئاً، والملك يطلب كشف اللغز المستحيل.",
        "suspects": ["قائد الحرس", "المستشار الملكي", "مهرج البلاط", "السفير الأجنبي"],
        "clues": [
            "الخزانة لها مفتاح واحد فقط، يحتفظ به الملك شخصياً.",
            "تم اكتشاف ممر سري خلف خزانة كتب في غرفة المستشار الملكي.",
            "كان المهرج يقدم عرضاً في المأدبة أثناء وقت السرقة المقدر.",
            "غادرت سفينة السفير بشكل غير معتاد في الصباح الباكر.",
            "سجلات تبديل الحراس تظهر فجوة لمدة 15 دقيقة في الساعة 2 صباحاً صرح بها القائد.",
            "عُثر على آثار بهار أجنبي نادر قرب مدخل الخزانة.",
            "اشترى المستشار مؤخراً قصراً كبيراً رغم راتبه المتواضع."
        ],
        "questions": [
            {"question": "مفتاح الخزانة مع الملك فقط. كيف فُتحت الخزانة؟", "choices": "تم نسخ المفتاح|ممر سري تجاوز الباب الرئيسي|فتح القفل خبير أقفال محترف|الملك متورط في الأمر", "answer": "ممر سري تجاوز الباب الرئيسي", "time_limit": 20},
            {"question": "ممر سري يتصل بغرفة المستشار. هل المستشار متورط؟", "choices": "بالتأكيد، الممر يثبت إدانته|محتمل، لكن الممر قد يكون قديماً|لا، أي شخص كان بإمكانه استخدامه|الممر غير مرتبط بالسرقة", "answer": "محتمل، لكن الممر قد يكون قديماً", "time_limit": 30},
            {"question": "قائد الحرس سمح بفجوة حراسة 15 دقيقة. لماذا؟", "choices": "تلقى رشوة لتوفير ثغرة للمنفذين|إجراء روتيني لتبديل الحرس|كان مهملاً لكن غير متواطئ|قام بالسرقة شخصياً", "answer": "تلقى رشوة لتوفير ثغرة للمنفذين", "time_limit": 25},
            {"question": "بهار أجنبي قرب الخزانة ومغادرة السفير مبكراً. ما الرابط؟", "choices": "السفير هو العقل المدبر|السفير تولى نقل وتهريب المسروقات|البهار سقط من هدية السفير|مجرد صدفة بحتة", "answer": "السفير تولى نقل وتهريب المسروقات", "time_limit": 35},
            {"question": "المستشار ثري فجأة، والقائد وفّر الثغرة، والسفير هرب بالبضائع. ما الصورة الكاملة؟", "choices": "تآمر الثلاثة معاً في العملية|المستشار خطط منفرداً واستغل الآخرين|القائد والسفير تآمرا دون المستشار|شخص واحد فقط هو المذنب", "answer": "تآمر الثلاثة معاً في العملية", "time_limit": 45},
            {"question": "الاستنتاج النهائي: من هو العقل المدبر لسرقة الخزانة الملكية؟", "choices": "قائد الحرس|المستشار الملكي|مهرج البلاط|السفير الأجنبي", "answer": "المستشار الملكي", "time_limit": 60}
        ]
    }
]


class InvestigationCase:
    """
    Represents an active crime investigation case.
    Supports both legacy quiz-style deduction and the new 10-message branching
    detective mode with hidden scoring, clues dossier, and suspect rosters.
    """

    def __init__(self, case_data: dict, lang: str = "2"):
        self.raw_data = case_data
        self.lang = str(lang)
        self.id = case_data["id"]
        self.title = case_data["title"]
        self.category = case_data.get("category", "Mystery")
        self.difficulty = case_data.get("difficulty", "Medium")
        self.target_or_victim = case_data.get("target_or_victim", "Victim")
        self.crime_scene = case_data.get("crime_scene", "Crime Scene")
        self.briefing = case_data.get("briefing", "")
        self.suspects = case_data.get("suspects", [])
        self.clues = case_data.get("clues", [])
        self.timeline = case_data.get("timeline", [])
        self.messages = case_data.get("messages", [])
        self.true_culprit = case_data.get("true_culprit", "")
        self.true_solution = case_data.get("true_solution", "")
        self.rank_thresholds = case_data.get("rank_thresholds", {"S": 75, "A": 55, "B": 35, "C": 20})

        # Legacy questions support
        self.questions = case_data.get("questions", [])

        # ── HIDDEN INVESTIGATION SCORE ENGINE ──
        # Player NEVER sees these raw numerical metrics directly during gameplay!
        self.killer_probability = 0      # -10 (far) to +10 (pinpointed culprit)
        self.evidence_score = 0          # 0 to 100 total points
        self.timeline_accuracy = 0       # 0 to 100
        self.motive_understanding = 0    # 0 to 100

        # Dossier state
        self.unlocked_clue_ids = set()
        self.choices_log = []            # list of {step, choice_text, feedback, delta}

        # 5 Advanced Investigation Features State
        self.intuition_charges = 2       # Feature 3: Sherlock Intuition Lifelines (2 per case)
        self.analyzed_clues = set()      # Feature 1: Forensic Lab Magnifier analyzed clues
        self.forensic_findings = {}      # Feature 1: Spectral & microscopic readouts
        self.interrogated_suspects = {}  # Feature 2: Cross-examination dossiers
        self.badges_earned = []          # Feature 5: Case badges earned (Sherlock, Forensics, etc.)

        # Step navigation (0 to 9)
        self.current_step_idx = 0
        self.is_complete = False
        self.is_won = False
        self.rank = "F"
        self.rank_title = "Unsolved"
        self.accused_suspect = None
        self.xp_awarded = 0
        self.coins_awarded = 0

        # Legacy timer & questions tracking
        self.current_q_idx = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.clues_discovered = 0
        self.total_time = 0.0
        self.answers_log = []
        self.q_start_time = 0.0
        self.q_time_limit = 20.0

    # ── DETECTIVE MODE PROPERTIES ──

    @property
    def total_steps(self) -> int:
        """Total investigation steps (usually 10)."""
        if self.messages:
            return len(self.messages)
        return len(self.questions)

    @property
    def current_message(self) -> dict | None:
        """Returns active investigation turn message."""
        if 0 <= self.current_step_idx < len(self.messages):
            return self.messages[self.current_step_idx]
        return None

    @property
    def is_final_accusation_step(self) -> bool:
        """True when investigator reaches Message 10 (Final Accusation)."""
        if not self.messages:
            return False
        return self.current_step_idx >= len(self.messages) - 1

    def get_atmospheric_sentiment(self, lang: str | None = None) -> str:
        """
        Returns atmospheric narrative guidance indicating the state of the trail
        without exposing raw score percentages to the player.
        """
        active_lang = str(lang) if lang is not None else getattr(self, "lang", "2")
        kp = self.killer_probability
        es = self.evidence_score

        if active_lang == "1":
            if kp <= -4:
                return "⚠️ التحقيق ينحرف في ظلال مظلمة. الخيوط المضللة تتزايد."
            elif kp <= 0:
                return "🔍 الأثر بارد. تحتاج إلى أدلة جنائية ملموسة ووضوح في الدوافع."
            elif kp <= 4:
                return "🕯️ خيط أمل يلوح بالأفق. تناقضات شهادات المشتبه بهم بدأت بالظهور."
            elif kp <= 7:
                return "✨ خيوط القضية تترابط بدقة. دائرة الحقيقة تضيق بسرعة."
            else:
                return "🎯 الدليل القاطع بين يديك! كل المؤشرات الجنائية تشير مباشرة إلى الجاني الخفي."
        else:
            if kp <= -4:
                return "⚠️ The investigation is straying into deep shadows. False leads and decoys multiply."
            elif kp <= 0:
                return "🔍 The trail is cold. You need more concrete forensic links and motive clarity."
            elif kp <= 4:
                return "🕯️ A faint thread emerges. Suspect alibis and contradictions begin to surface."
            elif kp <= 7:
                return "✨ The pieces are locking into place. The circle of truth narrows rapidly."
            else:
                return "🎯 The scent is undeniable! Every forensic sign points directly toward the hidden hand."

    def choose_turn_option(self, option_idx: int) -> dict:
        """
        Investigator makes one of 4 tactical decisions in the current message.
        Updates hidden scores, unlocks clues in the Case Dossier, and advances turn.
        """
        msg = self.current_message
        if not msg or self.is_complete:
            return {"accepted": False, "reason": "No active investigation turn"}

        options = msg.get("options", [])
        if not (0 <= option_idx < len(options)):
            return {"accepted": False, "reason": "Invalid choice index"}

        opt = options[option_idx]
        delta_k = opt.get("killer_delta", 0)
        delta_e = opt.get("evidence_score_delta", 0)
        clue_id = opt.get("unlocked_clue_id")
        feedback = opt.get("feedback", "")

        # Update hidden score mechanics
        self.killer_probability = max(-10, min(10, self.killer_probability + delta_k))
        self.evidence_score = max(0, min(100, self.evidence_score + delta_e))

        # Unlock clue in dossier if attached
        clue_unlocked_obj = None
        if clue_id and clue_id not in self.unlocked_clue_ids:
            self.unlocked_clue_ids.add(clue_id)
            clue_unlocked_obj = self.get_clue_by_id(clue_id)

        # Log investigator choice
        self.choices_log.append({
            "step": self.current_step_idx + 1,
            "choice_text": opt.get("text", ""),
            "feedback": feedback,
            "killer_delta": delta_k,
            "evidence_delta": delta_e,
            "clue_unlocked": clue_id,
        })

        # Advance to next message
        self.current_step_idx += 1

        is_accusation = self.is_final_accusation_step

        return {
            "accepted": True,
            "feedback": feedback,
            "sentiment": self.get_atmospheric_sentiment(),
            "clue_unlocked": clue_unlocked_obj,
            "is_accusation": is_accusation,
            "next_step": self.current_step_idx + 1,
        }

    def make_final_accusation(self, suspect_name: str, username: str | None = None) -> dict:
        """
        Turn 10 Final Accusation. Evaluates suspect choice against hidden metrics.
        Assigns ranks: S, A, B, C, D, F and grants user XP & coins.
        """
        self.accused_suspect = suspect_name
        self.is_complete = True

        is_culprit = suspect_name.strip().lower() == self.true_culprit.strip().lower()
        self.is_won = is_culprit

        # Multi-Tier Ranking Engine
        is_ar = str(getattr(self, "lang", "2")) == "1"
        if is_culprit:
            if self.evidence_score >= self.rank_thresholds.get("S", 75):
                self.rank = "S"
                self.rank_title = "محقق أسطوري" if is_ar else "MASTER DETECTIVE"
                self.xp_awarded = 150
                self.coins_awarded = 25
            elif self.evidence_score >= self.rank_thresholds.get("A", 55):
                self.rank = "A"
                self.rank_title = "محقق نخبة" if is_ar else "ELITE INVESTIGATOR"
                self.xp_awarded = 120
                self.coins_awarded = 18
            elif self.evidence_score >= self.rank_thresholds.get("B", 35):
                self.rank = "B"
                self.rank_title = "محقق قدير" if is_ar else "COMPETENT DETECTIVE"
                self.xp_awarded = 90
                self.coins_awarded = 12
            else:
                self.rank = "C"
                self.rank_title = "تخمين محظوظ" if is_ar else "LUCKY GUESS"
                self.xp_awarded = 60
                self.coins_awarded = 8
        else:
            if self.evidence_score >= self.rank_thresholds.get("C", 20):
                self.rank = "D"
                self.rank_title = "اتهام خاطئ" if is_ar else "WRONG ACCUSATION"
                self.xp_awarded = 20
                self.coins_awarded = 2
            else:
                self.rank = "F"
                self.rank_title = "قضية معلقة" if is_ar else "CASE UNSOLVED"
                self.xp_awarded = 0
                self.coins_awarded = 0

        # Feature 5: Evaluate Badges Earned
        if self.is_won and self.rank == "S" and "Mind of Sherlock" not in self.badges_earned:
            self.badges_earned.append("Mind of Sherlock")
        if len(self.analyzed_clues) >= 2 and "Master of Forensics" not in self.badges_earned:
            self.badges_earned.append("Master of Forensics")
        if len(self.interrogated_suspects) >= max(1, len(self.suspects)) and "Ironclad Interrogator" not in self.badges_earned:
            self.badges_earned.append("Ironclad Interrogator")

        # Award persistent user progression
        if username:
            try:
                if award_avatar_win_xp and self.is_won:
                    award_avatar_win_xp(username, mode="investigation")
                if add_user_coins and self.coins_awarded > 0:
                    add_user_coins(self.coins_awarded, username)
                if award_detective_career_xp:
                    award_detective_career_xp(username, self.xp_awarded, case_won=self.is_won, badges=self.badges_earned)
                if self.is_won:
                    from game.accounts import record_case_solved
                    record_case_solved(username, self.id)
            except Exception:
                pass

        return self.get_final_evaluation(username=username)

    # ── FEATURE 1: FORENSIC LAB EVIDENCE MAGNIFIER & DEEP ANALYSIS ────────────
    def analyze_clue(self, clue_id: str) -> dict:
        """
        Forensic Lab Magnifier: Examines clue under spectral/microscopic analysis.
        Uncovers latent fingerprints, chemical markers, or micro-traces.
        Awards +15 Evidence Score points and records forensic findings.
        """
        clue = self.get_clue_by_id(clue_id)
        is_ar = str(getattr(self, "lang", "2")) == "1"

        title = "Evidence Note"
        desc = "Forensic sample"
        if clue:
            title = clue.get("title", "Evidence Note")
            desc = clue.get("description", "")
        else:
            for idx, c in enumerate(self.clues):
                if f"clue_{idx+1}" == clue_id or str(idx+1) == str(clue_id):
                    title = f"Evidence Note #{idx+1}"
                    desc = str(c)
                    clue_id = f"clue_{idx+1}"
                    break

        self.analyzed_clues.add(clue_id)
        self.unlocked_clue_ids.add(clue_id)

        pts = 15
        self.evidence_score = min(100, self.evidence_score + pts)

        if is_ar:
            finding = f"🔬 الفحص المجهري لـ '{title}': تم رصد تطابق دقيق في البصمات الجنائية والآثار المجهرية مع مسرح الجريمة (+15 نقطة أدلة)."
        else:
            finding = f"🔬 Spectral Micro-Analysis for '{title}': Latent forensic markers and toolmark striations precisely match the crime scene (+15 Evidence Points)."

        self.forensic_findings[clue_id] = finding

        if len(self.analyzed_clues) >= 2 and "Master of Forensics" not in self.badges_earned:
            self.badges_earned.append("Master of Forensics")

        return {
            "success": True,
            "clue_id": clue_id,
            "title": title,
            "finding": finding,
            "evidence_score": self.evidence_score,
            "analyzed_count": len(self.analyzed_clues),
            "total_clues": len(self.clues),
        }

    # ── FEATURE 2: SUSPECT INTERROGATION & ALIBI CROSS-EXAMINATION ───────────
    def interrogate_suspect(self, suspect_name: str) -> dict:
        """
        Cross-examines suspect alibi against collected forensic evidence.
        Measures psychological stress markers, exposes contradictions,
        and calculates real-time suspicion probability.
        """
        is_ar = str(getattr(self, "lang", "2")) == "1"
        profiles = self.get_suspect_profiles()
        suspect = None
        for p in profiles:
            if p.get("name", "").strip().lower() == suspect_name.strip().lower():
                suspect = p
                break
        if not suspect:
            suspect = {
                "name": suspect_name,
                "role": "Person of Interest",
                "public_story": "Under investigation.",
                "private_secret": "Classified.",
                "motive": "Unknown.",
                "alibi": "Unverified.",
                "weakness": "None recorded.",
            }

        is_culprit = suspect_name.strip().lower() == getattr(self, "true_culprit", "").strip().lower()

        unlocked_count = len(self.unlocked_clue_ids)
        if is_culprit:
            suspicion = min(98, 62 + unlocked_count * 6)
            stress = "مرتبك للغاية ويتصبب عرقاً" if is_ar else "Panicked & Sweating"
            contradictions = [
                "تضارب صارخ بين توقيت الخروج المزعوم والأدلة المادية في مسرح الجريمة" if is_ar else "Direct conflict between departure time and crime scene evidence",
                "سجلات الدخول تُكذّب ادعاء عدم التواجد قرب الموقع" if is_ar else "Access logs directly refute claims of absence from the area",
                f"نقطة الضعف المكشوفة: {suspect.get('weakness', 'ارتباك غير مبرر')}" if is_ar else f"Exposed weakness: {suspect.get('weakness', 'Unexplained agitation')}"
            ]
            q_text = "أين كنت بالتحديد أثناء ارتكاب الجريمة، ولماذا تتطابق الأدلة الجنائية معك؟" if is_ar else "Where were you at the exact hour of the crime, and why does the physical evidence point to you?"
            a_text = "هذا... هذا افتراء! كنت في مكاني المعتاد! لا يمكنكم إثبات شيء ضدي بمجرد شكوك زائفة!" if is_ar else "That's... that's ridiculous! I was in my quarters! You cannot prove anything against me with mere circumstantial noise!"
        else:
            suspicion = max(12, 38 - unlocked_count * 4)
            stress = "هادئ وواثق من براءته" if is_ar else "Calm & Cooperative"
            contradictions = [
                "شهادات الشهود المستقلين تؤكد صحة عذره" if is_ar else "Independent witness testimonies corroborate the stated alibi",
                "لا توجد أي بصمات أو آثار مادية تربطه بمسرح الجريمة" if is_ar else "No forensic traces or fingerprints link them to the crime scene"
            ]
            q_text = "هل يمكنك تأكيد تحركاتك وتقديم ما يثبت عدم صلتك بالقضية؟" if is_ar else "Can you corroborate your movements and confirm your detachment from the incident?"
            a_text = "لقد قدمت كل ما لدي لحرس التحقيق. عذري موثق بالشهود وليس لدي ما أخفيه إطلاقاً." if is_ar else "I have shared everything with the investigators. My alibi is documented and I have nothing to hide."

        interrogation_record = {
            "name": suspect["name"],
            "role": suspect.get("role", "Suspect"),
            "suspicion": suspicion,
            "stress": stress,
            "contradictions": contradictions,
            "question": q_text,
            "answer": a_text,
            "is_prime": suspicion >= 60,
        }

        self.interrogated_suspects[suspect["name"]] = interrogation_record

        if len(self.interrogated_suspects) >= max(1, len(self.suspects)) and "Ironclad Interrogator" not in self.badges_earned:
            self.badges_earned.append("Ironclad Interrogator")

        return {
            "success": True,
            "suspect": interrogation_record,
            "interrogated_count": len(self.interrogated_suspects),
            "total_suspects": len(self.suspects),
        }

    # ── FEATURE 3: DETECTIVE INTUITION / SHERLOCK INSIGHT LIFELINE ───────────
    def use_detective_intuition(self) -> dict:
        """
        Sherlock Intuition Lifeline: Deductive insight that eliminates a deceptive decoy
        option and pinpoints the strongest forensic deduction. 2 charges per case.
        """
        is_ar = str(getattr(self, "lang", "2")) == "1"
        if self.intuition_charges <= 0:
            return {
                "success": False,
                "reason": "نفذت محاولات إلهام المحقق لهذه القضية!" if is_ar else "No Intuition charges remaining for this case!"
            }

        self.intuition_charges -= 1

        eliminated_idx = None
        recommended_idx = None
        whisper = ""

        # Check if turn-based interactive mode
        msg = self.current_message
        if msg and msg.get("options"):
            opts = msg["options"]
            min_score = 999
            max_score = -999
            for i, opt in enumerate(opts):
                k = opt.get("killer_delta", 0) + opt.get("evidence_score_delta", 0)
                if k < min_score:
                    min_score = k
                    eliminated_idx = i
                if k > max_score:
                    max_score = k
                    recommended_idx = i

            if eliminated_idx == recommended_idx:
                for i in range(len(opts)):
                    if i != recommended_idx:
                        eliminated_idx = i
                        break

            ar_letters = ["أ", "ب", "ج", "د"]
            en_letters = ["A", "B", "C", "D"]
            e_let = ar_letters[eliminated_idx] if (is_ar and eliminated_idx is not None and eliminated_idx < len(ar_letters)) else en_letters[eliminated_idx if eliminated_idx is not None else 0]
            r_let = ar_letters[recommended_idx] if (is_ar and recommended_idx is not None and recommended_idx < len(ar_letters)) else en_letters[recommended_idx if recommended_idx is not None else 0]

            if is_ar:
                whisper = f"💡 إلهام شارلوك: احذر الخيار ({e_let})! إنه فخ مضلل. المسار الأدق هو ربط الأدلة في الخيار ({r_let})."
            else:
                whisper = f"💡 Sherlock Insight: Beware Option ({e_let})! It's a deceptive trap. The sharpest deduction lies in Option ({r_let})."

        elif self.current_question:
            # Legacy questions mode
            q = self.current_question
            raw_choices = q.get("choices", "")
            choices = [c.strip() for c in raw_choices.split("|")] if isinstance(raw_choices, str) else list(raw_choices)
            corr = q.get("answer", "").strip().lower()

            for i, c in enumerate(choices):
                if c.strip().lower() != corr:
                    eliminated_idx = i
                    break

            whisper = f"💡 حدس المحقق: تم استبعاد الخيار المضلل ({choices[eliminated_idx] if eliminated_idx is not None else ''})." if is_ar else f"💡 Detective Intuition: Deceptive option eliminated ({choices[eliminated_idx] if eliminated_idx is not None else ''})."

        return {
            "success": True,
            "charges_remaining": self.intuition_charges,
            "eliminated_idx": eliminated_idx,
            "recommended_idx": recommended_idx,
            "whisper": whisper,
        }

    # ── FEATURE 4: CRIME SCENE RECONSTRUCTION SIMULATION ─────────────────────
    def get_crime_scene_reconstruction(self) -> dict:
        """
        Reconstructs the 5 chronological phases of the crime scene:
        1. Pre-Meditation & Motive
        2. Security Infiltration & Breach
        3. The Execution of the Crime
        4. Escape & Evidence Tampering
        5. Fabrication of False Alibi
        Calculates reconstruction accuracy based on unlocked evidence.
        """
        is_ar = str(getattr(self, "lang", "2")) == "1"
        culprit = getattr(self, "true_culprit", "The Culprit")
        title = getattr(self, "title", "The Case")

        unlocked_count = len(self.unlocked_clue_ids)
        analyzed_count = len(self.analyzed_clues)
        intel_level = unlocked_count + analyzed_count

        phases = [
            {
                "phase": 1,
                "name": "التخطيط والدوافع المسبقة" if is_ar else "Pre-Meditation & Motive",
                "desc": f"دراسة نقاط الضعف واكتساب الأدوات ووسائل الوصول قبل تنفيذ العملية ضد {title}." if is_ar else f"Studying vulnerabilities, acquiring access tools, and establishing opportunity against {title}.",
                "verified": intel_level >= 1,
                "icon": "🧠",
            },
            {
                "phase": 2,
                "name": "اختراق الموقع وتجاوز الحراسة" if is_ar else "Point of Infiltration & Breach",
                "desc": "الدخول المتسلل تحت جنح الظلام وتفادي نقاط المراقبة والقفل دون إثارة الشبهات." if is_ar else "Covert entry under cover of darkness, bypassing surveillance and locks without alerting guards.",
                "verified": intel_level >= 2,
                "icon": "🚪",
            },
            {
                "phase": 3,
                "name": "تنفيذ الجريمة في مسرح الأحداث" if is_ar else "Execution of the Illicit Act",
                "desc": f"قام الجاني ({culprit}) بالاستيلاء على الهدف وإحداث الأثر الجنائي المكتشف في المختبر." if is_ar else f"The culprit ({culprit}) executed the primary deed, leaving latent traces confirmed by forensic lab.",
                "verified": intel_level >= 3,
                "icon": "⚡",
            },
            {
                "phase": 4,
                "name": "الهروب وتضليل مسار التحقيق" if is_ar else "Escape & Evidence Tampering",
                "desc": "مغادرة مسرح الجريمة بزرع خيوط تضليل وتشويه سجلات الحراسة لإبعاد الشبهة." if is_ar else "Fleeing the scene while planting misleading decoys and altering logs to misdirect inquiries.",
                "verified": intel_level >= 4,
                "icon": "👣",
            },
            {
                "phase": 5,
                "name": "تلفيق العذر وحبك الرواية الكاذبة" if is_ar else "Fabrication of False Alibi",
                "desc": "الظهور بمظهر البريء وادعاء التواجد في مكان آخر لتفادي أصابع الاتهام." if is_ar else "Assuming an innocent demeanor and staging a fabricated alibi to deflect official scrutiny.",
                "verified": intel_level >= 5,
                "icon": "🎭",
            },
        ]

        verified_cnt = sum(1 for p in phases if p["verified"])
        confidence = min(100, int((verified_cnt / 5.0) * 100))

        return {
            "case_title": title,
            "culprit": culprit,
            "phases": phases,
            "verified_phases": verified_cnt,
            "total_phases": 5,
            "confidence_percent": confidence,
        }

    def get_clue_by_id(self, clue_id: str) -> dict | None:
        """Find clue dictionary by ID."""
        for c in self.clues:
            if isinstance(c, dict) and c.get("id") == clue_id:
                return c
        return None

    def get_unlocked_clues(self) -> list[dict]:
        """Returns all clues currently unlocked in the player's Case Dossier."""
        results = []
        for idx, c in enumerate(self.clues):
            if isinstance(c, dict):
                cid = c.get("id")
                if cid and cid in self.unlocked_clue_ids:
                    results.append(c)
            else:
                str_id = f"clue_{idx+1}"
                if str_id in self.unlocked_clue_ids or "all" in self.unlocked_clue_ids:
                    results.append({"id": str_id, "title": f"Evidence Note #{idx+1}", "description": str(c), "category": "Note", "role": "Supporting"})
        return results

    def get_suspect_profiles(self) -> list[dict]:
        """Returns structured suspect rosters for the Dossier modal."""
        profiles = []
        for s in self.suspects:
            if isinstance(s, dict):
                profiles.append(s)
            else:
                profiles.append({
                    "name": str(s),
                    "role": "Person of Interest",
                    "public_story": "Under investigation.",
                    "private_secret": "Classified.",
                    "motive": "Unknown.",
                    "alibi": "Unverified.",
                    "weakness": "None recorded.",
                    "relationship": "Associate",
                })
        return profiles

    def get_final_evaluation(self, username: str | None = None) -> dict:
        """Returns complete case resolution and rank breakdown."""
        eval_data = {
            "case_id": self.id,
            "case_title": self.title,
            "category": self.category,
            "difficulty": self.difficulty,
            "is_won": self.is_won,
            "rank": self.rank,
            "rank_title": self.rank_title,
            "accused_suspect": self.accused_suspect,
            "true_culprit": self.true_culprit,
            "true_solution": self.true_solution,
            "evidence_score": self.evidence_score,
            "clues_unlocked": len(self.unlocked_clue_ids),
            "total_clues": len(self.clues),
            "analyzed_clues_count": len(self.analyzed_clues),
            "interrogated_suspects_count": len(self.interrogated_suspects),
            "intuition_used": 2 - self.intuition_charges,
            "badges_earned": self.badges_earned,
            "xp_awarded": self.xp_awarded,
            "coins_awarded": self.coins_awarded,
            "choices_history": self.choices_log,
        }
        if username and get_detective_career:
            try:
                eval_data["career"] = get_detective_career(username, is_arabic=str(getattr(self, "lang", "2")) == "1")
            except Exception:
                pass
        return eval_data

    # ── LEGACY BACKWARD COMPATIBILITY (Questions API) ──

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def current_question(self) -> dict | None:
        if 0 <= self.current_q_idx < len(self.questions):
            return self.questions[self.current_q_idx]
        return None

    def start_question(self):
        q = self.current_question
        if q:
            self.q_time_limit = q.get("time_limit", 20)
            self.q_start_time = time.time()

    def get_time_remaining(self) -> float:
        elapsed = time.time() - self.q_start_time
        return max(0.0, self.q_time_limit - elapsed)

    def is_time_expired(self) -> bool:
        return self.get_time_remaining() <= 0.0

    def submit_answer(self, chosen: str) -> dict:
        q = self.current_question
        if not q or self.is_complete:
            return {"accepted": False, "reason": "No active question"}

        time_taken = time.time() - self.q_start_time
        correct_answer = q.get("answer", "").strip().lower()
        chosen_clean = chosen.strip().lower()

        is_correct = chosen_clean == correct_answer

        if is_correct:
            self.correct_count += 1
            self.evidence_score = min(100, self.evidence_score + 20)
        else:
            self.wrong_count += 1

        self.total_time += min(time_taken, self.q_time_limit)
        self.answers_log.append({
            "question": q["question"],
            "chosen": chosen,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "time_taken": round(time_taken, 2),
        })

        self.current_q_idx += 1
        if self.current_q_idx >= len(self.questions):
            self._finalize_legacy()

        return {
            "accepted": True,
            "is_correct": is_correct,
            "correct_answer": q["answer"],
            "time_taken": round(time_taken, 2),
        }

    def timeout_answer(self) -> dict:
        if self.is_complete:
            return {"accepted": False, "reason": "Case already complete"}
        q = self.current_question
        if not q:
            return {"accepted": False}

        self.wrong_count += 1
        self.total_time += self.q_time_limit
        self.answers_log.append({
            "question": q["question"],
            "chosen": "[TIMED OUT]",
            "correct_answer": q["answer"],
            "is_correct": False,
            "time_taken": self.q_time_limit,
        })

        self.current_q_idx += 1
        if self.current_q_idx >= len(self.questions):
            self._finalize_legacy()

        return {"accepted": True, "is_correct": False, "timed_out": True}

    def _finalize_legacy(self, username: str | None = None):
        self.is_complete = True
        self.is_won = (self.correct_count / max(1, self.total_questions)) > 0.5
        self.clues_discovered = len(self.clues)
        if not username:
            try:
                from game.accounts import get_current_username
                username = get_current_username()
            except Exception:
                username = None
        if username and self.is_won:
            try:
                from game.accounts import award_avatar_win_xp, add_user_coins, record_case_solved
                award_avatar_win_xp(username, mode="investigation")
                add_user_coins(15, username)
                record_case_solved(username, self.id)
            except Exception:
                pass

    def get_results(self) -> dict:
        return {
            "case_title": self.title,
            "difficulty": self.difficulty,
            "is_won": self.is_won,
            "correct_deductions": self.correct_count,
            "incorrect_deductions": self.wrong_count,
            "total_questions": self.total_questions,
            "score_percent": round((self.correct_count / max(1, self.total_questions)) * 100, 1),
            "evidence_discovered": self.clues_discovered,
            "total_evidence": len(self.clues),
            "total_time": round(self.total_time, 1),
            "answers_log": self.answers_log,
        }


# ── MODULE LEVEL API ─────────────────────────────────────────────────────────

def get_available_cases(category: str = "legacy", lang: str = "2") -> list[dict]:
    """
    Returns available cases.
    Defaults to 3 legacy starter cases for 100% backward compatibility
    with existing unit tests (`len(get_available_cases()) == 3`).
    """
    if category == "detective" or category == "all_new":
        return get_all_detective_cases(lang=lang)

    # Legacy built-in cases
    cases_source = BUILTIN_CASES_AR if str(lang) == "1" else BUILTIN_CASES
    cases = []
    for c in cases_source:
        cases.append({
            "id": c["id"],
            "title": c["title"],
            "difficulty": c.get("difficulty", "Medium" if str(lang) != "1" else "متوسط"),
            "questions_count": len(c.get("questions", [])),
            "suspects_count": len(c.get("suspects", [])),
        })
    return cases


def get_detective_cases(lang: str = "2") -> list[dict]:
    """Returns all 20 advanced interactive detective cases."""
    return get_all_detective_cases(lang=lang)


def load_case(case_id: str, lang: str = "2") -> InvestigationCase | None:
    """
    Load a case by ID. Supports:
      - 'case_001', 'case_002', 'case_003' (built-in legacy starter cases)
      - 'case_01' through 'case_20' (the 20 full detective cases)
    """
    # 1. Check built-in legacy cases
    legacy_list = BUILTIN_CASES_AR if str(lang) == "1" else BUILTIN_CASES
    for c in legacy_list:
        if c["id"] == case_id:
            return InvestigationCase(c, lang=lang)

    # Fallback to English legacy if not in Arabic
    for c in BUILTIN_CASES:
        if c["id"] == case_id:
            return InvestigationCase(c, lang=lang)

    # 2. Check 20-case master database
    case_data = get_detective_case_by_id(case_id, lang=lang)
    if case_data:
        return InvestigationCase(case_data, lang=lang)

    return None
