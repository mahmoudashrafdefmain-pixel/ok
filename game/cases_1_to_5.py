# -*- coding: utf-8 -*-
"""
game/cases_1_to_5.py — Crime Cases 1 through 5 for Investigation Mode.
Case 01: Murder in the Penthouse (Murder)
Case 02: Theft of the Blue Moon Diamond (Theft)
Case 03: Kidnapping of the Diplomat's Daughter (Kidnapping)
Case 04: The Midnight Bank Heist (Robbery)
Case 05: The Vanishing Scientist (Disappearance)
"""

CASES_1_TO_5 = [
    # ── CASE 01: MURDER IN THE PENTHOUSE ──
    {
        "id": "case_01",
        "title": "Murder in the Penthouse",
        "category": "Murder",
        "difficulty": "Medium",
        "target_or_victim": "Victor Stone, Real Estate Tycoon",
        "crime_scene": "Penthouse Suite 40B, Skyview Tower",
        "briefing": "Victor Stone was discovered dead slumped over his mahogany desk at 11:15 PM, poisoned by potassium cyanide in his 18-year vintage scotch. The penthouse door was secured with an electronic deadlock.",
        "suspects": [
            {
                "name": "Clara Stone",
                "role": "Estranged Wife",
                "public_story": "Was dining with friends across town until midnight.",
                "private_secret": "Deep in personal debt; Victor rewrote his will yesterday to disinherit her.",
                "motive": "Sole beneficiary under the previous will worth $40 million.",
                "alibi": "Restaurant receipt from Bistro Belle at 10:45 PM.",
                "weakness": "Paid cash and arrived alone at 10:45 PM after driving aimlessly.",
                "relationship": "Wife of 12 years, bitter divorce ongoing.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Julian Vance",
                "role": "Business Partner",
                "public_story": "Was reviewing acquisition contracts on floor 12 of the tower.",
                "private_secret": "Embezzled $6M from Stone Holdings; Stone scheduled an unannounced audit for 9:00 AM.",
                "motive": "Desperation to prevent financial ruined and 10 years imprisonment.",
                "alibi": "Keycard log shows entry on floor 12 at 9:30 PM.",
                "weakness": "Floor 12 fire stairwell leads directly to floor 40 with disabled sensor.",
                "relationship": "Co-founder of Stone Holdings.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Evelyn Reed",
                "role": "Executive Secretary",
                "public_story": "Left the office at 6:00 PM and went straight home to sleep.",
                "private_secret": "Had a passionate affair with Stone that he abruptly ended last week.",
                "motive": "Humiliation, betrayal, and heartbreak.",
                "alibi": "Apartment doorman saw her enter at 6:45 PM.",
                "weakness": "Cell phone GPS pinged a tower near Skyview Tower at 10:15 PM.",
                "relationship": "Personal secretary for 5 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Dr. Robert Hale",
                "role": "Personal Physician",
                "public_story": "Delivered cardiac medication at 8:00 PM and drove home.",
                "private_secret": "Prescribed off-label stimulants to Stone under pressure.",
                "motive": "Fear of medical board inquiry if Stone toxicology is analyzed.",
                "alibi": "Highway toll camera snapped his sedan crossing the bridge at 8:40 PM.",
                "weakness": "Accidentally left his medical bag in the guest room.",
                "relationship": "Doctor and longtime club friend.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Leo Martinez",
                "role": "Head Butler",
                "public_story": "Retired to staff quarters on floor 39 at 10:00 PM.",
                "private_secret": "Selling confidential gossip to tabloid reporters.",
                "motive": "Stone caught him recording a conversation earlier that day.",
                "alibi": "Staff service elevator logs verify departure at 10:00 PM.",
                "weakness": "Had unrestricted access to the bar cart and glassware.",
                "relationship": "Employed as butler for 3 years.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c1_glass", "title": "Residue in Scotch Tumbler", "category": "Physical", "role": "Critical", "description": "Cyanide residue detected on the rim. Smudged latex glove prints found."},
            {"id": "c1_card", "title": "Master Keycard 04 Log", "category": "Digital", "role": "Supporting", "description": "Penthouse exterior door unlocked at 9:55 PM using Master Card 04, checked out to Executive Suite."},
            {"id": "c1_stairs", "title": "Fire Stairwell Scuffs", "category": "Physical", "role": "Critical", "description": "Fresh rubber shoe dust on stairwell 12-40 matching size 10 Italian leather oxfords."},
            {"id": "c1_cufflink", "title": "Silver Monogrammed Cufflink", "category": "Physical", "role": "Red Herring", "description": "Initials 'E.R.' belonging to Evelyn Reed, dropped days earlier during an argument."},
            {"id": "c1_audit", "title": "Audit Voicemail Record", "category": "Digital", "role": "Supporting", "description": "Stone called forensic auditor at 9:15 PM stating Julian Vance embezzlement was discovered."}
        ],
        "timeline": [
            {"time": "20:00", "event": "Dr. Hale delivers cardiac medication and leaves at 20:30."},
            {"time": "21:15", "event": "Stone leaves voicemail exposing Julian Vance $6M embezzlement."},
            {"time": "21:30", "event": "Julian Vance logs keycard entry on Floor 12."},
            {"time": "21:55", "event": "Master Keycard 04 unlocks Penthouse door from exterior."},
            {"time": "22:15", "event": "Evelyn Reed phone pings nearby cell tower as she drives by."},
            {"time": "22:45", "event": "Clara Stone pays cash bill at Bistro Belle."},
            {"time": "23:15", "event": "Butler Leo Martinez discovers Stone body at desk."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "You arrive at Penthouse Suite 40B. Victor Stone slumps over the desk, crystal tumbler nearby. Bitter almond scent hangs in the air. How do you begin?",
                "options": [
                    {"text": "Secure the scotch tumbler for rapid toxicology analysis.", "killer_delta": 1, "evidence_score_delta": 10, "unlocked_clue_id": "c1_glass", "feedback": "Forensics confirms potassium cyanide dissolved in the scotch tumbler."},
                    {"text": "Search under the desk and along the bookshelf for dropped items.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c1_cufflink", "feedback": "You find a silver cufflink with 'E.R.' engraving under the chair."},
                    {"text": "Review electronic door access logs for Suite 40B.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c1_card", "feedback": "Door was opened from exterior at 9:55 PM using Master Card 04."},
                    {"text": "Question Butler Leo Martinez on who served the liquor.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Leo insists the bottle was placed unopened on the bar cart at 6:00 PM."}
                ]
            },
            {
                "step": 2,
                "prompt": "Master Keycard 04 was checked out by the Executive Suite on Floor 12. Julian Vance claims he was alone in his office all evening. What do you pursue?",
                "options": [
                    {"text": "Inspect the emergency fire stairwell between Floor 12 and Floor 40.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c1_stairs", "feedback": "Dust and rubber scuffs on stairs 12-40 match expensive Italian dress shoes!"},
                    {"text": "Subpoena Stone phone voicemail records.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c1_audit", "feedback": "Voicemail at 9:15 PM reveals Stone scheduled an unannounced audit targeting Vance."},
                    {"text": "Interrogate estranged wife Clara Stone about her alibi.", "killer_delta": -1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Clara admits she had no dinner companions at Bistro Belle; she was crying in her car."},
                    {"text": "Inspect Dr. Hale medical bag in the guest room.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Contains nitroglycerin tablets and stethoscope, but zero traces of cyanide."}
                ]
            },
            {
                "step": 3,
                "prompt": "Evelyn Reed cell phone pinged near the tower at 10:15 PM. How do you press the interrogation?",
                "options": [
                    {"text": "Confront Evelyn Reed about why her phone was near Skyview Tower.", "killer_delta": 0, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Evelyn breaks down: she drove past hoping to speak with Stone, but never entered."},
                    {"text": "Confront Julian Vance regarding the 9:15 PM audit threat.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Vance stutters and claims the audit was routine, visibly sweating."},
                    {"text": "Examine Clara Stone bank accounts and financial records.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Heavily in debt, but her browser search history shows only divorce attorneys."},
                    {"text": "Search Butler Leo Martinez quarters for poison vials.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Found tabloid payments of $500, but no chemicals or lockpicks."}
                ]
            },
            {
                "step": 4,
                "prompt": "Stairwell scuffs match size 10 Italian dress shoes. Detectives execute a search of Vance office on Floor 12.",
                "options": [
                    {"text": "Examine Julian Vance footwear and wardrobe in his office.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Under his credenza: bespoke Italian oxfords with dust matching the stairwell!"},
                    {"text": "Examine Dr. Hale bridge toll record timestamps.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Bridge toll cameras prove Hale was across the river at 8:40 PM; alibi is rock solid."},
                    {"text": "Inspect the bar cart for additional cyanide traces.", "killer_delta": 1, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Cyanide was in the tumbler, not in the bottle. The killer dusted the glass directly."},
                    {"text": "Check Evelyn Reed locker for toxins.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Locker contains personal diaries and old love letters, but no poisons."}
                ]
            },
            {
                "step": 5,
                "prompt": "Forensic auditors confirm that $6M was siphoned from Stone Holdings into a Cayman shell company.",
                "options": [
                    {"text": "Trace beneficial ownership of the Cayman shell corporation.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Beneficial owner is Julian Vance! Stone signature on wire authorizations was forged."},
                    {"text": "Check if Clara Stone received offshore wire transfers.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Clara accounts are local and overdrawn; she was completely unaware of the shell."},
                    {"text": "Interrogate building maintenance on stairwell camera status.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Stairwell camera sensor was disabled for scheduled repainting last Monday."},
                    {"text": "Search commercial chemical distributors for cyanide orders.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Cyanide order shipped to dummy lab registered to Vance Cayman shell address."}
                ]
            },
            {
                "step": 6,
                "prompt": "Vance computer cache contains browser searches on lethal cyanide dosages and unmonitored stairwell routes.",
                "options": [
                    {"text": "Subpoena Vance laptop browser cache and deleted files.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Browser history shows searches: 'potassium cyanide onset time' and 'Skyview stairwell specs'."},
                    {"text": "Re-interrogate Clara Stone on her movements at 10:45 PM.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Clara explains she bought wine at the bistro to calm her nerves, corroborated by cashier."},
                    {"text": "Verify the ER cufflink timeline with Butler Leo.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Butler confirms Stone dropped the cufflink behind the desk three days earlier."},
                    {"text": "Review Stone last email sent at 9:40 PM.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Stone emailed Vance: 'Come up to 40B now with the ledger or I call the police.'"}
                ]
            },
            {
                "step": 7,
                "prompt": "You reconstruct the timeline: Vance entered Floor 12 at 9:30 PM, climbed stairs at 9:45 PM, opened 40B at 9:55 PM, and slipped back down by 10:25 PM.",
                "options": [
                    {"text": "Perform timed physical reenactment of the stairwell climb.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "The 28-flight ascent and descent takes exactly 18 minutes; fits the timeline flawlessly."},
                    {"text": "Check if Evelyn Reed high heels could climb the stairwell.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Physical test proves climbing 28 flights in 4-inch stilettos would be impossible."},
                    {"text": "Review Dr. Hale cellular tower records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Hale phone was connected to his home Wi-Fi starting at 8:55 PM."},
                    {"text": "Examine elevator motor logs.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "No elevators traveled between floor 12 and 40 during the critical window."}
                ]
            },
            {
                "step": 8,
                "prompt": "All evidence chains are solidifying: motive ($6M fraud), means (cyanide order), opportunity (stairwell scuffs & Keycard 04).",
                "options": [
                    {"text": "Assemble formal evidence docket for District Attorney.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Comprehensive dossier assembled: keycard logs, shoe match, Cayman wire, search history."},
                    {"text": "Formally clear Clara Stone and Evelyn Reed of murder charges.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both women are exonerated of the homicide."},
                    {"text": "Check Butler Leo phone records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Calls were only to entertainment reporters; no contact with poison suppliers."},
                    {"text": "Verify cyanide lot number with manufacturer.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Lot number matches chemical shipment delivered to Vance freight mailbox."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Suspects are gathered in the penthouse library under police guard. One final confrontation will seal the case.",
                "options": [
                    {"text": "Present the size 10 oxford scuffs, cyanide delivery, and $6M audit threat to Julian Vance.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Vance turns pale as death, drops his head, and whispers: 'Victor was going to ruin me.'"},
                    {"text": "Ask Clara Stone if she will inherit the estate.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Clara weeps quietly, stating she just wants peace from the nightmare."},
                    {"text": "Review the final toxicology report timestamps.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Confirmed: death occurred between 10:10 PM and 10:20 PM."},
                    {"text": "Signal the arresting detective.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Handcuffs unclipped; ready for the final formal accusation."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who murdered Victor Stone in Penthouse Suite 40B?",
                "options": []
            }
        ],
        "true_culprit": "Julian Vance",
        "true_solution": "Julian Vance embezzled $6M from Stone Holdings. When Stone scheduled an audit and summoned him at 9:40 PM, Vance took the unmonitored fire stairwell from floor 12 to 40, entered with Master Card 04, poisoned Stone scotch tumbler with cyanide, watched him collapse, and returned down the stairs to create an alibi.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 02: THEFT OF THE BLUE MOON DIAMOND ──
    {
        "id": "case_02",
        "title": "Theft of the Blue Moon Diamond",
        "category": "Theft",
        "difficulty": "Medium",
        "target_or_victim": "The Blue Moon Diamond ($25M)",
        "crime_scene": "Vault, Kensington Manor",
        "briefing": "During the Harrington Charity Gala, the 120-carat Blue Moon Diamond was replaced with a synthetic cubic zirconia duplicate inside a pressure-sensitive vault.",
        "suspects": [
            {
                "name": "Lord Arthur Harrington",
                "role": "Estate Patriarch",
                "public_story": "Delivering keynote speech in ballroom.",
                "private_secret": "Manor is mortgaged to the hilt; facing bankruptcy.",
                "motive": "Collect $30M insurance payout to save the ancestral estate.",
                "alibi": "Speech recorded on video 22:00-22:30.",
                "weakness": "Held physical master override key.",
                "relationship": "Estate owner",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Lady Cynthia Harrington",
                "role": "Daughter-in-Law & Gemologist",
                "public_story": "Greeted gala guests and managed auction catalog.",
                "private_secret": "Runs illicit antique fencing ring in Antwerp.",
                "motive": "Offered $15M cash by private foreign collector.",
                "alibi": "Claims she stayed on west terrace during theft.",
                "weakness": "Synthetic replica laser cut marks match her private gem lab.",
                "relationship": "Resident gem expert",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Nathan Drake",
                "role": "Stage Magician & Guest",
                "public_story": "Performed sleight of hand at the bar.",
                "private_secret": "Former convicted jewel thief on probation.",
                "motive": "Thrill of impossible heist and reputation.",
                "alibi": "Guests saw card tricks at 22:15 at the bar.",
                "weakness": "Carrying lockpicks in tuxedo pocket.",
                "relationship": "Hired entertainment",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Chief Guard Burke",
                "role": "Head of Security",
                "public_story": "Monitored central control room.",
                "private_secret": "Owes $80,000 to underground loan sharks.",
                "motive": "Bribe money to wipe gambling debt.",
                "alibi": "Badge logged at terminal all night.",
                "weakness": "Vault camera experienced a 4-min video loop at 22:18.",
                "relationship": "Security head for 15 years",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Sergei Volkov",
                "role": "Diamond Merchant",
                "public_story": "Browsed upstairs art gallery.",
                "private_secret": "Bitter rivalry with Harrington over a failed mine.",
                "motive": "Humiliate Harrington family internationally.",
                "alibi": "Photo in gallery background at 22:12.",
                "weakness": "Found carrying an empty velvet jewelry pouch.",
                "relationship": "Business rival",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c2_rep", "title": "Synthetic Zirconia Duplicate", "category": "Physical", "role": "Critical", "description": "Duplicate weighs exactly 24.1g; laser micro-etching matches Cynthia private lab."},
            {"id": "c2_cam", "title": "Vault Camera 4-Min Loop", "category": "Digital", "role": "Critical", "description": "Camera 3 was fed a pre-recorded loop injected from family suite iPad Wi-Fi at 22:18."},
            {"id": "c2_pic", "title": "Titanium Tension Wrench", "category": "Physical", "role": "Red Herring", "description": "Magician Nathan lockpick dropped on stairs during an unauthorized explore."},
            {"id": "c2_prf", "title": "Scent of Jasmine & Vanilla", "category": "Behavioral", "role": "Supporting", "description": "Traces of bespoke perfume found in vault pedestal air seal, unique to Cynthia."},
            {"id": "c2_not", "title": "Foreclosure Demand Notice", "category": "Circumstantial", "role": "Supporting", "description": "Bank demand for $4.2M found in Lord Harrington desk drawer."}
        ],
        "timeline": [
            {"time": "20:00", "event": "Charity gala begins in Kensington Ballroom."},
            {"time": "22:00", "event": "Lord Harrington takes stage for keynote address."},
            {"time": "22:18", "event": "Vault camera feed replaced with pre-recorded loop."},
            {"time": "22:21", "event": "Pressure plate recalibrated with synthetic replica."},
            {"time": "22:30", "event": "Harrington finishes keynote address."},
            {"time": "23:00", "event": "Curator inspects vault and identifies fake diamond."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Inside the vault, polarized light reveals the diamond is cubic zirconia. Pressure sensors never tripped. Where do you begin?",
                "options": [
                    {"text": "Examine replica diamond under 40x magnification.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c2_rep", "feedback": "Laser micro-faceting matches equipment in Lady Cynthia private workshop!"},
                    {"text": "Inspect floor around pedestal for trace scents and fibers.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c2_prf", "feedback": "Bespoke jasmine-vanilla perfume detected inside the airtight pedestal."},
                    {"text": "Search exterior stairs leading to vault.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c2_pic", "feedback": "Titanium lockpick found. Belonging to magician Nathan Drake."},
                    {"text": "Interrogate Chief Guard Burke about alarms.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Burke insists sensors were green across the entire estate."}
                ]
            },
            {
                "step": 2,
                "prompt": "Camera 3 suffered a 4-minute frozen loop at 10:18 PM. What do you investigate?",
                "options": [
                    {"text": "Trace the IP address that injected the video loop.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c2_cam", "feedback": "Loop transmitted from family suite iPad connected to manor Wi-Fi!"},
                    {"text": "Interrogate Magician Nathan Drake about lockpicks.", "killer_delta": -1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Nathan admits he snooped out of curiosity, but fled when he saw a shadow."},
                    {"text": "Search Lord Harrington private office.", "killer_delta": 0, "evidence_score_delta": 7, "unlocked_clue_id": "c2_not", "feedback": "Foreclosure notice demanding $4.2M found. Harrington had strong motive."},
                    {"text": "Question merchant Sergei Volkov about velvet pouch.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Volkov brought pouch hoping to make a private purchase offer."}
                ]
            },
            {
                "step": 3,
                "prompt": "The pressure sensor required the fake to match within 0.05 grams. Who calibrated the weight?",
                "options": [
                    {"text": "Check who had authorized access to calibrate the diamond weight.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Records show Lady Cynthia performed the annual gem appraisal 2 weeks ago."},
                    {"text": "Ask Lord Harrington about appraisal authorizations.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Harrington trusted his daughter-in-law completely with gemstones."},
                    {"text": "Inspect Nathan Drake magic props.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Trick coins and cards, but no high-precision jewelers scale."},
                    {"text": "Audit Chief Guard Burke banking records.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Severe gambling debts, but no contact with gem buyers."}
                ]
            },
            {
                "step": 4,
                "prompt": "The family iPad was logged into at 10:18 PM. Who held the session?",
                "options": [
                    {"text": "Extract credentials and browser cache from iPad.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Active session belonged to Cynthia, with encrypted Antwerp chats!"},
                    {"text": "Confront Lady Cynthia about her 10:18 PM alibi.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Claims she was alone on west terrace; no cameras corroborate."},
                    {"text": "Check ballroom video for Lord Harrington.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Video shows Harrington speaking on podium until 10:30 PM continuously."},
                    {"text": "Search Sergei Volkov vehicle.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Trunk is empty; no high-tech gear found."}
                ]
            },
            {
                "step": 5,
                "prompt": "A courier was booked from Kensington to Brussels Airport at 11:30 PM.",
                "options": [
                    {"text": "Intercept the courier vehicle before it departs estate gates.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Real Blue Moon Diamond recovered inside cosmetic jar in courier bag!"},
                    {"text": "Ask Nathan Drake about the courier service.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Drake has never heard of the courier company."},
                    {"text": "Search Lord Harrington coat pockets.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Only speech index cards and vault master key found."},
                    {"text": "Analyze Chief Guard Burke cell phone.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "No communications with logistics or couriers."}
                ]
            },
            {
                "step": 6,
                "prompt": "The real diamond is recovered. You analyze Cynthia encrypted messages.",
                "options": [
                    {"text": "Decrypt Antwerp WhatsApp logs on Cynthia phone.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Logs show $15M wire transfer pending upon courier receipt in Brussels."},
                    {"text": "Confront Lord Harrington with recovered diamond.", "killer_delta": 1, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Harrington breaks down, horrified his family member is a thief."},
                    {"text": "Formally clear Nathan Drake.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Drake is exonerated and released from custody."},
                    {"text": "Analyze the camera loop duration.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "4-minute window allowed experienced gemologist to execute swap."}
                ]
            },
            {
                "step": 7,
                "prompt": "Chemical swab from Cynthia evening gloves matches mounting silicone.",
                "options": [
                    {"text": "Present silicone match to Cynthia attorney.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Attorney advises Cynthia to exercise her right to remain silent."},
                    {"text": "Check if Guard Burke helped bypass sensors.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Sensor bypass was purely software-based; Burke had no part in it."},
                    {"text": "Verify Sergei Volkov alibi with witnesses.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Ambassador confirms Volkov was chatting with him at 10:15 PM."},
                    {"text": "Document replica manufacturing records.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Lab records show Cynthia spent months synthesizing the stone."}
                ]
            },
            {
                "step": 8,
                "prompt": "The physical, digital, and testimonial chains are established.",
                "options": [
                    {"text": "Compile comprehensive indictment dossier.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Watertight dossier linking laser etch, iPad loop, and recovered stone."},
                    {"text": "Have Harrington verify diamond authenticity with spectrometer.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Confirmed: authentic 120-carat Blue Moon Diamond."},
                    {"text": "Check for outside accomplices.", "killer_delta": 1, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Cynthia acted alone to keep the full $15M payoff."},
                    {"text": "Review Nathan witness testimony.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Drake recalls seeing a woman in emerald satin gown near vault stairs."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Suspects are assembled in Grand Library. The time for guessing is over.",
                "options": [
                    {"text": "Observe Lady Cynthia posture and reactions.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Cynthia trembles and clutches her handbag as police block the door."},
                    {"text": "Re-verify Harrington speech timestamps.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Speech alibi remains 100% verified on news broadcast."},
                    {"text": "Review perfume lab certificate.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Exclusive scent formula registered only to Cynthia."},
                    {"text": "Signal arresting detective to step forward.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Handcuffs ready for formal declaration."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who stole the Blue Moon Diamond?",
                "options": []
            }
        ],
        "true_culprit": "Lady Cynthia Harrington",
        "true_solution": "Lady Cynthia used gemology access to craft a 24.1g replica, looped vault cameras from family iPad, executed swap in emerald gown, and booked private courier.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 03: KIDNAPPING OF THE DIPLOMAT'S DAUGHTER ──
    {
        "id": "case_03",
        "title": "Kidnapping of the Diplomat's Daughter",
        "category": "Kidnapping",
        "difficulty": "Medium",
        "target_or_victim": "Sofia Vance (Age 19)",
        "crime_scene": "Geneva Villa & Gardens",
        "briefing": "Ambassador daughter Sofia Vance was abducted during a storm; a $5M ransom note demanding bearer bonds was left in the villa study.",
        "suspects": [
            {
                "name": "Gabriel Ortiz",
                "role": "Head of Security",
                "public_story": "Patrolled north perimeter gate.",
                "private_secret": "Paid mercenary crew to abduct Sofia for son medical bills.",
                "motive": "$5M ransom split with crew.",
                "alibi": "Patrol log stamped every 20m.",
                "weakness": "Wire shears found in his locker cut garden camera.",
                "relationship": "4-year security chief",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Ambassador Donald Vance",
                "role": "Father & Diplomat",
                "public_story": "On diplomatic call in study.",
                "private_secret": "Under inquiry for missing embassy funds.",
                "motive": "Stage kidnapping to justify lost funds.",
                "alibi": "Call logs with Geneva Ministry.",
                "weakness": "Delayed 4 hours before reporting to police.",
                "relationship": "Father",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Marco Rossi",
                "role": "Chauffeur",
                "public_story": "Serviced limousine in garage.",
                "private_secret": "Helped Sofia plan an escape from her father.",
                "motive": "Romantic devotion to Sofia.",
                "alibi": "Garage cameras confirm presence.",
                "weakness": "Zurich train ticket in pocket.",
                "relationship": "Chauffeur & confidant",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Helena Lind",
                "role": "Private Tutor",
                "public_story": "Left at 20:30 by taxi.",
                "private_secret": "Anti-government activist sympathies.",
                "motive": "Political protest.",
                "alibi": "Taxi driver and phone logs hold.",
                "weakness": "Sent manifesto from villa IP.",
                "relationship": "Tutor",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c3_shears", "title": "Tactical Wire Shears", "category": "Physical", "role": "Critical", "description": "Found in Ortiz locker; blade striations match severed garden camera cable."},
            {"id": "c3_tire", "title": "Muddy Tire Tracks at North Gate", "category": "Circumstantial", "role": "Critical", "description": "Black van tracks entered and exited via north gate unlocked by Ortiz at 21:45."},
            {"id": "c3_radio", "title": "Encrypted Radio Transceiver", "category": "Digital", "role": "Supporting", "description": "Found hidden behind guardhouse preset to mercenary tactical frequency."},
            {"id": "c3_ticket", "title": "Zurich Train Ticket", "category": "Circumstantial", "role": "Red Herring", "description": "Found in Marco pocket; Sofia requested it to run away, but never used it."},
            {"id": "c3_ransom", "title": "Pasted Cut-out Ransom Note", "category": "Physical", "role": "Supporting", "description": "Demands $5M bearer bonds; cut from guardhouse newspapers."}
        ],
        "timeline": [
            {"time": "20:30", "event": "Tutor Helena departs villa by taxi."},
            {"time": "21:00", "event": "Ambassador Vance begins conference call in study."},
            {"time": "21:35", "event": "Garden camera feed severed with shears."},
            {"time": "21:45", "event": "Black extraction van slips through unlocked north gate."},
            {"time": "21:55", "event": "Van departs; Sofia abducted from garden terrace."},
            {"time": "23:30", "event": "Ambassador reports kidnapping to police."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Sofia bedroom window is open to the storm. Rain blows across the carpet. On the study desk lies a $5M ransom note. Where do you start?",
                "options": [
                    {"text": "Inspect severed perimeter security cables.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c3_shears", "feedback": "Clean diagonal cut. Cable was sliced from inside the perimeter."},
                    {"text": "Search muddy perimeter ground around north gate.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c3_tire", "feedback": "Deep delivery van tire tracks entered and exited through north gate."},
                    {"text": "Interrogate Chauffeur Marco Rossi.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c3_ticket", "feedback": "Marco panics as detectives find a train ticket in Sofia name."},
                    {"text": "Analyze ransom note typeface.", "killer_delta": 1, "evidence_score_delta": 7, "unlocked_clue_id": "c3_ransom", "feedback": "Cutout headlines match newspapers in the guardhouse breakroom."}
                ]
            },
            {
                "step": 2,
                "prompt": "Ortiz insists the gate was padlocked. Yet fresh van tracks clearly cross that threshold. What do you investigate?",
                "options": [
                    {"text": "Search guardhouse and security locker room.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c3_radio", "feedback": "Wire shears and encrypted tactical radio found in Ortiz locker!"},
                    {"text": "Confront Ambassador Vance about 4-hour reporting delay.", "killer_delta": 0, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Vance stammers about diplomatic embarrassment and panic."},
                    {"text": "Question Marco Rossi about the train ticket.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Marco weeps: Sofia wanted to flee, but kidnappers took her first."},
                    {"text": "Check Tutor Helena Lind alibi.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Taxi driver and phone company verify Helena was home all night."}
                ]
            },
            {
                "step": 3,
                "prompt": "Signals intelligence monitors the tactical radio frequency recovered from Ortiz locker. It pings near a lake boathouse.",
                "options": [
                    {"text": "Deploy tactical reconnaissance to lake boathouse.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Recon finds the black van! Sofia is inside, guarded by mercenaries!"},
                    {"text": "Confront Gabriel Ortiz with radio evidence.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Ortiz hand twitches toward his holster as his alibi dissolves."},
                    {"text": "Accuse Ambassador Vance of staging kidnapping.", "killer_delta": -2, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Vance collapses in grief, offering all his assets to save her."},
                    {"text": "Arrest Chauffeur Marco Rossi.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Marco offers his life savings to pay ransom; clearly innocent."}
                ]
            },
            {
                "step": 4,
                "prompt": "Tactical police storm the boathouse and rescue Sofia unharmed. Mercenaries in custody talk.",
                "options": [
                    {"text": "Secure captured mercenaries confession.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Commander names Gabriel Ortiz as the inside man who gave gate codes."},
                    {"text": "Interview Sofia Vance about the abduction.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Sofia testifies Ortiz lured her to terrace with a flashlight."},
                    {"text": "Check Ambassador ministerial logs.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Geneva server verifies continuous diplomatic call all night."},
                    {"text": "Examine mercenaries weapons.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Surplus weapons traced to black market contact of Ortiz."}
                ]
            },
            {
                "step": 5,
                "prompt": "Ortiz tries to flee through the service gate. How do you intercept?",
                "options": [
                    {"text": "Order perimeter blockade to arrest Ortiz immediately.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Ortiz captured! Duffel contains fake passports and cash slips."},
                    {"text": "Search Marco quarters again.", "killer_delta": -1, "evidence_score_delta": 3, "unlocked_clue_id": None, "feedback": "Nothing new found. Marco is crying with relief."},
                    {"text": "Question Tutor Helena again.", "killer_delta": 0, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Helena was completely disconnected from the armed kidnappers."},
                    {"text": "Audit Vance bank accounts.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Slush fund was unrelated embassy dispute, not kidnapping."}
                ]
            },
            {
                "step": 6,
                "prompt": "Forensic data dump of Ortiz phone exposes encrypted negotiations.",
                "options": [
                    {"text": "Extract encrypted chat archive on Ortiz phone.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Texts show 60-40 ransom split negotiated by Ortiz for weeks."},
                    {"text": "Interrogate captured van driver.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Driver testifies Ortiz held gate open and pointed out Sofia room."},
                    {"text": "Microscopic analysis of cable shears.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Striations on severed wire match Ortiz shears perfectly."},
                    {"text": "Formally clear Ambassador Vance.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Ambassador is cleared of complicity."}
                ]
            },
            {
                "step": 7,
                "prompt": "Sofia provides sworn deposition naming her captors.",
                "options": [
                    {"text": "Record Sofia deposition with legal counsel.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Sofia identifies Ortiz as the man who signaled the van."},
                    {"text": "Trace Ortiz offshore accounts.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found $50k advance wire from mercenary front account."},
                    {"text": "Verify Marco garage camera timestamps.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Video verifies Marco worked on brakes during entire event."},
                    {"text": "Check weather radar correlation.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Thunderclap masked engine noise of van."}
                ]
            },
            {
                "step": 8,
                "prompt": "The complete indictment is assembled for the Swiss Federal Court.",
                "options": [
                    {"text": "Compile comprehensive indictment dossier.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Case closed: shears, radio, phone logs, accomplice IDs."},
                    {"text": "Formally exonerate Marco and Helena.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both are released and cleared of all charges."},
                    {"text": "Debrief tactical rescue commander.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Rescue operation was executed with zero casualties."},
                    {"text": "Confirm alpine drop coordinates.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "GPS coordinates in Ortiz phone match drop site."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Ortiz is in handcuffs before the magistrate. Final confrontation.",
                "options": [
                    {"text": "Present the shears, radio logs, and Sofia eye-witness ID.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Ortiz breaks down and confesses to organizing the plot."},
                    {"text": "Ask him about Ambassador Vance finances.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Ortiz confirms Vance knew nothing about the plot."},
                    {"text": "Review the timeline for the court.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline matches every movement down to the minute."},
                    {"text": "Prepare final verdict summary.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Evidence dossier is signed and sealed."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who orchestrated the kidnapping of Sofia Vance?",
                "options": []
            }
        ],
        "true_culprit": "Gabriel Ortiz",
        "true_solution": "Security chief Ortiz conspired with mercenaries to pay medical bills. He severed camera wires, unlocked the north gate, lured Sofia to the garden terrace, and coordinated the ransom drop.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 04: THE MIDNIGHT BANK HEIST ──
    {
        "id": "case_04",
        "title": "The Midnight Bank Heist",
        "category": "Robbery",
        "difficulty": "Hard",
        "target_or_victim": "Metropolitan Bank Vault ($40M)",
        "crime_scene": "Subterranean Vault 3, Central Metropolitan Bank",
        "briefing": "30-ton vault door opened cleanly at 2 AM without explosive damage; $40M in cash and gold missing.",
        "suspects": [
            {
                "name": "Martin Becker",
                "role": "Senior Vault Engineer",
                "public_story": "Home in bed 15 miles away.",
                "private_secret": "Coded secret backdoor into vault firmware.",
                "motive": "Facing 10yr sentence for debt fraud.",
                "alibi": "Thermostat timer logged him at home.",
                "weakness": "Motorcycle clocked on highway at 140mph.",
                "relationship": "Designed vault lock",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Victoria Cross",
                "role": "Bank Branch Manager",
                "public_story": "At charity dinner until 23:30.",
                "private_secret": "Approved fraudulent loans under duress.",
                "motive": "Cover up bad loans before federal audit.",
                "alibi": "Valet saw her leave at 23:45.",
                "weakness": "Cloned keycard logged at 01:50.",
                "relationship": "Branch director",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Ray Kowalski",
                "role": "Night Security Guard",
                "public_story": "Patrolled upper floors.",
                "private_secret": "Gambled heavily on sports.",
                "motive": "Paid off to look away.",
                "alibi": "Radio check-ins every 15 mins.",
                "weakness": "$10,000 cash bundle in locker.",
                "relationship": "Night supervisor",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Alonzo Vance",
                "role": "Sewer Contractor",
                "public_story": "Fixing water pipes nearby.",
                "private_secret": "Had blueprints of old bank foundation.",
                "motive": "Sell blueprints to thieves.",
                "alibi": "City work order stamped 01:00.",
                "weakness": "Hydraulic drill bits in truck.",
                "relationship": "City contractor",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c4_backdoor", "title": "Firmware Exploitation Script", "category": "Digital", "role": "Critical", "description": "Vault lock controller received override signed by Martin Becker private key."},
            {"id": "c4_toll", "title": "Highway Toll Camera Image", "category": "Digital", "role": "Critical", "description": "Becker Ducati motorcycle photographed speeding into city at 01:20 and back at 02:50."},
            {"id": "c4_cash", "title": "Locker Cash Bundle", "category": "Physical", "role": "Red Herring", "description": "$10k in Kowalski locker traced to football bet win, not bank money."},
            {"id": "c4_card", "title": "Cloned Manager RFID Badge", "category": "Digital", "role": "Supporting", "description": "Turnstile badge at 01:50 had Victoria Cross telemetry but was a cloned card."},
            {"id": "c4_grate", "title": "Sewer Tunnel Grate", "category": "Physical", "role": "Supporting", "description": "Subway grate untouched with intact rust and cobwebs; heist was above ground."}
        ],
        "timeline": [
            {"time": "01:20", "event": "Becker motorcycle crosses northbound highway toll."},
            {"time": "01:50", "event": "Cloned keycard opens basement turnstile."},
            {"time": "02:05", "event": "Firmware executes override script on vault lock."},
            {"time": "02:12", "event": "30-ton vault door swings open with zero alarm."},
            {"time": "02:15", "event": "Seismic sensor trips as gold pallets are moved."},
            {"time": "02:19", "event": "Police arrive; thieves fled via alley."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "The 30-ton vault door stands open without explosive marks or drill holes. $40M is missing. Where do you begin?",
                "options": [
                    {"text": "Extract firmware logs from vault PLC locking controller.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c4_backdoor", "feedback": "Zero-day override script discovered signed by engineer Martin Becker!"},
                    {"text": "Search guard lockers on basement level.", "killer_delta": 0, "evidence_score_delta": 7, "unlocked_clue_id": "c4_cash", "feedback": "Found $10k cash in Officer Kowalski locker. He insists it was gambling winnings."},
                    {"text": "Inspect municipal sewer grate beneath bank.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c4_grate", "feedback": "Rusted solid with cobwebs. Burglars did not enter through sewer."},
                    {"text": "Question Manager Victoria Cross about keycard use at 01:50.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c4_card", "feedback": "Manager Cross is bewildered; she was asleep and her badge was on her dresser."}
                ]
            },
            {
                "step": 2,
                "prompt": "The keycard was cloned. Meanwhile Becker claims he was in bed 15 miles away. What do you check?",
                "options": [
                    {"text": "Subpoena highway automated license plate readers.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": "c4_toll", "feedback": "Becker Ducati motorcycle was photographed at 01:20 speeding toward the bank!"},
                    {"text": "Examine Victoria Cross home Wi-Fi.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Her cell phone remained connected to home Wi-Fi all night."},
                    {"text": "Interrogate Alonzo Vance about blueprints.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Vance was fixing a ruptured main surrounded by 4 city witnesses."},
                    {"text": "Check Kowalski bookmaker to verify bet.", "killer_delta": 1, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Bookie confirms Kowalski hit a 10-team parlay, explaining the cash."}
                ]
            },
            {
                "step": 3,
                "prompt": "With the motorcycle toll match, detectives search Becker residence.",
                "options": [
                    {"text": "Examine motorcycle engine in Becker garage.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Ducati engine block is still hot to the touch and dripping rain!"},
                    {"text": "Interrogate Victoria Cross about loans.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Bad loans were a financial issue; she had no ability to hack the vault."},
                    {"text": "Search Becker computer partition.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Encrypted partition holds the RFID cloning profile of Cross badge."},
                    {"text": "Review alley camera video.", "killer_delta": 1, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Masked figure in motorcycle leathers wheeling duffel bags at 02:16."}
                ]
            },
            {
                "step": 4,
                "prompt": "A transport van met the motorcyclist at a dockside warehouse. SWAT moves in.",
                "options": [
                    {"text": "Raid dockside warehouse immediately.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "SWAT secures the warehouse. All $40M cash and gold recovered!"},
                    {"text": "Check Becker smart thermostat.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Automated timer script was programmed to fake bedroom presence."},
                    {"text": "Re-interview Officer Kowalski.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Kowalski diagnostic log confirms cloned card triggered turnstile."},
                    {"text": "Check Cross bank balance.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "No sudden deposits or offshore wires found."}
                ]
            },
            {
                "step": 5,
                "prompt": "In the warehouse office, detectives find the control laptop.",
                "options": [
                    {"text": "Forensically mirror the warehouse laptop.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Command prompt reveals exact keystrokes used to open vault at 02:05."},
                    {"text": "Confront Becker with warm motorcycle engine.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Becker puts head in hands as his smart-home alibi collapses."},
                    {"text": "Check bank subcontractor registry.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Becker had sole admin privileges to update vault firmware."},
                    {"text": "Review seismic sensor threshold.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Tripped only when heavy gold bullion struck the dolly."}
                ]
            },
            {
                "step": 6,
                "prompt": "Cyber team traces the RFID skimmer hardware.",
                "options": [
                    {"text": "Trace RFID skimmer serial number.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Purchased online using credit card registered to Martin Becker!"},
                    {"text": "Check Victoria Cross search history.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Only banking regulations and golf vacations in history."},
                    {"text": "Check Kowalski calls.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Zero phone calls between Kowalski and Becker."},
                    {"text": "Examine warehouse lease.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Leased using Becker verified crypto wallet."}
                ]
            },
            {
                "step": 7,
                "prompt": "Defense attorney demands dismissal claiming lack of direct eye-witness.",
                "options": [
                    {"text": "Present cryptographic digital signature match.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Attorney advises Becker to cooperate after seeing private key match."},
                    {"text": "Present toll camera photo of custom helmet.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Photo shows Becker distinctive custom helmet and jacket."},
                    {"text": "Re-interview tellers.", "killer_delta": 0, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Tellers know nothing about the vault technical backend."},
                    {"text": "Count recovered loot.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Full $40M accounted for to the cent."}
                ]
            },
            {
                "step": 8,
                "prompt": "The complete indictment for the federal grand jury is prepared.",
                "options": [
                    {"text": "Compile federal indictment dossier.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Watertight case: toll photos, warm engine, RFID cloner, private key."},
                    {"text": "Exonerate Victoria Cross and Kowalski.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both bank employees cleared of burglary charges."},
                    {"text": "Inspect vault mechanical bolts.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Bolts retracted via software without a scratch."},
                    {"text": "Prepare final confrontation.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Detectives and FBI assemble for the verdict."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Becker sits at the table, his high-tech alibi completely dismantled.",
                "options": [
                    {"text": "Play toll camera video and show cryptographic key match.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Becker confesses to executing the midnight bank heist."},
                    {"text": "Ask him about the sewer grate.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Becker sneers: why crawl through sewer when you have root admin access?"},
                    {"text": "Review timeline for federal judge.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline accounted for minute-by-minute."},
                    {"text": "Prepare final warrant sign-off.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Federal magistrate signs arrest warrant."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who engineered and executed the Midnight Bank Heist?",
                "options": []
            }
        ],
        "true_culprit": "Martin Becker",
        "true_solution": "Senior engineer Becker coded a firmware backdoor, spoofed his smart home presence, rode his Ducati to the bank, used a cloned card, and commanded the vault to open.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 05: THE VANISHING SCIENTIST ──
    {
        "id": "case_05",
        "title": "The Vanishing Scientist",
        "category": "Disappearance",
        "difficulty": "Expert",
        "target_or_victim": "Dr. Aris Thorne",
        "crime_scene": "Helios Labs Cleanroom 4B",
        "briefing": "Physicist vanishes from sealed cleanroom with glasses and coat left on desk; laser array active.",
        "suspects": [
            {
                "name": "Dr. Nadine Vance",
                "role": "Co-Director of Research",
                "public_story": "Compiling grant reports in office 302.",
                "private_secret": "Signed $10M deal with foreign defense contractor.",
                "motive": "Thorne refused to militarize quantum patent.",
                "alibi": "Keycard in Office 302.",
                "weakness": "Sedative requisition signed by her.",
                "relationship": "10-year partner",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Lucas Drake",
                "role": "Senior Lab Tech",
                "public_story": "Cooling maintenance until 23:00.",
                "private_secret": "Selling data secrets to venture capitalists.",
                "motive": "Stole research datasets.",
                "alibi": "Substation log stamped.",
                "weakness": "Stolen hard drive found in backpack.",
                "relationship": "Thorne assistant",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Elena Rostova",
                "role": "Safety Inspector",
                "public_story": "Radiation inspection on sub-level 4.",
                "private_secret": "Falsified radiation safety certificates.",
                "motive": "Thorne threatened to expose violations.",
                "alibi": "Radiation wand sensor log.",
                "weakness": "Hazmat suit missing from decontamination bay.",
                "relationship": "Compliance officer",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "David Chen",
                "role": "Facility Guard",
                "public_story": "At main airlock reception.",
                "private_secret": "Fell asleep between 01:00 and 02:30.",
                "motive": "None.",
                "alibi": "Turnstile log shows presence.",
                "weakness": "Erased 30m of video to hide nap.",
                "relationship": "Security guard",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c5_gas", "title": "Isoflurane Residue in Cleanroom Vent", "category": "Physical", "role": "Critical", "description": "Hospital-grade anesthetic pumped into cleanroom 4B through HVAC ducts."},
            {"id": "c5_cask", "title": "Modified Liquid Nitrogen Cask", "category": "Physical", "role": "Critical", "description": "Cryo-cask wheeled out to loading dock at 01:45 with drilled air holes."},
            {"id": "c5_drive", "title": "Encrypted NVMe Drive", "category": "Digital", "role": "Red Herring", "description": "Stolen physics data drive found on Lucas Drake; data theft, not kidnapping."},
            {"id": "c5_deal", "title": "Defense Contractor NDA & Wire", "category": "Circumstantial", "role": "Supporting", "description": "$10M contract signed by Dr. Nadine Vance promising delivery of Thorne patent."},
            {"id": "c5_lock", "title": "Airlock Override 9901", "category": "Digital", "role": "Supporting", "description": "Cleanroom airlock cycled at 01:30 using director override code 9901."}
        ],
        "timeline": [
            {"time": "21:00", "event": "Dr. Thorne enters sealed cleanroom 4B for experiments."},
            {"time": "23:30", "event": "Tech Lucas Drake copies data drive and leaves."},
            {"time": "01:15", "event": "Isoflurane anesthetic released through cleanroom HVAC."},
            {"time": "01:30", "event": "Airlock cycled with code 9901; Thorne placed in cryo-cask."},
            {"time": "01:45", "event": "Cryo-cask loaded onto medical transport van."},
            {"time": "06:00", "event": "Morning shift discovers empty cleanroom with glasses left behind."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "In the sealed cleanroom, Dr. Thorne lab coat and glasses sit on his desk. Laser array active, but Thorne has vanished. How do you begin?",
                "options": [
                    {"text": "Analyze HVAC system and air duct filters.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c5_gas", "feedback": "Spectrometry detects isoflurane anesthetic residue in ceiling vents!"},
                    {"text": "Inspect loading dock manifests.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c5_cask", "feedback": "Cryo-transport container checked out for urgent transfer at 01:45."},
                    {"text": "Search technician Lucas Drake backpack.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c5_drive", "feedback": "Stolen data drive found. Drake confesses to data theft, but not kidnapping."},
                    {"text": "Review turnstile logs with guard David Chen.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Chen admits he dozed off for an hour around 01:30."}
                ]
            },
            {
                "step": 2,
                "prompt": "Cleanroom airlock records show entry at 01:30 using master override code 9901.",
                "options": [
                    {"text": "Intercept medical transport van with cryo-cask.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": None, "feedback": "Transport intercepted! Dr. Thorne found alive inside, sedated!"},
                    {"text": "Search Dr. Nadine Vance office on 3rd floor.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c5_deal", "feedback": "Found $10M defense contract promising delivery of Thorne patents."},
                    {"text": "Interrogate Inspector Elena Rostova about hazmat suit.", "killer_delta": 0, "evidence_score_delta": 7, "unlocked_clue_id": None, "feedback": "Elena claims her hazmat suit was taken from locker without permission."},
                    {"text": "Examine cooling substation logs.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Drake substation video confirms he was working on pipes until 23:00."}
                ]
            },
            {
                "step": 3,
                "prompt": "Emergency medics revive Dr. Thorne. He recalls a sweet gas hissing from ceiling vents.",
                "options": [
                    {"text": "Trace requisition authorization for isoflurane anesthetic.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Only Co-Director Dr. Nadine Vance had clearance to order isoflurane!"},
                    {"text": "Ask Thorne about disputes with colleagues.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Thorne reveals explosive argument with Vance over selling patents to military."},
                    {"text": "Question Elena Rostova on ventilation dampers.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Elena verifies only director terminal could override ventilation dampers."},
                    {"text": "Search guard David Chen locker.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Energy drinks and magazines; Chen was merely asleep on duty."}
                ]
            },
            {
                "step": 4,
                "prompt": "Detectives trace the medical transport van dispatch orders.",
                "options": [
                    {"text": "Examine transport dispatch paperwork.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Dispatch signed by Dr. Nadine Vance ordering transfer to private airstrip."},
                    {"text": "Examine Dr. Vance computer search history.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Browser history shows charter flight to non-extradition country."},
                    {"text": "Audit technician Drake data sales.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Drake sold datasets to VC firms, totally unaware of abduction."},
                    {"text": "Verify airlock override code registration.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": "c5_lock", "feedback": "Code 9901 belongs exclusively to Dr. Nadine Vance."}
                ]
            },
            {
                "step": 5,
                "prompt": "Dr. Vance attempts to leave Helios Labs via executive parking garage.",
                "options": [
                    {"text": "Detain Dr. Nadine Vance at parking garage gate.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Vance apprehended! Briefcase holds Thorne notebooks and international tickets."},
                    {"text": "Question Inspector Elena Rostova again.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Elena is horrified by military scheme and cooperates fully."},
                    {"text": "Examine HVAC timer logs.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Timer programmed from director console at 22:45."},
                    {"text": "Inspect loading dock video.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dock camera shows woman in hazmat suit wheeling cryo-cask onto lift."}
                ]
            },
            {
                "step": 6,
                "prompt": "Deleted correspondence with defense contractor is recovered from Vance terminal.",
                "options": [
                    {"text": "Restore deleted emails from Vance terminal.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Emails state: 'Thorne will be delivered asleep. He will collaborate abroad.'"},
                    {"text": "Review Thorne blood toxicology report.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Blood confirms isoflurane matching batch ordered by Vance."},
                    {"text": "Interview Drake about patent fights.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Drake confirms Thorne threatened to resign if research was militarized."},
                    {"text": "Exonerate guard David Chen of conspiracy.", "killer_delta": 1, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Chen receives reprimand for sleeping, cleared of crime."}
                ]
            },
            {
                "step": 7,
                "prompt": "Defense contractor legal counsel disavows Vance and turns over wire records.",
                "options": [
                    {"text": "Subpoena contractor wire transfer records.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Records show $2M advance transfer to Vance offshore Cayman account."},
                    {"text": "Examine cryo-cask breathing holes.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Holes drilled with precision and padded with gauze to keep Thorne breathing."},
                    {"text": "Check if Elena Rostova helped wheel cask.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Dock video confirms motorized dolly was operated by a lone individual."},
                    {"text": "Verify cleanroom contamination levels.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Cleanroom was wiped down with alcohol to eliminate fingerprints."}
                ]
            },
            {
                "step": 8,
                "prompt": "The complete high-tech kidnapping docket is compiled.",
                "options": [
                    {"text": "Compile federal indictment dossier.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Complete evidence: isoflurane batch, code 9901, wire transfers, email trail."},
                    {"text": "Return research drives to Dr. Thorne.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dr. Thorne warmly expresses gratitude to investigators."},
                    {"text": "File data theft charges against Drake.", "killer_delta": 1, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Drake faces misdemeanor corporate espionage."},
                    {"text": "Confirm victim recovery.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Physicians confirm Thorne has suffered no long-term harm."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Dr. Vance sits in federal interrogation under complete documentary proof.",
                "options": [
                    {"text": "Present isoflurane requisition, code 9901, and $2M wire transfer.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Vance breaks down: she couldn't let Thorne ruin a $10M windfall."},
                    {"text": "Ask if Drake helped with the abduction.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance scoffs: she used the motorized dolly alone."},
                    {"text": "Review timeline for federal court.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline matches every event down to the second."},
                    {"text": "Prepare final verdict documentation.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Federal prosecution file is sealed and ready."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who orchestrated the disappearance of Dr. Aris Thorne?",
                "options": []
            }
        ],
        "true_culprit": "Dr. Nadine Vance",
        "true_solution": "Dr. Nadine Vance gassed Thorne with isoflurane via the HVAC vents, entered with code 9901, placed him in a modified cryo-cask, and dispatched him in a medical transport for a $10M defense contract.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    }
]
