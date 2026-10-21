# 0.5.0 — Field Guide systems integration

Added the guide's catalog, bounded seeded encounter generator, graded checks with exact odds, AP combat, finite ammunition/salvage, earned-XP progression, material wear/repair/replacement and companion support costs. Added an integrated field interface and host-controlled legacy-save adoption. Preserved map assets and existing character/history data. Fixed departing-seat combat turns and post-Growth reconnect behavior. See FIELD-GUIDE-UPDATE.md and FIELD-GUIDE-VALIDATION.md.

# 0.4.0 — 2026-10-18

- Share a stable regional content grammar across Thorns, Stem and Rose.
- Persist dialogue variation and bounded local witness memory.
- Keep source character histories, supplies and access under existing authority.
- Add regression checks for state fidelity and save compatibility.

# Stem release history

## 0.3.0

- Unified checks for every accepted game action, with skill, equipment, experience, conditions, local context, shared/personal reputation, contact trust/attitude, and trained companion support.
- Added up to two voluntary companion agreements per player, using the existing traveling NPC registry. NPC designation includes stable generated lore, attributes, skills, personal items and supplies, experience, health, attitude, faction engagement, contract readiness, and saved dialogue/work histories.
- Added lore/plans/contracts/factions/history/needs/attitude conversation, scoped tasks, shared/requested supplies, companion care, withdrawal, and five-stage autonomous engagement.
- Added finite field businesses, stock/reserve transfers, reputation/demand pricing, maintenance, and local-stock restocking.
- Added checked infrastructure inspection/operation, public relays, and bounded hostile-construct encounters with strikes, registered ballistics, guarding, companion defense, transit truces and adjacent disengagement.
- Added full companion profiles, task/supply controls, check history, shop ledgers, infrastructure and encounter panels. Expanded model context and validated NPC action catalogs.
- Preserved existing map layouts and identities. Source-character biographies remain documentary rather than receiving generated private histories.

68 Python tests and the expanded real-HTTP Node interface harness pass. Browser rendering and live model inference remain unverified.

## 0.2.0

Integrated THORNS-derived survival adventure and playable map conversion:

- Converted the two map photographs and document topology into 28 landmarks, terrain, river barriers, interpreted crossings, mountain approaches, woodland, dustland, and boundary observation. Added an interactive atlas with real stepwise routes, commitment targets, original photographs, and interpretation confidence.
- Added six disciplines, four customizable attributes, 25 proficiency records, and comprehensive identity, appearance, biography, voice, mannerisms, goal, boundary, and starting blueprint fields. Added draft/template tools and THORNS character-template import.
- Added persistent characterized custodians at every landmark, six dialogue topics, player descriptions carried into conversations, per-contact relationships, and a saved dialogue ledger.
- Added survey, delivery, restoration, and diplomatic commitments, once-only rewards, abandonment, 25 standing records, and personal care benefits.
- Added sleep debt, injuries, ailments, medkits, condition penalties, institution-specific care, WN_MED client relationships, and free CHECKPOINT.RESID provisions.
- Added bounded registration, eight equipment options, three installed slots, relevant proficiency effects, and local study.
- Expanded the optional local narrator context to the registered character and recent dialogue; reviewed model intentions can select mapped destinations, commitments, dialogue topics, and equipment.
- Preserved v0.1 geography, positions, and survey commitments in legacy saves. New worlds use the atlas.
- Increased Stem character-template and host request limits to 64 KiB, with a 10,000-character biography limit.

43 Python tests and the real-HTTP Node interface smoke test pass. Real-browser rendering and live local-model inference remain unverified. No THORNS files are replaced and no native installer is included.

## 0.1.0

First independent sequel prototype: seeded exploration, changing biome indices, shared autonomous clock, procedural sensory descriptions, persistent field traces, travelers, bounded intentions, optional local model prose, six-player rooms, survival, habitat work, survey commissions, browser resume, and journal export.
