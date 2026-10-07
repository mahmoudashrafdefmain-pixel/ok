# -*- coding: utf-8 -*-
"""
game/cases_6_to_10.py — Crime Cases 6 through 10 for Investigation Mode.
Case 06: Arson at the Grand Theatre (Arson)
Case 07: Blackmail on Capitol Hill (Blackmail)
Case 08: The Waterfront Smuggling Ring (Smuggling)
Case 09: Corporate Espionage at Apex Biotech (Corporate Crime)
Case 10: The High Stakes Casino Fraud (Fraud)
"""

CASES_6_TO_10 = [
    # ── CASE 06: ARSON AT THE GRAND THEATRE ──
    {
        "id": "case_06",
        "title": "Arson at the Grand Theatre",
        "category": "Arson",
        "difficulty": "Medium",
        "target_or_victim": "The Velvet Opera House & Costumes Collection",
        "crime_scene": "Stage Wing B & Fly Loft, Velvet Opera House",
        "briefing": "At 1:30 AM, an accelerant-fueled blaze destroyed the historic stage and costume warehouse of the Velvet Opera House. Fire marshals found evidence of deliberate incendiary ignition.",
        "suspects": [
            {
                "name": "Sebastian Vane",
                "role": "Stage Director",
                "public_story": "Left the theatre at 11:00 PM after dress rehearsal.",
                "private_secret": "Heavily in debt to theatre loan sharks; bought $2M insurance rider last month.",
                "motive": "$2M insurance payout to clear his debts and start his own company.",
                "alibi": "Claims he was at an all-night diner until 2:00 AM.",
                "weakness": "Diner waitress remembers he stepped out for 50 minutes around 1:00 AM.",
                "relationship": "Lead director for 6 seasons.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Madeline Croft",
                "role": "Lead Soprano",
                "public_story": "Went straight to her hotel suite after rehearsal.",
                "private_secret": "Furious after being replaced by a younger understudy for opening night.",
                "motive": "Spite and vengeance to ruin the premiere.",
                "alibi": "Hotel room card reader shows entry at 11:45 PM.",
                "weakness": "Her silver lighter was found near the costume storage door.",
                "relationship": "Star performer.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Arthur Pendelton",
                "role": "Pyrotechnics Technician",
                "public_story": "Packed flash powders into fireproof locker and locked up.",
                "private_secret": "Fired earlier that afternoon for drinking on duty.",
                "motive": "Retaliation for abrupt termination.",
                "alibi": "Drinking at the Gilded Anchor pub until closing at 2:00 AM.",
                "weakness": "Smelled strongly of sulfur and kerosene when questioned.",
                "relationship": "Former crew technician.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Gideon Sterling",
                "role": "Property Developer",
                "public_story": "Sleeping at his penthouse across the river.",
                "private_secret": "Wants to buy the land to construct luxury high-rise condominiums.",
                "motive": "Force the theatre board into selling the scorched property cheap.",
                "alibi": "Doorman confirmed he was home by 10:30 PM.",
                "weakness": "Sent threatening acquisition letters to the board last week.",
                "relationship": "Commercial rival.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c6_accelerant", "title": "Industrial Methylated Spirit Canister", "category": "Physical", "role": "Critical", "description": "Empty 5-liter metal canister found in stage dumpster with Vane fingerprints on handle."},
            {"id": "c6_diner", "title": "Diner Security Footage", "category": "Digital", "role": "Critical", "description": "Camera shows Sebastian Vane slipping out of diner back door at 1:05 AM and returning at 1:55 AM."},
            {"id": "c6_lighter", "title": "Silver Engraved Lighter", "category": "Physical", "role": "Red Herring", "description": "Madeline Croft lighter; she dropped it during the tense afternoon dressing room row."},
            {"id": "c6_policy", "title": "Expedited Fire Insurance Rider", "category": "Circumstantial", "role": "Supporting", "description": "$2M fire policy added 3 weeks ago naming Sebastian Vane as personal beneficiary."},
            {"id": "c6_lock", "title": "Stage Wing B Padlock", "category": "Physical", "role": "Supporting", "description": "Padlock was opened with a key, not cut or forced; only director and manager had keys."}
        ],
        "timeline": [
            {"time": "23:00", "event": "Dress rehearsal ends; staff departs."},
            {"time": "23:45", "event": "Madeline Croft enters hotel room."},
            {"time": "00:45", "event": "Sebastian Vane orders coffee at 24-hr diner."},
            {"time": "01:05", "event": "Vane slips out diner back exit."},
            {"time": "01:22", "event": "Wing B unlocked with director key; methylated spirits poured."},
            {"time": "01:30", "event": "Fire alarms trigger across theatre district."},
            {"time": "01:55", "event": "Vane returns to diner booth smelling of smoke."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Smoldering ruins of stage wing B fill the air with acrid chemical fumes. Fire marshals indicate two distinct ignition points. How do you investigate?",
                "options": [
                    {"text": "Search stage wing dumpsters and alleyways for containers.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c6_accelerant", "feedback": "Recovered empty 5-liter canister of industrial methylated spirits with latent prints!"},
                    {"text": "Examine scorched costume rack area for igniters.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c6_lighter", "feedback": "Found silver monogrammed lighter belonging to soprano Madeline Croft."},
                    {"text": "Inspect stage wing exterior entrance lock.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c6_lock", "feedback": "Padlock was opened cleanly with a key; zero signs of pry marks."},
                    {"text": "Interrogate pyrotechnician Arthur Pendelton.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Arthur admits he was angry about being fired, but claims he was at the pub."}
                ]
            },
            {
                "step": 2,
                "prompt": "The methylated spirits canister carries partial thumbprints. Sebastian Vane claims he was at the diner all night.",
                "options": [
                    {"text": "Subpoena the 24-hour diner interior and parking lot cameras.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c6_diner", "feedback": "Video shows Vane slipped out the rear exit at 1:05 AM and sneaked back at 1:55 AM!"},
                    {"text": "Interrogate Madeline Croft about her silver lighter.", "killer_delta": -1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Madeline explains she flung the lighter in rage during the afternoon row; cleaning staff saw it on the floor."},
                    {"text": "Audit theatre corporate financial documents.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c6_policy", "feedback": "Discovered $2M insurance rider taken out by Vane naming himself sole beneficiary."},
                    {"text": "Check pub surveillance for Arthur Pendelton.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Pub bartender confirms Arthur was sitting on a barstool drinking pints from 11:30 PM to 2:00 AM."}
                ]
            },
            {
                "step": 3,
                "prompt": "Fingerprint technicians match the right thumbprint on the accelerant canister.",
                "options": [
                    {"text": "Run the latent print through the city criminal database.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Direct match to Director Sebastian Vane!"},
                    {"text": "Question developer Gideon Sterling on land bids.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Sterling made legal offers; his doorman confirms he never left his apartment."},
                    {"text": "Check Madeline Croft hotel keycard logs.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Hotel electronic lock shows Madeline did not exit her room after 11:45 PM."},
                    {"text": "Inspect Arthur Pendelton work jacket for chemical traces.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Arthur sulfur smell was from stage flash powder earlier that morning, not accelerant."}
                ]
            },
            {
                "step": 4,
                "prompt": "The diner waitress gives a sworn statement: when Vane returned at 1:55 AM, his wool overcoat smelled of smoke.",
                "options": [
                    {"text": "Seize Sebastian Vane wool overcoat from his apartment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Forensic lab detects microscopic soot and methylated spirit traces in the wool fabric!"},
                    {"text": "Confront Vane with the diner rear camera footage.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Vance turns white, stammering that he just went out for a breath of fresh air."},
                    {"text": "Review property development zoning records.", "killer_delta": 0, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Zoning permits were months away; Sterling had no rush to burn the theatre."},
                    {"text": "Examine theatre stage fire sprinkler logs.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Sprinkler valve was manually shut off using the director emergency key."}
                ]
            },
            {
                "step": 5,
                "prompt": "Hardware store records in the south district show a purchase of 5-liter methylated spirit cans.",
                "options": [
                    {"text": "Pull receipt and credit card records from the south hardware store.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Purchased yesterday at 4:00 PM using Sebastian Vane personal Visa card!"},
                    {"text": "Interrogate Madeline Croft understudy.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Understudy was rehearsing lines with the vocal coach until midnight."},
                    {"text": "Examine Arthur Pendelton toolbox.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Toolbox contains theatrical spark igniters, but no liquid fuels."},
                    {"text": "Audit Vane personal bank accounts.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found multiple overdue debt notices totaling $350,000 to dangerous creditors."}
                ]
            },
            {
                "step": 6,
                "prompt": "The insurance underwriter confirms Vane filed a preliminary claim at 8:00 AM, just hours after the fire.",
                "options": [
                    {"text": "Subpoena insurance claim filing timestamps and audio recording.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Vane called the insurance claim hotline sounding calm, before fire investigators had even finished."},
                    {"text": "Question Gideon Sterling regarding buyout bids.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling withdraws his bid, refusing to buy a contaminated arson site."},
                    {"text": "Check Madeline Croft phone text history.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Texts show she was crying to her mother about losing the lead role."},
                    {"text": "Verify the stage wing padlock keys.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Vane key ring carries the exact brass key that opened Wing B."}
                ]
            },
            {
                "step": 7,
                "prompt": "Digital forensics reconstructs Vane cell phone GPS during the 50-minute diner absence.",
                "options": [
                    {"text": "Overlay phone GPS coordinates with the theatre alleyway.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "GPS tracks Vane walking 3 blocks to the theatre, entering Wing B at 1:22 AM, and returning."},
                    {"text": "Check Arthur Pendelton phone location.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Phone connected to pub Wi-Fi continuously all evening."},
                    {"text": "Re-interview the stage manager.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Stage manager confirms only Vane knew the manual sprinkler shutoff valve location."},
                    {"text": "Testify regarding the overcoat chemical traces.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Accelerant on overcoat is a 100% molecular match to the canister residue."}
                ]
            },
            {
                "step": 8,
                "prompt": "The case against Sebastian Vane is complete across all four pillars: means, motive, opportunity, and forensic evidence.",
                "options": [
                    {"text": "Compile comprehensive arson indictment docket.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Watertight docket: canister fingerprints, Visa receipt, GPS track, diner video, overcoat soot."},
                    {"text": "Formally clear Madeline Croft and Arthur Pendelton.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both innocent parties are officially cleared of all arson allegations."},
                    {"text": "Brief the fire marshal and district attorney.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "District attorney approves immediate grand jury submission."},
                    {"text": "Verify estimated property destruction value.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Total damages exceed $1.8M in historic costumes and stage machinery."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Vane is brought into the interrogation room. One final confrontation will shatter his defense.",
                "options": [
                    {"text": "Confront Vane with the hardware store Visa receipt, GPS track, and overcoat soot match.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Vane collapses into sobs, confessing: 'The loan sharks gave me two days. The insurance was my only way out!'"},
                    {"text": "Ask him if Madeline Croft helped.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Vane scoffs: 'Madeline had nothing to do with it; I planned it alone.'"},
                    {"text": "Review timeline for the court record.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Minute-by-minute timeline leaves zero doubt of guilt."},
                    {"text": "Seal the formal investigation report.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Case file signed and ready for verdict."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who committed the arson that destroyed the Velvet Opera House?",
                "options": []
            }
        ],
        "true_culprit": "Sebastian Vane",
        "true_solution": "Director Sebastian Vane was drowning in $350k debt to loan sharks. He bought a $2M fire insurance policy, slipped out of an alibi diner, used his master key to unlock Wing B, shut off the sprinklers, doused the costumes in methylated spirits, and ignited the blaze before returning to the diner.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 07: BLACKMAIL ON CAPITOL HILL ──
    {
        "id": "case_07",
        "title": "Blackmail on Capitol Hill",
        "category": "Blackmail",
        "difficulty": "Hard",
        "target_or_victim": "Senator Donald Vance (Senate Armed Services)",
        "crime_scene": "The Russell Senate Office Suite 312",
        "briefing": "Senator Vance received a sealed black envelope containing classified defense voting kickback documents and a demand for $1.5M in cryptocurrency, threatening release before tomorrow's committee vote.",
        "suspects": [
            {
                "name": "Chloe Davenport",
                "role": "Campaign Manager",
                "public_story": "Drafted press releases at campaign headquarters until 10:00 PM.",
                "private_secret": "Siphoned campaign funds into bad crypto margin trading; deeply in debt.",
                "motive": "Extract $1.5M to cover up her embezzlement before quarterly audit.",
                "alibi": "Badge log at headquarters terminal.",
                "weakness": "The encrypted Tor relay node used to send ransom email was hosted on her personal home server.",
                "relationship": "Trusted campaign chief for 4 years.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Julian Price",
                "role": "Investigative Journalist",
                "public_story": "Working at the Capitol press gallery.",
                "private_secret": "Possesses a leaked copy of the kickback ledger.",
                "motive": "Career-defining scoop to destroy the Senator.",
                "alibi": "Published live articles on news portal all evening.",
                "weakness": "Visited Vance office at 4:00 PM demanding an interview.",
                "relationship": "Hostile press adversary.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "Harrison Cole",
                "role": "Chief Legislative Aide",
                "public_story": "Organized briefing binders in the inner committee room.",
                "private_secret": "Passed over for Chief of Staff promotion last month.",
                "motive": "Bitterness and desire to humiliate Vance.",
                "alibi": "Camera confirms presence in committee room until 9:00 PM.",
                "weakness": "Has physical access to the Senator private safe.",
                "relationship": "Staffer for 3 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Victoria Sterling",
                "role": "Defense Contractor Lobbyist",
                "public_story": "Attending Capitol Hill fundraisers.",
                "private_secret": "Paid the original kickbacks that were documented in the ledger.",
                "motive": "Prevent exposure of her defense firm bribery network.",
                "alibi": "Dozens of lobbyists saw her at the Senate Club.",
                "weakness": "Threatened to cut Vance campaign contributions yesterday.",
                "relationship": "Financial backer.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c7_tor", "title": "Home Tor Relay Server Logs", "category": "Digital", "role": "Critical", "description": "The blackmail ransom demand was routed through a Tor exit node operating on Chloe Davenport IP address."},
            {"id": "c7_envelope", "title": "Watermarked Stationery Envelope", "category": "Physical", "role": "Critical", "description": "The black envelope matches bespoke heavyweight cardstock ordered by Davenport campaign office."},
            {"id": "c7_ledger", "title": "Journalist Leaked Notes", "category": "Physical", "role": "Red Herring", "description": "Julian Price notebook contains notes on kickbacks, but zero extortion demands; pure journalism."},
            {"id": "c7_crypto", "title": "Monero Wallet Creation Timestamp", "category": "Digital", "role": "Supporting", "description": "Extortion Monero wallet created yesterday from a browser with Davenport personal Google account cached."},
            {"id": "c7_safe", "title": "Senator Safe Access Log", "category": "Digital", "role": "Supporting", "description": "Safe opened with master code at 6:30 PM; only Vance, Davenport, and Cole knew code."}
        ],
        "timeline": [
            {"time": "16:00", "event": "Journalist Julian Price demands on-the-record interview."},
            {"time": "18:30", "event": "Senator private safe opened using master staff code."},
            {"time": "20:00", "event": "Blackmail Monero wallet created via Tor browser."},
            {"time": "21:15", "event": "Black envelope slipped under Senator inner office door."},
            {"time": "22:00", "event": "Senator Vance discovers envelope and contacts federal investigators."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Inside the Senator suite, the black envelope sits on his leather desk. Inside: classified kickback ledgers and a Monero ransom demand. How do you begin?",
                "options": [
                    {"text": "Analyze the black cardstock envelope for paper fibers and watermarks.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c7_envelope", "feedback": "Bespoke linen watermark matches stationery ordered by Chloe Davenport campaign HQ."},
                    {"text": "Trace the Monero cryptocurrency deposit address on blockchain.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c7_crypto", "feedback": "Wallet created yesterday. IP trace hints at a local Washington residential connection."},
                    {"text": "Interrogate journalist Julian Price about his leaks.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c7_ledger", "feedback": "Price displays his notebook: he is investigating corruption, not demanding money."},
                    {"text": "Inspect safe digital audit log in Senator office.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c7_safe", "feedback": "Safe opened at 6:30 PM with staff code shared by Vance, Davenport, and Cole."}
                ]
            },
            {
                "step": 2,
                "prompt": "Cyber forensics traces the ransom email routing through the Tor network.",
                "options": [
                    {"text": "Subpoena ISP logs for Tor bridge and relay nodes in DC metro area.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c7_tor", "feedback": "The Tor entry node was hosted directly on Chloe Davenport home gigabit fiber IP address!"},
                    {"text": "Interrogate Legislative Aide Harrison Cole about the safe code.", "killer_delta": -1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Cole admits he resented Vance, but his committee room alibi is verified by 3 staffers."},
                    {"text": "Confront Lobbyist Victoria Sterling about kickbacks.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Sterling is terrified of exposure; she wants the ledger buried, not publicized."},
                    {"text": "Check Senator Vance personal secretary.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Secretary was on vacation in Florida; alibi 100% corroborated."}
                ]
            },
            {
                "step": 3,
                "prompt": "Federal agents execute a search warrant on Chloe Davenport apartment.",
                "options": [
                    {"text": "Inspect Davenport home server and desktop computer.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Desktop browser history contains active sessions for the exact Monero wallet and Tor server!"},
                    {"text": "Check Davenport desk for stationery supplies.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found a box of identical black linen envelopes with matching batch number."},
                    {"text": "Interrogate Harrison Cole on financial debts.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Cole has a modest savings account and zero risky investments."},
                    {"text": "Review Julian Price news draft.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Price planned to publish his story next Tuesday via mainstream media."}
                ]
            },
            {
                "step": 4,
                "prompt": "Forensic audit of campaign accounts reveals Davenport siphoned $800,000.",
                "options": [
                    {"text": "Confront Chloe Davenport with the $800k embezzlement audit.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Davenport stutters, claiming she lost the funds on crypto margin leverage and needed $1.5M to cover it."},
                    {"text": "Check if Victoria Sterling funded the shortfall.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling made no transfers to Davenport personal accounts."},
                    {"text": "Review Capitol building corridor CCTV.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Corridor camera shows a woman matching Davenport coat slipping letter under door at 21:15."},
                    {"text": "Examine Senator Vance schedule.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Vance was speaking at a dinner gala at 21:15, confirming he received the letter."}
                ]
            },
            {
                "step": 5,
                "prompt": "Davenport attorney claims the Tor node was an open relay used by an unknown third party.",
                "options": [
                    {"text": "Examine device MAC address and browser cookie authentication.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "The Tor browser session used Davenport hardware MAC address and personal Google login token!"},
                    {"text": "Question Harrison Cole regarding hallway sightings.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Cole saw Davenport near the Senator suite at 21:00 carrying a manila folder."},
                    {"text": "Examine Julian Price phone records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Zero calls between Price and the extortion wallet operator."},
                    {"text": "Check Lobbyist Sterling bank accounts.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling bribery trail is referred to federal public integrity section."}
                ]
            },
            {
                "step": 6,
                "prompt": "A draft of the blackmail note was recovered from Davenport cloud storage recycle bin.",
                "options": [
                    {"text": "Restore deleted Word documents from Davenport cloud account.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Recovered 'Demand_Vance.docx' with metadata matching Davenport user profile created yesterday!"},
                    {"text": "Interview Senator Vance on campaign oversight.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance admits he gave Davenport total unmonitored financial authority."},
                    {"text": "Examine the Monero wallet seed phrase.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Seed phrase recovery words found written in Davenport daily planner."},
                    {"text": "Clear Harrison Cole formally.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Harrison Cole is officially exonerated of all extortion charges."}
                ]
            },
            {
                "step": 7,
                "prompt": "The Senator safe keypad was forensically dusted for latent prints.",
                "options": [
                    {"text": "Compare safe keypad prints to Chloe Davenport fingers.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Davenport index finger print found on keys 6, 8, 3, and Enter at 18:30."},
                    {"text": "Check Julian Price fingerprints.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Price never had access to the safe or inner suite."},
                    {"text": "Review campaign committee audit timeline.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The quarterly audit was scheduled for tomorrow morning at 9:00 AM."},
                    {"text": "Confirm the Monero wallet balance.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Zero transactions completed; extortion stopped in its tracks."}
                ]
            },
            {
                "step": 8,
                "prompt": "Every link in the chain is forged: envelope batch, cloud draft, MAC address, safe keypad print, and urgent audit deadline.",
                "options": [
                    {"text": "Assemble the federal extortion and wire fraud indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Complete docket: digital metadata, seed phrase, keypad prints, and envelope paper match."},
                    {"text": "Exonerate journalist Julian Price of criminal extortion.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Price is cleared to pursue his journalistic reporting legally."},
                    {"text": "Brief Capitol Police Chief and US Attorney.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Federal magistrate approves immediate formal charging."},
                    {"text": "Secure Senator Vance classified documents.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Classified papers returned to Senate classified document repository."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Davenport sits with her defense lawyer. The proof is irrefutable.",
                "options": [
                    {"text": "Present the cloud draft metadata, seed phrase in her planner, and safe keypad prints.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Her lawyer turns to Davenport and says: 'Take the plea deal. They have you cold.' Davenport nods and confesses."},
                    {"text": "Ask if Senator Vance knew about the crypto losses.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Davenport admits Vance was completely in the dark until the envelope appeared."},
                    {"text": "Review timeline for federal court.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline matches every movement between 16:00 and 22:00."},
                    {"text": "Finalize case documentation.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Official case docket signed and ready."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who orchestrated the blackmail and extortion against Senator Vance?",
                "options": []
            }
        ],
        "true_culprit": "Chloe Davenport",
        "true_solution": "Campaign manager Chloe Davenport embezzled $800k in campaign funds for crypto margin bets. Facing a morning audit, she opened the Senator safe at 18:30, stole the kickback ledger, generated a Monero extortion wallet on her home Tor node, slipped the demand under his door, and demanded $1.5M to cover her theft.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 08: THE WATERFRONT SMUGGLING RING ──
    {
        "id": "case_08",
        "title": "The Waterfront Smuggling Ring",
        "category": "Smuggling",
        "difficulty": "Hard",
        "target_or_victim": "Pier 42 Freight Terminal ($30M Contraband Weapons & Relics)",
        "crime_scene": "Container Yard Berth 7, Pier 42 Harbor",
        "briefing": "Customs agents raided container 409 at Pier 42, discovering military-grade missile guidance systems and plundered antiquities. The shipping manifest had been forged with master port clearance.",
        "suspects": [
            {
                "name": "Captain Gregory Drake",
                "role": "Harbor Port Master",
                "public_story": "Supervised crane operations from the control tower.",
                "private_secret": "Received $500,000 per shipment from an international arms syndicate.",
                "motive": "Multimillion-dollar syndicate kickbacks for greenlighting containers.",
                "alibi": "Tower terminal logged his user account all evening.",
                "weakness": "The digital greenlight signature was authenticated with his private biometric token.",
                "relationship": "Port Master for 12 years.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Dmitri Volkov",
                "role": "Freight Cargo Broker",
                "public_story": "Filed customs paperwork from his dockside office.",
                "private_secret": "Under heavy financial pressure from Eastern European creditors.",
                "motive": "Earn brokerage fees on off-the-books freight.",
                "alibi": "Office camera showed him at his desk reviewing invoices.",
                "weakness": "His signature was on the preliminary bill of lading.",
                "relationship": "Cargo broker.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Frankie 'The Hook' Morales",
                "role": "Longshoremen Union Boss",
                "public_story": "Overseeing union shift change in the break hall.",
                "private_secret": "Takes bribes to look the other way when unvetted dockworkers load cargo.",
                "motive": "Union protection payoffs.",
                "alibi": "Thirty dockworkers testify he was in the break hall at 11:00 PM.",
                "weakness": "Found with $20,000 cash envelope in his jacket.",
                "relationship": "Dock labor chief.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Inspector Sarah Chen",
                "role": "Federal Customs Inspector",
                "public_story": "Conducting random cargo x-rays on Berth 3.",
                "private_secret": "Investigating Drake independently for 6 months.",
                "motive": "Bust the smuggling syndicate.",
                "alibi": "Scanner console records confirm her scanning Berth 3.",
                "weakness": "Disobeyed orders to wait for federal backup.",
                "relationship": "Lead investigator.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c8_token", "title": "Biometric Port Master Token", "category": "Digital", "role": "Critical", "description": "Manifest 8812 was cleared into the country using Captain Drake physical YubiKey hardware token."},
            {"id": "c8_ledger", "title": "Offshore Kickback Ledger", "category": "Digital", "role": "Critical", "description": "Encrypted ledger on Drake yacht records $3.2M in wire payments from the arms cartel."},
            {"id": "c8_cash", "title": "Union Payoff Envelope", "category": "Physical", "role": "Red Herring", "description": "$20k in Morales jacket traced to standard union kickbacks, not the weapons syndicate."},
            {"id": "c8_manifest", "title": "Forged Agricultural Manifest", "category": "Physical", "role": "Supporting", "description": "Container 409 was falsely labeled 'Refrigerated Citrus Fruit' from Valencia."},
            {"id": "c8_crane", "title": "Gantry Crane Automated Log", "category": "Digital", "role": "Supporting", "description": "Crane 4 bypassed standard x-ray lane at 23:15 by direct manual override from the tower."}
        ],
        "timeline": [
            {"time": "21:30", "event": "Container ship 'Neptune Star' docks at Berth 7."},
            {"time": "22:45", "event": "Manifest 8812 greenlit using Port Master biometric token."},
            {"time": "23:15", "event": "Gantry Crane 4 manually overrides automated inspection route."},
            {"time": "23:45", "event": "Customs Inspector Chen intercepts container 409 at the gate."},
            {"time": "00:15", "event": "Federal raid team secures weapons and seals perimeter."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Container 409 stands cracked open under harbor floodlights, revealing missile guidance chips inside hollowed crates. How do you launch the investigation?",
                "options": [
                    {"text": "Extract digital authentication logs for manifest 8812 from the port mainframe.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c8_token", "feedback": "Manifest was approved using Captain Gregory Drake personal biometric hardware key!"},
                    {"text": "Interrogate Union Boss Frankie Morales about cargo loading.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c8_cash", "feedback": "Morales has $20k cash in his pocket, but insists it was standard local dock payoffs."},
                    {"text": "Inspect the shipping bill of lading for origin paperwork.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c8_manifest", "feedback": "Cargo falsely marked 'Citrus Fruit', but broker Dmitri Volkov claims he was duped by foreign shippers."},
                    {"text": "Check Gantry Crane automated movement tracking.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c8_crane", "feedback": "Crane 4 bypassed the x-ray bay via a direct manual override command from the tower."}
                ]
            },
            {
                "step": 2,
                "prompt": "Tower logs prove the crane override command came from the Port Master station at 23:15.",
                "options": [
                    {"text": "Search Captain Drake private yacht moored at the harbor marina.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": "c8_ledger", "feedback": "Concealed safe on yacht holds satellite phone and an encrypted ledger showing $3.2M in cartel wires!"},
                    {"text": "Interrogate cargo broker Dmitri Volkov about shipping routes.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Volkov confesses he was paid $5k to file paperwork blindly, but didn't know about weapons."},
                    {"text": "Check Customs Inspector Sarah Chen badge records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Chen has spent months tracking Drake; her rogue raid is what caught the container."},
                    {"text": "Search the longshoremen breakroom for weapons.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Only card games and thermoses found; the dockers were not part of the arms ring."}
                ]
            },
            {
                "step": 3,
                "prompt": "Captain Drake asserts an unauthorized hacker cloned his biometric key token.",
                "options": [
                    {"text": "Analyze the hardware key physical security logs.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "The hardware token requires a physical fingerprint touch on the sensor; cloning is physically impossible!"},
                    {"text": "Subpoena Dmitri Volkov bank accounts.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Volkov accounts show minor brokerage deposits, consistent with low-level paperwork handling."},
                    {"text": "Question Frankie Morales on tower access.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Morales confirms only Drake and his direct deputies have keycards to the crane tower."},
                    {"text": "Review Inspector Chen surveillance photos.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Photos show Drake meeting with known cartel arms traffickers at a marina bar last Thursday."}
                ]
            },
            {
                "step": 4,
                "prompt": "Federal cyber intelligence decrypts the satellite phone found aboard Drake yacht.",
                "options": [
                    {"text": "Read the decrypted messages on the satellite phone.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Messages read: 'Berth 7 is clear. Crane 4 will skip inspection. Wire the final $500k to Zurich.'"},
                    {"text": "Interrogate the ship captain of the 'Neptune Star'.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Ship captain claims he only follows port docking signals from Drake tower."},
                    {"text": "Check if Morales knew about the missile guidance chips.", "killer_delta": -1, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Morales is visibly shocked; union dockworkers refuse to handle illegal military weapons."},
                    {"text": "Audit the harbor authority budget.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Harbor budget shows no irregularities; payments were completely off-the-books."}
                ]
            },
            {
                "step": 5,
                "prompt": "Drake prepares to cast off his yacht under cover of the predawn fog.",
                "options": [
                    {"text": "Deploy Coast Guard cutters to surround Drake yacht.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Coast Guard boards the yacht. Drake is detained at the helm with $100k cash and fake Greek passports!"},
                    {"text": "Question cargo broker Volkov again.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Volkov signs a full cooperation agreement with federal prosecutors."},
                    {"text": "Inspect the crane control console for prints.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Drake fingerprints found on the manual override toggle switch."},
                    {"text": "Check Berth 7 container seals.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Container seals were counterfeit duplicates supplied to bypass gate barcode scans."}
                ]
            },
            {
                "step": 6,
                "prompt": "Swiss banking authorities confirm the $3.2M wire transfers into Drake numbered account.",
                "options": [
                    {"text": "Verify Swiss bank account ownership and wire origin.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Account registered to a shell company in Drake name, funded by overseas arms trafficking syndicates."},
                    {"text": "Check if Inspector Chen had unauthorized communications.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Inspector Chen file is spotless; she receives commendation for initiating the bust."},
                    {"text": "Review longshoremen shift logs.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Shift logs confirm dockers simply loaded containers as directed by crane signals."},
                    {"text": "Catalogue the military equipment.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dozens of missile guidance gyroscopes and radar jamming units recovered."}
                ]
            },
            {
                "step": 7,
                "prompt": "Drake defense lawyer argues the satellite phone was planted aboard the yacht.",
                "options": [
                    {"text": "Present DNA and fingerprint swab from the satellite phone keypad.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Drake DNA and prints coat the power button, antenna, and phone screen."},
                    {"text": "Interview Dmitri Volkov on who ordered the Valencia cargo.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Volkov testifies Drake personally instructed him to create the 'Citrus' shipping label."},
                    {"text": "Check union boss Morales for weapon ties.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Morales cash is confiscated for tax evasion, but he is cleared of arms trafficking."},
                    {"text": "Review maritime radar logs.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The ship docked at the exact minute Drake authorized the override."}
                ]
            },
            {
                "step": 8,
                "prompt": "The case is airtight: biometric token, crane override prints, Swiss account, satellite texts, and escape attempt.",
                "options": [
                    {"text": "Draft the federal arms trafficking and racketeering indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Comprehensive RICO indictment finalized for federal prosecution."},
                    {"text": "Formally clear the longshoremen union of international trafficking.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Union cleared of conspiracy; dock resumes normal operations."},
                    {"text": "Formally commend Customs Inspector Sarah Chen.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Chen is promoted to Regional Customs Enforcement Director."},
                    {"text": "Secure container 409 in federal military armory.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Contraband weapons locked in military vault."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Captain Drake sits in federal detention, his high-seas escape crushed. Prepare the final accusation.",
                "options": [
                    {"text": "Confront Drake with the Swiss accounts, biometric hardware proof, and DNA on the satellite phone.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Drake slumps in his chair: 'I served this port 12 years for government peanuts. The cartel made me rich.'"},
                    {"text": "Ask if broker Volkov received a share.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Drake laughs: 'Volkov is an idiot who worked for pocket change.'"},
                    {"text": "Review timeline for federal court.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The timeline proves continuous orchestration from docking to crane override."},
                    {"text": "Seal the formal investigation docket.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The docket is closed and ready for the final verdict."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who was the corrupt inside mastermind of the Waterfront Smuggling Ring?",
                "options": []
            }
        ],
        "true_culprit": "Captain Gregory Drake",
        "true_solution": "Port Master Gregory Drake took $3.2M in syndicate bribes to smuggle military electronics. He used his biometric YubiKey to greenlight the forged citrus manifest, manually overrode the crane to skip x-ray scanning, coordinated via satellite phone, and attempted to flee on his yacht with $100k cash and fake passports.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 09: CORPORATE ESPIONAGE AT APEX BIOTECH ──
    {
        "id": "case_09",
        "title": "Corporate Espionage at Apex Biotech",
        "category": "Corporate Crime",
        "difficulty": "Hard",
        "target_or_victim": "Gene Therapy Formula X (Valued at $1.2 Billion)",
        "crime_scene": "Vault Server Room 7, Apex Biotech HQ",
        "briefing": "The proprietary genetic sequence for Formula X was downloaded onto an unauthorized flash drive and erased from the cloud backup. A rival pharmaceutical conglomerate was preparing to patent it tomorrow morning.",
        "suspects": [
            {
                "name": "Dr. Linus Finch",
                "role": "Lead Biochemist",
                "public_story": "Was calibrating gene synthesizers on sub-level 2 until midnight.",
                "private_secret": "Passed over for Chief Science Officer; accepted $5M offer from rival PharmaCorp.",
                "motive": "$5M payout and promised CSO title at rival corporation.",
                "alibi": "Gene synthesizer automated job ran under his account.",
                "weakness": "His personal encrypted thumb drive was found hidden in his hollowed desktop dictionary.",
                "relationship": "Co-inventor of Formula X.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Cassandra Croft",
                "role": "CEO & Founder",
                "public_story": "Hosting investor dinner in downtown hotel.",
                "private_secret": "Apex Biotech is burning cash rapidly and facing insolvency in 6 months.",
                "motive": "Stage intellectual theft to claim insurance or blame failure on espionage.",
                "alibi": "Dozens of venture capitalists saw her at the dinner until 11:30 PM.",
                "weakness": "Her executive password was used to access the cloud backup portal.",
                "relationship": "Company head.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Travis Vance",
                "role": "IT Infrastructure Director",
                "public_story": "Performing scheduled server maintenance from home.",
                "private_secret": "Day-trading tech stocks using inside knowledge.",
                "motive": "Short Apex stock before the theft becomes public.",
                "alibi": "VPN logs show connection from his home IP address.",
                "weakness": "Disabled server room intrusion cameras for 'firmware upgrade'.",
                "relationship": "IT Director for 5 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Nadia Ray",
                "role": "Patent Attorney",
                "public_story": "Filing domestic regulatory patent forms at her office.",
                "private_secret": "Had secret job interview with PharmaCorp legal team last month.",
                "motive": "Steal patent claims to curry favor with new employer.",
                "alibi": "Electronic timestamps on USPTO patent filing portal.",
                "weakness": "Carrying printouts of Formula X chemical structures in briefcase.",
                "relationship": "Legal counsel.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c9_drive", "title": "Encrypted Corsair USB Drive", "category": "Physical", "role": "Critical", "description": "Recovered from Finch office dictionary; contains the exact decrypted Formula X genome files."},
            {"id": "c9_keylogger", "title": "Hardware Keylogger Dongle", "category": "Physical", "role": "Critical", "description": "Found plugged into CEO Cassandra Croft keyboard, which Finch used to capture her cloud password."},
            {"id": "c9_short", "title": "Stock Shorting Order", "category": "Digital", "role": "Red Herring", "description": "Travis Vance placed short options on Apex; insider trading, but he didn't download the formula."},
            {"id": "c9_contract", "title": "PharmaCorp Employment Contract", "category": "Circumstantial", "role": "Supporting", "description": "Signed draft offering Finch $5M signing bonus and CSO position upon patent delivery."},
            {"id": "c9_vpn", "title": "Server Room Air Gap Breach", "category": "Digital", "role": "Supporting", "description": "The genomic vault was air-gapped; it could only be downloaded via physical USB insertion."}
        ],
        "timeline": [
            {"time": "19:00", "event": "CEO Cassandra Croft departs for investor dinner."},
            {"time": "21:30", "event": "IT Director Vance disables server cameras for maintenance."},
            {"time": "22:15", "event": "Hardware keylogger records Croft cloud master password."},
            {"time": "22:40", "event": "Physical USB inserted into air-gapped genomic server in Room 7."},
            {"time": "23:05", "event": "Formula X erased from main storage and cloud backup wiped."},
            {"time": "08:00", "event": "Lab researchers discover missing project files."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Server Room 7 is freezing and silent. The air-gapped genomic mainframe was wiped clean at 23:05. How do you launch the inquiry?",
                "options": [
                    {"text": "Inspect the physical USB ports and hardware on the air-gapped server.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c9_vpn", "feedback": "System logs confirm a physical USB thumb drive was inserted at 22:40. It was an inside job!"},
                    {"text": "Examine CEO Cassandra Croft office workstation.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c9_keylogger", "feedback": "A covert hardware USB keylogger is found nestled between her keyboard cable and PC tower!"},
                    {"text": "Subpoena IT Director Travis Vance financial trading accounts.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c9_short", "feedback": "Found suspicious put options on Apex stock; Vance was insider trading, but was he the thief?"},
                    {"text": "Search Patent Attorney Nadia Ray briefcase.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Contains public regulatory forms; Nadia insists she was preparing patent filings."}
                ]
            },
            {
                "step": 2,
                "prompt": "The keylogger on the CEO computer captured her cloud master credentials at 22:15. Who was on the executive floor?",
                "options": [
                    {"text": "Execute a search warrant on Dr. Linus Finch office and private lab.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": "c9_drive", "feedback": "Behind his bookshelf in a hollowed English dictionary: an encrypted Corsair flash drive!"},
                    {"text": "Confront CEO Cassandra Croft regarding the cloud deletion password.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Croft is furious and terrified; she had no idea a keylogger was siphoning her passwords."},
                    {"text": "Interrogate IT Director Vance about the disabled cameras.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Vance confesses he disabled cameras to take a nap during his shift, terrified of losing his job."},
                    {"text": "Check Nadia Ray interview records with PharmaCorp.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Nadia had an exploratory interview, but declined their offer weeks ago."}
                ]
            },
            {
                "step": 3,
                "prompt": "Cyber forensics decrypts the Corsair flash drive recovered from Finch office.",
                "options": [
                    {"text": "Analyze the file headers and hashes on the decrypted Corsair drive.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Contains the complete, proprietary Formula X source genome with original developer timestamps!"},
                    {"text": "Trace the keylogger hardware serial number.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The hardware keylogger was bought on Amazon using an account tied to Finch personal email."},
                    {"text": "Question CEO Croft about venture debt.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Croft explains the new investor dinner was to raise $50M; she wanted Formula X patented ASAP."},
                    {"text": "Check Vance VPN connection logs.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance VPN IP never touched the physical air-gapped server."}
                ]
            },
            {
                "step": 4,
                "prompt": "Federal agents obtain Finch personal email and cloud storage records.",
                "options": [
                    {"text": "Review decrypted emails between Finch and PharmaCorp executives.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c9_contract", "feedback": "Emails state: 'Deliver the raw sequence by Thursday. $5M wire will be credited to your Zurich account.'"},
                    {"text": "Interrogate IT Director Vance regarding the insider trading.", "killer_delta": 1, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance is arrested by the SEC for insider shorting, but cleared of physical theft."},
                    {"text": "Check gene synthesizer automated logs.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The automated synthesizer job was programmed in advance to run unattended as a fake alibi."},
                    {"text": "Verify Nadia Ray USPTO patent timestamps.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "USPTO servers confirm Nadia was uploading legal drafts all night."}
                ]
            },
            {
                "step": 5,
                "prompt": "Finch claims an outside hacker framed him by placing the USB drive in his dictionary.",
                "options": [
                    {"text": "Swab the Corsair USB drive and keylogger for epithelial DNA and latent prints.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Finch DNA is plastered across the USB casing, keylogger dongle, and the hollowed book pages."},
                    {"text": "Re-interview CEO Croft.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Croft confirms Finch had physical card access to Server Room 7 as lead biochemist."},
                    {"text": "Examine the wipe script used on the cloud backup.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The script was executed at 23:05 using Croft credentials harvested from the keylogger."},
                    {"text": "Check building turnstile badge logs for Finch.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Turnstiles show Finch never left the facility between 18:00 and 01:00."}
                ]
            },
            {
                "step": 6,
                "prompt": "PharmaCorp legal counsel abruptly issues a press release suspending all talks with Dr. Finch.",
                "options": [
                    {"text": "Subpoena PharmaCorp internal communications and wire logs.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "PharmaCorp turns over negotiations showing Finch demanded immediate payment upon file verification."},
                    {"text": "Check if CEO Croft planned to file an insurance claim.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "No claim filed; Croft was desperately working with IT to recover the wiped data."},
                    {"text": "Examine Finch personal bank statements.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Finch had recently applied for mortgages on luxury properties in Switzerland."},
                    {"text": "Restore the wiped Formula X data from offsite cold storage.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "An uncorrupted cold tape copy was secured, saving the company from total ruin."}
                ]
            },
            {
                "step": 7,
                "prompt": "Finch defense attorney realizes every single technological defense has crumbled.",
                "options": [
                    {"text": "Present the keylogger purchase, Amazon invoice, DNA swab, and PharmaCorp emails.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Attorney advises Finch that a trial would result in a guaranteed 15-year federal sentence."},
                    {"text": "Confirm the timeline of the physical server room entry.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Keycard and server logs prove Finch entered Room 7 at 22:38 and left at 22:45."},
                    {"text": "Formally clear Attorney Nadia Ray.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Ray is commended for ethical conduct and cleared of suspicion."},
                    {"text": "Review SEC charges against Travis Vance.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance will face securities fraud charges separately."}
                ]
            },
            {
                "step": 8,
                "prompt": "The case docket for Economic Espionage and Federal CFAA Violations is compiled.",
                "options": [
                    {"text": "Compile the federal Economic Espionage indictment against Dr. Linus Finch.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Comprehensive indictment: keylogger hardware, DNA, USB contents, deleted backup script, PharmaCorp deal."},
                    {"text": "Deliver restored Formula X research files to Apex Biotech executive team.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "CEO Croft expresses deep relief; clinical trials can proceed on schedule."},
                    {"text": "Coordinate with federal cyber crime division.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Federal prosecutors sign off on felony indictment."},
                    {"text": "Review all forensic hashes.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Cryptographic hashes match the original sequencing files byte-for-byte."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Finch is escorted into the federal courtroom. The moment of truth has arrived.",
                "options": [
                    {"text": "Demand formal plea from Dr. Linus Finch.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Finch breaks down: 'I created Formula X! Croft got all the glory and the stock. I was taking what was mine!'"},
                    {"text": "Ask if IT Director Vance helped him.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Finch scoffs: 'Vance was a useless fool who knew nothing about real science.'"},
                    {"text": "Review timeline for the court record.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline proves Finch planned and executed the heist alone."},
                    {"text": "Seal the formal investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Investigation docket stamped and sealed."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who committed corporate espionage and stole Formula X from Apex Biotech?",
                "options": []
            }
        ],
        "true_culprit": "Dr. Linus Finch",
        "true_solution": "Lead biochemist Dr. Linus Finch was passed over for promotion. He planted a hardware keylogger to capture CEO Croft cloud master password, entered the air-gapped server room at 22:38, downloaded Formula X onto an encrypted USB drive, executed a wipe script on the cloud backups, and hid the drive in his hollowed book to deliver to rival PharmaCorp for $5M.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 10: THE HIGH STAKES CASINO FRAUD ──
    {
        "id": "case_10",
        "title": "The High Stakes Casino Fraud",
        "category": "Fraud",
        "difficulty": "Master",
        "target_or_victim": "The Royale Mirage Casino ($8.5M High Roller Payout)",
        "crime_scene": "High Limit Baccarat Suite 8, Royale Mirage Casino",
        "briefing": "Over three consecutive nights, an obscure high-roller won an unprecedented 32 straight shoes of Baccarat, walking away with $8.5 million. State gaming regulators suspect a sophisticated internal card-sorting or shuffling conspiracy.",
        "suspects": [
            {
                "name": "Monique Laurent",
                "role": "Chief Pit Boss",
                "public_story": "Supervised VIP tables and player comps from the floor.",
                "private_secret": "Partnered with a syndicate that rigged the automated shuffler firmware.",
                "motive": "50% split of the $8.5M haul ($4.25 million).",
                "alibi": "Floor cameras confirm she was pacing the floor continuously.",
                "weakness": "Her personal electronic inspection key was used to calibrate Shuffler 4 before each winning run.",
                "relationship": "15-year veteran pit supervisor.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Armand Cruz",
                "role": "The High Roller / Player",
                "public_story": "Claimed to be an eccentric venture investor from Monaco.",
                "private_secret": "Recruited front-man; a washed-up card counter with heavy gambling debts.",
                "motive": "Promised 10% commission on all winnings.",
                "alibi": "Sat at the baccarat table placing bets in plain sight of cameras.",
                "weakness": "Micro-earpiece receiver found in his ear canal during detention.",
                "relationship": "The face of the betting operation.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Dax Sterling",
                "role": "Surveillance Director",
                "public_story": "Monitored the eye-in-the-sky camera room.",
                "private_secret": "Addicted to sports betting and lost $200k this season.",
                "motive": "Bribe money to overlook anomalies.",
                "alibi": "Console telemetry shows his badge logged into the surveillance desk.",
                "weakness": "Delayed reporting the 32-shoe anomaly for 48 hours.",
                "relationship": "Security head.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Elena Rostova",
                "role": "Baccarat Dealer",
                "public_story": "Dealt the cards according to standard house rules.",
                "private_secret": "Suspected something was wrong with the deck order, but feared getting fired.",
                "motive": "None; was merely terrified of losing her dealer license.",
                "alibi": "Dealt under direct overhead high-speed video recording.",
                "weakness": "Failed to call a pit supervisor during the 20th consecutive win.",
                "relationship": "House dealer.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c10_shuffler", "title": "Tampered Automated Shuffler Firmware", "category": "Digital", "role": "Critical", "description": "Shuffler 4 was loaded with an exploit that sorted cards into a predictable pseudo-random sequence."},
            {"id": "c10_key", "title": "Supervisor Calibration Key Log", "category": "Digital", "role": "Critical", "description": "Shuffler 4 firmware was flashed at 19:45 using Monique Laurent personal electronic service key."},
            {"id": "c10_earpiece", "title": "Miniature Bone-Conduction Receiver", "category": "Physical", "role": "Supporting", "description": "Found in Armand Cruz ear; received card sequence prompts transmitted from an offsite computer."},
            {"id": "c10_delay", "title": "Surveillance Log Delay", "category": "Digital", "role": "Red Herring", "description": "Dax Sterling delayed reporting because he was distracted watching playoff football on an iPad."},
            {"id": "c10_offshore", "title": "Zurich Escrow Agreement", "category": "Circumstantial", "role": "Supporting", "description": "Contract on Laurent phone detailing 50-50 split between 'The Architect' and the offshore Syndicate."}
        ],
        "timeline": [
            {"time": "19:45", "event": "Shuffler 4 calibrated using Laurent electronic supervisor key."},
            {"time": "20:30", "event": "Armand Cruz buys in for $500,000 in Baccarat Suite 8."},
            {"time": "22:00", "event": "Cruz wins 15 straight bets; bets maximum limit of $250k/hand."},
            {"time": "23:45", "event": "Cruz cashes out $8.5M in cashier cage; leaves in limousine."},
            {"time": "09:00", "event": "Gaming Commission auditor flags mathematical impossibility of 32 straight shoes."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "In High Limit Suite 8, the automated shuffler machine and decks of cards are quarantined by gaming agents. The statistical probability of Cruz run is 1 in 4.2 billion. How do you begin?",
                "options": [
                    {"text": "Dismantle automated Shuffler 4 and dump its internal memory.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c10_shuffler", "feedback": "Memory dump reveals rogue firmware injected to stack card orders into a predictable pattern!"},
                    {"text": "Interrogate player Armand Cruz in the holding room.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c10_earpiece", "feedback": "Medical inspection reveals a microscopic bone-conduction radio receiver hidden in his ear canal!"},
                    {"text": "Audit surveillance director Dax Sterling shift records.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c10_delay", "feedback": "Sterling delayed alerting management because he was watching football on his iPad during duty."},
                    {"text": "Check shuffler machine calibration history.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c10_key", "feedback": "Shuffler 4 was flashed with new firmware at 19:45 using Pit Boss Monique Laurent service key."}
                ]
            },
            {
                "step": 2,
                "prompt": "Shuffler 4 was flashed with rogue firmware right before Cruz arrived, using Monique Laurent service key. What do you investigate?",
                "options": [
                    {"text": "Subpoena Monique Laurent cell phone and personal bank accounts.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c10_offshore", "feedback": "Encrypted notes on her phone reveal an escrow agreement splitting the $8.5M with the syndicate!"},
                    {"text": "Interrogate dealer Elena Rostova about the shuffler.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Elena confirms Monique personally swapped out the shuffler unit right before Cruz sat down."},
                    {"text": "Interrogate Armand Cruz about who fed him the bets.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Cruz confesses he was hired in Macau by Monique contacts to act as the big-money frontman."},
                    {"text": "Check Dax Sterling sports betting debts.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling has bad debts, but zero connection to the shuffler firmware exploit."}
                ]
            },
            {
                "step": 3,
                "prompt": "Signal analysis of the radio earpiece identifies a transmitter operating from a hotel room on floor 14.",
                "options": [
                    {"text": "Raid room 1408 immediately with gaming agents.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Inside room 1408: laptop calculating shuffler sequence in real time and transmitting to Cruz earpiece!"},
                    {"text": "Check who booked room 1408 on the hotel registry.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Booked using a credit card belonging to Monique Laurent romantic partner."},
                    {"text": "Check surveillance room camera logs.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Camera coverage was active; the scam relied on the rigged machine, not camera blackouts."},
                    {"text": "Interrogate dealer Elena Rostova on card cuts.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Elena explains Monique taught her a specific 'shallow cut' technique last month."}
                ]
            },
            {
                "step": 4,
                "prompt": "Monique Laurent claims someone stole her service key while she was on her dinner break.",
                "options": [
                    {"text": "Cross-reference key usage with casino biometric hand scanners.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "The service key cabinet requires a palm-vein biometric scan. Monique scanned her own hand at 19:42!"},
                    {"text": "Check Cruz cashier payout checks.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "$8.5M payout was frozen in escrow before Cruz could wire it out of the country."},
                    {"text": "Question Dax Sterling regarding camera angles.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling admits negligence, but is cleared of active criminal conspiracy."},
                    {"text": "Audit the casino shuffler supplier security certificates.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Manufacturer confirms the rogue firmware was a custom-coded black market hack."}
                ]
            },
            {
                "step": 5,
                "prompt": "Armand Cruz signs a full sworn confession detailing how Monique recruited him in Macau.",
                "options": [
                    {"text": "Record Cruz sworn testimony with gaming commission attorneys.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Cruz testifies Monique gave him the earpiece, instructed him when to bet maximum limit, and handled the cut."},
                    {"text": "Examine Monique luggage in the employee locker.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found one-way first class tickets to Zurich departing tomorrow morning."},
                    {"text": "Check Elena Rostova dealer tips.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Cruz tipped her $10k; Elena had immediately declared the tip to the IRS."},
                    {"text": "Review the mathematical distribution of the 32 shoes.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Every single shoe followed the exact sequence generated by the laptop algorithm."}
                ]
            },
            {
                "step": 6,
                "prompt": "Laurent attempts to exit the casino via the underground valet tunnel.",
                "options": [
                    {"text": "Apprehend Monique Laurent at the valet garage exit.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Laurent is arrested. Her purse contains the master service USB dongle and $50k in cash chips."},
                    {"text": "Audit surveillance tapes for other tables.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Only Shuffler 4 was compromised; other tables functioned normally."},
                    {"text": "Examine Cruz passport.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Cruz real identity is an indebted former croupier from Macau."},
                    {"text": "Confirm the frozen $8.5M funds status.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Full $8.5M secured in casino escrow accounts."}
                ]
            },
            {
                "step": 7,
                "prompt": "Forensic lab analyzes the master service USB dongle taken from Laurent purse.",
                "options": [
                    {"text": "Verify code hash on Laurent USB dongle against Shuffler 4 memory.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Exact 1-to-1 SHA-256 cryptographic match to the rogue firmware!"},
                    {"text": "Check if Dax Sterling received text messages from Laurent.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Zero text messages found between Sterling and Laurent."},
                    {"text": "Interview the casino general manager.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Manager confirms Laurent had been arguing against upgrading to cloud-monitored shufflers."},
                    {"text": "Document the bone-conduction earpiece electronics.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Frequency matched the transmitter in Room 1408 down to the megahertz."}
                ]
            },
            {
                "step": 8,
                "prompt": "All evidence pillars are rock solid: palm-vein scanner, firmware hash, room 1408 transmitter, earpiece, and Cruz confession.",
                "options": [
                    {"text": "Compile the state gaming fraud and grand larceny indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Indictment includes grand theft, computer tampering, gaming racketeering, and conspiracy."},
                    {"text": "Formally clear dealer Elena Rostova of criminal charges.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Elena is cleared of all wrongdoing; retains her gaming license."},
                    {"text": "Issue administrative discipline for Surveillance Director Sterling.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling is suspended for dereliction of duty, but cleared of felonies."},
                    {"text": "Return $8.5M to the Royale Mirage vault.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Casino reserves restored; gaming commission closes the financial freeze."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Monique Laurent sits before the Nevada Gaming Control Board with her legal counsel.",
                "options": [
                    {"text": "Present the SHA-256 firmware hash match, palm-vein log, and room 1408 transmitter.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Laurent sighs deeply: 'The casino takes billions from players every year. I just engineered our turn.' She signs the confession."},
                    {"text": "Ask if Armand Cruz came up with the scam.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Laurent scoffs: 'Cruz was just a puppet who did what the earpiece told him.'"},
                    {"text": "Review the timeline for the board record.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline proves every step of the three-night operation."},
                    {"text": "Seal the formal gaming investigation report.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The report is officially sealed for the grand jury."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who was the corrupt inside architect of the High Stakes Casino Fraud?",
                "options": []
            }
        ],
        "true_culprit": "Monique Laurent",
        "true_solution": "Chief Pit Boss Monique Laurent used her biometric palm-vein access to check out the master service key, flashed Shuffler 4 with hacked firmware that pre-sorted decks into a predictable pattern, set up a transmitter in Room 1408, hired front-man Armand Cruz to wear a bone-conduction earpiece, and rigged 32 consecutive shoes to steal $8.5M.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    }
]
