# -*- coding: utf-8 -*-
"""
game/cases_16_to_20.py — Crime Cases 16 through 20 for Investigation Mode.
Case 16: The Cyber Extortion Syndicate (Cyber Extortion)
Case 17: The Diplomatic Courier Murder (Murder)
Case 18: The Hospital Malpractice Conspiracy (Conspiracy / Murder)
Case 19: The Multiple Murders of the Clockwork Killer (Serial Murder)
Case 20: The Perfect Crime: The Illusionist's Last Act (Master Mystery Finale)
"""

CASES_16_TO_20 = [
    # ── CASE 16: THE CYBER EXTORTION SYNDICATE ──
    {
        "id": "case_16",
        "title": "The Cyber Extortion Syndicate",
        "category": "Cyber Extortion",
        "difficulty": "Hard",
        "target_or_victim": "Global Fintech Grid ($50 Million Ransomware Attack)",
        "crime_scene": "Network Operations Center, Global Fintech Headquarters",
        "briefing": "At 3:00 AM, the central clearinghouse for international wires was locked down by 'PhantomLock' ransomware. A ransom of 800 Bitcoin ($50M) was demanded, with the decryption key set to self-destruct in 24 hours.",
        "suspects": [
            {
                "name": "Victor 'Zero' Sterling",
                "role": "Chief Security Architect",
                "public_story": "Lead the emergency incident response team from the conference room.",
                "private_secret": "Author of the PhantomLock kernel exploit; created it over 8 months to cash out and retire abroad.",
                "motive": "$50 million cryptocurrency extortion bounty.",
                "alibi": "Appeared on video calls with the board starting at 3:15 AM.",
                "weakness": "His personal hardware development laptop contained the master private RSA-4096 decryption key.",
                "relationship": "Lead cyber defense architect.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Maya Vance",
                "role": "Senior System Administrator",
                "public_story": "On call at home; logged in remotely when alerts fired.",
                "private_secret": "Neglected to patch an Apache server vulnerability three months ago.",
                "motive": "Cover up administrative negligence before internal audit.",
                "alibi": "Home fiber connection logs verify remote login at 3:12 AM.",
                "weakness": "Her administrator credentials were used to execute the initial payload script.",
                "relationship": "Lead infrastructure admin.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Felix Drake",
                "role": "Penetration Tester / White Hat",
                "public_story": "Sleeping at home; arrived at 4:30 AM after being summoned.",
                "private_secret": "Posted encrypted malware snippets to underground hacker forums last month.",
                "motive": "Thrill and notoriety in the underground hacking scene.",
                "alibi": "Apartment smart lock showed he left home at 4:00 AM.",
                "weakness": "Found carrying a USB boot drive containing reverse-engineering tools.",
                "relationship": "Contract security auditor.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Harrison Cole",
                "role": "Chief Technology Officer",
                "public_story": "At an executive summit in Chicago; called into the crisis bridge.",
                "private_secret": "Secretly shorted company stock through an offshore broker.",
                "motive": "Profit from stock market panic.",
                "alibi": "Hotel cameras in Chicago show him on the phone all night.",
                "weakness": "Demanded the board pay the ransom immediately.",
                "relationship": "Executive management.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c16_laptop", "title": "Encrypted Hardware Development Laptop", "category": "Digital", "role": "Critical", "description": "Found in Victor Sterling backpack; hidden VeraCrypt partition contains the master PhantomLock RSA private key."},
            {"id": "c16_script", "title": "Ransomware Deployment Cron Job", "category": "Digital", "role": "Critical", "description": "Scheduled job set up at 18:30 yesterday from an internal IP terminal assigned to Sterling office."},
            {"id": "c16_creds", "title": "Harvested Admin Credentials", "category": "Digital", "role": "Supporting", "description": "Maya Vance credentials were stolen via a pass-the-hash exploit staged from Sterling machine."},
            {"id": "c16_forum", "title": "Dark Web Forum Postings", "category": "Digital", "role": "Red Herring", "description": "Felix Drake posted harmless proof-of-concept exploits for research, not the weaponized PhantomLock."},
            {"id": "c16_wallet", "title": "800 BTC Extortion Address", "category": "Digital", "role": "Supporting", "description": "Multi-sig wallet created via VPN connected to a private server registered to Sterling alias."}
        ],
        "timeline": [
            {"time": "18:30", "event": "Sterling programs automated ransomware deployment cron job."},
            {"time": "02:58", "event": "Pass-the-hash attack exploits Maya Vance cached credentials."},
            {"time": "03:00", "event": "PhantomLock encrypts 1,400 servers across 3 continents."},
            {"time": "03:15", "event": "Sterling joins crisis video bridge looking 'shocked'."},
            {"time": "04:30", "event": "Felix Drake arrives to assist with incident containment."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Every server terminal in the Network Operations Center displays a red skull and a 24-hour countdown demanding 800 Bitcoin. Wire settlements worldwide are frozen. Where do you start?",
                "options": [
                    {"text": "Isolate the infected subnets and dump server memory before encryption completes.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c16_script", "feedback": "Memory dump reveals the execution was triggered by an automated cron job scheduled from Sterling office terminal!"},
                    {"text": "Search contract pen-tester Felix Drake laptop and flash drives.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c16_forum", "feedback": "Drake drives contain harmless penetration testing utilities and published academic white papers."},
                    {"text": "Trace the credential token used to execute the domain controller lock.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c16_creds", "feedback": "Admin token belonged to Maya Vance, but authentication logs show a pass-the-hash relay from an internal IP."},
                    {"text": "Interrogate CTO Harrison Cole on Chicago hotel video call.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Cole is panicking about stock price collapse, demanding the board authorize payment."}
                ]
            },
            {
                "step": 2,
                "prompt": "The cron job was created at 18:30 yesterday from Terminal SEC-01 in Victor Sterling office. Sterling claims his machine was hacked.",
                "options": [
                    {"text": "Seize Victor Sterling development laptop from his backpack.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": "c16_laptop", "feedback": "Hidden encrypted container uncovered! Inside: the compiled PhantomLock source code and master RSA key!"},
                    {"text": "Interrogate Maya Vance regarding the credential leak.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Maya explains her password hash was dumped during a routine vulnerability scan authorized by Sterling."},
                    {"text": "Trace the 800 Bitcoin extortion address on blockchain explorers.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c16_wallet", "feedback": "The multi-sig wallet was seeded from a server in Iceland registered to Sterling fake identity."},
                    {"text": "Examine Felix Drake dark web accounts.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Drake forum posts were strictly educational; no link to the extortion syndicate."}
                ]
            },
            {
                "step": 3,
                "prompt": "With the master RSA-4096 key extracted from Sterling laptop, federal cyber agents begin restoring the clearinghouse.",
                "options": [
                    {"text": "Deploy the recovered RSA key to decrypt the primary wire transaction servers.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Decryption successful! International financial grid restored without paying a cent of ransom!"},
                    {"text": "Confront Victor Sterling with the compiled ransomware source code.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Sterling turns pale as his developer comments and Git commits match his personal coding style."},
                    {"text": "Check CTO Harrison Cole trading profits.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "SEC is investigating Cole short-selling, but he is cleared of creating the ransomware."},
                    {"text": "Audit Maya Vance home computer.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Maya system shows she was completely clean; her credentials were hijacked internally."}
                ]
            },
            {
                "step": 4,
                "prompt": "Git repository commit logs on Sterling laptop show he developed PhantomLock over 8 months under the handle 'ZeroDay'.",
                "options": [
                    {"text": "Correlate 'ZeroDay' Git commit history with Sterling work calendar.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Commits were uploaded during late night hours from Sterling verified home IP address!"},
                    {"text": "Interrogate Felix Drake about 'ZeroDay'.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Drake confirms 'ZeroDay' was a legendary underground coder whom everyone assumed was in Russia."},
                    {"text": "Review building turnstile badge logs for Sterling.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Turnstile logs show Sterling was physically sitting at Terminal SEC-01 at 18:30 yesterday."},
                    {"text": "Check Maya Vance disciplinary record.", "killer_delta": 0, "evidence_score_delta": 4, "unlocked_clue_id": None, "feedback": "Maya receives retraining on credential rotation, cleared of criminal charges."}
                ]
            },
            {
                "step": 5,
                "prompt": "Sterling attempts to slip out through the building basement loading dock carrying a burner phone.",
                "options": [
                    {"text": "Detain Victor Sterling at the basement security barrier.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Sterling arrested! Pockets contain hardware crypto cold wallets, fake Canadian passport, and cash."},
                    {"text": "Examine the burner phone messages.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Burner phone received automated alerts confirming the ransom deadline countdown."},
                    {"text": "Re-interview CTO Harrison Cole.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Cole resigns in disgrace over insider shorting, but avoids hacking charges."},
                    {"text": "Verify the server decryptor integrity.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "All 1,400 enterprise servers brought back online with zero data corruption."}
                ]
            },
            {
                "step": 6,
                "prompt": "Cyber forensics verifies the cryptographic hash of the compiled payload against the source on Sterling laptop.",
                "options": [
                    {"text": "Perform binary SHA-256 hash comparison between payload and source.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Byte-for-byte SHA-256 match! The payload was compiled on Sterling machine at 18:15 yesterday."},
                    {"text": "Check Icelandic server payment records.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Icelandic server paid with Monero tracked back to Sterling personal crypto exchange deposit."},
                    {"text": "Formally clear Felix Drake.", "killer_delta": 1, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Drake is offered a full-time contract to lead the external security audit."},
                    {"text": "Check company backup disaster recovery tapes.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Backups were intentionally targeted and wiped by Sterling cron job."}
                ]
            },
            {
                "step": 7,
                "prompt": "Sterling defense counsel claims the laptop was a staging sandbox planted by foreign state actors.",
                "options": [
                    {"text": "Present biometric keystroke dynamics and hardware security token logs.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Keystroke rhythm and his biometric fingerprint on the laptop sensor establish continuous personal use."},
                    {"text": "Review email exchanges between Sterling and management.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Sterling repeatedly warned management of ransomware vulnerabilities to establish plausible deniability."},
                    {"text": "Confirm the status of international wire transfers.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Global financial system resumed normal operations with zero monetary loss."},
                    {"text": "Check Maya Vance testimony on terminal proximity.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Maya testifies she saw Sterling at Terminal SEC-01 at 18:30 drinking coffee."}
                ]
            },
            {
                "step": 8,
                "prompt": "The federal cyber extortion and Computer Fraud and Abuse Act (CFAA) indictment is assembled.",
                "options": [
                    {"text": "Compile the federal cyber extortion indictment docket.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Overwhelming docket: source code, binary hash, cron job logs, fake passport, recovered private key."},
                    {"text": "Formally exonerate Maya Vance and Felix Drake.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both employees are fully cleared and restored to duty."},
                    {"text": "Brief the Federal Bureau of Investigation and Department of Homeland Security.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Federal agencies commend the team for preventing global financial panic."},
                    {"text": "Secure the master decryption key in federal cryptographic vault.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Key sealed for court evidence."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Victor Sterling sits in the federal courthouse with his defense attorney.",
                "options": [
                    {"text": "Present the binary hash match, biometric keystrokes, and recovered private key.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Sterling sighs: 'I spent 15 years protecting banks for an annual salary while executives made hundreds of millions. I wrote the best code of my life.' He signs the confession."},
                    {"text": "Ask if Maya Vance helped him.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling admits: 'Maya was just an easy password hash to grab.'"},
                    {"text": "Review the timeline for the federal judge.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline proves the exact sequence of development, staging, and deployment."},
                    {"text": "Seal the formal investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Investigation file signed, stamped, and ready for trial."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who engineered and deployed the Global Fintech ransomware attack?",
                "options": []
            }
        ],
        "true_culprit": "Victor 'Zero' Sterling",
        "true_solution": "Chief Security Architect Victor Sterling secretly spent 8 months developing the PhantomLock ransomware under the handle 'ZeroDay'. He set up an automated cron job from his terminal at 18:30, used stolen admin hashes to deploy across 1,400 servers at 3:00 AM, demanded $50M in Bitcoin, and kept the master RSA decryption key hidden on his laptop to cash out and escape abroad.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 17: THE DIPLOMATIC COURIER MURDER ──
    {
        "id": "case_17",
        "title": "The Diplomatic Courier Murder",
        "category": "Murder",
        "difficulty": "Hard",
        "target_or_victim": "Mikhail Rostov, Embassy Diplomatic Courier",
        "crime_scene": "Consular Mail Room, Eastern European Embassy",
        "briefing": "Diplomatic courier Mikhail Rostov was found shot twice in the chest with a silenced pistol inside the secure embassy pouch room. His diplomatic dispatch pouch, containing classified treaty annexes, was sliced open and emptied.",
        "suspects": [
            {
                "name": "Agent Sean Gallagher",
                "role": "Rogue Intelligence Attaché",
                "public_story": "Conducting counter-surveillance sweep in the embassy courtyard.",
                "private_secret": "Recruited by a hostile foreign intelligence service for $2M.",
                "motive": "Steal the treaty annexes and eliminate Rostov who recognized him in the hallway.",
                "alibi": "Courtyard log says he was on patrol from 22:00 to 23:00.",
                "weakness": "9mm casing from his issued SIG Sauer sidearm matches the two bullets extracted from Rostov chest.",
                "relationship": "Embassy security officer.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Ambassador Elena Vane",
                "role": "Deputy Chief of Mission",
                "public_story": "Drafting diplomatic cables in her top-floor office.",
                "private_secret": "The treaty annexes contained evidence of her unauthorized offshore bank accounts.",
                "motive": "Prevent disclosure of her financial corruption.",
                "alibi": "Cable timestamps confirm continuous draft transmissions until 23:30.",
                "weakness": "Held the master keycard to the diplomatic pouch room.",
                "relationship": "Embassy superior.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Igor Petrov",
                "role": "Embassy Mail Clerk",
                "public_story": "Sorting incoming consular correspondence in the outer sorting bay.",
                "private_secret": "Fell asleep in the breakroom after drinking vodka on duty.",
                "motive": "None; terrified of being deported.",
                "alibi": "Sorting machine ran on auto-feed.",
                "weakness": "Found with blood on his shirt from trying to assist Rostov after finding the body.",
                "relationship": "Mail clerk.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Nadia Vance",
                "role": "Visiting Trade Negotiator",
                "public_story": "In the embassy guest suite packing her luggage.",
                "private_secret": "Opposed the treaty terms; wanted the negotiations to fail.",
                "motive": "Derail the treaty by leaking the annexes.",
                "alibi": "Guest suite phone logs show call with foreign ministry until 22:45.",
                "weakness": "Carrying an encrypted satellite telephone in her handbag.",
                "relationship": "Diplomatic delegate.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c17_ballistics", "title": "9mm Sub-Sonic Ballistics Match", "category": "Physical", "role": "Critical", "description": "Rifling grooves on extracted bullets match Agent Sean Gallagher issued service weapon."},
            {"id": "c17_silencer", "title": "Improvised Tactical Silencer", "category": "Physical", "role": "Critical", "description": "Found hidden in embassy incinerator exhaust with Gallagher fingerprints on the threaded barrel adapter."},
            {"id": "c17_blood", "title": "Petrov Bloodstained Shirt", "category": "Physical", "role": "Red Herring", "description": "Transfer stains from when clerk Petrov discovered Rostov and desperately attempted CPR."},
            {"id": "c17_annex", "title": "Stolen Treaty Annex Microfilm", "category": "Physical", "role": "Supporting", "description": "Found concealed inside the battery compartment of Gallagher two-way radio."},
            {"id": "c17_keycard", "title": "Pouch Room Access Log", "category": "Digital", "role": "Supporting", "description": "Door opened at 22:38 using cloned security badge with Gallagher RFID signature."}
        ],
        "timeline": [
            {"time": "22:15", "event": "Courier Rostov enters pouch room with secure leather diplomatic bag."},
            {"time": "22:30", "event": "Mail clerk Petrov dozes off in outer breakroom."},
            {"time": "22:38", "event": "Gallagher enters pouch room using cloned security badge."},
            {"time": "22:41", "event": "Two silenced shots fired; treaty microfilm stolen."},
            {"time": "22:48", "event": "Gallagher hides silencer in incinerator chute."},
            {"time": "23:05", "event": "Petrov discovers Rostov and calls embassy medical team."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Inside the reinforced consular pouch room, courier Mikhail Rostov lies dead behind the sorting table, shot twice in the chest. His leather diplomatic pouch is slashed open. How do you begin?",
                "options": [
                    {"text": "Recover spent bullets and examine the victim entry wounds.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c17_ballistics", "feedback": "Sub-sonic 9mm rounds extracted. Rifling marks match embassy diplomatic security service weapons!"},
                    {"text": "Search embassy incinerator room and ventilation ducts.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c17_silencer", "feedback": "Found an improvised tactical silencer in the incinerator exhaust with latent prints on the adapter!"},
                    {"text": "Interrogate Mail Clerk Igor Petrov about his bloodstained shirt.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c17_blood", "feedback": "Petrov cries in despair; he tried to apply chest compressions when he discovered the body."},
                    {"text": "Check pouch room electronic door lock logs.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c17_keycard", "feedback": "Door opened at 22:38 using a security badge assigned to Agent Sean Gallagher."}
                ]
            },
            {
                "step": 2,
                "prompt": "Agent Gallagher claims his security badge was stolen from his desk during dinner. Ballistics links his issued SIG Sauer to the bullets.",
                "options": [
                    {"text": "Seize Agent Gallagher issued sidearm and uniform equipment for inspection.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Barrel rifling is an exact 1-to-1 match to the bullets that killed Rostov!"},
                    {"text": "Search Gallagher two-way radio and tactical vest.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c17_annex", "feedback": "Inside the radio battery compartment: the stolen treaty annex microfilm canisters!"},
                    {"text": "Interrogate Ambassador Elena Vane regarding her master keycard.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Vane was drafting cables on her terminal; computer timestamps prove her continuous presence upstairs."},
                    {"text": "Question trade negotiator Nadia Vance about the satellite phone.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Nadia was talking to ministry superiors; satellite logs match her phone records."}
                ]
            },
            {
                "step": 3,
                "prompt": "Latent prints on the silencer adapter match Agent Sean Gallagher right index finger.",
                "options": [
                    {"text": "Confront Gallagher with the fingerprint on the silencer and the microfilm in his radio.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Gallagher goes completely silent, realizing his tactical gear was recovered intact."},
                    {"text": "Check embassy courtyard surveillance video.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Courtyard camera shows Gallagher left his patrol post at 22:32 and re-entered the embassy."},
                    {"text": "Examine Mail Clerk Petrov breakroom alibi.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Empty vodka bottle found in breakroom; Petrov was asleep until 23:00."},
                    {"text": "Audit Ambassador Vane bank records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Her financial irregularities are referred to diplomatic ethics; cleared of murder."}
                ]
            },
            {
                "step": 4,
                "prompt": "Intelligence officers decrypt a burner email account accessed from Gallagher terminal.",
                "options": [
                    {"text": "Analyze emails on the hostile intelligence contact chain.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Emails show Gallagher negotiated a $2M cash payment for delivering the treaty annexes at a dead drop tonight."},
                    {"text": "Check gunshot residue on Gallagher uniform cuffs.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Heavy barium and antimony residue found on his jacket sleeves."},
                    {"text": "Verify Nadia Vance guest suite phone records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Ministerial records confirm her call lasted until 22:45 without interruption."},
                    {"text": "Interview embassy medical staff.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Doctors confirm Rostov died instantly from shots through the aorta."}
                ]
            },
            {
                "step": 5,
                "prompt": "Gallagher demands diplomatic immunity under the Vienna Convention.",
                "options": [
                    {"text": "Request formal waiver of diplomatic immunity from the Foreign Ministry.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Foreign Ministry immediately revokes Gallagher immunity for treason and murder on embassy grounds!"},
                    {"text": "Check if Clerk Petrov was offered a bribe.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Petrov had zero contact with Gallagher and had no money."},
                    {"text": "Examine the slashed leather diplomatic pouch.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The pouch was cut using a serrated combat knife issued to embassy tactical security."},
                    {"text": "Verify the planned dead drop coordinates.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Drop site was set for midnight in a suburban railway locker."}
                ]
            },
            {
                "step": 6,
                "prompt": "Federal counter-espionage agents secure the dead drop locker in the train station.",
                "options": [
                    {"text": "Ambush the dead drop site and arrest the foreign intelligence handler.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Handler arrested at the locker carrying a briefcase containing $2M in unmarked $100 bills!"},
                    {"text": "Confront Gallagher with the foreign handler arrest.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Gallagher head sags; all operational ties and escapes are destroyed."},
                    {"text": "Formally clear Mail Clerk Igor Petrov.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Petrov is cleared of homicide; commended for attempting CPR."},
                    {"text": "Examine the microfilm contents.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Microfilm contains sensitive radar defense deployment coordinates."}
                ]
            },
            {
                "step": 7,
                "prompt": "Gallagher service knife is retrieved from his locker; microscopic leather fibers match the diplomatic pouch.",
                "options": [
                    {"text": "Microscopic analysis of Gallagher combat knife blade.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Serrated blade teeth hold leather dye and reinforced Kevlar fibers from the dispatch pouch!"},
                    {"text": "Re-interview Ambassador Elena Vane.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vane cooperates fully with counter-espionage investigators."},
                    {"text": "Check trade negotiator Nadia Vance travel documents.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Nadia is fully cleared and departs on schedule."},
                    {"text": "Confirm chain of custody on the $2M payoff cash.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Payoff cash impounded in federal evidence vault."}
                ]
            },
            {
                "step": 8,
                "prompt": "The espionage, treason, and first-degree murder indictment is prepared.",
                "options": [
                    {"text": "Compile the federal espionage and capital murder indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Indictment finalized: ballistics match, silencer prints, microfilm in radio, combat knife fibers, handler arrest."},
                    {"text": "Safely return the classified treaty annexes to Foreign Ministry custody.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Classified defense documents returned with zero public leakage."},
                    {"text": "Post-incident embassy security review.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Protocol overhauled to require dual-keycard biometric access to pouch rooms."},
                    {"text": "Certify autopsy findings for embassy court record.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Autopsy report certified by chief medical examiner."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Agent Sean Gallagher sits in the federal courthouse after immunity revocation.",
                "options": [
                    {"text": "Present the ballistics rifling match, silencer fingerprint, and the $2M handler arrest.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Gallagher speaks bitterly: 'Rostov walked in while I was slicing the bag. He reached for his gun. It was him or me.' He signs the confession."},
                    {"text": "Ask if Ambassador Vane was involved.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Gallagher sneers: 'Vane is a bureaucrat who knows nothing about black ops.'"},
                    {"text": "Review timeline for federal court.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Minute-by-minute timeline leaves zero doubt of premeditation."},
                    {"text": "Seal the formal murder investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Investigation docket signed, stamped, and ready for trial."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who murdered diplomatic courier Mikhail Rostov?",
                "options": []
            }
        ],
        "true_culprit": "Agent Sean Gallagher",
        "true_solution": "Rogue attaché Sean Gallagher was bribed $2M by a hostile foreign intelligence service to steal classified treaty annexes. At 22:38, he used his security badge to enter the pouch room, was surprised by courier Rostov, shot him twice with his silenced service pistol, sliced open the diplomatic pouch with his combat knife, hid the microfilm in his radio battery, and hid the silencer in the incinerator chute.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 18: THE HOSPITAL MALPRACTICE CONSPIRACY ──
    {
        "id": "case_18",
        "title": "The Hospital Malpractice Conspiracy",
        "category": "Conspiracy",
        "difficulty": "Expert",
        "target_or_victim": "Dr. Julian Croft, Senior Cardiac Surgeon",
        "crime_scene": "Surgical Suite 4 & Executive Office, St. Jude Medical",
        "briefing": "Renowned cardiac surgeon Dr. Julian Croft collapsed dead in his office after performing a high-profile heart valve replacement. Autopsy revealed succinylcholine paralytic injected into his saline IV flush.",
        "suspects": [
            {
                "name": "Dr. Arthur Price",
                "role": "Chief of Surgery",
                "public_story": "Observing surgeries from the overhead surgical gallery.",
                "private_secret": "Covered up fatal surgical errors and kickbacks from a defective prosthetic valve manufacturer.",
                "motive": "Croft had prepared a whistleblower dossier to deliver to the Medical Board tomorrow.",
                "alibi": "Nursing staff saw him in the gallery at 3:00 PM.",
                "weakness": "Surveillance shows him entering Croft private office at 3:30 PM carrying an insulated medical pouch.",
                "relationship": "Croft supervisor and department head.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Nurse Evelyn Reed",
                "role": "Lead Surgical Nurse",
                "public_story": "Sterilizing instruments in the wash bay.",
                "private_secret": "Stole fentanyl ampoules from the hospital narcotic dispenser.",
                "motive": "Croft threatened to report missing narcotics.",
                "alibi": "Wash bay camera recorded her cleaning trays.",
                "weakness": "Her badge was used to open the automated pharmacy dispenser.",
                "relationship": "Surgical assistant for 3 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Dr. Marcus Vance",
                "role": "Chief Anesthesiologist",
                "public_story": "Monitoring patient vitals in recovery room B.",
                "private_secret": "Prescribed high doses of off-label tranquilizers to wealthy private clients.",
                "motive": "Fear of malpractice lawsuit.",
                "alibi": "Heart monitors confirm his continuous badge presence in recovery.",
                "weakness": "Signed the pharmacy requisition for the succinylcholine batch.",
                "relationship": "Anesthesiologist.",
                "is_culprit": False,
                "is_liar": False
            },
            {
                "name": "David Sterling",
                "role": "Prosthetic Valve Manufacturer Rep",
                "public_story": "Waiting in the hospital lobby with technical specifications.",
                "private_secret": "Paid $200,000 in kickbacks to Dr. Price to use uncertified valves.",
                "motive": "Protect his company multi-million dollar valve supply contract.",
                "alibi": "Lobby security desk camera recorded him until 4:00 PM.",
                "weakness": "Argued with Croft in the hallway earlier this morning.",
                "relationship": "Commercial supplier.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c18_succinyl", "title": "Succinylcholine Saline Vial", "category": "Physical", "role": "Critical", "description": "Recovered from Croft office sharps container; carries Dr. Arthur Price latent fingerprints."},
            {"id": "c18_whistle", "title": "Medical Board Whistleblower Dossier", "category": "Circumstantial", "role": "Critical", "description": "Found in Croft safe; documents 8 patient deaths caused by defective valves approved by Price for kickbacks."},
            {"id": "c18_fentanyl", "title": "Stolen Fentanyl Ampoules", "category": "Physical", "role": "Red Herring", "description": "Found in Nurse Evelyn locker; petty narcotic theft, not the paralytic poison."},
            {"id": "c18_video", "title": "Office Corridor CCTV", "category": "Digital", "role": "Supporting", "description": "Dr. Arthur Price seen entering Croft private office at 3:30 PM with an insulated pouch."},
            {"id": "c18_kickback", "title": "Offshore Valve Royalty Ledger", "category": "Digital", "role": "Supporting", "description": "Bank wire confirms $200,000 transfer from valve company into Dr. Price Swiss account."}
        ],
        "timeline": [
            {"time": "14:00", "event": "Dr. Croft performs successful heart valve operation."},
            {"time": "15:00", "event": "Chief Dr. Price leaves observation gallery."},
            {"time": "15:30", "event": "Price enters Croft office and injects succinylcholine into Croft vitamin IV drip."},
            {"time": "15:45", "event": "Croft returns to office, connects his routine hydration IV drip."},
            {"time": "16:00", "event": "Croft suffers respiratory paralysis and cardiac arrest."},
            {"time": "16:15", "event": "Nurse Evelyn discovers body and calls emergency code blue."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "Inside Dr. Croft private executive office, the surgeon sits lifeless in his leather armchair. A personal saline hydration IV drip is connected to his left forearm. How do you launch the investigation?",
                "options": [
                    {"text": "Seize the saline IV bag and test the fluid for paralytic toxins.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c18_succinyl", "feedback": "Toxicology confirms lethal concentration of succinylcholine injected into the IV bag!"},
                    {"text": "Search Dr. Croft office safe and document drawers.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c18_whistle", "feedback": "Recovered a whistleblower dossier exposing 8 patient deaths from defective valves approved by Dr. Price!"},
                    {"text": "Search Nurse Evelyn Reed locker.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c18_fentanyl", "feedback": "Found 4 stolen ampoules of fentanyl. Evelyn weeps, admitting drug dependency but denying murder."},
                    {"text": "Review hospital pharmacy dispenser logs for succinylcholine.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Batch requisition was signed by Anesthesiologist Dr. Vance for morning surgical schedule."}
                ]
            },
            {
                "step": 2,
                "prompt": "CCTV outside Croft office captures someone in surgical scrubs entering at 3:30 PM carrying an insulated medical pouch.",
                "options": [
                    {"text": "Enhance corridor video and cross-reference biometric gait analysis.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c18_video", "feedback": "Facial and gait recognition confirms the figure is Chief of Surgery Dr. Arthur Price!"},
                    {"text": "Confront Dr. Arthur Price with the whistleblower dossier.", "killer_delta": 3, "evidence_score_delta": 10, "unlocked_clue_id": None, "feedback": "Price turns pale, claiming the report was 'unverified slander' by a paranoid colleague."},
                    {"text": "Interrogate Anesthesiologist Dr. Marcus Vance.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Vance was continuously monitoring patient recovery; vitals telemetry proves his uninterrupted presence."},
                    {"text": "Question valve rep David Sterling in the lobby.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Lobby security cameras prove Sterling never passed the reception turnstile."}
                ]
            },
            {
                "step": 3,
                "prompt": "The sharps disposal container in Croft office yields the discarded glass syringe used to taint the IV bag.",
                "options": [
                    {"text": "Dust the discarded glass syringe for latent epithelial DNA and prints.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Dr. Arthur Price thumbprint and skin DNA found on the syringe barrel and plunger!"},
                    {"text": "Subpoena Dr. Price bank accounts and offshore financial ties.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c18_kickback", "feedback": "Bank subpoena reveals $200,000 wire payment from the valve company into Price Swiss account!"},
                    {"text": "Check Nurse Evelyn pharmacy badge timestamps.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Evelyn only accessed the fentanyl lockbox, not the paralytic shelf."},
                    {"text": "Examine the operating room schedule.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Croft was scheduled to meet the State Medical Board tomorrow at 9:00 AM."}
                ]
            },
            {
                "step": 4,
                "prompt": "David Sterling, the valve manufacturer rep, is interrogated under threat of federal conspiracy charges.",
                "options": [
                    {"text": "Interrogate David Sterling regarding the $200,000 kickback wire.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Sterling cracks: he admits paying Dr. Price kickbacks to bury failure reports on defective heart valves."},
                    {"text": "Search Dr. Price executive office suite.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Inside his briefcase: shredded draft of Croft whistleblower report and one-way tickets to Zurich."},
                    {"text": "Check Dr. Marcus Vance phone records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Zero calls between Vance and the valve company."},
                    {"text": "Verify Croft hydration IV habit.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Surgical staff confirm Croft routinely took an electrolyte IV flush after every 6-hour surgery."}
                ]
            },
            {
                "step": 5,
                "prompt": "Dr. Price attempts to claim he visited Croft office at 3:30 PM merely to deliver a medical journal.",
                "options": [
                    {"text": "Counter with the syringe prints, succinylcholine residue, and $200k wire proof.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Price lawyer advises him that the forensic physical evidence makes an accidental explanation impossible."},
                    {"text": "Check the medical journal found on Croft desk.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Journal was from last year; used as a flimsy prop to carry the insulated syringe pouch."},
                    {"text": "Formally clear Nurse Evelyn of homicide charges.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Evelyn is transferred to drug diversion rehabilitation; cleared of murder."},
                    {"text": "Verify the patient heart valve condition.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The surgery was successful; Croft saved the patient before being killed."}
                ]
            },
            {
                "step": 6,
                "prompt": "Autopsy toxicology definitively confirms fatal blood levels of succinylcholine without anesthetic sedation.",
                "options": [
                    {"text": "Record chief medical examiner deposition on mechanism of death.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Mechanism: total diaphragm paralysis causing suffocation within 4 minutes while fully conscious."},
                    {"text": "Audit the 8 patient death files documented by Croft.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "All 8 deaths involved the defective valve model endorsed by Dr. Price."},
                    {"text": "Confirm valve rep Sterling cooperation agreement.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Sterling signs state evidence agreement testifying against Price."},
                    {"text": "Check hospital security card archives.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Card logs confirm Price was the only person who entered Croft office between 15:00 and 15:45."}
                ]
            },
            {
                "step": 7,
                "prompt": "Dr. Price defense attorney realizes his client faces multiple counts of murder, bribery, and manslaughter.",
                "options": [
                    {"text": "Present the full evidence binder to Dr. Arthur Price.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Price stares in silence at the DNA match on the syringe and the Zurich wire transfer receipts."},
                    {"text": "Interview Anesthesiologist Dr. Vance regarding the missing vial.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Vance testifies Price requested an extra succinylcholine ampoule claiming an emergency in Suite 4."},
                    {"text": "Clear hospital nursing staff of complicity.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "All staff cleared of conspiracy."},
                    {"text": "Review hospital board emergency actions.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Hospital board immediately strips Price of medical privileges and recalls all defective valves."}
                ]
            },
            {
                "step": 8,
                "prompt": "The premeditated first-degree murder, commercial bribery, and health care fraud docket is prepared.",
                "options": [
                    {"text": "Compile the comprehensive murder and racketeering indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Complete docket: syringe DNA and prints, video timestamps, $200k kickback wires, whistleblower files."},
                    {"text": "Formally close the investigation against Nurse Evelyn and Dr. Vance.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both medical professionals are exonerated of the homicide."},
                    {"text": "Turn over defective valve evidence to federal FDA investigators.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "FDA issues nationwide recall of the defective valve model, saving hundreds of lives."},
                    {"text": "Certify Croft whistleblower report for the State Medical Board.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dr. Croft integrity and heroism are posthumously honored by the medical community."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Chief of Surgery Dr. Arthur Price sits before the grand jury prosecutor.",
                "options": [
                    {"text": "Present the syringe DNA match, corridor CCTV, and valve kickback trail to Dr. Price.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Price breaks down into tears: 'Croft was going to ruin my life! 30 years of medical prestige destroyed over a few valve complications! I couldn't let him go to the board!' He signs the confession."},
                    {"text": "Ask if Nurse Evelyn had any role.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Price scoffs: 'Evelyn is a nurse. She knew nothing.'"},
                    {"text": "Review the timeline for the court record.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline matches every movement between 14:00 and 16:15 with total precision."},
                    {"text": "Seal the formal murder investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Investigation docket signed, stamped, and ready for trial."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who murdered Dr. Julian Croft in his hospital office?",
                "options": []
            }
        ],
        "true_culprit": "Dr. Arthur Price",
        "true_solution": "Chief of Surgery Dr. Arthur Price received $200,000 in kickbacks to approve defective heart valves that killed 8 patients. When Dr. Croft prepared a whistleblower dossier to deliver to the Medical Board, Price obtained succinylcholine under a false surgical pretext, entered Croft office at 15:30, injected the paralytic poison into Croft routine saline IV flush, and discarded the syringe in the office sharps bin.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 19: THE MULTIPLE MURDERS OF THE CLOCKWORK KILLER ──
    {
        "id": "case_19",
        "title": "The Multiple Murders of the Clockwork Killer",
        "category": "Serial Murder",
        "difficulty": "Master",
        "target_or_victim": "The 4 Victims of the Old Town Clocktower",
        "crime_scene": "The Belfry Vault, St. Jude Gothic Belltower",
        "briefing": "Over four consecutive full moons, four prominent citizens were found dead at exactly 12:00 midnight inside the historic belltower, each clutching an antique brass clock gear inscribed with cryptic Latin numerals.",
        "suspects": [
            {
                "name": "Jonas Bell",
                "role": "Master Horologist & Antique Clock Restorer",
                "public_story": "Working in his workshop across the square until 10:00 PM.",
                "private_secret": "Obsessed with an occult clockwork prophecy; blames the victims for an old church fire that killed his family.",
                "motive": "Retribution against the 4 town aldermen who covered up the parish arson 25 years ago.",
                "alibi": "Workshop timer chimed on the square every hour.",
                "weakness": "Inscribed brass clock gears were cut using a proprietary gear-cutting lathe found in his basement.",
                "relationship": "Church clock restorer.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Father Thomas Vance",
                "role": "Parish Priest",
                "public_story": "Conducting midnight prayers in the lower chapel.",
                "private_secret": "Discovered the victims were blackmailing the church over land deeds.",
                "motive": "Cleanse the church of corruption.",
                "alibi": "Altar boys saw him kneeling in the chancel at 11:30 PM.",
                "weakness": "Held the iron keys to the belltower spiral staircase.",
                "relationship": "Parish pastor.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Silas Finch",
                "role": "Night Town Watchman",
                "public_story": "Patrolling the cobblestone square.",
                "private_secret": "Takes bribes from local smugglers to leave the catacombs unmonitored.",
                "motive": "Silence victims who threatened to expose his smuggling bribes.",
                "alibi": "Clocked in at the town hall punch-clock at 11:45 PM.",
                "weakness": "Was seen walking toward the belltower door at 11:50 PM.",
                "relationship": "Town guard.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Gideon Croft",
                "role": "City Historian & Archivist",
                "public_story": "Researching historical manuscripts in the library.",
                "private_secret": "Authored a book on the 1901 church fire and the aldermen conspiracy.",
                "motive": "Generate sensational publicity for his new book.",
                "alibi": "Library desk logs show him reading until midnight.",
                "weakness": "Owned original mechanical blueprints of the belltower clock.",
                "relationship": "Parish historian.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c19_lathe", "title": "Inscribed Brass Gears & Lathe Tool Marks", "category": "Physical", "role": "Critical", "description": "Gears left in victims hands have microscopic machining striations matching Jonas Bell Swiss gear-cutting lathe."},
            {"id": "c19_diary", "title": "Vengeance Ledger & Prophecy Journal", "category": "Physical", "role": "Critical", "description": "Found behind a false brick in Jonas Bell cellar; names all 4 victims as the men who set the 1901 fire."},
            {"id": "c19_keys", "title": "Belltower Staircase Keys", "category": "Physical", "role": "Supporting", "description": "Father Thomas kept the keys in the sacristy; Jonas Bell had made wax impression duplicates years ago."},
            {"id": "c19_watchman", "title": "Watchman Punch-Clock Log", "category": "Digital", "role": "Red Herring", "description": "Silas Finch was checking the catacomb door to collect a $50 smuggler payoff, not committing murder."},
            {"id": "c19_cyanide", "title": "Aconite (Wolfsbane) Tincture Bottle", "category": "Physical", "role": "Supporting", "description": "Found in Jonas Bell herb drying shed; aconite poison was used to paralyze all 4 victims before placing them under the bell."}
        ],
        "timeline": [
            {"time": "21:00", "event": "Victim 4, Alderman Sterling, lured to belltower by anonymous letter."},
            {"time": "23:15", "event": "Jonas Bell enters belltower using duplicate brass key."},
            {"time": "23:30", "event": "Bell incapacitates victim with aconite tincture; positions under great bell."},
            {"time": "23:50", "event": "Watchman Silas checks catacomb door for bribe."},
            {"time": "00:00", "event": "Belltower strikes 12; great brass clapper crushes victim; gear placed in hand."},
            {"time": "00:15", "event": "Bell slips through catacombs back into his workshop."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "At midnight, the great bell tolls. High in the belfry, the 4th victim lies beneath the massive swinging clapper. In his cold hand is a polished brass gear etched with Roman numeral 'IV'. Where do you begin?",
                "options": [
                    {"text": "Analyze the machining marks on the brass gear with an optical comparator.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c19_lathe", "feedback": "Micro-grooves match a specialized antique Swiss horological gear-cutting lathe!"},
                    {"text": "Search Jonas Bell clock repair shop across the square.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c19_diary", "feedback": "Behind a false cellar wall: an occult journal detailing the 4 murders as divine retribution for the 1901 parish fire!"},
                    {"text": "Interrogate Night Watchman Silas Finch about his 11:50 PM presence.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c19_watchman", "feedback": "Silas confesses he was picking up an illegal $50 cash payoff from a smuggler; he saw nobody in the tower."},
                    {"text": "Check Father Thomas sacristy key cabinet.", "killer_delta": 1, "evidence_score_delta": 8, "unlocked_clue_id": "c19_keys", "feedback": "The master key was in the cabinet, but wax residue on the lock indicates someone made impressions."}
                ]
            },
            {
                "step": 2,
                "prompt": "The Swiss lathe in Jonas Bell workshop is inspected by forensic machinists. The cutting tool profile is unique in the region.",
                "options": [
                    {"text": "Run forensic metallurgical casting of Jonas Bell Swiss lathe blades.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Exact 1-to-1 match! The 4 brass gears were cut on Jonas Bell personal workbench!"},
                    {"text": "Examine victim toxicology for chemical incapacitation.", "killer_delta": 2, "evidence_score_delta": 10, "unlocked_clue_id": "c19_cyanide", "feedback": "Lethal aconite (wolfsbane) detected in blood; victim was paralyzed before being placed under the bell hammer!"},
                    {"text": "Interrogate Father Thomas Vance regarding the 1901 church fire.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Father Thomas confirms the 4 victims were aldermen who covered up the fire that killed Jonas Bell mother and sister."},
                    {"text": "Search Historian Gideon Croft library desk.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Croft manuscript is a factual historical monograph; he had no access to the lathe or poison."}
                ]
            },
            {
                "step": 3,
                "prompt": "Aconite plants and distillation equipment are uncovered in Jonas Bell greenhouse garden.",
                "options": [
                    {"text": "Analyze aconite extract from Bell workshop bottles.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Chemical chromatography matches the exact aconitine alkaloid profile in all 4 victims!"},
                    {"text": "Confront Jonas Bell with the journal and lathe match.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Bell eyes blaze with religious fervor: 'The four horsemen set the fire that burned my family! The great bell struck their final hour!'"},
                    {"text": "Check Watchman Silas Finch boots for belfry dust.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Silas boots have catacomb mud, but zero belfry pigeon guano or bell grease."},
                    {"text": "Review Father Thomas altar boy testimonies.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Altar boys confirm Father Thomas was praying in the chancel at midnight continuously."}
                ]
            },
            {
                "step": 4,
                "prompt": "Detectives trace the underground catacomb passage connecting the belltower to Bell basement.",
                "options": [
                    {"text": "Map the secret catacomb passage between the belfry and Bell cellar.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "The tunnel connects Bell workshop basement directly into the belltower spiral stair base, bypassing all square cameras!"},
                    {"text": "Search Bell workshop for the 5th gear.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found gear 'V' on his workbench; Bell intended to take his own life at midnight on the next full moon."},
                    {"text": "Interrogate Silas Finch about the catacomb passage.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Silas confirms he noticed the heavy iron grille had its lock picked months ago."},
                    {"text": "Review Historian Gideon Croft research files.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Croft is horrified; his historical book had unwittingly given Bell the names of the 4 aldermen."}
                ]
            },
            {
                "step": 5,
                "prompt": "Bell clothing in his bedroom wardrobe is seized for trace analysis.",
                "options": [
                    {"text": "Examine Bell black wool cloak for belfry particulate evidence.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Cloak carries bell casting bronze dust, bat guano, and blood from the first three victims!"},
                    {"text": "Check Bell banking and property records.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Bell was living as an ascetic recluse; money was irrelevant to his motive."},
                    {"text": "Formally clear Watchman Silas of murder charges.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Silas faces suspension for taking smuggler payoffs, but is cleared of all homicides."},
                    {"text": "Exonerate Father Thomas Vance.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Father Thomas is cleared of all suspicion."}
                ]
            },
            {
                "step": 6,
                "prompt": "Fingerprint analysis of the bronze clockwork gear 'IV' yields a full thumbprint match.",
                "options": [
                    {"text": "Dust the polished gear teeth for latent fingerprints.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Jonas Bell left thumbprint is embedded in the jewelers rouge polish on the gear face!"},
                    {"text": "Test the aconite delivery vehicle.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Bell used antique silver tea cups to administer the poisoned tea to each lured victim."},
                    {"text": "Check Historian Croft alibi for the first three murders.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Croft was lecturing in London during the 2nd murder; 100% corroborated."},
                    {"text": "Confirm the 1901 church fire historical record.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Parish records confirm the 4 victims were indeed the corrupt councilmen who burned the church for insurance."}
                ]
            },
            {
                "step": 7,
                "prompt": "Jonas Bell legal advocate attempts to enter an immediate plea of insanity.",
                "options": [
                    {"text": "Counter insanity defense with meticulous 2-year planning documentation.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "The journal proves cold, calculated premeditation, engineering precision, and complete awareness of criminal illegality."},
                    {"text": "Interview the families of the four victims.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Families admit the dark history of the 1901 fire, but express relief that the serial terror has ended."},
                    {"text": "Secure the belltower catacomb entrance.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Tunnel sealed with steel reinforcement bars."},
                    {"text": "Document the clock striking mechanism.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Bell modified the strike weight tripwire to deliver maximum downward kinetic force at 12:00."}
                ]
            },
            {
                "step": 8,
                "prompt": "The four-count serial murder docket is finalized for the High Court of Justice.",
                "options": [
                    {"text": "Compile the four-count serial murder and domestic terrorism indictment.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Complete docket: lathe striations, aconite chromatography, journal confession, gear prints, secret tunnel map."},
                    {"text": "Formally clear Father Thomas, Watchman Silas, and Historian Croft.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "All innocent suspects formally exonerated by the magistrate."},
                    {"text": "Return the historic belltower to the parish trustees.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Parish conducts memorial service for the victims; clock tower cleansed."},
                    {"text": "Impound Jonas Bell workshop machinery into state museum archives.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Lathe and tools catalogued as criminal evidence."}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Jonas Bell stands in the dock of the High Court. The moment of final judgment.",
                "options": [
                    {"text": "Present the matched Swiss lathe striations, aconite bottles, and the fifth gear found on his bench.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Bell bows his head: 'The clock has run down. The gears of justice have ground their final turn.' He enters a full confession."},
                    {"text": "Ask if anyone in the parish aided him.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Bell smiles darkly: 'A true clockmaker works alone. None of them could understand the mechanism.'"},
                    {"text": "Review the timeline of the four full moons.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline proves the exact sequence across all four full moon executions."},
                    {"text": "Seal the formal investigation file.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The Clockwork Killer case file is officially signed, stamped, and closed."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who was the serial killer known as the Clockwork Killer?",
                "options": []
            }
        ],
        "true_culprit": "Jonas Bell",
        "true_solution": "Master horologist Jonas Bell sought vengeance for the 1901 church fire that killed his mother and sister, which was covered up by 4 corrupt aldermen. Using a proprietary Swiss lathe, he crafted inscribed brass gears, used a secret catacomb passage from his workshop, paralyzed each victim with aconite tincture, positioned them beneath the great bell at midnight, and left an inscribed gear in their hands.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    },

    # ── CASE 20: THE PERFECT CRIME: THE ILLUSIONIST'S LAST ACT ──
    {
        "id": "case_20",
        "title": "The Perfect Crime: The Illusionist's Last Act",
        "category": "Perfect Crime",
        "difficulty": "Master",
        "target_or_victim": "Alistair Black, Master Illusionist",
        "crime_scene": "The Water Chamber, The Grand Coliseum Theatre, London",
        "briefing": "In front of a sold-out audience of 3,000 people, world-famous illusionist Alistair Black was lowered handcuffed into a sealed 2,000-gallon water tank for his signature 'Immortal Escape'. When the red velvet curtain dropped 90 seconds later, the tank was shattered, the stage drenched in blood, and Black was dead inside the locked iron box with a poisoned steel stiletto through his heart.",
        "suspects": [
            {
                "name": "Morgana LeFay",
                "role": "Stage Partner & Master Illusion Architect",
                "public_story": "Stood at the front stage apron pulling the red curtain cord.",
                "private_secret": "Black was secretly married to another woman and planned to retire to Bermuda with all their illusion patents worth $25M.",
                "motive": "Rage, betrayal, and sole ownership of the world-famous magic brand.",
                "alibi": "Visible to 3,000 spectators on stage apron holding the curtain rope.",
                "weakness": "The release mechanism of the iron box was rigged with a pneumatic spring that fired the stiletto when the stage curtain fell.",
                "relationship": "Stage co-star and secret lover for 12 years.",
                "is_culprit": True,
                "is_liar": True
            },
            {
                "name": "Dorian Vance",
                "role": "Chief Stage Engineer & Rigging Master",
                "public_story": "Operating the hydraulic winch from the overhead catwalk.",
                "private_secret": "Black fired him earlier that afternoon for cutting corners on hydraulic safety lines.",
                "motive": "Revenge for career ruin.",
                "alibi": "Console telemetry confirms his hands were on the winch controls.",
                "weakness": "His toolbox contained spare cables and a missing solenoid valve.",
                "relationship": "Lead engineer for 8 years.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Silas Sterling",
                "role": "Rival Celebrity Magician",
                "public_story": "Sitting in Box Seat 1 in the dress circle watching the show.",
                "private_secret": "Hired an industrial spy to steal Black water escape mechanical schematics.",
                "motive": "Destroy Black reputation to become the premier magician in the world.",
                "alibi": "Surrounded by high-society guests and photographers in Box 1.",
                "weakness": "Had a duplicate water chamber blueprint hidden in his silk coat.",
                "relationship": "Bitter professional rival.",
                "is_culprit": False,
                "is_liar": True
            },
            {
                "name": "Inspector Felix Drake",
                "role": "Private Bodyguard & Former Detective",
                "public_story": "Guarding the stage wing backstage access door.",
                "private_secret": "Owed Black $150,000 in loan shark debt that Black threatened to enforce.",
                "motive": "Erase his crushing debt.",
                "alibi": "Backstage crew saw him standing by the door throughout the act.",
                "weakness": "Was seen arguing with Black in the dressing room 30 minutes before showtime.",
                "relationship": "Head of security.",
                "is_culprit": False,
                "is_liar": False
            }
        ],
        "clues": [
            {"id": "c20_stiletto", "title": "Pneumatic Spring-Loaded Stiletto Trap", "category": "Physical", "role": "Critical", "description": "The steel stiletto was not stabbed by human hands; it was loaded inside the false base of the iron box, triggered when Morgana pulled the curtain rope tension line."},
            {"id": "c20_patent", "title": "Secret Marriage & Patent Assignment", "category": "Circumstantial", "role": "Critical", "description": "Found in Black dressing room safe: marriage license to a secret wife and assignment of all illusion patents to her, cutting Morgana out completely."},
            {"id": "c20_blueprint", "title": "Stolen Escape Schematics", "category": "Physical", "role": "Red Herring", "description": "Found in Silas Sterling coat; stolen trade secrets, but Silas was sitting in Box 1 drinking champagne."},
            {"id": "c20_solenoid", "title": "Wireless Pneumatic Solenoid Receiver", "category": "Digital", "role": "Supporting", "description": "Concealed inside the iron box latch; triggered by a 433MHz micro-transmitter hidden in Morgana stage wand."},
            {"id": "c20_debt", "title": "Felix Drake Promissory Note", "category": "Circumstantial", "role": "Red Herring", "description": "$150k debt notice; Drake had motive, but physical evidence proves mechanical remote triggering."}
        ],
        "timeline": [
            {"time": "20:00", "event": "Show begins; Black and Morgana perform opening acts."},
            {"time": "21:15", "event": "Black enters dressing room; locks safe containing patent assignment."},
            {"time": "21:40", "event": "Black handcuffed and lowered into water tank; curtain raised."},
            {"time": "21:41", "event": "Morgana pulls curtain cord; triggers wireless 433MHz solenoid in box."},
            {"time": "21:42", "event": "Pneumatic stiletto fires into Black chest; water tank glass shattered by pre-set explosive squib."},
            {"time": "21:43", "event": "Curtain drops; stage in chaos; Black dead in pool of crimson water."}
        ],
        "messages": [
            {
                "step": 1,
                "prompt": "On the grand stage, 2,000 gallons of blood-tinted water flood the orchestra pit. Shattered acrylic glass covers the boards. Inside the iron escape box lies Alistair Black, impaled by a steel stiletto through the chest. 3,000 witnesses saw nobody enter the tank. Where do you begin?",
                "options": [
                    {"text": "Examine the base and locking mechanism of the iron escape box.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": "c20_stiletto", "feedback": "Under the velvet lining: a precision pneumatic spring mechanism! The stiletto was fired mechanically from inside the box itself!"},
                    {"text": "Search Alistair Black private dressing room safe.", "killer_delta": 2, "evidence_score_delta": 12, "unlocked_clue_id": "c20_patent", "feedback": "Safe holds a secret marriage certificate and legal paperwork transferring all $25M in magic patents away from Morgana!"},
                    {"text": "Interrogate rival magician Silas Sterling in Box 1.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c20_blueprint", "feedback": "Sterling has stolen blueprints in his coat, but 50 high-society witnesses swear he never left his seat."},
                    {"text": "Question bodyguard Felix Drake about his backstage row.", "killer_delta": -1, "evidence_score_delta": 5, "unlocked_clue_id": "c20_debt", "feedback": "Drake admits he owed Black money, but backstage crew confirm Drake never moved from the access door."}
                ]
            },
            {
                "step": 2,
                "prompt": "The pneumatic spring was triggered by a miniature radio solenoid hidden inside the iron box latch.",
                "options": [
                    {"text": "Scan the stage area for radio frequency transmitters operating on the 433MHz band.", "killer_delta": 3, "evidence_score_delta": 15, "unlocked_clue_id": "c20_solenoid", "feedback": "RF scanner detects a micro-transmitter hidden inside the silver tip of Morgana stage wand!"},
                    {"text": "Interrogate Chief Rigging Engineer Dorian Vance on catwalk controls.", "killer_delta": 0, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dorian winch cables are clean; telemetry proves he only operated the vertical hoist."},
                    {"text": "Search Silas Sterling limousine.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Limousine contains magic props and press kits; no radio triggering equipment."},
                    {"text": "Examine the water tank glass shards.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The acrylic was fractured by a miniature primer cord that ignited when the box pressure released."}
                ]
            },
            {
                "step": 3,
                "prompt": "Morgana stage wand is seized by forensic technicians. X-ray reveals a battery, microswitch, and transmitter coil.",
                "options": [
                    {"text": "Disassemble the silver tip of Morgana stage wand under magnifying microscope.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "The microswitch is connected to a slide mechanism: when she pulled the curtain cord, the switch closed and fired the stiletto!"},
                    {"text": "Confront Morgana with the secret marriage certificate and disinheritance papers.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Morgana eyes flash with fury: 'Twelve years! I built every illusion with my own blood and intellect! And he was going to discard me for a socialite!'"},
                    {"text": "Interrogate Dorian Vance about the pneumatic spring fabrication.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Dorian reveals Morgana ordered custom machine parts from an engineering shop two weeks ago without Black knowledge."},
                    {"text": "Examine Felix Drake service revolver.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Revolver unfired; Drake debt is handled through civil probate, cleared of homicide."}
                ]
            },
            {
                "step": 4,
                "prompt": "Machine shop invoices from South London confirm Morgana LeFay paid £4,000 cash for the precision spring-loaded piston assembly.",
                "options": [
                    {"text": "Subpoena the South London machine shop invoices and technical blueprints.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Blueprints drawn in Morgana distinct handwriting labeled 'Pneumatic Actuator - Project Bermuda'!"},
                    {"text": "Interrogate rival magician Silas Sterling regarding the trade secrets.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling is arrested for trade secret theft, but completely cleared of murder."},
                    {"text": "Check Dorian Vance toolbox.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Dorian tools were for stage winch maintenance; no match to the spring trap."},
                    {"text": "Review high-speed audience camera footage.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Footage shows Morgana thumb pressing the wand tip at the precise instant the curtain fell!"}
                ]
            },
            {
                "step": 5,
                "prompt": "Morgana claims Black rigged the mechanism himself for a dangerous publicity stunt that went catastrophically wrong.",
                "options": [
                    {"text": "Counter with the Curare paralytic poison coating the tip of the stiletto.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "Toxicology proves the blade was coated in deadly Curare poison; no illusionist would ever coat their own escape prop in lethal poison!"},
                    {"text": "Search Morgana hotel suite and dressing room.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Found a vial of Curare extract and correspondence with a South American botanical supplier."},
                    {"text": "Examine the water tank drainage valves.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Valves functioned normally; the death was instant from heart perforation."},
                    {"text": "Interview the stage crew who helped Black into the box.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Crew testify Black was relaxed and smiling, completely unaware of the hidden trap beneath the false floor."}
                ]
            },
            {
                "step": 6,
                "prompt": "DNA analysis of skin cells on the false bottom latch of the iron box matches Morgana LeFay.",
                "options": [
                    {"text": "Swab the hidden pneumatic mounting brackets for epithelial DNA.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Morgana DNA covers the mounting screws, the spring coil, and the radio receiver casing."},
                    {"text": "Check if Dorian Vance helped install the box.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Dorian was barred from touching the magic props; Black and Morgana maintained sole access."},
                    {"text": "Examine Black secret wife statement.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The wife confirms Black lived in mortal fear of Morgana discovering their marriage."},
                    {"text": "Review the curtain rope tension telemetry.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Tension was rigged so the curtain drop masked the sound of the pneumatic piston firing."}
                ]
            },
            {
                "step": 7,
                "prompt": "Morgana legal team realizes the physical trap, wand transmitter, machine shop blueprints, Curare vial, and DNA form an inescapable net.",
                "options": [
                    {"text": "Present the machine shop blueprints, wand transmitter, Curare vial, and DNA match to Morgana.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Her lawyer turns to Morgana and whispers: 'There is no defense in English law that can save you from this.' Morgana posture crumbles."},
                    {"text": "Confirm the timeline of the 90-second illusion.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The 90-second window was engineered down to the tenth of a second for maximum theatrical impact."},
                    {"text": "Formally clear Dorian Vance and Felix Drake.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Both stage professionals are fully cleared and exonerated."},
                    {"text": "Impound the water chamber apparatus into Scotland Yard custody.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "The lethal magic prop is sealed in the Black Museum of Scotland Yard."}
                ]
            },
            {
                "step": 8,
                "prompt": "The case docket for Premeditated Capital Murder in the First Degree is finalized.",
                "options": [
                    {"text": "Compile the comprehensive capital murder indictment against Morgana LeFay.", "killer_delta": 3, "evidence_score_delta": 14, "unlocked_clue_id": None, "feedback": "The ultimate murder indictment: pneumatic trap, 433MHz wand, handwriting match, Curare poison, disinheritance motive."},
                    {"text": "Release Silas Sterling to face civil intellectual property charges.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Sterling faces copyright litigation; cleared of murder."},
                    {"text": "Deliver Alistair Black will to the High Court of Probate.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Black estate and patents transferred to his lawful widow."},
                    {"text": "Conduct final debriefing with the Metropolitan Police Commissioner.", "killer_delta": 1, "evidence_score_delta": 6, "unlocked_clue_id": None, "feedback": "Commissioner declares: 'The most baffling locked-room illusion in criminal history has been solved.'"}
                ]
            },
            {
                "step": 9,
                "prompt": "Turn 9: Morgana LeFay stands before the Old Bailey magistrate. The final curtain has fallen on the Illusionist's Last Act.",
                "options": [
                    {"text": "Demand formal plea from Morgana LeFay before the court.", "killer_delta": 3, "evidence_score_delta": 12, "unlocked_clue_id": None, "feedback": "Morgana smiles coldly through her tears: 'Alistair promised the audience the Immortal Escape. I gave them the only illusion he could never escape from.' She signs the confession."},
                    {"text": "Ask if Dorian Vance assisted with the mechanics.", "killer_delta": 0, "evidence_score_delta": 5, "unlocked_clue_id": None, "feedback": "Morgana sneers: 'Dorian is a stagehand. I was the architect of every miracle we ever performed.'"},
                    {"text": "Review the timeline of the grand illusion.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "Timeline matches every movement between 20:00 and 21:43 with absolute mechanical perfection."},
                    {"text": "Seal the master investigation docket.", "killer_delta": 2, "evidence_score_delta": 8, "unlocked_clue_id": None, "feedback": "The case of The Perfect Crime is officially solved, signed, and closed."}
                ]
            },
            {
                "step": 10,
                "prompt": "FINAL ACCUSATION: Who executed 'The Perfect Crime' and murdered Alistair Black inside the locked water chamber?",
                "options": []
            }
        ],
        "true_culprit": "Morgana LeFay",
        "true_solution": "Master illusion architect Morgana LeFay discovered her partner Alistair Black was secretly married and planned to flee to Bermuda with all their $25M patents. She engineered a spring-loaded pneumatic piston hidden inside the false base of the iron escape box, loaded it with a Curare-poisoned stiletto, disguised a 433MHz wireless transmitter inside her stage wand, and triggered the fatal shot at the exact instant she pulled the curtain cord before 3,000 spectators.",
        "rank_thresholds": {"S": 75, "A": 55, "B": 35, "C": 20}
    }
]
