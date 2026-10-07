"""
language.py — language selection, Arabic option formatting, and UI localization.
Uses __file__-relative paths so the game works from any working directory.
"""
import re
from pathlib import Path
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from player_info import player

# Absolute path to question_bank/ — works whether launched as .py or .exe
_QB_DIR = Path(__file__).parent / "question_bank"

# Arabic open-answer markers (normalize both English and Arabic "none")
_NO_CHOICE_MARKERS = {"none", "لا أحد", "لايوجد", ""}

# ── ARABIC MULTIPLE CHOICE OPTION MAPPINGS ─────────────────────────────────────
EN_TO_AR_CHOICE = {"A": "أ", "B": "ب", "C": "ج", "D": "د", "a": "أ", "b": "ب", "c": "ج", "d": "د"}
AR_TO_EN_CHOICE = {"أ": "a", "ب": "b", "ج": "c", "د": "d", "ا": "a", "إ": "a", "آ": "a", "A": "a", "B": "b", "C": "c", "D": "d", "a": "a", "b": "b", "c": "c", "d": "d"}


def format_choice_for_lang(choice_text: str, is_arabic: bool = False) -> str:
    """
    Format multiple choice prefix for Arabic (أ، ب، ج، د) or English (A, B, C, D).
    e.g. 'A) القاهرة' -> 'أ) القاهرة' if is_arabic.
    """
    if not choice_text:
        return ""
    clean = choice_text.strip()
    if is_arabic:
        m = re.match(r"^([A-Da-d])\)\s*(.*)", clean)
        if m:
            letter = m.group(1).upper()
            rest = m.group(2).strip()
            ar_letter = EN_TO_AR_CHOICE.get(letter, letter)
            return f"{ar_letter}) {rest}"
    return clean


def extract_choice_letter(chosen_text: str) -> str:
    """
    Extract normalized lowercase letter ('a', 'b', 'c', 'd') from any choice string,
    supporting both English ('A) Paris') and Arabic ('أ) باريس').
    """
    if not chosen_text:
        return ""
    clean = chosen_text.strip()
    # Check Arabic prefix (e.g. 'أ) ' or 'أ : ')
    m_ar = re.match(r"^([أ-دإآا])[\)\:\.\s\-]\s*", clean)
    if m_ar:
        return AR_TO_EN_CHOICE.get(m_ar.group(1), clean.lower())

    # Check English prefix (e.g. 'A) ' or 'b: ')
    m_en = re.match(r"^([A-Da-d])[\)\:\.\s\-]\s*", clean)
    if m_en:
        return m_en.group(1).lower()

    # Raw single letter check
    if clean.lower() in AR_TO_EN_CHOICE:
        return AR_TO_EN_CHOICE[clean.lower()]

    return clean.lower()


def format_answer_letter_display(letter: str, is_arabic: bool = False) -> str:
    """Returns 'أ' or 'A' based on language."""
    let = str(letter).strip().upper()
    if is_arabic:
        return EN_TO_AR_CHOICE.get(let, let)
    return let


# ── COMPREHENSIVE LOCALIZATION STRINGS ─────────────────────────────────────────
LOCALIZATION = {
    # Main Menu
    "game_title": {
        "1": "من هو الأكثر غباءً؟",
        "2": "WHO IS THE DUMPEST OF ALL?"
    },
    "game_subtitle": {
        "1": "النسخة المتكاملة • قتال مباشر ومعارك جماعية حية",
        "2": "Ultimate Commercial Edition • Real-Time Combat & Team Battles"
    },
    "btn_singleplayer": {
        "1": "🎮 طور اللعب الفردي",
        "2": "🎮 SINGLEPLAYER CAMPAIGN"
    },
    "btn_multiplayer": {
        "1": "⚔️ أونلاين والغرف الجماعية",
        "2": "⚔️ MULTIPLAYER & ROOM ARENA"
    },
    "btn_investigation": {
        "1": "🔍 طور التحقيق الجنائي",
        "2": "🔍 INVESTIGATION MODE"
    },
    "btn_avatar_hub": {
        "1": "👑 ملف المحارب والهالة",
        "2": "👑 AVATAR PROFILE HUB"
    },
    "btn_store": {
        "1": "🏰 متجر الأسلحة والعتاد",
        "2": "🏰 AAA GAME STORE & SHOP"
    },
    "btn_journal": {
        "1": "📜 سجل المعارك والمسيرة",
        "2": "📜 MATCH CAREER JOURNAL"
    },
    "btn_hall_of_fame": {
        "1": "🏆 قائمة الشرف العالمية",
        "2": "🏆 GLOBAL HALL OF FAME"
    },
    "btn_spin": {
        "1": "🎰 عجلة الحظ (24س)",
        "2": "🎰 SPIN (24H)"
    },
    "btn_settings": {
        "1": "⚙️ الإعدادات",
        "2": "⚙️ SETTINGS"
    },
    "btn_logout": {
        "1": "🚪 تسجيل خروج",
        "2": "🚪 LOGOUT"
    },
    "btn_exit_game": {
        "1": "❌ خروج من اللعبة",
        "2": "❌ EXIT GAME"
    },
    "btn_lang_toggle": {
        "1": "🌐 English",
        "2": "🌐 العربية"
    },
    "col_battle_modes": {
        "1": "🕹️ أطوار اللعب والتحدي",
        "2": "🕹️ BATTLE & GAME MODES"
    },
    "col_player_hub": {
        "1": "👑 المركز الشخصي والمتجر",
        "2": "👑 PLAYER HUB & STORE"
    },
    "spin_ready": {
        "1": "✨ جاهز للسحب الآن!",
        "2": "✨ SPIN READY!"
    },
    "spin_cooldown": {
        "1": "⏱️ السحب القادم خلال:",
        "2": "⏱️ Spin in:"
    },

    # Singleplayer Setup Screen
    "setup_title": {
        "1": "إعدادات المعركة الفردية",
        "2": "SINGLEPLAYER BATTLE SETUP"
    },
    "setup_subjects_hdr": {
        "1": "📚 اختر مجالات المعرفة (مجالين على الأقل):",
        "2": "📚 Select Knowledge Subjects (At least 2):"
    },
    "setup_diff_hdr": {
        "1": "⚡ اختر مستوى الصعوبة:",
        "2": "⚡ Select Match Difficulty:"
    },
    "btn_start_quiz": {
        "1": "▶️ بدء التحدي",
        "2": "▶️ START QUIZ"
    },
    "btn_back": {
        "1": "← رجوع",
        "2": "← BACK"
    },
    "sub_math": {"1": "📐 رياضيات", "2": "📐 Math"},
    "sub_science": {"1": "🔬 علوم", "2": "🔬 Science"},
    "sub_history": {"1": "🏛️ تاريخ", "2": "🏛️ History"},
    "sub_programming": {"1": "💻 برمجة", "2": "💻 Coding"},
    "sub_sports": {"1": "⚽ رياضة", "2": "⚽ Sports"},
    "sub_cars": {"1": "🏎️ سيارات", "2": "🏎️ Cars"},
    "sub_car_badges": {"1": "🛡️ شعارات السيارات", "2": "🛡️ Car Badges"},
    "sub_literature": {"1": "📚 أدب ولغة", "2": "📚 Literature"},
    "sub_anime": {"1": "⚔️ أنمي", "2": "⚔️ Anime"},
    "sub_general": {"1": "💡 ثقافة عامة", "2": "💡 General"},

    "diff_novice": {"1": "مبتدئ (8 أسئلة)", "2": "NOVICE (8 Qs)"},
    "diff_apprentice": {"1": "متدرب (12 سؤالاً)", "2": "APPRENTICE (12 Qs)"},
    "diff_adept": {"1": "محترف (16 سؤالاً)", "2": "ADEPT (16 Qs)"},
    "diff_master": {"1": "خبير (20 سؤالاً)", "2": "MASTER (20 Qs)"},
    "diff_nightmare": {"1": "كابوس (25 سؤالاً)", "2": "NIGHTMARE (25 Qs)"},
    "diff_blitz": {"1": "⚡ البرق (15 سؤالاً)", "2": "⚡ BLITZ (15 Qs)"},

    # Gameplay Screen
    "btn_giveup": {
        "1": "استسلام [Ctrl+Q]",
        "2": "GIVE UP [Ctrl+Q]"
    },
    "btn_5050": {
        "1": "حذف خيارين [Ctrl+1]",
        "2": "50:50 [Ctrl+1]"
    },
    "btn_freeze": {
        "1": "تجميد [Ctrl+2]",
        "2": "FREEZE [Ctrl+2]"
    },
    "btn_swap": {
        "1": "تبديل [Ctrl+3]",
        "2": "SWAP [Ctrl+3]"
    },
    "btn_poll": {
        "1": "الجمهور [Ctrl+4]",
        "2": "POLL [Ctrl+4]"
    },
    "btn_heal": {
        "1": "جرعة شفاء [Ctrl+H]",
        "2": "POTION [Ctrl+H]"
    },
    "typing_placeholder": {
        "1": "اكتب إجابتك هنا واضغط ENTER...",
        "2": "Type answer here and press ENTER..."
    },
    "hit_feedback": {
        "1": "✨ ضربة ذكاء خارقة! (+{dmg} ضرر، حماس x{streak})!",
        "2": "✨ 300 IQ HIT! (+{dmg} DMG, Streak x{streak})!"
    },
    "wrong_feedback": {
        "1": "❌ إجابة خاطئة! الإجابة الصحيحة: {correct}",
        "2": "❌ WRONG! Correct: {correct}"
    },
    "shield_absorb": {
        "1": "🛡️ الدرع امتص الخطأ وحماك!",
        "2": "🛡️ SHIELD ABSORBED THE MISTAKE!"
    },
    "notice_5050": {
        "1": "🎯 تم حذف خيارين خاطئين!",
        "2": "🎯 50:50: Two wrong options eliminated!"
    },
    "notice_freeze": {
        "1": "❄️ تجميد الوقت: تم إضافة +10 ثوانٍ!",
        "2": "❄️ CHRONO FREEZE: +10s Time Added!"
    },
    "notice_swap": {
        "1": "🔀 تم استبدال السؤال بنجاح!",
        "2": "🔀 ASTRAL SWAP: Question Swapped!"
    },
    "notice_poll": {
        "1": "📊 استطلاع الجمهور: 74% اختاروا [{ans}]!",
        "2": "📊 AUDIENCE POLL: 74% choose [{ans}]!"
    },
    "notice_potion": {
        "1": "🧪 جرعة الفينيق: تم استعادة +35 صحة!",
        "2": "🧪 PHOENIX POTION: +35 HP Restored!"
    },
    "notice_special": {
        "1": "⚡ مهارة خارقة: {name} (+{dmg} ضرر، +{heal} صحة)!",
        "2": "⚡ SPECIAL SKILL: {name} (+{dmg} DMG, +{heal} HP)!"
    },

    "notice_5050_invalid": {
        "1": "⚠️ خاصية 50:50 تنطبق فقط على الاختيار من متعدد!",
        "2": "⚠️ 50:50 is unavailable for this question type!"
    },
    "notice_poll_invalid": {
        "1": "⚠️ استطلاع الجمهور غير متاح للأسئلة الكتابية!",
        "2": "⚠️ Audience Poll is unavailable for this question type!"
    },
    "diff_easy": {
        "1": "سهل",
        "2": "EASY"
    },
    "diff_mid": {
        "1": "متوسط",
        "2": "MID"
    },
    "diff_hard": {
        "1": "صعب",
        "2": "HARD"
    },
    "diff_extreme": {
        "1": "خارق",
        "2": "EXTREME"
    },
    "diff_blitz": {
        "1": "⚡ البرق",
        "2": "⚡ BLITZ"
    },
    "diff_novice": {
        "1": "سهل",
        "2": "EASY"
    },
    "diff_apprentice": {
        "1": "سهل",
        "2": "EASY"
    },
    "diff_adept": {
        "1": "متوسط",
        "2": "MID"
    },
    "diff_master": {
        "1": "صعب",
        "2": "HARD"
    },
    "diff_nightmare": {
        "1": "خارق",
        "2": "EXTREME"
    },
    "btn_play_the_same": {
        "1": "⚡ العب بنفس الإعدادات",
        "2": "⚡ PLAY THE SAME"
    },

    # Store Screen
    "store_title": {
        "1": "🏰 متجر الأسلحة والعتاد الخارق",
        "2": "🏰 AAA RPG STORE & SHOP"
    },
    "cat_featured": {"1": "⭐ المميز", "2": "⭐ FEATURED"},
    "cat_avatars":  {"1": "👤 الشخصيات", "2": "👤 AVATARS"},
    "cat_weapons":  {"1": "⚔️ الأسلحة", "2": "⚔️ WEAPONS"},
    "cat_support":  {"1": "🧪 الدعم والسحر", "2": "🧪 SUPPORT"},
    "cat_shields":  {"1": "🛡️ الدروع", "2": "🛡️ SHIELDS"},
    "cat_arrows":   {"1": "🏹 السهام", "2": "🏹 ARROWS"},
    "btn_purchase": {"1": "شراء", "2": "PURCHASE"},
    "btn_equip":    {"1": "تجهيز", "2": "EQUIP"},
    "btn_equipped": {"1": "مجهز حالياً", "2": "EQUIPPED"},
    "btn_owned":    {"1": "مملوك", "2": "OWNED"},

    # Settings Screen
    "settings_title": {
        "1": "⚙️ إعدادات اللعبة والتفضيلات",
        "2": "⚙️ GAME SETTINGS & PREFERENCES"
    },
    "settings_lang_hdr": {
        "1": "🌐 لغة اللعبة والأسئلة:",
        "2": "🌐 Global Game & Question Language:"
    },
    "settings_view_hdr": {
        "1": "🎨 مظهر وخلفية اللعبة:",
        "2": "🎨 Visual Background Theme:"
    },
    "settings_normal_view": {
        "1": "🌌 المظهر الافتراضي",
        "2": "🌌 NORMAL VIEW"
    },
    "settings_space_view": {
        "1": "✨ مظهر الفضاء",
        "2": "✨ SPACE VIEW"
    },
    "settings_fullscreen": {
        "1": "🖥️ ملء الشاشة / نافذة",
        "2": "🖥️ TOGGLE FULLSCREEN"
    },
}


def t(key: str, lang: str = "2", **kwargs) -> str:
    """Lookup translation for key in specified language ('1' Arabic, '2' English)."""
    item = LOCALIZATION.get(key, {})
    val = item.get(str(lang), item.get("2", key))
    if kwargs:
        try:
            val = val.format(**kwargs)
        except Exception:
            pass
    return val


def display(text: str) -> str:
    """Reshape and reorder Arabic text for correct display."""
    text = str(text)
    if player.language == "1" or any("\u0600" <= c <= "\u06FF" for c in text):
        return get_display(reshape(text))
    return text


def get_path() -> Path:
    """Return the absolute Path to the correct CSV based on player language."""
    if player.language == "1":
        return _QB_DIR / "arabic.csv"
    return _QB_DIR / "english.csv"


def is_open_answer(choices_raw: str) -> bool:
    """Return True if this question has no multiple-choice options."""
    return choices_raw.strip().lower() in _NO_CHOICE_MARKERS

