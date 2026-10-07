# -*- coding: utf-8 -*-
"""
game/cases_11_to_15.py — Crime Cases 11 through 15 for Investigation Mode.
Case 11: Murder on the Orient Line (Murder)
Case 12: The Stolen Renaissance Masterpiece (Theft)
Case 13: Kidnapping at the Tech Summit (Kidnapping)
Case 14: The Armored Car Robbery (Robbery)
Case 15: Poison in the Vineyard (Poisoning)
"""

CASES_11_TO_15 = [
    # ── CASE 11: MURDER ON THE ORIENT LINE ──
    {
        "id": "case_11",
        "title": "Murder on the Orient Line",
        "category": "Murder",
        "difficulty": "Hard",
        "target_or_victim": "Countess Isabella Montez",
        "crime_scene": "First Class Compartment 7, Orient Express",
        "briefing": "As the Orient Express navigated an alpine mountain pass during a blizzard, Countess Isabella Montez was discovered strangled in her private sleeper compartment. The train was trapped by a snowdrift with all passengers aboard.",
        "suspects": [
            {
                "name": "Baron Wolfgang Klein",
                "role": "Antiquities Collector",
                "public_story": "Reading in the observation lounge until midnight.",
                "private_secret": "The Countess was blackmailing him with proof of forged Roman artifacts he sold.",
                "motive": "Silence the Countess and retrieve the incriminating appraisal dossier.",
                "alibi": "Lounge steward served him tea at 11:15 PM.",
                "weakness": "Golden silk cord torn from his smoking jacket found clutched in victim dead hand.",
                "relationship": "Social peer and bitter rival.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Greta Miller",
                "role": "Personal Maid",
                "public_story": "Asleep in the adjacent second-class staff berth.",
                "private_secret": "Stole diamond earrings from the Countess jewelry box yesterday.",
                "motive": "Fear of being arrested and ruined.",
                "alibi": "Berth door remained locked until 6:00 AM.",
                "weakness": "Countess pearl earrings found hidden inside her sewing basket.",
                "relationship": "Personal servant for 2 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Conductor Pierre Dubois",
                "role": "Train Conductor",
                "public_story": "Checking carriage tickets and clearing snow from outer vestibule.",
                "private_secret": "Smuggling black-market caviar across the border in the coal car.",
                "motive": "Countess threatened to report his smuggling to railroad authorities.",
                "alibi": "Engineer confirms Dubois checked in at the locomotive at 11:30 PM.",
                "weakness": "Possesses the master carriage passkey.",
                "relationship": "Train crew.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Colonel Arthur Hastings",
                "role": "Retired Military Officer",
                "public_story": "Playing bridge in the dining car with fellow travelers.",
                "private_secret": "Carrying an unauthorized service revolver in his trunk.",
                "motive": "Ancient inheritance grudge from the Spanish civil campaign.",
                "alibi": "Dining car passengers confirm he played cards until 1:00 AM.",
                "weakness": "Had an argument with the Countess during lunch.",
                "relationship": "Acquaintance.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c11_cord", "title": "Golden Silk Robe Cord", "category": "Physical", "role": "Critical", "description": "Strangulation ligature; threads match the bespoke Austrian smoking jacket worn by Baron Klein."},
            {"id": "c11_dossier", "title": "Charred Antiquities Ledger", "category": "Physical", "role": "Critical", "description": "Found half-burned in the observation lounge heating stove; details forged Roman antiquities sold by Klein."},
            {"id": "c11_earrings", "title": "Stolen Diamond Earrings", "category": "Physical", "role": "Red Herring", "description": "Found in maid Greta sewing kit; petty theft, but completely unrelated to the murder."},
            {"id": "c11_snow", "title": "Vestibule Snow Discrepancy", "category": "Circumstantial", "role": "Supporting", "description": "No exterior snow entered Compartment 7; the killer walked inside the heated train corridor."},
            {"id": "c11_scratch", "title": "Scratches on Klein Wrist", "category": "Behavioral", "role": "Supporting", "description": "Baron Klein has fresh fingernail scratches on his right wrist hidden beneath his cuff."}
        ],
        "timeline": [
            {"time": "20:00", "event": "Dinner served in dining car; Countess and Klein exchange sharp words."},
            {"time": "22:30", "event": "Countess retires to Compartment 7."},
            {"time": "23:15", "event": "Lounge steward serves Baron Klein tea in observation car."},
            {"time": "23:40", "event": "Klein slips into Compartment 7 using an unlocked connecting latch."},
            {"time": "23:55", "event": "Countess strangled; Klein burns the blackmail dossier in the stove."},
            {"time": "06:30", "event": "Maid Greta enters Compartment 7 and discovers the body."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "The luxury express sits motionless in the blizzard. Countess Montez lies strangled in berth 7. In her right hand, she tightly clutches a frayed strand of gold silk cord. Where do you start?",
                "options": [
                    {"text": "Examine the gold silk cord threads under magnifying glass.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c11_cord", "feedback": "Gold silk cord is spun from Austrian imperial thread, identical to Baron Klein smoking jacket!"},
                    {"text": "Search maid Greta Miller quarters and luggage.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c11_earrings", "feedback": "Found stolen diamond earrings in her sewing basket. Greta weeps, confessing to theft but denying murder."},
                    {"text": "Inspect the observation car coal and heating stove.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c11_dossier", "feedback": "Among the embers: charred paper fragments listing Baron Klein and forged antiquities sales!"},
                    {"text": "Check Conductor Dubois master key ring.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dubois insists all passkeys were accounted for in the crew locker."}
                ]
            },
            {
                "step": 2,
                "prompt": "Baron Klein smoking jacket is missing its belt cord. Klein claims he lost it during lunch in Vienna.",
                "options": [
                    {"text": "Inspect Baron Klein wrists and hands under bright light.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c11_scratch", "feedback": "Deep, fresh fingernail gouges on his right wrist! Countess Montez had defensive skin under her nails!"},
                    {"text": "Interrogate Colonel Hastings about his lunch argument with the victim.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Hastings explains they debated Spanish wine tariffs; passengers confirm his uninterrupted bridge game."},
                    {"text": "Examine the train exterior windows and snowdrifts.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": "c11_snow", "feedback": "Compartment window was latched shut from inside. The killer entered from the interior corridor."},
                    {"text": "Search Conductor Dubois coal tender.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Found contraband tins of Beluga caviar; Dubois was smuggling food, not committing murder."}
                ]
            },
            {
                "step": 3,
                "prompt": "Doctor aboard confirms Countess Montez died between 23:30 and 00:15. Who was unaccounted for?",
                "options": [
                    {"text": "Interrogate the observation lounge steward regarding Klein movements.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Steward recalls serving tea at 11:15, but Baron was absent from the lounge between 11:30 and 00:10!"},
                    {"text": "Check maid Greta alibi with the night conductor.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Second-class berth attendant verifies Greta door remained shut all night."},
                    {"text": "Re-examine the charred dossier fragments.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Deciphered fragment: 'Klein Roman bronzes are 19th-century replicas. Full report to Police Prefect.'"},
                    {"text": "Search Colonel Hastings military trunk.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Pistol is locked in holster, unfired and clean."}
                ]
            },
            {
                "step": 4,
                "prompt": "Defensive skin scrapings taken from the Countess fingernails are analyzed by the ship surgeon.",
                "options": [
                    {"text": "Compare fingernail epithelial tissue to Baron Klein blood type.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Blood type and cellular scrapings match Baron Wolfgang Klein exactly!"},
                    {"text": "Confront Klein with the charred dossier from the stove.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Klein twitches violently, muttering: 'She had no right to ruin my reputation.'"},
                    {"text": "Search maid Greta coat for blood or fibers.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "No physical traces of fibers, blood, or silk on Greta belongings."},
                    {"text": "Check Conductor Dubois locomotive log.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Locomotive engineer confirms Dubois was assisting with snow shoveling at 23:45."}
                ]
            },
            {
                "step": 5,
                "prompt": "The connecting interior door latch between Compartment 7 and the corridor was unlocked.",
                "options": [
                    {"text": "Dust the brass latch of Compartment 7 for latent prints.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Right thumbprint on the interior latch matches Baron Wolfgang Klein!"},
                    {"text": "Question Colonel Hastings on Klein demeanor.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Hastings noticed Klein was breathing heavily and sweating when he re-entered the lounge at 00:15."},
                    {"text": "Verify Conductor Dubois master key usage.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "The master key was never removed from the lockbox; the door had simply been unlatched by the Countess."},
                    {"text": "Inspect luggage rack in Compartment 7.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Countess briefcase lock was forced open with a pocket knife; papers missing."}
                ]
            },
            {
                "step": 6,
                "prompt": "Klein pocket knife is seized. The blade tip carries brass shavings from the Countess briefcase lock.",
                "options": [
                    {"text": "Microscopic examination of Klein pocket knife blade.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Blade tip shows microscopic scratches matching the tumblers of the forced briefcase lock!"},
                    {"text": "Check maid Greta hands for scratches.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Her hands are completely free of cuts or bruising."},
                    {"text": "Interview the dining car passengers.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "All confirm Colonel Hastings never left the table during the crucial hour."},
                    {"text": "Examine the observation stove ash composition.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Paper ashes match high-rag bond paper from the Countess personal stationery."}
                ]
            },
            {
                "step": 7,
                "prompt": "Baron Klein attempts to bribe Conductor Dubois with 50,000 Swiss francs to open an exterior door into the snow.",
                "options": [
                    {"text": "Dubois brings the bribe money directly to the detectives.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Dubois turns over the cash stack, stating Klein begged him to help him escape into the blizzard."},
                    {"text": "Detain Baron Klein under armed guard in the baggage car.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Klein is handcuffed to a stanchion. He refuses to answer further questions."},
                    {"text": "Formally clear Conductor Dubois of homicide.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dubois is commended for reporting the escape attempt."},
                    {"text": "Examine the blizzard conditions outside.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Snowdrifts reach 8 feet; no human could survive on foot."}
                ]
            },
            {
                "step": 8,
                "prompt": "The snowplow engine arrives, clearing the tracks towards Zurich. The case dossier is finalized.",
                "options": [
                    {"text": "Assemble the international murder and evidence dossier for Swiss Federal Police.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Ironclad dossier: silk cord match, wrist scratches, DNA, latch prints, knife brass shavings, bribe cash."},
                    {"text": "Transfer maid Greta to local authorities for petty larceny.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Greta will face misdemeanor jewelry theft charges; cleared of murder."},
                    {"text": "Formally exonerate Colonel Hastings.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Hastings is formally cleared and his service record preserved."},
                    {"text": "Catalogue the Countess personal effects.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Recovered jewelry and belongings sealed for the Montez estate executors."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: As the train pulls into Zurich station, Swiss detectives board. One final formal accusation.",
                "options": [
                    {"text": "Present the gold robe cord, DNA match, and burned dossier evidence to Baron Klein.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Klein sneers bitterly: 'She thought she could destroy the House of Klein with a scrap of paper. I took back my honor!'"},
                    {"text": "Ask if the maid helped him.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Klein scoffs: 'I don't consort with servants.'"},
                    {"text": "Review the timeline for the Swiss prosecutor.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline matches every movement between 23:15 and 00:15."},
                    {"text": "Seal the formal investigation report.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Investigation docket signed and sealed."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who murdered Countess Isabella Montez aboard the Orient Express?",
                "options": []
            }
        ],
        "true_culprit": "Baron Wolfgang Klein",
        "true_solution": "Baron Wolfgang Klein was being blackmailed by the Countess over forged antiquities. During the blizzard, he slipped out of the observation lounge, entered Compartment 7, used the cord from his smoking jacket to strangle her, pried open her briefcase to steal the dossier, and burned the papers in the lounge stove before attempting to bribe his way out.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 12: THE STOLEN RENAISSANCE MASTERPIECE ──
    {
        "id": "case_12",
        "title": "The Stolen Renaissance Masterpiece",
        "category": "Theft",
        "difficulty": "Hard",
        "target_or_victim": "'The Weeping Seraph' by Caravaggio ($60 Million)",
        "crime_scene": "The Grand Salon, Galerie Lumière, Paris",
        "briefing": "During a midnight thunderstorm, the priceless 16th-century painting 'The Weeping Seraph' was sliced from its gilded frame. Infrared laser tripwires were cleanly bypassed without triggering the alarm console.",
        "suspects": [
            {
                "name": "Maurice Belrose",
                "role": "Chief Conservator & Restorer",
                "public_story": "Working in the basement restoration studio.",
                "private_secret": "Commissioned by an international art syndicate to replace the masterpiece with an oil replica.",
                "motive": "$8 million wire payment in a Swiss account.",
                "alibi": "Restoration studio timer recorded him solvent-cleaning a Flemish landscape.",
                "weakness": "Scalpel blade found in the frame groove has pigment residue matching his custom restoration palette.",
                "relationship": "Lead restorer for 18 years.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Claire Dupont",
                "role": "Museum Curator",
                "public_story": "In her 2nd-floor office preparing the exhibition catalogue.",
                "private_secret": "Discovered the museum is $12M in debt and faced closure.",
                "motive": "Collect the $70M insurance payout to save the museum.",
                "alibi": "Catalog files saved on her computer at 11:30 PM.",
                "weakness": "Held the master disarm code for the laser grid.",
                "relationship": "Curator for 10 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Jean-Luc Moreau",
                "role": "Night Security Guard",
                "public_story": "Conducting perimeter patrol on the lower sculpture court.",
                "private_secret": "Sleeping in the breakroom for 45 minutes.",
                "motive": "None; fear of termination.",
                "alibi": "Turnstile logs showed him entering sculpture court.",
                "weakness": "Admitted he skipped the Grand Salon round at midnight.",
                "relationship": "Night guard.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Antoine Vane",
                "role": "Private Art Collector & Patron",
                "public_story": "Attending the donor reception upstairs until 10:30 PM.",
                "private_secret": "Tried to buy 'The Weeping Seraph' privately three times and was rejected.",
                "motive": "Obsessive desire to possess the masterpiece.",
                "alibi": "Hotel camera across the street photographed him entering at 11:15 PM.",
                "weakness": "Left an empty climate-controlled canvas transport tube in his limousine.",
                "relationship": "Major museum benefactor.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c12_scalpel", "title": "Surgical Scalpel Blade No. 11", "category": "Physical", "role": "Critical", "description": "Left snapped in the wooden frame corner; carries trace rabbit-skin glue and pigment unique to Belrose studio."},
            {"id": "c12_laser", "title": "Mirror Reflector Prism Bypass", "category": "Physical", "role": "Critical", "description": "Small quartz optical prisms clamped to the gallery floor redirected the infrared beams around the canvas."},
            {"id": "c12_tube", "title": "Leather Canvas Tube", "category": "Physical", "role": "Red Herring", "description": "Found in Antoine Vane limousine; held an antique tapestry he purchased earlier that afternoon."},
            {"id": "c12_replica", "title": "Unfinished Canvas on Easel", "category": "Physical", "role": "Supporting", "description": "Found hidden behind a velvet curtain in Belrose studio; exact identical copy of 'The Weeping Seraph'."},
            {"id": "c12_code", "title": "Laser Grid Console Override", "category": "Digital", "role": "Supporting", "description": "Laser alarm was not electronically turned off; it was optically bounced using prisms."}
        ],
        "timeline": [
            {"time": "22:30", "event": "Donor reception concludes; visitors depart."},
            {"time": "23:15", "event": "Antoine Vane arrives at hotel across the street."},
            {"time": "23:45", "event": "Guard Moreau dozes off in staff breakroom."},
            {"time": "00:15", "event": "Optical prisms set up around Caravaggio laser perimeter."},
            {"time": "00:25", "event": "Canvas sliced from frame with surgical scalpel; rolled in oilcloth."},
            {"time": "06:00", "event": "Morning guard discovers empty gilded frame on Grand Salon wall."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Inside the Grand Salon, Caravaggio gilded baroque frame hangs empty on the silk wallpaper. The canvas was excised with surgical precision. Where do you begin?",
                "options": [
                    {"text": "Examine the wooden frame corners with a forensic magnifying loupe.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c12_scalpel", "feedback": "Snapped surgical scalpel tip recovered from the frame rabbet! Contains rare rabbit-skin gesso."},
                    {"text": "Inspect the infrared laser tripwire sensors on the floor.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c12_laser", "feedback": "Four optical quartz prisms found clamped to the molding, redirecting the lasers into an empty loop!"},
                    {"text": "Search Antoine Vane limousine parked outside.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c12_tube", "feedback": "Leather tube in Vane car contains a 17th-century tapestry with purchase invoices; not the Caravaggio."},
                    {"text": "Interrogate Guard Jean-Luc Moreau about his patrol.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Moreau breaks down and admits he took a nap in the breakroom from 23:45 to 00:30."}
                ]
            },
            {
                "step": 2,
                "prompt": "The optical prisms required professional optical knowledge and gallery measurements to align. Who had access?",
                "options": [
                    {"text": "Search Chief Conservator Maurice Belrose restoration studio.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c12_replica", "feedback": "Hidden behind a drying rack: a nearly completed duplicate of 'The Weeping Seraph' on identical aged linen!"},
                    {"text": "Interrogate Curator Claire Dupont regarding the laser disarm codes.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": "c12_code", "feedback": "Console logs confirm the electronic disarm code was never entered; the bypass was purely optical."},
                    {"text": "Check Antoine Vane hotel surveillance footage.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Hotel lobby cameras confirm Vane was having a nightcap at the hotel bar until 1:00 AM."},
                    {"text": "Inspect guard breakroom lockers.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Moreau locker contains only a sandwich and a coffee thermos."}
                ]
            },
            {
                "step": 3,
                "prompt": "Pigment spectrometry on the snapped scalpel blade matches the exact hand-ground cinnabar red used by Belrose.",
                "options": [
                    {"text": "Analyze chemical profile of pigment residue on the scalpel blade.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "100% chemical match to Belrose personal batch of hand-ground Italian cinnabar pigment!"},
                    {"text": "Confront Belrose about the duplicate canvas on his easel.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Belrose claims it was 'an innocent technical study' for conservation training, sweating profusely."},
                    {"text": "Check Claire Dupont bank accounts for insurance fraud ties.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Claire accounts show no illicit transactions or contact with art thieves."},
                    {"text": "Inspect the museum roof skylights.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "All skylight latch seals are intact and covered in undisturbed dust."}
                ]
            },
            {
                "step": 4,
                "prompt": "Detectives trace the purchase of the specialized quartz optical prisms.",
                "options": [
                    {"text": "Subpoena optical instrument supplier records in Paris.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Prisms purchased 3 weeks ago by Maurice Belrose under the museum restoration account!"},
                    {"text": "Question Antoine Vane on his private art offers.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vane admits he wanted the painting legally, but would never buy stolen art."},
                    {"text": "Check Belrose restoration timer logs.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The solvent-cleaning machine was left running automatically to simulate his working presence."},
                    {"text": "Audit museum alarm service logs.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "The alarm technicians serviced the sensors last month with zero anomalies."}
                ]
            },
            {
                "step": 5,
                "prompt": "A search of Belrose home residence in Montmartre is authorized.",
                "options": [
                    {"text": "Search Belrose attic and private basement workshop.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Inside a moisture-sealed aluminum shipping crate: the authentic rolled Caravaggio canvas!"},
                    {"text": "Check Belrose computer for foreign buyer correspondence.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found encrypted emails with an offshore buyer arranging delivery in Geneva for $8M."},
                    {"text": "Interrogate Guard Moreau again.", "killer_delta": 0, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Moreau confirms Belrose had free 24-hour keycard access to all exhibition rooms."},
                    {"text": "Review Curator Dupont catalog notes.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Her files confirm she was writing catalog text continuously until midnight."}
                ]
            },
            {
                "step": 6,
                "prompt": "The recovered canvas is brought to the museum for authentication by independent experts.",
                "options": [
                    {"text": "Verify authenticity of recovered canvas under X-ray and UV light.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Confirmed: 100% genuine original 16th-century Caravaggio 'The Weeping Seraph'!"},
                    {"text": "Match the cut canvas edge to the canvas remnants in the gilded frame.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The weave and thread counts match the severed border down to the millimeter."},
                    {"text": "Check if Claire Dupont helped roll the canvas.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Zero fingerprints from Dupont found on the crate or canvas edges."},
                    {"text": "Analyze the Swiss escrow account details.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Account set up under Belrose false Panamanian corporation."}
                ]
            },
            {
                "step": 7,
                "prompt": "Belrose defense lawyer claims an unknown syndicate framed his client by planting the crate in his attic.",
                "options": [
                    {"text": "Present DNA and fingerprint match on the scalpel handle and crate latches.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Belrose fingerprints cover the scalpel handle, the optical prisms, and the crate foam padding."},
                    {"text": "Interrogate Belrose apprentice in the restoration studio.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Apprentice testifies Belrose had been secretly copying the Caravaggio for four months."},
                    {"text": "Formally clear Antoine Vane.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vane is completely exonerated of all complicity."},
                    {"text": "Confirm Guard Moreau disciplinary status.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Moreau receives an administrative reprimand for sleeping on duty."}
                ]
            },
            {
                "step": 8,
                "prompt": "Every link in the grand art heist is forged: optical prisms, scalpel tip, replica canvas, attic recovery, and DNA proof.",
                "options": [
                    {"text": "Assemble the grand art theft and heritage destruction indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Prosecution docket finalized: physical scalpel match, recovered canvas, invoice for prisms, buyer emails."},
                    {"text": "Formally return 'The Weeping Seraph' to the museum board.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Board members weep with gratitude as the masterpiece is safely returned."},
                    {"text": "Clear Curator Claire Dupont of insurance conspiracy.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dupont is cleared of all criminal suspicion."},
                    {"text": "Seal the recovered canvas in high-security preservation vault.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Artwork secured under 24-hour federal police protection."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Belrose sits in the Palace of Justice. The evidence against him is total.",
                "options": [
                    {"text": "Present the matched canvas threads, cinnabar scalpel, and attic crate recovery.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Belrose buries his face in his hands: 'I restored paintings for 30 years while billionaires bought them for pocket change. I wanted my own fortune!'"},
                    {"text": "Ask if Curator Dupont knew about the replica.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Belrose sighs: 'Claire knew nothing. I took advantage of her trust.'"},
                    {"text": "Review timeline for French judicial magistrate.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline proves the exact sequence of the optical bypass and excision."},
                    {"text": "Seal the formal investigation docket.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Case file signed, stamped, and ready for verdict."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who stole 'The Weeping Seraph' from Galerie Lumière?",
                "options": []
            }
        ],
        "true_culprit": "Maurice Belrose",
        "true_solution": "Chief Conservator Maurice Belrose spent four months painting a replica of the masterpiece. On the night of the theft, he used optical quartz prisms to bypass the infrared tripwires, sliced the original canvas with a surgical scalpel (snapping the blade tip in the frame), rolled it in oilcloth, hid it in his Montmartre attic, and prepared to ship it to an overseas buyer for $8M.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 13: KIDNAPPING AT THE TECH SUMMIT ──
    {
        "id": "case_13",
        "title": "Kidnapping at the Tech Summit",
        "category": "Kidnapping",
        "difficulty": "Hard",
        "target_or_victim": "Kenji Sato, AI Robotics Pioneer",
        "crime_scene": "Green Room VIP Suite, Moscone Center, San Francisco",
        "briefing": "Moments before delivering his keynote on autonomous robotics at the Global AI Summit, pioneer Kenji Sato vanished from his guarded green room. A digital ransom demanded 200 Bitcoin ($14M) or his neural code would be wiped.",
        "suspects": [
            {
                "name": "Aaron Cross",
                "role": "Former Co-Founder",
                "public_story": "Attending breakout sessions in Hall B.",
                "private_secret": "Ousted by Sato 3 years ago without equity; company is now worth $3 billion.",
                "motive": "Extract $14M in Bitcoin and force Sato to sign over core patent royalties.",
                "alibi": "Scan badge logged him into Hall B at 10:00 AM.",
                "weakness": "His badge was carried by an accomplice, while Cross entered the service tunnels wearing catering uniform.",
                "relationship": "Bitter former co-founder.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Maya Lin",
                "role": "Chief Operating Officer",
                "public_story": "Greeting corporate sponsors in the VIP lounge.",
                "private_secret": "Secretly negotiating an acquisition by a rival search giant.",
                "motive": "Delay the keynote to finalize the acquisition terms.",
                "alibi": "Dozens of tech executives spoke with her between 10:00 and 10:45 AM.",
                "weakness": "Had the VIP room security override code on her smartphone.",
                "relationship": "COO for 4 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Viktor Vance",
                "role": "Private Bodyguard",
                "public_story": "Guarding the exterior green room corridor.",
                "private_secret": "Addicted to online poker; lost $60,000 this month.",
                "motive": "Bribe money to look away.",
                "alibi": "Corridor video shows him standing outside the door.",
                "weakness": "Stepped away for 8 minutes at 10:20 AM claiming a bathroom emergency.",
                "relationship": "Personal bodyguard.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Dr. Sarah Chen",
                "role": "Lead Research Scientist",
                "public_story": "Testing robotics demonstration on main stage.",
                "private_secret": "Upset that Sato took sole credit for the neural algorithms.",
                "motive": "Humiliate Sato publicly on live stream.",
                "alibi": "Stage technicians confirm she was debugging code continuously.",
                "weakness": "Argued loudly with Sato in the hallway this morning.",
                "relationship": "Key scientist.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c13_chloroform", "title": "Medical Chloroform Mask", "category": "Physical", "role": "Critical", "description": "Found inside service tunnel trash bin; carries cosmetic foundation and Aaron Cross hair strand."},
            {"id": "c13_laundry", "title": "Catering Linen Cart", "category": "Physical", "role": "Critical", "description": "Used to wheel the unconscious Sato through service tunnels into the underground loading dock."},
            {"id": "c13_badge", "title": "Cloned Hall B Badge", "category": "Digital", "role": "Supporting", "description": "Cross badge in Hall B was scanned by a hired temp worker paid $200 on Craigslist."},
            {"id": "c13_bitcoin", "title": "Cold Storage Bitcoin Wallet", "category": "Digital", "role": "Supporting", "description": "Ransom address created from an IP linked to Cross private yacht in Sausalito."},
            {"id": "c13_poker", "title": "Poker Debt Notice", "category": "Circumstantial", "role": "Red Herring", "description": "Viktor Vance gambling debt; he really just had an upset stomach from catering sushi."}
        ],
        "timeline": [
            {"time": "09:45", "event": "Kenji Sato enters Green Room VIP suite."},
            {"time": "10:00", "event": "Cross accomplice scans badge into Hall B."},
            {"time": "10:18", "event": "Cross enters service tunnel in catering uniform."},
            {"time": "10:20", "event": "Bodyguard Vance steps away to restroom."},
            {"time": "10:24", "event": "Sato subdued with chloroform and loaded into linen cart."},
            {"time": "10:35", "event": "Linen cart loaded into refrigeration delivery truck at dock."},
            {"time": "11:00", "event": "Keynote stage announcer declares Sato missing."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Inside the VIP green room, Sato tablet is unlocked on the coffee table. A glass of spilled water and a faint sweet chemical smell linger. Where do you begin?",
                "options": [
                    {"text": "Follow the service tunnel exit behind the VIP suite pantry.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c13_chloroform", "feedback": "Trash bin in service tunnel yields a discarded medical mask smelling of chloroform!"},
                    {"text": "Inspect the loading dock freight and delivery manifests.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c13_laundry", "feedback": "A catering linen cart was logged departing through the service elevator to the loading dock."},
                    {"text": "Interrogate Bodyguard Viktor Vance about his 8-minute absence.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c13_poker", "feedback": "Vance produces medical receipts; he suffered food poisoning from bad seafood."},
                    {"text": "Question COO Maya Lin about the keynote presentation.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Maya is panicked; the missing keynote is causing company stock to plunge."}
                ]
            },
            {
                "step": 2,
                "prompt": "Security logs show Aaron Cross badge attended Hall B at 10:00 AM, but convention cameras tell another story.",
                "options": [
                    {"text": "Pull Hall B video feed and match faces to badge scans.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c13_badge", "feedback": "The person holding Cross badge is a 20-year-old college student hired via Craigslist!"},
                    {"text": "Interrogate the Craigslist temp worker in Hall B.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Temp confesses he was paid $200 in cash by a man matching Aaron Cross to sit in Hall B with the badge."},
                    {"text": "Check Dr. Sarah Chen stage alibi.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Stage crew and video cameras confirm Sarah was on stage debugging robots the whole time."},
                    {"text": "Audit Maya Lin phone for acquisition talks.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Maya acquisition emails show she needed Sato present to close the $3B sale."}
                ]
            },
            {
                "step": 3,
                "prompt": "DNA analysis of hair from the chloroform mask matches Aaron Cross. The refrigeration delivery truck was traced heading north.",
                "options": [
                    {"text": "Trace the refrigeration delivery truck license plate on highway toll cameras.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Truck crossed Golden Gate Bridge heading toward a marina in Sausalito!"},
                    {"text": "Trace the 200 Bitcoin ransom wallet origin.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c13_bitcoin", "feedback": "Wallet IP traces directly to satellite internet registered to Cross yacht 'The Singularity'!"},
                    {"text": "Re-interview Bodyguard Vance.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance phone confirms zero calls or texts from kidnappers."},
                    {"text": "Check Moscone Center catering contractor files.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "A catering uniform was reported stolen from the locker room at 9:30 AM."}
                ]
            },
            {
                "step": 4,
                "prompt": "FBI tactical teams and maritime patrol converge on the Sausalito marina.",
                "options": [
                    {"text": "Raid the yacht 'The Singularity' with tactical federal agents.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Tactical raid breaches the yacht! Kenji Sato is rescued unharmed from the master stateroom!"},
                    {"text": "Apprehend Aaron Cross on the marina dock.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Cross is arrested on the dock carrying a laptop with the Bitcoin wallet open and patent transfer papers!"},
                    {"text": "Check if Maya Lin had contact with Cross.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Zero calls or contacts between Maya and Cross."},
                    {"text": "Inspect the delivery truck cargo bay.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Driver confesses he was paid $1,000 cash by Cross to transport the heavy laundry bin."}
                ]
            },
            {
                "step": 5,
                "prompt": "Kenji Sato is given medical evaluation. He testifies Cross forced him at gunpoint to sign patent transfers.",
                "options": [
                    {"text": "Seize the forced patent assignment documents from Cross laptop bag.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Documents assign 50% of neural network royalties to Cross, signed under duress."},
                    {"text": "Review yacht security video.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Video shows Cross carrying the drugged Sato aboard at 10:55 AM."},
                    {"text": "Formally clear Bodyguard Viktor Vance.", "killer_delta": 1, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance is cleared of criminal collusion; relieved of duty for negligence."},
                    {"text": "Examine Dr. Sarah Chen reaction.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sarah is overjoyed at Sato rescue; reconciles their research dispute."}
                ]
            },
            {
                "step": 6,
                "prompt": "Cross defense attorney claims Cross was rescuing Sato from a corporate hit ordered by Maya Lin.",
                "options": [
                    {"text": "Counter with the Craigslist ad, chloroform mask hair, and $14M Bitcoin demand.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "The attorney drops the defense immediately when presented with the digital paper trail."},
                    {"text": "Inspect the chloroform supply source.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Chemical bottle purchased online using Cross verified credit card."},
                    {"text": "Check Maya Lin personal devices.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "All devices audited by FBI; 100% clean."},
                    {"text": "Review delivery truck toll timestamps.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Tolls match the exact timeline from Moscone dock to Sausalito."}
                ]
            },
            {
                "step": 7,
                "prompt": "The Craigslist temp worker gives sworn testimony identifying Cross in a formal lineup.",
                "options": [
                    {"text": "Conduct formal physical lineup with the Craigslist witness.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Witness identifies Aaron Cross instantly as the man who handed him the badge and cash."},
                    {"text": "Analyze fingerprint on the stolen catering uniform buttons.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Cross fingerprints all over the discarded uniform found on the yacht."},
                    {"text": "Check Sato medical toxicology.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Chloroform levels match the mask residue; Sato makes full recovery."},
                    {"text": "Audit convention security protocols.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Convention security tightens badge-swapping detection protocols."}
                ]
            },
            {
                "step": 8,
                "prompt": "The federal kidnapping and extortion indictment is finalized.",
                "options": [
                    {"text": "Compile comprehensive federal kidnapping and extortion indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Ironclad docket: DNA on mask, Craigslist temp witness, linen cart video, forced patent papers, yacht raid."},
                    {"text": "Formally clear COO Maya Lin and Dr. Sarah Chen.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both executive team members are fully exonerated."},
                    {"text": "Sato returns to Moscone Center to deliver rescheduled keynote.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Keynote delivered to standing ovation; company shares soar."},
                    {"text": "Secure evidence chain of custody.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "All physical evidence transferred to federal vault."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Aaron Cross sits in federal detention before the US Magistrate.",
                "options": [
                    {"text": "Present the Craigslist badge proxy, DNA mask, and yacht raid testimony to Aaron Cross.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Cross snaps: 'I built that company with him! He became a billionaire while I was left with nothing! I deserved half!'"},
                    {"text": "Ask if Maya Lin gave him the override code.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Cross admits: 'I didn't need a code; I walked in through the unlocked pantry door.'"},
                    {"text": "Review timeline for federal judge.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Minute-by-minute timeline leaves zero doubt."},
                    {"text": "Seal the formal investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Federal prosecution docket signed and sealed."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who orchestrated the kidnapping of AI pioneer Kenji Sato?",
                "options": []
            }
        ],
        "true_culprit": "Aaron Cross",
        "true_solution": "Former co-founder Aaron Cross was consumed by bitter jealousy after being ousted. He hired a Craigslist temp to fake his presence in Hall B, slipped into the green room in a stolen catering uniform, chloroformed Sato, wheeled him out in a laundry bin to a refrigeration truck, and held him on his Sausalito yacht demanding $14M in Bitcoin and patent rights.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 14: THE ARMORED CAR ROBBERY ──
    {
        "id": "case_14",
        "title": "The Armored Car Robbery",
        "category": "Robbery",
        "difficulty": "Expert",
        "target_or_victim": "Federal Reserve Armored Transport 204 ($18 Million Cash)",
        "crime_scene": "Route 9 Mountain Pass Underpass",
        "briefing": "Armored Car 204 was ambushed in an isolated mountain cut. The reinforced steel doors were opened without thermal explosives, the two guards were handcuffed with department zip-ties, and $18 million in Federal Reserve currency vanished.",
        "suspects": [
            {
                "name": "Officer Derek Shaw",
                "role": "Escort Vehicle Guard",
                "public_story": "Driving the trailing security escort cruiser.",
                "private_secret": "Mastermind who planned the route ambush with a mercenary crew.",
                "motive": "$9 million split; facing foreclosure on multiple rental properties.",
                "alibi": "Claims his cruiser engine was disabled by a spike strip.",
                "weakness": "Cruiser dashcam memory card was found physically removed in his uniform boot.",
                "relationship": "Lead transport officer for 7 years.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Marcus Kane",
                "role": "Armored Car Driver",
                "public_story": "Driving Transport 204 when forced off the road.",
                "private_secret": "Deep in debt to illegal sports bookies.",
                "motive": "Bribe money to unlock the doors.",
                "alibi": "Found handcuffed to the steering wheel with head contusions.",
                "weakness": "Had phone calls with an unknown burner phone earlier that morning.",
                "relationship": "Armored truck driver for 3 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Frank 'Grizzly' Vance",
                "role": "Local Heavy Equipment Operator",
                "public_story": "Clearing roadside gravel half a mile away.",
                "private_secret": "Prior convictions for armed bank robbery 15 years ago.",
                "motive": "Return to old criminal habits.",
                "alibi": "Excavator GPS log confirms he was digging on the hill.",
                "weakness": "Owned a flatbed tow truck capable of hauling cash pallets.",
                "relationship": "Highway contractor.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Dispatcher Chloe Brooks",
                "role": "Central Routing Dispatcher",
                "public_story": "Monitoring vehicle GPS trackers at headquarters.",
                "private_secret": "Had an affair with driver Marcus Kane.",
                "motive": "Help Marcus stage a heist and flee together.",
                "alibi": "Console telemetry shows she was logged in continuously.",
                "weakness": "Authorized the last-minute detour onto Route 9.",
                "relationship": "Route dispatcher.",
                "is_culprit": False,
                "is_liar": True
            }
        ],
        "clues": [
            {"id": "c14_dashcam", "title": "Removed Dashcam SD Card", "category": "Digital", "role": "Critical", "description": "Found hidden in Officer Derek Shaw boot; footage shows Shaw getting out and opening the truck doors with his master bypass key."},
            {"id": "c14_detour", "title": "Route 9 Detour Radio Log", "category": "Digital", "role": "Supporting", "description": "Shaw requested the Route 9 mountain detour, claiming road construction on the interstate."},
            {"id": "c14_zipties", "title": "Police-Issue Tactical Zip-Ties", "category": "Physical", "role": "Critical", "description": "Batch number matches the tactical supplies issued directly to Shaw squad vehicle."},
            {"id": "c14_excavator", "title": "Excavator Telemetry Log", "category": "Digital", "role": "Red Herring", "description": "GPS proves Frank Vance was operating his digger non-stop; completely uninvolved."},
            {"id": "c14_burner", "title": "Marcus Kane Burner Phone", "category": "Digital", "role": "Red Herring", "description": "Calls were to his secret lover Dispatcher Chloe Brooks, not criminal accomplices."}
        ],
        "timeline": [
            {"time": "04:15", "event": "Armored Car 204 departs Federal Reserve depot."},
            {"time": "04:45", "event": "Officer Shaw requests Route 9 mountain pass detour."},
            {"time": "05:10", "event": "Shaw stages a spike strip blow-out behind Transport 204."},
            {"time": "05:15", "event": "Shaw approaches Transport 204, uses master key, zip-ties Kane."},
            {"time": "05:22", "event": "Accomplice van loads $18M cash pallets and speeds west."},
            {"time": "05:40", "event": "Shaw radio calls headquarters reporting an armed ambush."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "On the misty mountain cut of Route 9, Transport 204 sits with its rear doors swung wide. Driver Kane is handcuffed to the wheel. Officer Shaw cruiser sits behind with punctured front tires. Where do you begin?",
                "options": [
                    {"text": "Search Officer Derek Shaw cruiser and uniform equipment.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c14_dashcam", "feedback": "The cruiser dashcam slot is empty. In Shaw boot: the missing high-res SD memory card!"},
                    {"text": "Examine the tactical zip-ties binding driver Marcus Kane.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c14_zipties", "feedback": "Batch numbers on the zip-ties match tactical gear issued exclusively to Officer Shaw!"},
                    {"text": "Interrogate driver Marcus Kane about his burner phone.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c14_burner", "feedback": "Burner texts reveal Marcus was hiding a secret romance with Dispatcher Chloe Brooks."},
                    {"text": "Inspect contractor Frank Vance excavator and flatbed truck.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": "c14_excavator", "feedback": "Telemetry shows Vance was clearing rock slides continuously; he is not involved."}
                ]
            },
            {
                "step": 2,
                "prompt": "Forensics plays the recovered dashcam SD card found in Shaw boot.",
                "options": [
                    {"text": "Review the video footage recorded on the recovered dashcam card.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Video shows Shaw throwing his own spike strip, walking up to Transport 204, opening it with a key, and waving in an accomplice van!"},
                    {"text": "Interrogate Dispatcher Chloe Brooks about the Route 9 detour.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c14_detour", "feedback": "Radio logs prove Shaw called in a fake rockslide on the interstate to force the Route 9 detour."},
                    {"text": "Confront Marcus Kane with his gambling debts.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Kane was genuinely beaten by Shaw during the takeover; contusions are authentic."},
                    {"text": "Search the mountain pass ditches for discarded weapons.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Found Shaw personal firearm holster; no spent casings from outside attackers."}
                ]
            },
            {
                "step": 3,
                "prompt": "Dashcam video captured the license plate of the accomplice van: an unmarked gray Ford Econoline.",
                "options": [
                    {"text": "Issue statewide BOLO and deploy highway patrol for the gray Econoline.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Econoline intercepted at a remote barn! Three accomplices arrested with all $18M cash pallets!"},
                    {"text": "Confront Officer Derek Shaw with the dashcam footage.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Shaw jaw drops as he sees his own face on the monitor opening the armored doors."},
                    {"text": "Audit Dispatcher Chloe Brooks bank accounts.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Brooks has zero financial ties to the robbery; she was merely an unwitting pawn in the detour."},
                    {"text": "Check contractor Frank Vance alibi witnesses.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "County road inspector confirms Vance worked on the road cut all morning."}
                ]
            },
            {
                "step": 4,
                "prompt": "The captured accomplices in the barn identify Officer Shaw as the ringleader who supplied the codes and schedule.",
                "options": [
                    {"text": "Secure sworn confessions and text records from the captured accomplices.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Accomplices testify Shaw planned the robbery for 6 months and promised them a 50% cut."},
                    {"text": "Examine Shaw personal financial records.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Shaw was facing $1.2M in foreclosure demands across 4 real estate properties."},
                    {"text": "Check driver Marcus Kane medical report.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Hospital verifies Kane suffered a severe concussion from being pistol-whipped by Shaw."},
                    {"text": "Verify the armored car master bypass key origin.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Key was checked out under Shaw supervisor ID yesterday afternoon."}
                ]
            },
            {
                "step": 5,
                "prompt": "Shaw attempts to claim he was coerced by armed cartel members who threatened his family.",
                "options": [
                    {"text": "Investigate Shaw claims of cartel coercion with FBI threat analysts.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Coercion claim is completely debunked; Shaw family was safely vacationing in Hawaii with tickets he bought."},
                    {"text": "Search Shaw personal locker at the security depot.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found duplicate vehicle keys and handwritten ambush diagrams with Route 9 landmarks."},
                    {"text": "Formally clear driver Marcus Kane.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Kane is cleared of robbery charges; receives worker compensation for injuries."},
                    {"text": "Clear Dispatcher Chloe Brooks.", "killer_delta": 1, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Brooks is cleared of criminal collusion."}
                ]
            },
            {
                "step": 6,
                "prompt": "Forensic count of the recovered cash pallets confirms the full $18 million is intact.",
                "options": [
                    {"text": "Verify serial numbers of the recovered Federal Reserve currency.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Every bundle matches the Federal Reserve shipment manifest 204 to the dollar."},
                    {"text": "Analyze tire marks at the ambush underpass.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Tread marks match Shaw cruiser tires and the intercepted Econoline van."},
                    {"text": "Check contractor Frank Vance equipment.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance flatbed was never used; he is formally exonerated."},
                    {"text": "Review spike strip serial numbers.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Spike strip matches department inventory issued to Shaw cruiser trunk."}
                ]
            },
            {
                "step": 7,
                "prompt": "Shaw defense lawyer reviews the dashcam video and advises his client to plead guilty.",
                "options": [
                    {"text": "Present the dashcam video, zip-tie batch, accomplice testimony, and recovered $18M.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Lawyer advises Shaw that trial would be futile against such crushing physical proof."},
                    {"text": "Confirm the timeline of the fake radio detour call.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Voice analysis on the radio call confirms Shaw personally requested the mountain detour."},
                    {"text": "Interview driver Marcus Kane on the ambush moment.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Kane testifies Shaw told him to pull over for a 'warning light' before striking him."},
                    {"text": "Check Shaw cellphone call history.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Calls to the accomplice van driver recorded minutes before the ambush."}
                ]
            },
            {
                "step": 8,
                "prompt": "The federal armed robbery and public corruption indictment is completed.",
                "options": [
                    {"text": "Compile the comprehensive federal robbery and corruption indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Comprehensive indictment finalized: video proof, zip-ties, master key, accomplice confessions, all $18M recovered."},
                    {"text": "Return $18M cash to the Federal Reserve branch vault.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Cash pallets safely returned to the central reserve vault."},
                    {"text": "Formally commend the highway patrol and investigative unit.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Unit receives commendation for solving the heist in under 8 hours."},
                    {"text": "Seal all tactical evidence files.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Evidence sealed for federal court trial."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Officer Derek Shaw sits in federal custody, stripped of his badge. The final confrontation.",
                "options": [
                    {"text": "Demand formal plea and confession from Officer Derek Shaw.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Shaw breaks down: 'I spent 7 years driving billions for the government while my own bank was foreclosing on my home. I thought I planned the perfect score.'"},
                    {"text": "Ask if Marcus Kane was in on it.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Shaw admits: 'Kane knew nothing. I had to knock him out so he wouldn't hit the alarm.'"},
                    {"text": "Review timeline for the court.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline matches every movement between 04:15 and 05:40 flawlessly."},
                    {"text": "Seal the formal investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The docket is closed and ready for the final verdict."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who was the inside mastermind behind the Armored Car Robbery?",
                "options": []
            }
        ],
        "true_culprit": "Officer Derek Shaw",
        "true_solution": "Lead escort officer Derek Shaw orchestrated the heist to escape personal bankruptcy. He fabricated a highway rockslide to reroute the transport onto Route 9, threw down his own spike strip, used a stolen master key to unlock the armored doors, assaulted driver Kane, bound him with department zip-ties, and loaded $18M into an accomplice van before hiding the cruiser dashcam SD card in his boot.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 15: POISON IN THE VINEYARD ──
    {
        "id": "case_15",
        "title": "Poison in the Vineyard",
        "category": "Poisoning",
        "difficulty": "Hard",
        "target_or_victim": "Henri Dupont, Master Winemaker",
        "crime_scene": "The Barrel Cellar, Domaine Dupont, Bordeaux",
        "briefing": "During the grand barrel-tasting of the 2015 reserve vintage, master vintner Henri Dupont collapsed clutching his throat, dead from concentrated nicotine pesticide poison mixed into his personal tasting pipette.",
        "suspects": [
            {
                "name": "Etienne Dupont",
                "role": "Brother & Co-Vintner",
                "public_story": "Greeting guests in the courtyard reception.",
                "private_secret": "Heavily in debt; Henri refused to sell the estate to a luxury resort developer.",
                "motive": "Inherit the sole ownership of the vineyard and sell it for 30 million euros.",
                "alibi": "Courtyard guests saw him refilling wine glasses at 5:00 PM.",
                "weakness": "Concentrated nicotine sulfate pesticide bottle missing from his private gardening shed.",
                "relationship": "Brother and 50% co-owner.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Camille Laurent",
                "role": "Chief Sommelier",
                "public_story": "Arranging crystal glassware in the dining pavilion.",
                "private_secret": "Discovered Henri was secretly blending cheap bulk wine into the reserve vintage.",
                "motive": "Expose the fraud and ruin Henri reputation.",
                "alibi": "Wine writers confirm she was decanting wine in the pavilion.",
                "weakness": "Had an argument with Henri this morning over wine labeling.",
                "relationship": "Sommelier for 5 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Luc Moreau",
                "role": "Cellar Master",
                "public_story": "Checking humidity levels in the north maturation cave.",
                "private_secret": "Fired earlier this week for poor barrel sanitization.",
                "motive": "Spite and vengeance against Henri.",
                "alibi": "Cellar log stamped his barcode in the north cave at 4:45 PM.",
                "weakness": "Had direct access to all barrel pipettes.",
                "relationship": "Former cellar worker.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Gaston Vance",
                "role": "Resort Developer & Guest",
                "public_story": "Tasting wines with investors in the main tasting room.",
                "private_secret": "Made a buyout offer of 30M euros that Henri publicly mocked.",
                "motive": "Remove Henri to force a quick sale by the surviving brother.",
                "alibi": "Dozens of wine journalists saw him in the main hall.",
                "weakness": "Carrying architectural plans of the proposed luxury golf resort in his briefcase.",
                "relationship": "Prospective buyer.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c15_pipette", "title": "Glass Tasting Pipette Residue", "category": "Physical", "role": "Critical", "description": "Tasting pipette rubber bulb coated in concentrated agricultural nicotine sulfate; fingerprints belong to Etienne Dupont."},
            {"id": "c15_developer", "title": "Secret Buyout Contract", "category": "Circumstantial", "role": "Supporting", "description": "Found in Etienne desk: preliminary agreement with Gaston Vance promising to sell Domaine Dupont for 30M euros if Henri dies."},
            {"id": "c15_bottle", "title": "Empty Nicotine Sulfate Flask", "category": "Physical", "role": "Critical", "description": "Found buried in the compost heap behind Etienne private greenhouse with his gardening gloves."},
            {"id": "c15_sommelier", "title": "Sommelier Tasting Notes", "category": "Physical", "role": "Red Herring", "description": "Camille notes criticize Henri blending practices, but contain zero toxicological references."},
            {"id": "c15_barrel", "title": "Barrel 14 Chemical Analysis", "category": "Physical", "role": "Supporting", "description": "The wine inside the barrel itself is pure; only Henri personal glass pipette was poisoned."}
        ],
        "timeline": [
            {"time": "16:00", "event": "VIP reserve tasting begins at Domaine Dupont."},
            {"time": "16:45", "event": "Etienne slips into barrel cellar and coats pipette bulb with nicotine."},
            {"time": "17:00", "event": "Etienne refills wine in courtyard as an alibi."},
            {"time": "17:15", "event": "Henri extracts wine from Barrel 14 using his personal pipette."},
            {"time": "17:18", "event": "Henri ingests toxic dose, collapses, and dies within 3 minutes."},
            {"time": "17:25", "event": "Emergency medical team arrives; announces fatal poisoning."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "In the vaulted oak barrel cellar, Henri Dupont lies beside Barrel 14. His glass tasting pipette is shattered on the stone floor. Bitter smell of tobacco and pesticide hangs in the air. How do you investigate?",
                "options": [
                    {"text": "Analyze the chemical residue on the shattered glass pipette and rubber bulb.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c15_pipette", "feedback": "Spectrometry confirms lethal concentration of nicotine sulfate on the rubber suction bulb!"},
                    {"text": "Examine the wine inside Barrel 14 for contamination.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c15_barrel", "feedback": "The wine in the barrel is pure! The poison was placed directly onto Henri private pipette bulb."},
                    {"text": "Search Sommelier Camille Laurent notebook.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c15_sommelier", "feedback": "Notebook shows complaints about bulk wine blending, but no poisons."},
                    {"text": "Interrogate developer Gaston Vance about his buyout offers.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Vance admits he wanted the land, but insists he was drinking wine in full view of 40 journalists."}
                ]
            },
            {
                "step": 2,
                "prompt": "Nicotine sulfate is a banned agricultural pesticide. Who had access to estate chemical stores?",
                "options": [
                    {"text": "Search the estate greenhouse and composting bins.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c15_bottle", "feedback": "Buried in the compost heap behind Etienne greenhouse: an empty flask of nicotine sulfate and muddy gloves!"},
                    {"text": "Search brother Etienne Dupont private office desk.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c15_developer", "feedback": "Found a signed preliminary contract with developer Vance promising 30M euros once Henri is 'no longer an obstacle'."},
                    {"text": "Interrogate Cellar Master Luc Moreau about barrel access.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Moreau barcode proves he was in the north cave; he had no access to the reserve cellar."},
                    {"text": "Question Sommelier Camille Laurent about the tasting order.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Camille confirms Henri always tasted Barrel 14 first using his personal pipette."}
                ]
            },
            {
                "step": 3,
                "prompt": "The muddy gardening gloves found with the poison bottle are analyzed for epithelial skin cells.",
                "options": [
                    {"text": "Test DNA inside the gardening gloves recovered from the compost.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "DNA inside the gloves is a 100% match to Etienne Dupont!"},
                    {"text": "Confront Etienne with the developer contract found in his desk.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Etienne turns pale, stammering that the contract was merely a preliminary negotiation."},
                    {"text": "Interrogate Gaston Vance regarding the buyout clause.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Vance reveals Etienne assured him this morning that Henri would agree to sell before the day was out."},
                    {"text": "Check Luc Moreau work locker.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Locker contains ordinary winemaking tools and personal clothes; no pesticides."}
                ]
            },
            {
                "step": 4,
                "prompt": "Cellar humidity sensors and electronic door sensors log movements into the reserve cellar.",
                "options": [
                    {"text": "Extract door sensor timestamps for the reserve cellar.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Reserve cellar door opened at 16:45 using Etienne master keycard, 30 minutes before Henri arrived!"},
                    {"text": "Question courtyard guests regarding Etienne movements at 16:45.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Guests recall Etienne disappeared from the courtyard for about 15 minutes between 16:40 and 16:55."},
                    {"text": "Check Sommelier Camille decanting schedule.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Camille was serving guests in the dining pavilion continuously from 16:30 to 17:15."},
                    {"text": "Audit estate pesticide purchase archives.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Old stock of nicotine sulfate was grandfathered into Etienne personal botanical garden shed."}
                ]
            },
            {
                "step": 5,
                "prompt": "Fingerprint specialists dust the rubber bulb of the poisoned pipette.",
                "options": [
                    {"text": "Dust the rubber pipette bulb for latent thumbprints.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Etienne right thumbprint is clearly visible in dried chemical residue on the bulb!"},
                    {"text": "Check Henri wine glass for secondary poisons.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "No other poisons found; death was caused exclusively by the pipette bulb application."},
                    {"text": "Interrogate developer Gaston Vance on wire transfers.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance escrow was waiting for signed deeds; he had no part in the poisoning."},
                    {"text": "Re-interview Cellar Master Luc Moreau.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Moreau is deeply saddened by Henri death; completely exonerated."}
                ]
            },
            {
                "step": 6,
                "prompt": "Forensic pathologists confirm nicotine was absorbed transdermally and ingested orally when Henri tasted the wine drop.",
                "options": [
                    {"text": "Review toxicology onset time and dosage calculations.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Dosage on the bulb was over 500mg, enough to kill an adult within 2 minutes of mucosal contact."},
                    {"text": "Search Etienne vehicle parked in the driveway.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found one-way flight booking to Monaco and a debt repayment schedule to French banks."},
                    {"text": "Check Camille Laurent phone records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Calls only to wine critics and sommeliers; cleared of all involvement."},
                    {"text": "Examine Barrel 14 oak wood.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Oak wood is uncontaminated; the wine stock is completely safe."}
                ]
            },
            {
                "step": 7,
                "prompt": "Etienne legal counsel arrives and attempts to blame the murder on disgruntled former cellar master Luc Moreau.",
                "options": [
                    {"text": "Present the thumbprint on the bulb, DNA inside the gloves, and 16:45 keycard log.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "The attorney turns to Etienne in stunned silence and advises him to stop speaking immediately."},
                    {"text": "Show Moreau electronic barcode alibi in the north cave.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Moreau alibi is 100% corroborated by automated cave environmental logs."},
                    {"text": "Interview the winery accountant on Etienne debts.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Accountant confirms Etienne owed 4.5 million euros in overdue personal mortgages."},
                    {"text": "Review the 30M euro resort buyout clause.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Contract specified that upon Henri death, Etienne became 100% owner entitled to sell."}
                ]
            },
            {
                "step": 8,
                "prompt": "All evidence pillars are complete: nicotine flask, DNA gloves, thumbprint on pipette, keycard timestamp, and 30M euro motive.",
                "options": [
                    {"text": "Assemble the comprehensive premeditated murder indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Watertight indictment for murder by poison, forgery, and grand fraud ready for the French court."},
                    {"text": "Formally clear Camille Laurent and Luc Moreau.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both employees are fully exonerated and retained by the estate trustees."},
                    {"text": "Cancel the fraudulent buyout contract with developer Gaston Vance.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Estate trustees void the buyout; the historic vineyard will be preserved in trust."},
                    {"text": "Secure the vintage barrels under police seal.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Winery inventory certified safe and protected."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Etienne Dupont sits in the Gendarmerie interrogation room. The final confrontation.",
                "options": [
                    {"text": "Confront Etienne with the thumbprint on the bulb, his DNA in the compost gloves, and the 30M euro resort contract.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Etienne weeps into his hands: 'Henri was an arrogant fool! He wanted us to go bankrupt making prestige wine! I had to save myself!'"},
                    {"text": "Ask if Camille Laurent helped him.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Etienne scoffs: 'Camille loved Henri's wine more than her own life. She knew nothing.'"},
                    {"text": "Review timeline for the examining magistrate.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Minute-by-minute timeline leaves zero doubt of premeditation."},
                    {"text": "Seal the formal murder investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Investigation docket signed, stamped, and ready for trial."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who poisoned master winemaker Henri Dupont?",
                "options": []
            }
        ],
        "true_culprit": "Etienne Dupont",
        "true_solution": "Etienne Dupont was drowning in 4.5M euros in debt and wanted to sell the family vineyard to a resort developer for 30M euros, which Henri refused. At 16:45, Etienne used his master keycard to enter the cellar, coated the rubber bulb of Henri personal tasting pipette with concentrated nicotine sulfate from his greenhouse, buried the bottle and gloves in the compost, and watched Henri taste the poisoned pipette.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    }
]
