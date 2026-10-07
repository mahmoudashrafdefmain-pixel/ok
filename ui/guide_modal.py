"""
ui/guide_modal.py — Scrollable Comprehensive In-Game Rulebook Modal for Dump's Test.
Features:
  - 5 Full Information Tabs
  - Smooth Mouse-Wheel and Drag Scrollbar for tall content
  - Full game systems guide
"""
import pygame
from ui.fonts import render_text
from ui.widgets import (
    Button, draw_rounded_rect, BG_DARK, BG_CARD, CARD_BORDER, PRIMARY_GLOW,
    ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED, TEXT_WHITE, TEXT_MUTED
)

TABS_EN = ["🎮 Game Modes", "👥 Team Mode (2v2-4v4)", "⚡ Skills & Controls", "⚔️ Combat & Streaks", "🏰 Shop & Economy"]
TABS_AR = ["🎮 أوضاع اللعب", "👥 طور الفرق (2 ضد 2)", "⚡ المهارات والتحكم", "⚔️ القتال والسلاسل", "🏰 المتجر والاقتصاد"]

GUIDE_DATA_EN = {
    0: [
        ("⚡ Singleplayer Campaign & 60% Rule:", "Conquer levels by scoring strictly > 60% accuracy! 60% or lower is Defeat (0 coins)."),
        ("🪙 Progressive Level Coin Rewards:", "Level 1: 1🪙, Level 2: 2🪙, Level 3: 4🪙, Level 4: 6🪙, Level 5: 8🪙 (scales +2/level)."),
        ("⚡ Blitz Sudden Death Mode:", "15 rapid questions, 6.0s timer per question. 1 wrong answer triggers instant Elimination!"),
        ("🎰 Daily Lucky Spin:", "Spin once every 24 hours on the Main Menu to win free RPG coins (+2 to +10 coins with equal odds)."),
        ("🌐 Generated-Link Web Client:", "Friends join directly via web browser. Note: Instant web client features streamlined RPG visual effects.")
    ],
    1: [
        ("👥 4 Dynamic Teams Arena:", "4 Teams: Blue Dragons, Red Phoenix, Green Emerald, Yellow Titans (1v1 to 4v4 duels)."),
        ("🏆 Authoritative Winner Determination:", "HP is primary ranking: Highest remaining HP wins! If tied, lower cumulative answering time wins!"),
        ("👑 Team Leader & Typing Rules:", "Teammates elect Leader (no self-votes). In typing questions, ONLY the Leader can type and submit!"),
        ("🔒 Private Team Chat & Voting:", "Secret votes accumulate live. Private team chat (120-char limit, anti-spam) enables tactics."),
        ("⚔️ Simultaneous Combat & Elimination:", "All teams answer simultaneously. Faster correct answer attacks first. 0 HP eliminates team!"),
        ("💎 Online Diamonds Economy:", "Online Team Mode rewards Diamonds (💎). Losing team loses 0 currency. No entry fees!")
    ],
    2: [
        ("⚡ [CTRL] Unique Active Skill:", "Press CTRL once per game to activate avatar skill (+20 Burst Damage & +15 HP Heal)!"),
        ("⌨️ Lifeline Shortcuts (Ctrl + 1-4):", "Hold Ctrl to prevent typing interference: [Ctrl+1] 50:50, [Ctrl+2] Freeze, [Ctrl+3] Swap, [Ctrl+4] Poll."),
        ("🧪 [Ctrl + H] Phoenix Potion:", "Instantly restores +25 HP to your health bar (1 use per match)."),
        ("🏳️ [Ctrl + Q] / [Ctrl + G] Give Up:", "Surrender match safely with a confirmation dialog to prevent accidental forfeit.")
    ],
    3: [
        ("⚔️ Live Player Combat (250 HP):", "Every correct answer deals damage to rival teams. Team drops to 0 HP = Defeated & Eliminated!"),
        ("🔥 Strike Scaling (5 -> 10 DMG):", "Base damage scales: 5 ➔ 6 ➔ 7 ➔ 8 ➔ 9 ➔ 10 DMG per consecutive strike! Resets on mistake."),
        ("🛡️ Damage Protection & Absorbs:", "Shields mitigate incoming damage and absorb initial mistakes safely without HP penalty."),
        ("🎲 Winner Punishments:", "Winning team can assign funny live punishments (push-ups, dances, or custom text) to defeated teams.")
    ],
    4: [
        ("🏰 AAA Game Store:", "Unlock 42 Avatars, 49 Swords, 64 Shields, and 16 Support items using Coins (offline) or Diamonds (online)!"),
        ("🔊 Zero-Cost Avatar Voice Preview:", "Click any locked avatar in the shop to preview voice lines with ZERO coin deduction!"),
        ("⚔️ Subtle Passive Item Effects:", "Equipped items give small, balanced permanent perks (+1 to +5 damage, +10 HP, absorb error)."),
        ("💎 Balanced Dual Currency:", "Diamonds are tuned (~10:1 coin ratio, e.g. 150 coins = 15 diamonds). Anti-negative protection active.")
    ]
}

GUIDE_DATA_AR = {
    0: [
        ("⚡ طور اللعب الفردي وقاعدة 60%:", "اجتز المستويات بتحقيق دقة تتجاوز 60% تماماً! تحقيق 60% أو أقل يعد هزيمة دون عملات."),
        ("🪙 مكافآت العملات التصاعدية:", "المستوى 1: 1🪙، المستوى 2: 2🪙، المستوى 3: 4🪙، المستوى 4: 6🪙، المستوى 5: 8🪙 تصاعدياً."),
        ("⚡ طور الموت المفاجئ (البرق):", "15 سؤالاً متتالياً، 6 ثوانٍ لكل سؤال. خطأ واحد يعني الإقصاء الفوري المباشر!"),
        ("🎰 عجلة الحظ اليومية:", "دور العجلة مرة واحدة كل 24 ساعة من القائمة الرئيسية لربح من 2 إلى 10 عملات RPG مجانية."),
        ("🌐 عميل الويب عبر الرابط:", "يمكن لأصدقائك الانضمام مباشرة من متصفح الهاتف أو الكمبيوتر بنقرة واحدة عبر الرابط.")
    ],
    1: [
        ("👥 ساحة الـ 4 فرق التنافسية:", "4 فرق: التنانين الزرقاء، العنقاء الحمراء، الزمرد الأخضر، والجبابرة الصفراء (1 ضد 1 حتى 4 ضد 4)."),
        ("🏆 التحديد الحاسم للفائز:", "نقاط الحياة (HP) هي المعيار الأول: الفريق الأعلى صحة يفوز! عند التعادل، الأسرع إجابة يفوز!"),
        ("👑 قائد الفريق وأسئلة الكتابة:", "ينتخب الفريق قائداً (بدون تصويت للنفس). في أسئلة الكتابة، القائد فقط هو المخول بالإجابة!"),
        ("🔒 شات الفريق والتصويت السري:", "أصوات الفريق سرية وتتجمع مباشرة. شات الفريق الخاص (120 حرفاً ومضاد للتكرار) يتيح التخطيط."),
        ("⚔️ قتال متزامن وإقصاء:", "جميع الفرق تجيب في آن واحد. الإجابة الصحيحة الأسرع تهاجم أولاً. وصول الصحة لـ 0 يقصي الفريق!"),
        ("💎 اقتصاد الألماس أونلاين:", "طور الفرق يكافئ بالألماس (💎). الفريق الخاسر لا يفقد عملاته أبداً. لا توجد رسوم اشتراك!")
    ],
    2: [
        ("⚡ مهارة البطل الخارقة [Ctrl]:", "اضغط مفتاح Ctrl مرة واحدة بالمباراة لتفعيل مهارة البطل (+20 ضرر فوري و +15 شفاء)!"),
        ("⌨️ اختصارات وسائل المساعدة (Ctrl + 1-4):", "استمر بالضغط على Ctrl لمنع التداخل أثناء الكتابة: [Ctrl+1] حذف إجابتين، [Ctrl+2] تجميد، [Ctrl+3] تبديل، [Ctrl+4] الجمهور."),
        ("🧪 جرعة طائر الفينيق [Ctrl + H]:", "تستعيد فوراً +25 نقطة صحة إلى شريط حياتك (استخدام واحد لكل مباراة)."),
        ("🏳️ الاستسلام والانسحاب [Ctrl + Q]:", "الانسحاب الآمن من المباراة مع نافذة تأكيد مسبقة لمنع أي نقرات غير مقصودة.")
    ],
    3: [
        ("⚔️ قتال اللاعبين المباشر (250 HP):", "كل إجابة صحيحة توجه ضربة قاضية للخصوم. وصول صحة الفريق لـ 0 يعني الهزيمة والإقصاء!"),
        ("🔥 تصاعد قوة الضربات (5 -> 10 DMG):", "يتصاعد الضرر مع كل إجابة متتالية: 5 ➔ 6 ➔ 7 ➔ 8 ➔ 9 ➔ 10 ضرر! ويعود للبداية عند الخطأ."),
        ("🛡️ دروع الحماية وامتصاص الأخطاء:", "الدروع المجهزة تخفض الضرر المتلقى وتمتص الخطأ الأول دون احتساب ضرر على اللاعب."),
        ("🎲 عقوبات الفائزين المسلية:", "يمكن للفريق الفائز اختيار عقوبات حية ومضحكة للفريق الخاسر مثل تمارين الضغط أو رقصة فوز.")
    ],
    4: [
        ("🏰 متجر الأبطال والمعدات:", "افتح 42 بطلاً، 49 سيفاً، 64 درعاً، و 16 أداة مساعدة باستخدام العملات أو الألماس!"),
        ("🔊 معاينة صوتية مجانية للأبطال:", "انقر على أي بطل مقفل في المتجر للاستماع إلى نبرته الصوتية دون خصم أي عملة!"),
        ("⚔️ ميزات المعدات التكتيكية:", "تمنح المعدات المجهزة مزايا دائمة ومتوازنة (+1 إلى +5 ضرر، صحة إضافية، امتصاص أخطاء)."),
        ("💎 توازن العملة المزدوجة:", "الألماس متوازن بنسبة 10:1 مقارنة بالعملات (مثلاً 150 عملة = 15 ألماسة) مع حماية ضد الرصيد السالب.")
    ]
}


class GuideModal:
    def __init__(self, app):
        self.app = app
        self.is_open = False
        self.current_tab = 0
        self.scroll_y = 0
        self.max_scroll = 0
        
        self.btn_close = Button((1045, 95, 45, 40), "✖", callback=self.close, color=(220, 60, 80), text_color=TEXT_WHITE, font_size=20)
        
        self.tab_buttons = []
        for i in range(5):
            b = Button((170 + i * 185, 155, 180, 38), "", callback=lambda idx=i: self.set_tab(idx), color=BG_CARD, font_size=13)
            self.tab_buttons.append(b)
        self.refresh_labels()

    @property
    def is_ar(self) -> bool:
        return str(getattr(self.app, "language", "2")) == "1"

    def refresh_labels(self):
        tabs = TABS_AR if self.is_ar else TABS_EN
        for i, b in enumerate(self.tab_buttons):
            if i < len(tabs):
                b.text = tabs[i]

    def open(self):
        self.is_open = True
        self.current_tab = 0
        self.scroll_y = 0
        self.refresh_labels()

    def close(self):
        self.is_open = False

    def set_tab(self, idx: int):
        self.current_tab = idx
        self.scroll_y = 0
        self.app.play_sound("hover")

    def update(self):
        if not self.is_open: return
        mp = pygame.mouse.get_pos()
        self.btn_close.update(mp)
        for i, b in enumerate(self.tab_buttons):
            b.is_selected = (self.current_tab == i)
            b.update(mp)

    def handle_event(self, event):
        if not self.is_open: return
        self.btn_close.handle_event(event)
        for b in self.tab_buttons:
            b.handle_event(event)

        # Mouse wheel scroll support
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 30))

    def draw(self, surface: pygame.Surface):
        if not self.is_open: return
        is_ar = self.is_ar

        # Dark overlay
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((10, 8, 20, 235))
        surface.blit(overlay, (0, 0))

        # Main Card Box
        draw_rounded_rect(surface, BG_CARD, (140, 80, 1000, 560), radius=22, border_color=PRIMARY_GLOW, border_width=3)
        
        title_txt = "📖 دليل اللعبة وقوانين المبارزة الرسمية" if is_ar else "📖 DUMP'S TEST — OFFICIAL GAME GUIDE & RULEBOOK"
        title_surf = render_text(title_txt, size=26, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        if is_ar:
            surface.blit(title_surf, (1030 - title_surf.get_width(), 105))
        else:
            surface.blit(title_surf, (170, 105))
        self.btn_close.draw(surface)

        for b in self.tab_buttons:
            b.draw(surface, is_arabic=is_ar)

        # Viewport Box
        view_rect = pygame.Rect(170, 205, 940, 410)
        draw_rounded_rect(surface, (20, 15, 38), view_rect, radius=14, border_color=CARD_BORDER, border_width=2)

        # Tab Content Data
        data_source = GUIDE_DATA_AR if is_ar else GUIDE_DATA_EN
        lines = data_source.get(self.current_tab, [])

        # Calculate max scroll
        total_content_height = len(lines) * 68 + 30
        self.max_scroll = max(0, total_content_height - 390)

        # Render visible items with scroll offset
        content_surf = pygame.Surface((900, 390), pygame.SRCALPHA)
        y = 15 - self.scroll_y
        for title, desc in lines:
            if -65 <= y <= 390:
                t_surf = render_text(title, size=16, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
                d_surf = render_text(desc, size=14, color=TEXT_WHITE, is_arabic=is_ar)
                if is_ar:
                    content_surf.blit(t_surf, (885 - t_surf.get_width(), y))
                    content_surf.blit(d_surf, (885 - d_surf.get_width(), y + 24))
                else:
                    content_surf.blit(t_surf, (15, y))
                    content_surf.blit(d_surf, (15, y + 23))
            y += 68

        surface.blit(content_surf, (185, 215))

        # Scrollbar Track & Thumb
        if self.max_scroll > 0:
            track_rect = pygame.Rect(1095, 215, 8, 390)
            draw_rounded_rect(surface, (35, 28, 55), track_rect, radius=4)
            thumb_h = max(30, int(390 * (390 / total_content_height)))
            thumb_y = 215 + int((390 - thumb_h) * (self.scroll_y / self.max_scroll))
            draw_rounded_rect(surface, ACCENT_GOLD, (1095, thumb_y, 8, thumb_h), radius=4)
