# Stem 0.3 — contextual checks and companion expeditions

This guide describes implemented behavior. All numerical values, generated NPC biographies, field businesses, hostile constructs and equipment effects are Stem adaptations.

## Shared interaction resolver

Each accepted game action produces at least one D20 check. Combat may also produce a counteraction check. Unsupported intentions and rejected prerequisites do not commit a turn or spend saved supplies. Session controls and character-template validation remain administrative operations.

The total is:

`D20 + attribute + min(2, training + equipment) + experience − conditions + fatigue + reputation + context + trust + attitude + companions`

| Component | Value |
|---|---|
| Attribute | Chosen Body, Tech, Percept or Rapport score |
| Training | Matching proficiency rating, capped at 2 |
| Equipment | Matching active registered mod contribution; combined with training at a cap of 2 |
| Experience | `min(2, XP // 3)` |
| Conditions | −1 per injury, ailment, and hunger/thirst/sleep index at least 70, capped at −5 |
| Fatigue | −2 when energy is below 25 |
| Reputation | `(shared issuer standing + half personal standing) / 5`, truncated toward zero, capped at ±2 |
| Context | Relevant situational factors, total capped at ±3 |
| Contact trust | +1 when this contact’s recorded relationship trust reaches 3 |
| Contact attitude | +1 at attitude ≥70, −1 below 30, otherwise 0 |
| Companions | +1 per eligible companion trained in the exact skill, maximum +2 |

Natural 1 fails; natural 20 succeeds. A successful margin of at least five, or natural 20, is marked **strong**. The interface exposes the roll, components, relevant faction, situational reasons, and the last eight checks. Up to 60 checks are saved per subject.

Field situations include night −1, exposed storm −2, instability below 35 −1, maintained shelter +1, a working field relay +1, and healthy growth above 65 +1 for selected habitat actions. Social situations use storm pressure −1 and local disruption −1. Combat guard can add +2 to its defensive counteraction check. Reputation on physical actions represents practical local support and route knowledge; it does not create clearance or override terrain.

| Interaction | Check and consequence |
|---|---|
| Dialogue | Rapport/community or teaching; elaboration, provisionality, attitude and relationship engagement |
| Companion lore | Percept/history; full narrated account or a briefer conversational account |
| Observation and records | Relevant Percept track; interpretation quality while confirmed indices, stock and route data remain readable |
| Movement | Body/transversal, DC 10 or 12 in exposed storms; ordinary setbacks cost 2 extra energy, storm setbacks can injure |
| Gathering | Percept/druid, Percept/resource or Tech/metallurgy, DC 10; withdraw real local supplies on success |
| Habitat work | Tech/fractech, druid or metallurgy, DC 9; costs are spent even when work fails |
| Contract acceptance | Rapport/contracts, DC 11; creates a commitment only when accepted |
| Contract fulfillment | Type-specific DC 10; all four families require successful acceptance of the submitted work or handover |
| Registration/mods | Bounded institutional prerequisites plus registration/integration checks; failed installation spends its materials |
| Business | Percept/resource review; Rapport/contracts purchases and consignments; Tech/metallurgy maintenance |
| Infrastructure | Percept/fractech inspection; Tech/fractech operation or construction |
| Combat | Transversal strikes, registered ballistics, fieldcraft defense, memetic transit protocol or transversal disengagement |
| Provision/rest/care | Preparation, rest quality or care handover; guaranteed eligible services preserve their policy |

Shared standing and personal standing are stored separately, each bounded −20 to +20. Completed contracts and successful work/aid update them. NPCs also have their own faction engagement records. A successful companion conversation can improve trust and attitude at most once per four cycles. A check cannot make an inventory number false, invent a road, force an NPC agreement, prevent voluntary dismissal, or replace an institutional prerequisite.

## Comprehensive NPC designation

Traveling NPCs are members of the same persistent actor registry that supplies migration and local provision behavior. New worlds start with two travelers at the field station. Later exploration can generate more, up to 24 roaming NPCs in the world. Named custodians remain at their institutions.

Every NPC receives a stable seeded designation. Traveling profiles include origin, pronouns, embodiment, discipline, eight attribute points, initial proficiency allocation, appearance, voice, mannerisms, a four-part biography, an unfinished personal question, goals, boundaries, items, health, energy, personal provisions/materials, experience, conditions, attitude, faction engagement, and engagement history. Source characters KHO, PYRI, PAMAN DAL and Lila retain document-based histories; they do not acquire a generated childhood or a confirmed sequel outcome.

The **Full Character Designation** is the readable profile. It reports readiness, preference, training and blockers for survey, delivery, restoration and diplomatic commitments. Health below 35, energy below 15, attitude below 30, or NPC standing with the current issuer at most −10 can block readiness. Delivery readiness also needs two food plus one water in the NPC’s own pack. This readiness describes support capability; the player still carries and fulfills the accepted player contract.

Items such as keepsakes contribute to characterization and do not grant a permission. The field staff supports the ordinary encounter action. Credentials and installed equipment are separately recorded; NPCs do not start with administrator powers.

## Voluntary recruitment and shared work

Each human player can retain up to two NPC agreements. An NPC can have only one current owner/leader, and must be physically present for recruitment, dialogue, assignments, transfer or treatment. Use its displayed name or designation ID; duplicate names require an ID.

Recruitment uses Rapport/community DC 11 and offers one food plus one water. On success, those supplies transfer into the NPC’s actual pack. Failure transfers nothing, lowers attitude by one, and starts a four-cycle reconsideration wait. Attitude below 30 or health below 35 prevents recruitment. The maximum is enforced by the host, including multiplayer requests.

Companions follow successful physical movement and remain in place when a route is merely planned. Matching training contributes +1 to a player check when the companion is alongside, willing, healthy, rested enough, and not in a recover phase. A moving companion can help from the departure sector as the group traverses the same connection. Each time-consuming action costs a companion one energy, or two when it contributed check support. Every six active expedition actions consumes one available food and one water from its own pack. Missing rations instead cost energy and attitude; background pulses do not deduct player needs.

Task proposals use Rapport/teaching DC 10. A failed proposal leaves the old task and slightly lowers attitude. Available tasks are support, survey, repair, forage, guard, mediate and rest. A support task chooses repair on weak local infrastructure when materials exist, otherwise a survey. Tasks do not grant teleportation, remote extraction, or unrestricted NPC authority.

**Share** transfers one real player item into the NPC pack; the community check affects engagement quality. **Request** asks for one item from the NPC’s pack at DC 11 and requires attitude at least 40. NPCs protect their final food/water ration. Both operations respect pack limits. **Care for** consumes a player medkit and checks Tech/medtech DC 10, restoring 30 companion health and resolving one condition on success.

Completed shared commitments can add one NPC issuer-engagement point. Shared successful habitat/provision work improves attitude. Abandoning a preferred commitment reduces companion attitude by three. Below attitude 20 an NPC can withdraw during its next engagement update. Dismissal always releases the agreement; the handover check affects the exchange, not the right to release. The NPC retains its own items, biography and history and resumes local autonomy. Releasing a human seat also releases all its NPC agreements.

## Dialogue and engagement cycles

Seven companion topics cover lore, plans, contracts, factions, history, needs and attitude. Dialogue generates from the stable biography and voice, current task and cycle, attitude, faction records, local weather, previous conversations, work events and the player’s stated goal. It is state-driven procedural language, not an unrestricted conversational model.

Conversations append to the player’s registered dialogue ledger and the NPC’s last 40 conversations. The NPC retains the last 30 engagement events. Repeated free conversation does not award experience or fabricate work. Declared backstory remains stable as new shared events accumulate.

Every four shared cycles, each traveling NPC takes one engagement stage:

| Stage | Behavior |
|---|---|
| Observe | Record local weather, resources and habitat stability |
| Plan | Weigh task, supplies, attitude and the current physical sector |
| Work | Attempt one bounded local task using NPC stats and actual NPC/local materials |
| Reflect | Compare the latest record with the NPC’s enduring personal aim |
| Recover | Regain energy; shelter can support modest health recovery |

A normal circuit takes 20 cycles. Work attempts wait at least 12 cycles and require energy at least 15. An exhausted or injured NPC enters recovery. Repair spends one personal scrap for +8 local stability; foraging transfers one local food into the NPC pack and adds disturbance. Mediation can add one personal NPC faction-engagement point. Survey and guard record local observations. Successful non-rest work can advance NPC experience, with the same bounded experience contribution to checks. Work cannot complete a player restoration contract on its own; that contract retains its player-work requirement.

Unrecruited actors also consume available local provisions on six-cycle intervals and can migrate among discovered neighboring cells on eight-cycle intervals. Recruited NPCs follow the leader instead. Named source custodians remain anchored.

## Finite businesses

A mapped trade, craft, mod or registration waypoint offers a field exchange. Stock begins with 4 food, 5 water, 2 seeds and 2 medkits, plus a six-scrap reserve. These are explicit prototype inventory, not a canonical universal economy.

| Good | Base purchase cost | Sale payment |
|---|---:|---:|
| Food | 1 scrap | 1 scrap |
| Water | 1 scrap | 1 scrap |
| Seed | 2 scrap | 1 scrap |
| Medkit | 3 scrap | 1 scrap |

Purchase costs add demand, subtract one at combined standing at least 10, or add one at combined standing at most −5; prices never fall below one. Rapport/contracts DC 10 governs buying and selling. Success transfers actual stock and scrap reserve; failure transfers neither. Packs cap at 99, shop stock at 20 for accepted consignments, and reserves at 999. A shop cannot pay money it lacks.

Maintenance spends one player scrap and checks Tech/metallurgy DC 11. Success restores 15 business condition, awards 1 XP and one faction standing. Failure spends the material. Every 12 cycles the exchange reviews weather and maintenance, loses one condition or three in storms, and marks demand high during storms or below condition 35. A functioning shop draws at most two food/water units each from actual local stocks toward eight in stock. It does not create medkits, seeds, scrap or portable infinite provisions. Its last 30 ledger entries persist.

## Infrastructure and combat

Inspection reports the accessible feature, stability, shelter, field relay and water stock. Tech/fractech DC 11 operates an accessible water apparatus, transferring one real local water and reducing disturbance by two on success. Relay construction spends three scrap, checks DC 13, and adds one relay level on success, maximum two; a maintained relay contributes +1 local field context. Neither operation confers administrator access.

One fifth of eligible generated unsheltered sectors can contain a hostile maintenance construct. Named landmarks and institutional interiors are not ordinary combat targets. The entity has persistent health, defense, counteraction difficulty, damage, intent and resolution state. It acts in response to player encounter turns, not by attacking an unattended tab.

A field-staff strike checks Body/transversal against defense 12 and deals `6 + Body` damage on success. A ranged crystallin shot requires bounded black.dot registration and an installed retrofit, costs one scrap charge, checks Body/ballistics, and deals `9 + Body` damage. An unresolved construct counters at Body/fieldcraft DC 11; a failed defense normally costs seven health. Guard checks DC 10 and can give +2 counteraction protection and reduce incoming damage by three. A ready companion assigned guard can share up to three damage, paying its own health and energy.

A Rapport/memetic DC 13 transit protocol can produce a truce without cache loot. Body/transversal DC 11 disengagement moves to one legal neighboring sector, cancels the route, and leaves the unresolved construct behind. Walking or disengaging into costly terrain applies its normal survival cycles. A disabled construct pays at most two scrap once and 1 XP; a truce pays 1 XP. Resolution also records one regional standing. NPC/player attack targets are rejected by this encounter system.

The existing field-station recovery rule applies to players. A companion at zero health withdraws from active support into a recovery state; this prototype does not implement permanent companion death.

## Persistence and scope

Everything described here lives in the existing SQLite world save. Character templates still import creation choices only. Existing maps and player positions are preserved on load, and existing eligible NPCs receive a stable designation. New worlds guarantee the opening pair; legacy saves may begin with fewer nearby travelers.

68 Python tests and the real-HTTP interface harness verify the implemented paths. The harness is not a browser renderer. Real-browser layout, Windows launch, human balance, multi-device networking and live local-model inference still need playtesting. Optional local-model scene prose receives bounded companion lore/status, while action interpretation receives the current NPC catalog and remains subject to engine checks and explicit review.
