# -*- coding: utf-8 -*-
"""
game/dialogue.py — Class-Themed Fantasy Dialogue Engine for Dump's Test v4.0.
Amendment 4: Unique personality voice lines for ALL 22 avatars across every supported event:
  - correct
  - wrong
  - attack
  - damage
  - ability
  - victory
  - defeat
No two avatars share the same sentence.
"""
import random

AVATAR_LINES = {
    "catgirl_gamer": {
        "correct": "Nya! 300 IQ gamer move executed perfectly!",
        "wrong": "Mew?! Was that a lag spike or a misclick?!",
        "attack": "Claw swipe critical combo, nya!",
        "damage": "Ouchie! My gamer headset got knocked!",
        "ability": "Paws of fury activated! Rapid fire!",
        "victory": "Victory royale, nya! Ranked #1 forever!",
        "defeat": "Game over... sniff... time to ragequit."
    },
    "denim_boy": {
        "correct": "Street smarts never fail on the sidewalk!",
        "wrong": "Tripped up on that one! Gotta watch my step.",
        "attack": "Denim jacket right hook incoming!",
        "damage": "Ugh, caught a nasty scuff on my boots!",
        "ability": "Double denim power surge ignited!",
        "victory": "Street king takes the crown! Unbeatable!",
        "defeat": "Tossed in the gutter... but I'll be back."
    },
    "vr_girl": {
        "correct": "Holographic simulation confirmed! 100% render match!",
        "wrong": "Glitch in the neural net! Recalibrating sensors!",
        "attack": "Laser visor beam cutting through defenses!",
        "damage": "Shield integrity dropping to critical levels!",
        "ability": "Overclocking reality matrix to maximum specs!",
        "victory": "Virtual world conquered! Flawless speedrun!",
        "defeat": "Connection terminated... system rebooting."
    },
    "tactical_soldier": {
        "correct": "Target eliminated with extreme tactical precision!",
        "wrong": "Friendly fire! Check your coordinates, soldier!",
        "attack": "Flashbang and breach! Clear the perimeter!",
        "damage": "Taking heavy fire, Kevlar vest absorbing impact!",
        "ability": "Tactical airstrike inbound on target position!",
        "victory": "Mission accomplished, HQ! Area secure!",
        "defeat": "Soldier down! Requesting immediate medevac!"
    },
    "cyborg_robot": {
        "correct": "Logical deduction complete. Result: 100% optimal.",
        "wrong": "Error 404: Optimal solution not found in memory.",
        "attack": "Plasma cannon discharge initiated!",
        "damage": "Chassis integrity compromised by incoming kinetic shock.",
        "ability": "Core fusion reactor overload deployed!",
        "victory": "Organic rivals rendered completely obsolete.",
        "defeat": "Critical system failure... entering emergency shutdown."
    },
    "headphones_guy": {
        "correct": "Dropping the bass on that question! Pure harmony!",
        "wrong": "A totally dissonant chord! My ears are ringing!",
        "attack": "Sonic beatdrop blast shattering eardrums!",
        "damage": "My wireless headset just took serious distortion!",
        "ability": "Amplifier pumped up to 11! Maximum volume!",
        "victory": "The crowd goes wild for the festival headliner!",
        "defeat": "Static noise fades... the music has stopped."
    },
    "nature_elf": {
        "correct": "The ancient forest whispers the truth of all things.",
        "wrong": "A wilted leaf falls in the quiet wind...",
        "attack": "Thorn whip lash tearing through the brush!",
        "damage": "The sacred bark groans under the impact!",
        "ability": "Blessing of Gaia blooms across the battlefield!",
        "victory": "Nature flourishes in eternal verdant triumph!",
        "defeat": "Returning quietly to the great soil of the woods..."
    },
    "shadow_assassin": {
        "correct": "Struck cleanly from the dark without a breath.",
        "wrong": "A clumsy shadow step... my blade wavered.",
        "attack": "Hidden twin daggers strike the vital point!",
        "damage": "Only grazed the phantom silhouette.",
        "ability": "Shadow clone execution deployed silently!",
        "victory": "They never saw the final strike coming.",
        "defeat": "The abyss draws back its faithful servant..."
    },
    "sunhat_girl": {
        "correct": "Bright and sunny wisdom shining through!",
        "wrong": "Dark thunderclouds blocked my morning sunshine...",
        "attack": "Sunbeam parasol twirl smashes forward!",
        "damage": "My pretty sunhat ribbon got torn up!",
        "ability": "Radiant solar flare blinding everyone around!",
        "victory": "Golden sunshine warms the true champion today!",
        "defeat": "A sudden rainy gloom washes over my smile..."
    },
    "cyber_android": {
        "correct": "Bio-synthetic neural network computation verified.",
        "wrong": "Memory corruption in high-speed parsing subroutines.",
        "attack": "High-frequency cyber blade slice executed!",
        "damage": "Titanium-alloy framework absorbing structural stress.",
        "ability": "Quantum overclock routines ignited!",
        "victory": "Android supremacy confirmed across all metrics.",
        "defeat": "Main power reserves depleted to absolute zero."
    },
    "paladin": {
        "correct": "By the Holy Light! A flawless strike of intellect!",
        "wrong": "A stumble in our crusade! Re-focus your faith!",
        "attack": "Radiant blessed warhammer brings holy retribution!",
        "damage": "The Aegis of Faith absorbs the wicked blow!",
        "ability": "Divine Righteous Smite purges all darkness!",
        "victory": "Honor and justice reign supreme across the land!",
        "defeat": "I fall on my sacred shield... with unyielding honor."
    },
    "archer": {
        "correct": "Bullseye! Right through the absolute center!",
        "wrong": "Wind speed zero, yet the arrow flew completely wide!",
        "attack": "Piercing arrow loosed with pinpoint precision!",
        "damage": "Armor pierced, but the ranger stance holds firm!",
        "ability": "Rain of thousand golden arrows blocks out the sky!",
        "victory": "The master marksman claims the ultimate prize!",
        "defeat": "Quiver empty... bowstring snapped in the dirt."
    },
    "mage": {
        "correct": "Arcane calculations confirmed! Pure intellectual mastery!",
        "wrong": "My incantation fizzled into embarrassing purple smoke!",
        "attack": "Scorching meteor shower crashing from the heavens!",
        "damage": "Mana shield barrier shattered under tremendous force!",
        "ability": "Infinite cosmic cataclysm spell unleashed!",
        "victory": "The Archmage rewrites reality in triumphant glory!",
        "defeat": "Banished back to the cold astral void..."
    },
    "druid": {
        "correct": "The spirit of the great dire bear guides my choice!",
        "wrong": "The ancient seasonal balance wavered off-course...",
        "attack": "Dire bear claws rend the earth and foe alike!",
        "damage": "Thick grizzly pelt cushions the crushing blow!",
        "ability": "Primal roar summons the fury of the wilderness!",
        "victory": "The alpha predator reigns supreme over the forest!",
        "defeat": "Fading peacefully into the deep winter hibernation..."
    },
    "bard": {
        "correct": "A legendary ballad of triumph shall echo for centuries!",
        "wrong": "That sour note shattered every glass in the tavern!",
        "attack": "Devastating sonic crescendo blast from the silver lute!",
        "damage": "My ornate lute took a brutal bash to the fretboard!",
        "ability": "Grand symphony of heroes inspires infinite courage!",
        "victory": "Standing ovation from kings, queens, and commoners!",
        "defeat": "The stage curtain falls in cold, sorrowful silence."
    },
    "necromancer": {
        "correct": "Ancient crypt spirits rise to applaud your intellect!",
        "wrong": "Even my brainless skeletons answer with better logic!",
        "attack": "Grave chill spectral claws strike from below!",
        "damage": "Bone armor splinters under the mighty concussion!",
        "ability": "Unholy vortex awakens the immortal legions of doom!",
        "victory": "The dark dominion of the dead spreads worldwide!",
        "defeat": "Dragged back down into the depths of the tomb..."
    },
    "shaman": {
        "correct": "The elemental totems burn with proud ancestors' fire!",
        "wrong": "The elemental spirits fell silent at that guess...",
        "attack": "Lightning totem calls down a furious thunderclap!",
        "damage": "Earth totem quakes as it absorbs the shockwave!",
        "ability": "Tempest of sky and earth converges into a maelstrom!",
        "victory": "The ancestral spirits celebrate with eternal thunder!",
        "defeat": "The totems crack and collapse into quiet dust..."
    },
    "warrior": {
        "correct": "Bred for battle and forged in relentless iron discipline!",
        "wrong": "Hesitation and poor form will cost your life on the field!",
        "attack": "Heavy broadsword cleave split through shields!",
        "damage": "Steel plate rings loud, but the warrior does not flinch!",
        "ability": "Berserker warcry shatters enemy courage completely!",
        "victory": "Iron discipline and raw martial strength conquer all!",
        "defeat": "My sword breaks today, but my warrior soul endures."
    },
    "elementalist": {
        "correct": "Fire, water, earth, and air harmonize in brilliant truth!",
        "wrong": "The elements collided into chaotic, swirling turbulence!",
        "attack": "Quad-elemental vortex bursts through enemy ranks!",
        "damage": "Elemental barrier fractures under severe pressure!",
        "ability": "Primordial elemental convergence reshapes the terrain!",
        "victory": "Mastery over the four primal elements is absolute!",
        "defeat": "The elemental sparks scatter quietly into the ether..."
    },
    "thief": {
        "correct": "Pocketed that answer without anyone noticing the trick!",
        "wrong": "Got my fingers caught in the lock! Blunder of the year!",
        "attack": "Shadow backstab with twin venom-coated blades!",
        "damage": "Quick acrobatic tumble softens the brutal blow!",
        "ability": "Grand heist diversion leaves the enemy disoriented!",
        "victory": "Stole the grand championship right before their eyes!",
        "defeat": "Cornered in an alley... the heist went completely sideways."
    },
    "barbarian": {
        "correct": "RAAAARGH! BIG BRAIN BATTLE SMASH CONFIRMED!",
        "wrong": "MY BATTLEAXE HAS MORE INTELLECT THAN THAT ANSWER!",
        "attack": "Whirlwind dual-axe decimation crushes the skull!",
        "damage": "Blood boils hotter through the searing pain!",
        "ability": "Mountain-shattering leap slam pulverizes the arena!",
        "victory": "FEAST IN THE GREAT HALL! VALHALLA WELCOMES US!",
        "defeat": "Battleaxes shattered on stone... sleep now, warrior..."
    },
    "priest": {
        "correct": "Blessed with radiant clarity from the heavens above!",
        "wrong": "Forgive this brief moment of mortal weakness and error...",
        "attack": "Pillar of sanctified holy fire descends upon the foe!",
        "damage": "Sanctuary ward shudders under the wicked impact!",
        "ability": "Celestial grace restores hope and smites the wicked!",
        "victory": "Divine peace and radiant grace prevail over darkness!",
        "defeat": "The altar candles flicker and slowly extinguish..."
    }
}

AVATAR_ARCHETYPE_LINES = {
    "fighter": {
        "correct": "A strike of pure focus! The blade hits true!",
        "wrong": "A clumsy parry! I must regain my battle stance!",
        "attack": "Power slash! Feel the weight of my steel!",
        "damage": "Just a flesh wound! I've endured far worse!",
        "ability": "Battle roar! Unleash the inner warrior!",
        "victory": "Honor and steel have triumphed this day!",
        "defeat": "I fall... but my fighting spirit never dies!"
    },
    "knight": {
        "correct": "By the sacred code! Truth and justice prevail!",
        "wrong": "Shield faltered! Forgive my lapse in vigilance!",
        "attack": "Righteous thrust! Stand and face judgment!",
        "damage": "My armor holds! Faith is my strongest bastion!",
        "ability": "Radiant aegis! Bastion of valor, rise!",
        "victory": "The banner of glory flies proud over our victory!",
        "defeat": "My sword is lowered, but the oath remains sworn..."
    },
    "wise": {
        "correct": "As the ancient scrolls predicted! Flawless deduction!",
        "wrong": "Fascinating anomaly... my calculations were slightly astray.",
        "attack": "Arcane insight strikes with mystic precision!",
        "damage": "My magical barrier wavers from the shockwave!",
        "ability": "Grand wisdom unveiled! Transcend mortal bounds!",
        "victory": "Knowledge is the supreme power in this realm!",
        "defeat": "The cosmic alignment fades into silence..."
    },
    "hero": {
        "correct": "Victory favors the brave! A commanding answer!",
        "wrong": "A tactical setback! Resetting my focus!",
        "attack": "Direct hit! Forward to glorious triumph!",
        "damage": "Took a blow, but my resolve remains unbroken!",
        "ability": "Supreme focus! Channeling ultimate power!",
        "victory": "Champion of the realm! Victory is ours!",
        "defeat": "Defeated in combat... I will return stronger!"
    }
}

AVATAR_LINES_AR = {
    "catgirl_gamer": {
        "correct": "مياو! حركة لاعب عبقري بذكاء 300 نفذت بنجاح!",
        "wrong": "ميااو؟! هل كان هذا بطئاً في النت أم ضغطة خاطئة؟!",
        "attack": "ضربة مخلبية حرجة متتالية، مياو!",
        "damage": "آوتش! كادت سماعتي الاحترافية أن تسقط!",
        "ability": "تفعيل مخالب الغضب الخاطفة! هجوم سريع!",
        "victory": "انتصار ملكي، مياو! المركز الأول إلى الأبد!",
        "defeat": "انتهت اللعبة... حان وقت الانسحاب المؤقت."
    },
    "denim_boy": {
        "correct": "ذكاء الشارع لا يخطئ الهدف أبداً!",
        "wrong": "تعثرت هذه المرة! عليّ الحذر في خطواتي القادمة.",
        "attack": "لكمة يمنى قوية بأسلوب الشارع!",
        "damage": "أوه، خدش قوي أصاب درعي!",
        "ability": "طاقة الجينز المزدوجة تتوهج بالقوة!",
        "victory": "ملك الشوارع يتوج بالبطولة بلا منازع!",
        "defeat": "سقطت أرضاً... لكنني سأعود أقوى بالتأكيد."
    },
    "vr_girl": {
        "correct": "تطابق محاكاة الهولوغرام مؤكد بنسبة 100%!",
        "wrong": "خطأ في الشبكة العصبية! إعادة ضبط المجسات!",
        "attack": "شعاع الليزر يخترق دفاعات الخصم بالكامل!",
        "damage": "سلامة درع الطاقة تنخفض إلى مستوى حرج!",
        "ability": "كسر سرعة مصفوفة الواقع إلى أقصى طاقة!",
        "victory": "تمت السيطرة على العالم الافتراضي بنجاح مبهر!",
        "defeat": "تم قطع الاتصال... جاري إعادة تشغيل النظام."
    },
    "tactical_soldier": {
        "correct": "تم تحييد الهدف بدقة تكتيكية متناهية!",
        "wrong": "نيران صديقة! راجع إحداثياتك فوراً أيها الجندي!",
        "attack": "قنبلة ضوئية واقتحام! تطهير المحيط فوراً!",
        "damage": "نتعرض لنيران كثيفة، السترة تمتص الصدمة!",
        "ability": "طلب ضربة جوية تكتيكية على موقع الهدف!",
        "victory": "تمت المهمة بنجاح يا قيادة! المنطقة آمنة!",
        "defeat": "سقط المقاتل! نطلب إخلاءً طبياً عاجلاً!"
    },
    "cyborg_robot": {
        "correct": "اكتمل الاستنتاج المنطقي. النتيجة: مثالية 100%.",
        "wrong": "خطأ 404: لم يتم العثور على الحل الأمثل في الذاكرة.",
        "attack": "إطلاق مدفع البلازما بقوة قصوى!",
        "damage": "تأثر الهيكل الخارجي بصدمة حركية شديدة.",
        "ability": "تفعيل التحميل الزائد لمفاعل الاندماج الأساسي!",
        "victory": "تم إثبات تفوق الذكاء الآلي على المنافسين.",
        "defeat": "عطل حرج في النظام... الدخول في وضع الإغلاق الطارئ."
    },
    "headphones_guy": {
        "correct": "إيقاع مثالي ونغمة في منتهى التناغم!",
        "wrong": "نغمة نشاز تماماً! أذناي ترنان من الصدمة!",
        "attack": "انفجار إيقاعي صوتي يهز المكان بقوة!",
        "damage": "سماعتي اللاسلكية تلقت تشويشاً عنيفاً!",
        "ability": "رفع صوت مكبرات الصوت إلى أقصى درجة!",
        "victory": "الجمهور يشتعل حماساً لنجم المهرجان الأسطوري!",
        "defeat": "يتلاشى الصوت ويسود الصمت... توقفت الموسيقى."
    },
    "nature_elf": {
        "correct": "الغابة القديمة تهمس بحقيقة كل الأشياء.",
        "wrong": "ورقة ذابلة تسقط في صمت الرياح...",
        "attack": "ضربة سوط الأشواك تمزق دروع العدو!",
        "damage": "لحاء الشجر المقدس يئن تحت وطأة الصدمة!",
        "ability": "بركة الطبيعة الخضراء تزهر في ساحة المعركة!",
        "victory": "الطبيعة تزدهر في نصر أخضر أبدي!",
        "defeat": "أعود في سلام وهدوء إلى تربة الغابة العظيمة..."
    },
    "shadow_assassin": {
        "correct": "ضربة خاطفة من قلب الظلام دون أن ينبس أحد.",
        "wrong": "خطوة ظل غير محسوبة... اهتز نصل خنجري.",
        "attack": "خناجر الظل المزدوجة تصيب النقطة القاتلة!",
        "damage": "مجرد خدش عابر في ظل خيالي.",
        "ability": "تفعيل مهارة استنساخ الظلال للإطاحة بالخصم!",
        "victory": "لم يدركوا من أين جاءت الضربة القاضية.",
        "defeat": "الهاوية تستعيد خادمها المخلص في سكون..."
    },
    "sunhat_girl": {
        "correct": "حكمة مشرقة تتلألأ كأشعة شمس الصباح!",
        "wrong": "غيوم داكنة حجبت شمس الصباح المشرقة...",
        "attack": "دوران مظلة الشمس يطلق شعاعاً ضوئياً مبهراً!",
        "damage": "تمزق شريط قبعتي الشمسية الجميلة!",
        "ability": "وهج شمسي وهاج يعمي أبصار الجميع!",
        "victory": "شمس النصر الذهبية تدفئ البطل الحقيقي اليوم!",
        "defeat": "مطر مفاجئ يحجب ابتسامتي المشرقة..."
    },
    "cyber_android": {
        "correct": "تم التحقق من حسابات الشبكة العصبية الاصطناعية.",
        "wrong": "تلف مؤقت في خوارزميات المعالجة السريعة.",
        "attack": "تنفيذ قطع سيف السايبر عالي التردد!",
        "damage": "هيكل التيتانيوم يمتص الضغط الميكانيكي.",
        "ability": "إشعال روتينات كسر السرعة الكمومية!",
        "victory": "تأكيد السيادة السيبرانية في كافة المؤشرات.",
        "defeat": "نفاد احتياطيات الطاقة الرئيسية بالكامل."
    },
    "paladin": {
        "correct": "بنور الحق المقدس! ضربة فكرية لا تشوبها شائبة!",
        "wrong": "عثرة في مسيرتنا! أعيدوا شحذ العزيمة والإيمان!",
        "attack": "مطرقة الحرب المباركة تنزل القصاص العادل!",
        "damage": "درع الإيمان الصلب يصد الضربة الغادرة!",
        "ability": "الضربة المقدسة تطهر كل ظلام في الميدان!",
        "victory": "الشرف والعدالة يسودان أرجاء المملكة بأكملها!",
        "defeat": "أسقط على درعي المقدس... بشرف لا ينحني أبداً."
    },
    "archer": {
        "correct": "إصابة مباشرة في قلب الهدف تماماً!",
        "wrong": "سرعة الرياح صفر، ومع ذلك انحرف السهم بعيداً!",
        "attack": "سهم خارق ينطلق بدقة متناهية وبلا رحمة!",
        "damage": "اخترق السهم درعي، لكن وضعية الرامي ثابتة!",
        "ability": "مطر من آلاف السهام الذهبية يحجب قرص الشمس!",
        "victory": "رامي السهام الأسطوري يحصد الجائزة الكبرى!",
        "defeat": "جعبة السهام فارغة... وانقطع وتر القوس في التراب."
    },
    "mage": {
        "correct": "تأكدت الحسابات السحرية! براعة فكرية مطلقة!",
        "wrong": "تبددت تعويذتي وتحولت إلى دخان أرجواني محرج!",
        "attack": "عاصفة نيازك حارقة تهبط من أعنان السماء!",
        "damage": "حاجز المانا انكسر تحت وطأة القوة الهائلة!",
        "ability": "إطلاق تعويذة الدمار الكوني اللانهائية!",
        "victory": "رئيس السحرة يعيد كتابة الواقع بنصر مجيد!",
        "defeat": "نُفيت مجدداً إلى الفراغ النجمي البارد..."
    },
    "druid": {
        "correct": "روح الدب العظيم ترشد اختياري نحو الصواب!",
        "wrong": "اختل التوازن الفصلي القديم عن مساره المعهود...",
        "attack": "مخالب الدب الضارية تمزق الأرض والخصوم معاً!",
        "damage": "فرو الدب الكثيف يمتص وطأة الصدمة الساحقة!",
        "ability": "زئير بري يستدعي غضب وحوش الطبيعة العظيمة!",
        "victory": "المفترس الأكبر يتربع على عرش الغابة المهيبة!",
        "defeat": "أغفو في سلام بسبات شتوي عميق في أحضان الطبيعة..."
    },
    "bard": {
        "correct": "قصيدة نصر أسطورية ستتردد أصداؤها لقرون قادمة!",
        "wrong": "تلك النغمة النشاز حطمت كل زجاج في الحانة!",
        "attack": "تصعيد موسيقي مدمّر ينطلق من العود الفضي!",
        "damage": "تعرض عودي المزخرف لصدمة عنيفة كادت تكسره!",
        "ability": "سيمفونية الأبطال الكبرى تبث شجاعة لا تنتهي!",
        "victory": "تصفيق حار ووقوف إجلال من الملوك والنبلاء!",
        "defeat": "يسدل الستار على المسرح في صمت وحزن عميق."
    },
    "necromancer": {
        "correct": "أرواح المقابر القديمة تنهض لتصفق لعبقريتك!",
        "wrong": "حتى هياكلي العظمية تجيب بمنطق أفضل من هذا!",
        "attack": "مخالب طيفية باردة تنقض من قاع الأجداث!",
        "damage": "درع العظام يتشظى تحت الصدمة العنيفة!",
        "ability": "دوامة مظلمة توقظ فيالق الموتى الخالدين!",
        "victory": "مملكة الظلام تبسط سيطرتها المطلقة في كل مكان!",
        "defeat": "جُررت إلى أعماق القبر المظلم مجدداً..."
    },
    "shaman": {
        "correct": "مشاعل الطوطم تتقد بفخر أرواح الأجداد القدامى!",
        "wrong": "صمتت أرواح العناصر تماماً عند هذا التخمين...",
        "attack": "طوطم البرق يستدعي صاعقة رعدية هادرة!",
        "damage": "طوطم الأرض يرتجف وهو يمتص الموجة الارتدادية!",
        "ability": "عاصفة السماء والأرض تتحد في إعصار جارف!",
        "victory": "أرواح الأجداد تحتفل برعد أبدي لا ينقطع!",
        "defeat": "تصدعت الطواطم وانهارت في هدوء إلى رماد..."
    },
    "warrior": {
        "correct": "صُنعت للمعارك وصُقلت في انضباط حديدي لا يلين!",
        "wrong": "التردد وسوء التقدير سيكلفانك حياتك في الميدان!",
        "attack": "ضربة سيف عريض ثقيل تشطر الدروع نصفين!",
        "damage": "رنين الصفائح الفولاذية مدوٍ، لكن المحارب لا يتراجع!",
        "ability": "صرخة الحرب الهائجة تحطم شجاعة الأعداء تماماً!",
        "victory": "الانضباط الحديدي والقوة الصافية يقهران المستحيل!",
        "defeat": "انكسر سيفي اليوم، لكن روحي القتالية لن تنكسر."
    },
    "elementalist": {
        "correct": "النار والماء والأرض والهواء تتناغم في حقيقة ساطعة!",
        "wrong": "اصطدمت العناصر ببعضها في اضطراب عاصف وفوضوي!",
        "attack": "دوامة العناصر الأربعة تخترق صفوف الأعداء!",
        "damage": "حاجز العناصر يتشقق تحت الضغط العنيف!",
        "ability": "التقاء العناصر الأزلية يعيد تشكيل تضاريس الميدان!",
        "victory": "السيادة على العناصر الأربعة أصبحت مطلقة لا جدال فيها!",
        "defeat": "تطايرت شرارات العناصر بهدوء في الأثير الواسع..."
    },
    "thief": {
        "correct": "خطفت تلك الإجابة دون أن يلاحظ أحد الحيلة الذكية!",
        "wrong": "عَلِقت أصابعي في القفل! خطأ فادح لم يكن في الحسبان!",
        "attack": "طعنة ظل مباغتة بخناجر مسمومة من الخلف!",
        "damage": "قفزة بهلوانية سريعة خففت وطأة الضربة القاسية!",
        "ability": "خديعة سرقة كبرى تشتت انتباه العدو بالكامل!",
        "victory": "سرقت لقب البطولة الكبرى أمام أعينهم جميعاً!",
        "defeat": "حوصِرت في زقاق ضيق... فشلت الخطة تماماً هذه المرة."
    },
    "barbarian": {
        "correct": "راااااه! ضربة ساحقة بذكاء قتالي خارق!",
        "wrong": "فأس المعركة يمتلك عقلاً أفضل من تلك الإجابة!",
        "attack": "إعصار الفؤوس المزدوجة يسحق دفاعات العدو!",
        "damage": "يغلي الدم في عروقي غضباً مع كل ألم!",
        "ability": "قفزة جبلية ساحقة تدك أرض الحلبة بالكامل!",
        "victory": "وليمة النصر في القاعة الكبرى! المجد لنا جميعاً!",
        "defeat": "تحطمت الفؤوس على الحجارة... ارقد بسلام الآن أيها المقاتل..."
    },
    "priest": {
        "correct": "مُبارك بنور الوضوح والهداية الساطعة من السماء!",
        "wrong": "اغفر هذه اللحظة العابرة من الضعف البشري والخطأ...",
        "attack": "عمود من النار المقدسة المطهرة يهبط على الأعداء!",
        "damage": "درع الملاذ المبارك يرتعش تحت وقع الضربة الآثمة!",
        "ability": "النعمة الإلهية تعيد الأمل وتبطش بكل ظالم!",
        "victory": "السلام والنور المبارك ينتصران على كل قوى الظلام!",
        "defeat": "تتمايل شموع المذبح المقدس وتنطفئ ببطء..."
    }
}

AVATAR_ARCHETYPE_LINES_AR = {
    "fighter": {
        "correct": "ضربة في منتهى التركيز! السيف يصيب كبد الحقيقة!",
        "wrong": "رد غير موفق! يجب أن أستعيد وضعيتي القتالية فوراً!",
        "attack": "ضربة قاطعة قوية! تذوق وزن الفولاذ الصارم!",
        "damage": "مجرد خدش سطحي! لقد تحملت ما هو أقسى بكثير!",
        "ability": "زئير المعركة! إطلاق العنان للمحارب الكامن!",
        "victory": "الشرف والفولاذ يسطران النصر في هذا اليوم المجيد!",
        "defeat": "أسقط في المعركة... لكن روحي المقاتلة لن تموت!"
    },
    "knight": {
        "correct": "بشرف العهد المقدس! الحق والعدالة ينتصران دائماً!",
        "wrong": "اهتز درعي! اعذروا هذا التقصير المؤقت في اليقظة!",
        "attack": "طعنة الحق العادلة! قف وواجه حكم العدالة!",
        "damage": "درعي الفولاذي صامد! العزيمة والإيمان أقوى حصوني!",
        "ability": "حاجز البسالة الساطع! ارتفع يا حصن الشجاعة!",
        "victory": "راية المجد ترفرف خفاقة فوق نصرنا العظيم!",
        "defeat": "أخفض سيفي اليوم، لكن قسم الفرسان يظل سارياً..."
    },
    "wise": {
        "correct": "كما تنبأت المخطوطات القديمة! استنتاج لا تشوبه شائبة!",
        "wrong": "ظاهرة غريبة تستحق التأمل... انحرفت حساباتي قليلاً.",
        "attack": "البصيرة السحرية تضرب بدقة غامضة وخاطفة!",
        "damage": "حاجزي السحري يهتز بفعل الموجة الارتدادية العنيفة!",
        "ability": "كشف الحكمة الكبرى! التسامي فوق قيود الفناء!",
        "victory": "المعرفة هي القوة الأسمى المطلقة في هذا الكون!",
        "defeat": "التناغم الكوني يتلاشى بهدوء في صمت الفضاء..."
    },
    "hero": {
        "correct": "النصر حليف الشجعان دائماً! إجابة حاسمة وموفقة!",
        "wrong": "عثرة تكتيكية عابرة! أعيد تركيزي بكل حزم!",
        "attack": "إصابة مباشرة ومحكمة! إلى الأمام نحو النصر المجيد!",
        "damage": "تلقيت ضربة، لكن عزيمتي تظل صلبة كالصخر!",
        "ability": "تركيز مطلق! شحن القوة القصوى للأبطال!",
        "victory": "بطل المملكة المتوج! النصر أصبح ملكنا بجدارة!",
        "defeat": "هُزمت في النزال اليوم... لكنني سأعود أقوى بالتأكيد!"
    }
}


def get_avatar_sentence(avatar_id: str, event: str, lang: str = "2") -> str:
    """
    Amendment 4 & Batch 4: Unique personality sentence retrieval with full Arabic & English support.
    Guarantees every avatar has its own distinct line for every event:
    correct, wrong, attack, damage, ability, victory, defeat.
    RPG store avatars map to their respective warrior, knight, or sage archetype.
    """
    is_ar = str(lang) == "1"
    lines_db = AVATAR_LINES_AR if is_ar else AVATAR_LINES
    archetype_db = AVATAR_ARCHETYPE_LINES_AR if is_ar else AVATAR_ARCHETYPE_LINES

    av_key = str(avatar_id).lower()
    av_data = lines_db.get(av_key)
    if not av_data:
        # Match RPG Archetypes for store avatars
        if "wise" in av_key or "mage" in av_key:
            av_data = archetype_db["wise"]
        elif "knight" in av_key or "kngiht" in av_key:
            av_data = archetype_db["knight"]
        elif "fighter" in av_key or "warrior" in av_key:
            av_data = archetype_db["fighter"]
        elif any(k in av_key for k in ("bronze", "seliver", "silver", "golden", "thunder", "royal", "elite", "deputy", "honorary")):
            av_data = archetype_db["knight"]
        else:
            av_data = archetype_db["hero"]

    ev_key = str(event).lower()
    if ev_key in ("joy", "right"): ev_key = "correct"
    elif ev_key in ("anger", "incorrect"): ev_key = "wrong"
    elif ev_key in ("hit", "slash"): ev_key = "attack"
    elif ev_key in ("hurt", "hit_received"): ev_key = "damage"

    default_word = "انتصار!" if is_ar else "Victory!"
    return av_data.get(ev_key, av_data.get("correct", default_word))


def get_class_dialogue(avatar_class: str, is_correct: bool, consecutive_count: int = 1, lang: str = "2") -> str:
    """Backward-compatible class dialogue wrapper with language support."""
    ev = "correct" if is_correct else "wrong"
    return get_avatar_sentence(avatar_class, ev, lang=lang)
