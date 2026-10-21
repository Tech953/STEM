# Stem 0.4.0 — shared content refinement

Stable regional surface descriptions, player-specific dialogue variation and local witness memory now share one generation module with Rose. Ask residents or companions about history after local work to hear their recorded observations. Read [the systems update](CONTENT-GENERATION-REFINEMENT.md) for controls, source boundaries, save behavior and verification.

# Stem

**A standalone THORNS sequel prototype · version 0.3.0**

Stem is a survival text adventure in a persistent, changing biome. This release adapts THORNS’s character creation, checks, contracts, reputation, regulated bio-mods, dialogue records, and survival needs into an explorable interpretation of the supplied map photographs. The map shapes affect movement; the photographs remain accessible inside the game. Every game interaction now resolves a skill, context, reputation, and support check. Up to two traveling NPCs can join each explorer’s expedition.

Stem remains a separate project. No THORNS game files or saves are replaced, and no particular THORNS ending is assumed.

## Start playing

**Windows:** Install Python 3.10 or newer, extract the package, and double-click `Start-Windows.bat` inside the `stem` folder. The launcher opens **http://localhost:8776**. Keep the console window open while playing. The launcher pauses if startup fails so its error remains visible.

**Linux/macOS:** Run `python3 server.py` or `./start.sh` inside `stem`. No third-party Python packages are needed.

Enter a name and select a discipline. Open **Comprehensive Character Creation** before entering the field. You can customize appearance, pronouns, embodiment, origin, affiliation, affinity, age description, biography, voice, mannerisms, goals, boundaries, attribute allocation, proficiency training, and a starting bio-mod blueprint. Six discipline presets provide starting allocations; you can redistribute them within the displayed budgets.

Create a world, optionally with a seed, or join an existing room code. One host supports up to six explorers. The host selects **Begin World** when the initial group is ready. Character editing locks when the expedition begins; late joiners create their character before joining.

Your character is registered with your seat. Conversations throughout the map record the character description that accompanied them, and local contacts remember prior conversations and trust. The character sheet, dialogue ledger, accepted commitment, completed contracts, equipment, conditions, and route survive a host restart.

## First crossing

The opening field station is at **The THORNS Encampment**. Try:

```text
ask about place
ask about history
accept delivery contract
go to commitment
travel next
look
eat
drink
rest
```

Repeat **travel next** to walk the planned route. Inspect the destination and use **fulfill** when the commitment’s conditions are met. Delivery requires two food and one water; keep enough to reach the target. Survival costs also apply to contract acceptance and fulfillment.

Open **World Route Atlas** to inspect the interpreted geography, choose any of 28 named destinations, and plan a route. Gold points identify landmarks, an orange ring identifies your commitment target, and the player marker shows your current sector. Planning does not move you. The **Travel Next Sector** button follows one physical connection at a time. Manual compass movement cancels the route. Mountain paths, woodland, and dustland cost two cycles per ordinary sector; landmark approaches cost one. Rivers and northern water block movement except at interpreted crossings. RED>GATE> remains a barrier.

The atlas includes the landmark’s description, services, source, and interpretation confidence. Its **Inspect the source drawings** section opens both original photographs. Read `MAP-CONVERSION.md` for what was read from the images, what came from the world documents, and what was inferred for playability.

Other supported intentions include:

```text
I inspect the habitat.
I collect water.
I forage.
I salvage.
I repair the habitat.
I plant a seed.
I build a shelter.
I talk to the traveler.
I negotiate a trade.
I help the traveler.
I accept a restoration contract.
I abandon contract.
```

## Characters, services, and commitments

Use **Body / Tech / Percept / Rapport**, totaling eight points, with up to six proficiency points across 25 tracks. Twenty-three tracks participate in checks or bounded study, including registered crystallin ballistics. Necra-mod theory and Life String extraction remain records only. The displayed result shows attribute, training, equipment, experience, conditions, situational modifiers, faction standing, trust, attitude, and companion contributions. Conditions include weather, night, shelter, terrain stability, and maintained infrastructure.

Every named landmark has a persistent local custodian and six dialogue topics. Roaming travelers inhabit generated sectors and can also be addressed when present. Conversations use your recorded identity, appearance, voice, mannerisms, goals, boundaries, and prior relationship. Their checks affect elaboration and engagement while preserving confirmed records. This is authored, state-driven dialogue with a persistent ledger, rather than an unrestricted conversational model.

Contract boards offer survey, delivery, restoration, and diplomatic introduction commitments. Their rewards affect supplies, experience, karma, faction standing, and a personal care benefit. You may abandon a commitment at a standing and karma cost. WN_MED’s desk offers a delivery commitment that establishes a care relationship when completed. CHECKPOINT.RESID supplies pilgrims freely and provides a free care waypoint.

Visit **The Arcturion** or **Black.Dot Outpost** to register a bounded field scope. Registration costs one scrap and activates your selected starting mod blueprint. Verified mod exchanges support eight equipment options and three slots; later installations cost two scrap. Stated affiliation and training do not grant administrator clearance.

Monitor health, energy, thirst, hunger, sleep debt, injuries, and ailments. Eat, drink, and rest in shelter. **Treat** spends a medkit and attempts field care; **clinic** uses an eligible care service. Exposed storm setbacks can cause injuries and irritation. At zero health the prototype returns you to the field station, retaining inventory and unresolved conditions. It has no permadeath.

## Companion expeditions

Open **Companions / Shared Work** to review nearby travelers. Two actual NPCs begin at a new world’s field station, with more found through exploration. Open a traveler’s **Full Character Designation** to read their origin, pronouns, embodiment, biography, attributes, training, voice, mannerisms, goals, boundaries, personal items, pack, experience, attitude, faction standing, and readiness for each commitment type.

Recruitment uses a Rapport/community check and offers one food plus one water. Failure leaves those supplies in your pack; that NPC waits four cycles before reconsidering. Each player may recruit at most two NPCs, and each NPC belongs to only one current agreement. Named institutional custodians retain their duties rather than becoming expedition recruits.

Recruit using the displayed name or designation ID. Example commands, substituting an actual name:

```text
recruit Sela Brace
speak with Sela Brace about lore
speak with Sela Brace about contracts
task Sela Brace repair
share Sela Brace water
request Sela Brace medkit
care for Sela Brace
dismiss Sela Brace
```

Buttons provide these actions without typing names. NPCs follow your actual movement, contribute relevant trained support, use their own materials for autonomous work, and retain their histories after dismissal. Tasks include support, survey, repair, forage, guard, mediation, and rest. Attitude, injuries, exhaustion, provisions, and faction conflicts affect their availability. Unwilling companions can withdraw, and an NPC protects their final food/water ration from supply requests.

Their generated biography remains stable. Dialogue assembles that history with the current task, attitude, engagement phase, weather, prior conversations, completed work, and your character’s goal. A five-stage engagement cycle runs alongside ecological time: observe, plan, work, reflect, recover. Personal rations are consumed after active expedition actions; unattended pulses do not starve the player.

## Businesses, infrastructure, and encounters

Mapped trade/craft/mod/registration sites have finite field exchanges. Review **Local Business**, buy or sell food, water, seed, and medkits, or maintain the exchange. Prices respond to faction standing and demand. Checks resolve transactions; failed purchases transfer nothing. Restocking draws from actual local supplies, and the ledger persists.

Inspect public infrastructure, operate an accessible water apparatus, or build a field relay. Successful operation transfers real local water, while relay construction spends three scrap and can fail. A maintained relay supports later local field checks. Existing habitat repairs, planting, and shelter construction use the same contextual resolver.

Generated unsheltered sectors may contain hostile maintenance constructs. The encounter panel exposes their condition and intentions. Strike with a field staff, guard, propose a transit truce, disengage to an adjacent sector, or use a registered crystallin retrofit for ranged work. Guard companions can share actual counteraction damage. Encounters retain their resolution and cannot repeatedly pay a cache reward.

Read `SYSTEMS.md` for the complete check formula, companion cycle, business economy, infrastructure, and combat rules.

## Generation and autonomy

Procedural generation works offline without a model. The map fixes named places and broad terrain. A world seed generates local features, vegetation, accessible stocks, traveling residents, and evolving biome conditions between those anchors. Descriptions combine material, weather, scent, sound, vegetation, construction, inhabitants, and persistent player traces.

A running active world receives an ecological pulse every 30 seconds. Personal actions also advance shared time. Weather, moisture, growth, disturbance, stability, AETHER pressure, resources, fauna indices, and roaming travelers evolve under rules. Named custodians stay at their landmarks. Only discovered sites are simulated.

The atlas spans a 37-by-25 sector rectangle, including impassable cells. These are abstract sectors rather than measured distances. Legacy generated worlds retain their older coordinate bounds. Each host supports at most 100 saved worlds, six seats per world, 2,048 discovered sites, and 24 roaming travelers per world.

Automatic pulses and other players’ actions do not consume your personal hunger, thirst, sleep, or energy. The host can pause time. Rooms stop pulsing after five minutes without authenticated activity; an open game tab polls and keeps its room active. No offline catch-up occurs when the server is stopped.

Open prompt input recognizes supported intentions in ordinary sentences. It does not implement arbitrary natural-language physics. Unknown, negated, hypothetical, and chained intentions do not spend resources or time. Buttons expose the important actions.

## Multiplayer, templates, and saves

All explorers must connect to the same server. On a LAN, open `http://HOST-LAN-ADDRESS:8776` and join its room code. Internet play requires a separately reachable host or private network; no matchmaking or public deployment is included.

A browser holds a private seat token for resuming. **Disconnect / Keep Seat** preserves the character. **Release My Seat** removes it and transfers host authority if needed. Do not share browser session storage. Journal exports omit session tokens and retain the field record; they are not restorable world backups.

Save locations are `%LOCALAPPDATA%\Stem\worlds.sqlite3` on Windows and `~/.local/share/Stem/worlds.sqlite3` elsewhere. Stop the host before copying that database as a backup.

Character templates can be saved as local browser drafts or exported as JSON. The creator imports Stem v2 templates and THORNS v1 character templates. It imports the creation choices, not possessions, earned credentials, progression, or a THORNS world save. A character template file is limited to 64 KiB, and a biography to 10,000 characters.

Existing Stem v0.1 saves keep their original quadrant geography and positions. Their character records gain the new fields and survival needs. Existing survey commitments keep their original completion rules. Create a new world to use the converted atlas and its institutions; old sites are not silently remapped. Existing v0.2 NPCs gain their saved designation when loaded and can be recruited where eligible. Their identities and positions are preserved; newly created worlds guarantee the opening pair.

## Optional local model

A separately running HTTP chat-completions service can expand descriptions and propose a supported interpretation for unusual wording:

```text
python server.py --narrator-url http://127.0.0.1:8080/v1/chat/completions --narrator-model local
```

Use your service’s model identifier. The adapter accepts only loopback HTTP hosts and does not follow redirects. It sends the current scene, your registered character description, companion lore/status, and three recent conversations for prose, or your typed intention and action/NPC catalogs for interpretation. Tokens and other players’ private character records are not included. A model and inference runtime are not bundled.

Model prose is labeled with its observation cycle and is not authoritative. An interpreted action requires explicit review and a second click; the engine still checks its costs, geography, and permissions. A failed or absent model leaves procedural play available. Live inference with a real model remains unverified.

Other host options:

```text
python server.py --port 8777
python server.py --no-browser
python server.py --pulse-seconds 60
python server.py --db ./my-stem-worlds.sqlite3
```

This package contains source code and browser UI, not a native Windows EXE. Read `RULES.md`, `DESIGN-AND-LORE.md`, and `VALIDATION.md` for exact mechanics and tested scope.
