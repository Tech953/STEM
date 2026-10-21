# Stem v0.3 rules

Numerical scales, costs, route placements, and rewards are game adaptations.

## Creation and checks

| Discipline | Body | Tech | Percept | Rapport |
|---|---:|---:|---:|---:|
| Needlurgist | 1 | 4 | 2 | 1 |
| NanoClad Scout | 4 | 1 | 2 | 1 |
| Fractech Archivist | 1 | 3 | 3 | 1 |
| Seam Mediator | 1 | 2 | 1 | 4 |
| Metal-kin Artisan | 3 | 3 | 1 | 1 |
| Light Reader | 1 | 1 | 4 | 2 |

These are presets. Each attribute is an integer from 1 to 4; their sum must be 8. Proficiency ratings are 0 to 3, totaling at most 6. Identity fields include pronouns, age description, origin, embodiment concept, affiliation, affinity, appearance, biography, voice, mannerisms, goal, boundaries, and a selected mod blueprint. Choices are validated by the host, and character editing locks at expedition start.

There are 25 recorded proficiency tracks. All except necra and lifestring participate in current checks or study. Those two do not create necra practice, extraction, or resurrection actions. Ballistics is used by registered crystallin ranged encounters.

Every accepted game action produces a skill check. The resolver combines D20, the selected attribute, up to 2 combined proficiency/equipment points, `min(2, XP // 3)`, situational context, faction standing, contact trust/attitude, and up to two trained companion contributions. Conditions subtract up to 5, and energy below 25 subtracts 2. Natural 1 fails; natural 20 succeeds. Full component details and recent check history appear in the interface.

Shared faction standing plus half the player’s personal standing determines a reputation contribution: one point per five standing, truncated toward zero and capped at ±2. Context caps at ±3. Night, exposed storms, unstable ground, shelter, healthy growth, and maintained relays affect relevant field actions. Social contexts use local disruption and storm pressure; contact trust and attitude also matter. Physical standing represents local route knowledge and support, not new permissions. Read `SYSTEMS.md` for exact values and all new systems.

Gathering and submissions generally use DC 10; habitat work uses DC 9; ordinary movement uses Body/transversal DC 10 and exposed storm movement DC 12. Study uses its local proficiency at DC 11. Contract acceptance uses Rapport/contracts DC 11. Completion checks use Percept/percept for survey, Tech/resource for delivery, Tech/metallurgy for restoration, and Rapport/contracts for diplomacy, all at DC 10. Trade negotiation uses DC 12, and ordinary barter DC 10. Registration uses Rapport/contracts DC 10; installation uses Tech/needlurgy DC 11, removal DC 9. Treatment uses Tech/medtech DC 10.

Checks do not fabricate map connections, alter confirmed inventory, prevent voluntary dismissal, or withhold RESID’s documented free provision. For observation, recordkeeping, and guaranteed services, the outcome controls interpretation or engagement quality. For uncertain work and agreements, it controls success, costs, and consequences.

## Geography and time

New worlds use 28 landmarks in an interpreted map bounded by X −18 to +18 and Y −12 to +12. North decreases Y. Each connection is one abstract sector; coordinates do not establish canonical scale. Northern water, river channels except interpreted crossings, the outer map edge, and the RED>GATE> barrier block walking.

Route planning chooses a shortest route by number of sectors, not a least-cost route by terrain or weather. It spends no time and does not move you. **Travel next** walks one connection, applying ordinary movement costs. Manual compass movement cancels the planned route. **Go to commitment** plans to its exact target, including a restoration sector beside a landmark.

Ordinary mountain, woodland, and dustland sectors cost two personal/shared cycles per step. Other sectors and named approaches cost one. Physical movement does not grant entry to restricted institution interiors; GRAVESITE and PEAK labels identify exterior boundaries.

Look, inspect, listen, inventory, map, dialogue, companion conversation/dismissal, route planning, abandonment, business review, infrastructure inspection, free RESID provision, remote observation, and return cost no personal cycle. Chat does not advance time. Other supported actions cost one cycle unless movement terrain specifies two. Unsupported intentions and rejected prerequisites spend nothing in saved state.

## Provisions, habitat, and trust

Start with 4 food, 5 water, 3 scrap, 2 seeds, and 2 medkits. Pack provisions and materials cap at 99. Gathering takes up to two units from actual local stock on success, increases disturbance, and grants 1 XP. Food harvesting also reduces growth. Failure takes time without obtaining stock.

| Work | Cost | Successful effect |
|---|---|---|
| Repair | 1 scrap | +18 stability, −12 disturbance |
| Plant | 1 seed | +16 growth, −4 moisture |
| Build shelter | 2 scrap | +1 shelter strength, maximum 3 |

Materials are spent even if the work check fails. Successful work gives 1 XP, 1 karma, and 1 regional standing. Work stops at the implementation’s condition limits; repeated work cannot exceed bounded indices.

A successful negotiation offers one exchange of two food or water for one scrap, lasting five cycles; a contact reconsiders at most once per six cycles. A present contact can barter one scrap for food, water, or seed. Food and water use local stocks; seed barter uses local growth. Giving a contact one needed unit improves shared local stock, personal relationship trust, contact trust, and karma. A successful engagement check also improves that contact’s faction standing. Provision aid is available at most once per four cycles for that contact. Trust caps at 5.

Each landmark has a persistent designated custodian. Traveling NPCs also have full designation and may enter companion agreements as described in `SYSTEMS.md`. Six dialogue topics cover place, routes, needs, commitments, history, and access. Named custodians keep their positions; procedural travelers may move. The last 200 dialogue records preserve place, speaker, topic, response, and relevant player characterization. Relationships persist by contact ID. The UI shows the most recent 12 conversations. This ledger is bounded memory, not unlimited retrieval or free-form model dialogue.

## Commitments and institutions

Only one commitment may be active per player. A local board offers four types; WN_MED’s desk offers delivery only. Targets rotate among nearby mapped survey destinations, with restoration normally placed in an adjacent generated sector.

| Type | Completion requirement |
|---|---|
| Survey | Reach exact target and pass Percept / percept check |
| Delivery | Reach exact target, pass Tech/resource handover check, and surrender 2 food plus 1 water |
| Restoration | Reach exact target, pass Tech/metallurgy acceptance check, and complete a successful personal repair there; stability ≥90 and growth ≥75 also qualifies |
| Diplomacy | Reach exact target and pass Rapport / contracts check |

Use **fulfill**; **survey** also submits a mapped commitment. Every completion type requires its check; failure keeps the commitment open. Delivery provisions are surrendered only on successful handover. Success pays 2 food, 2 water, 1 seed, 2 XP, +2 karma, +2 issuer standing, and one personal care-benefit tier, capped at 3. Completion removes the active commitment so it cannot pay twice. Completed history retains the last 60 commitments. Make room for reward stocks before submission.

**Abandon contract** removes the commitment and costs 1 issuer standing and 1 karma. Karma is personal, bounded −100 to +100; standing is shared, bounded −20 to +20. There are 25 faction/relationship standing records. Standing does not substitute for institutional clearance.

Successful registration at the Arcturion or Black.Dot Outpost costs one scrap and grants bounded black.dot and Merc Tag field records. It activates the selected starting blueprint, if any. Mod exchanges require that registration, allow three installed slots, and charge two scrap for a later installation attempt; failed integration spends those materials. Removal requires its check, consumes a cycle, and does not refund prior materials.

Eight options exist: LEG|SPIKES, Meta-Fingers, Corded Bio-Glass, Crystallin retrofit, survey lens, filter graft, rest regulator, and resonance link. The last four are new Stem equipment interpretations. Their effects are limited to listed check contributions, filtered storm protection, or reduced sleep accumulation. They do not enact unrestricted source-world powers.

## Survival and care

Each personal cycle consumes 3 energy, adds 4 thirst, 2 hunger, and 3 sleep debt. An active registered rest regulator reduces the sleep increase to 2. At an index of at least 90, each of thirst, hunger, and sleep causes 4 health damage per cycle. Each ailment causes one additional health damage. Automatic pulses and other players’ actions do not charge these personal costs.

Eating or drinking consumes one matching provision, reduces hunger or thirst by 45 on a successful preparation check or 35 on a setback, and adds 8 energy before the normal cycle cost. Rest requires shelter and a Body/fieldcraft DC 8 check, restoring 35 energy and 15 health on success or 25 energy and 8 health on a setback, and clears sleep debt before its one-cycle cost; ordinary rest therefore leaves sleep at 3.

A failed exposed storm crossing costs 8 health and records a strained leg. Without an active registered filter graft, it also records particulate irritation. Duplicate named conditions are not stacked.

Field treatment consumes one medkit. A successful medtech check restores 25 health and removes one injury, or one ailment if there is no injury. Failure spends the medkit. Clinic care clears recorded conditions and restores health, then applies the usual personal action cost; it does not supply food, water, or sleep. Its handover check can add five energy on success; basic eligible clinic treatment still occurs.

FOOTHILL CUSP and CHECKPOINT.RESID have care services. RESID care is free. Other care costs `max(1, 3 − care benefit tier)` scrap. WN_MED additionally requires the care relationship earned by completing its own desk’s delivery commitment. Free RESID provision clears hunger and thirst, bringing carried food to at least 4 and water to at least 5; it does not grant a portable infinite stock.

Zero health returns you to the world’s field station with health and energy 40 and needs 35. Inventory, injuries, and ailments remain. Projection and planned route are canceled. This prototype has no permadeath.

## Ecological autonomy and legacy saves

Day phases rotate in six-cycle blocks and seasons every 96 cycles. Weather changes in four-cycle blocks. Rain, dryness, neighbor conditions, disturbance, and AETHER influence moisture and growth. Healthy growth supports stability and resource renewal. Storms stress exposed structures; shelter wear can occur every 24 cycles. An abstract fauna index responds to habitat every six cycles and can add grazing pressure.

Procedural travelers consume an available needed stock every six cycles. Every eight cycles, an insecure or undersupplied traveler may move to a better discovered adjacent location. They do not simulate unseen routes or create supplies. Named custodians stay at their anchors. Traveling NPCs additionally follow the five-phase designation/engagement cycle in `SYSTEMS.md`; recruited companions follow their leader rather than migrating independently.

Stem v0.1 saves retain their original quadrant geography and positions. Old survey commitments retain the original reward of 2 seeds, 2 food, 2 water, 2 XP, and +2 standing, submitted with **survey**. They can now be abandoned. New atlas institutions require a new world.
