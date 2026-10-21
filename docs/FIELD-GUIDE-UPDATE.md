# Thorns / Stem — Field Guide systems update

Version: Thorns 0.6.0 · Stem 0.5.0 · ruleset `field-guide-1`

This update connects the Creature and Stat Guide to actual game actions, saves and interfaces. It supplies a shared numerical foundation for later Rose development. Each game remains independently runnable; Rose files are not changed.

## Start playing

Extract the entire game ZIP. Install Python 3.10 or newer and run `Start-Windows.bat`, or run the game's server from its extracted folder. Thorns uses port 8765; Stem uses 8776. New campaigns use the Field Guide automatically. In Thorns, choose **Open world grid** for field encounters and companions; the original voting chapter remains available.

Begin the expedition. The **FIELD GUIDE / SHARED RULES** panel shows active cycles, earned XP, Growth, pack bulk, material condition, the most recent check and its four exact outcome probabilities. Reading a panel or refreshing a page never creates a new encounter roll.

Travel through the existing map or use **SPEND A WATCH / 4 CYCLES**. A watch can be quiet, show evidence, or introduce a local encounter. Open each designation to read appearance, intent, present need, peaceful route, stats, stored attacks and specific narrative limits. A disposition is an opening, not a command to fight.

**BEGIN LOCAL TURNS** fixes initiative. Choose a target and approach until it is in range. Spend AP on a staff attack, registered crystallin shot, guard, passage offer, movement, field treatment or disengagement. Use **END TURN** when finished. Enemies act on their own turns; attacks do not cause an extra automatic counterattack. Incapacitated people are not treated as a material cache.

The record survives server restart, including spent ammo, remaining Health/Energy, weapon condition, actor identity, outcome rolls, companion agreements and whether salvage or a contract was already paid.

## Save compatibility

Existing SQLite databases remain valid and retain their previous rules until their host selects **ADOPT FIELD GUIDE 1.0**. This is an explicit campaign rules change. Original Thorns credit balances and previous inventories remain in old saves; the new rules do not award currency or convert those balances into materials. Previously earned XP is carried into the new earned-XP ledger. Character identity, route, conditions, completed history and active agreements remain recorded.

An old chapter should close its pending votes, encounter and training duel before adoption. New Thorns field play should begin in Open world mode. A carried Thorns survey without reserved provisions retains its destination and can close, but receives no invented provision escrow.

Back up the save database while the host is stopped before adopting. Thorns's desktop launcher uses the existing THORNS user-data folder and retains its old database migration behavior. Stem uses its existing Stem user-data folder. Keep room credentials and live save databases private.

## Shared numerical rules

| Component | Live behavior |
| --- | --- |
| Creation | Four attributes 1–4 totaling 8; six creation ranks across 25 proficiencies, each rank 0–3. Identity and affiliation grant no automatic permission. |
| Check | d20 + attribute + practice + earned-XP bonus + bounded context + standing + trust + attitude + trained support − conditions − fatigue. |
| Practice | Training plus one eligible registered tool contribution, combined maximum +2. A weapon does not grant an automatic tool bonus. Supporting equipment loses condition on use. |
| Experience | +1 per three **earned** XP, capped at +2. Spending Growth does not remove earned XP. |
| Context | −3 to +3; heavy loads affect movement. Native Stem actions also retain actual weather, shelter, disruption and infrastructure context. |
| Standing | Shared plus half personal standing, divided by five, truncated toward zero, capped at ±2. Standing remains within ±20. |
| Relationship | Trust 3+ gives +1; attitude 70+ gives +1 and below 30 gives −1. These never override an NPC's refusal or eligibility. |
| Support | At most two trained, ready, present NPCs; +1 each, with an actual energy cost and one support opportunity per action/owner turn. Combat support also spends the NPC's AP allowance. |
| Conditions | Combined penalty capped at 5. Energy below 25 applies −2 fatigue. |
| Grades | Natural 1: complication. Natural 20: strong. Otherwise margin ≥5 strong, ≥0 success, ≤−5 complication; remaining failures are setbacks. |
| Assured facts | Confirmed records, map/inventory review, route planning and voluntary dismissal do not require a permission roll or award XP. Dialogue checks can affect uncertain elaboration. |

For example, +4 against DC 12 has 65% success overall: 15% complication, 20% setback, 25% ordinary success and 40% strong. The interface enumerates the twenty possible faces rather than approximating these percentages.

## Progression

A meaningful resolved situation can award XP once. Repeating the same local gathering, repair, study or resolved encounter does not create another award. An introductory contract awards up to 2 XP within the ordinary cap, replacing a separate ordinary award for its completion.

The host declares session boundaries. Ordinary awards are capped at 3 XP per session; the host may record one additional agreed goal XP for each character. Session controls are a group bookkeeping responsibility, not automatic elapsed-time rewards.

Every three earned XP provides one Growth. Spend one Growth for a skill rank, maximum 3. Spend two for an attribute point, maximum 4 and total attributes maximum 10. Rank-3 mastery can soften one complication to a setback per session. It preserves failure and does not refund resolved damage, AP or supplies.

## Encounter generation

`creature_catalog.json` contains all 48 guide profiles, including people, wildlife, machines and exposed hazards. Original numerical profile values remain intact; variants are separate encounter instances. Each instance has a saved site/watch identity and persists after refusal or resolution.

The nine weighted habitat tables remain available in the shared module. Thorns and Stem select only the Fourth Corners tables. Woodland and Vines approaches can use the shellwood table; an explicitly named ArK approach can use the ArK table. Darkwood is not interpreted as the ArK. Long Tar and mundane Spirit Rush tables are retained as reference data and do not spawn through these games' ordinary geography. RED>GATE> and unverified remote projections remain boundaries.

One shared encounter opportunity belongs to each four active-cycle watch. Ordinary watches have a 2-in-6 opportunity, sheltered watches 1-in-6, disrupted ground 3-in-6. The profile uses twelve weighted tickets; two d6 select a uniformly distributed ticket. A 2d6 variant chooses depleted, typical or reinforced; desired group size is d3, capped at three and by budget. Disposition uses a separate 2d6 roll. Dice receipts preserve the procedure.

Normal budgets for one through six present PCs are 2, 3, 4, 6, 7, 9. NPCs in this release assist rather than taking independent attack turns. The guide's planning costs use the maximum of nominal threat, a fixed staff-effort estimate and a fixed incoming-pressure estimate. They are pacing heuristics, **not** measured full-fight victory odds. A profile over budget produces evidence, not an automatic reroll. A reinforced variant that cannot fit falls back to its typical profile, recorded explicitly.

The saved seed, roll counter, labels and scene state reproduce a continued campaign's rolls. Authentication tokens remain generated independently. This is a cooperative deterministic simulation, not a cryptographic dice service. Public map seeds are not secrets.

## Local tactical encounters

| Action | AP / cost |
| --- | --- |
| Hidden-hex step toward/away from the selected target | 1 AP |
| Field-staff attack | 3 AP; Body/transversal; range 1 |
| Crystallin shot | 4 AP; Body/ballistics; range 6; issued registered retrofit and one actual scrap per attempt |
| Guard | 2 AP; Body/fieldcraft DC 10; +2 until next own turn, combined context cap +3 |
| Passage offer | 3 AP; an offer can be refused |
| Medkit treatment | 3 AP, spend one medkit before the check |
| Disengage | 1 AP; Body/transversal DC 11 |
| End turn | 0 AP, no roll |

PC AP is 8 + min(2, Body // 2). Initiative is Body + Percept + d6 − 1, with Percept then Body as ties. Compact profile initiatives remain explicit data. Each foe spends its own AP, movement, attack limit and finite ammo. Anchored targets do not move. Actors use an invisible axial hex grid for local distance; the existing overworld map remains a separate travel system.

Staff base damage is 6 + Body; crystallin base damage is 9 + Body. Apply the weapon's material-condition factor first, floor it, add +2 for strong, then subtract armor capped at 5, minimum zero. A miss still consumes shot material and 2 weapon condition. Energy-channel attacks affect Energy directly and do not use Health armor or rewrite memories. Ordinary zero Energy causes fatigue, not an automatic generic stun.

Morale is checked once at the first half-Health threshold. Natural 1 holds and 20 withdraws. Withdrawn actors retain their possessions. Active guard companions may take up to three incoming Health damage once per round at a 2-Energy cost, conserving the total hit rather than erasing it.

Combat actions pause participants' ordinary survival cycles. Closing a battle applies one shared concluding cycle, with personal costs only to its participants. The existing local field-station rescue policy is retained for incapacitation; the game does not add a universal resurrection power. A departing seat no longer strands the active turn. Targeted body-part attacks, detailed cover/opaque scenery, manual reload/draw states and a selectable permadeath mode remain future tactical extensions; their narrative references are not presented as implemented controls.

## Survival, companions and materials

One personal active cycle costs 3 Energy, adds 4 thirst, 2 hunger and 3 sleep debt, with the existing registered regulator exception. Thorns still offers its Standard/Hardcore choice: Standard omits needs damage; field Energy, time and item costs still apply. Needs at 90+ and existing ailments retain their real damage costs. Idle seats do not inherit another player's needs costs.

Eat/drink spend one actual matching item and one cycle, then reduce the matching need by 45 on success or 35 on failure and add 8 Energy. A sheltered breather takes one cycle, restoring 35 Energy/8 Health on success or 25/4 otherwise and reducing sleep debt by 10. Full rest reserves one food and water, takes four safe cycles and restores Energy to 100, sleep debt to zero, reduces hunger/thirst by 45 and adds 25 Health. A defensive arrival can interrupt full recovery without refunding the consumed reservation. Field treatment spends its medkit first; success restores 25 Health and removes one condition, with the strong bonus applied separately. Vitals clamp to 0–100.

Two voluntary NPC agreements are supported across the party, normally one or two alongside a person. Existing larger Stem rosters are preserved on adoption; new recruitment respects the party cap. NPCs retain their full build, own supplies, lore, goals, limits, attitude, history and issuer relationships. Readiness includes Health 35+, Energy 15+, attitude 30+, a present route, an appropriate phase, training and issuer standing. Stem's designation also checks delivery provisions. An offer transfers one food/water only on acceptance; failure waits four cycles before reconsideration. Dismissal remains voluntary and free.

Support costs 2 Energy instead of the usual 1 for that active cycle, rather than adding an invisible free bonus. Six personal active cycles consume the companion's own food and water. Missing rations cost Energy and attitude. Stem retains its autonomous Observe → Plan → Work → Reflect → Recover infrastructure and actual-input work; Thorns now carries a smaller persistent companion cycle with support, guard and rest scopes. Thorns does not yet have Stem's full NPC business/task scheduler.

Personal equipment has an identity, material, condition and operating threshold. Sound is 60+, worn 30–59, fractured 1–29 and ruined 0. The damage factors are 1, 0.8 and 0.55. Exposed cloaks age on watches; packed tools avoid ordinary ambient aging. Stem weather contributes wet/storm exposure. Repair spends one scrap and one cycle, Tech/metallurgy DC 11, adding 25 condition on success. Ruined items require a sheltered replacement: two actual material units and a check, creating a new ID and retiring the old object. Failed work spends its inputs.

Salvage from a disabled non-person encounter uses the recorded finite exposed-component budgets and pays once for the scene. A peaceful agreement, a person's incapacitation, or a withdrawal does not yield an invented cache. Whole monoliths and immutable institutions are never reduced to an ordinary creature's Health bar.

## Scope and source boundaries

The Fallout, Cyberpunk, Night City and Shadowrun references inform legibility, roles, districts, explicit powers and statistical presentation. They do not replace the world's own d20 rules, currency conventions, characters or geography. No reference-book scans or OCR dumps are added to the game packages.

Some profile-specific instructions remain authored context for the peaceful route and narrative adjudication; they are visible alongside the fully active HP/AP/range/armor/ammo/morale rules. This release is a bounded text adventure with the existing CRT presentation and maps. It does not claim new hyper-realistic sprites, a complete physical world simulation, validated particulate measurements or a finished Windows executable. VREX/physics internals are not exposed as player measurements. Existing source drawings and presentation assets remain in place.

See `FIELD-GUIDE-VALIDATION.md` for test coverage and practical limits.
