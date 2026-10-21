# Stem 0.3.0 validation

Tested 2 October 2026 UTC.

**68 Python automated tests passed.** These cover the original procedural world and the integrated atlas adventure.

The integrated checks verify a physical land route from spawn to each of the 28 landmarks; terrain-based movement and boundaries; free route planning without teleportation; exact commitment routing; THORNS character-template validation; point budgets and forged credential rejection; characterization recorded in dialogue; persistent contacts and dialogue at every landmark; delivery costs and once-only rewards; restoration work requirements; diplomatic checks and standing; abandonment and personal care benefits; registration, equipment and slot limits; condition penalties, treatment and sleep; free RESID provision; WN_MED client scope; recovery without false route arrival; database restart persistence; editing locks; and legacy geography without moved characters.

The 25 expedition checks verify context and standing changing the same fixed roll, natural-1/20 behavior, checks across observation/dialogue/survival/records, partial dialogue without false facts, failed contract acceptance and handover, recruitment refusal/cooldown and conserved supplies, two-companion and single-owner limits, stable lore and variable registered dialogue, physical following and trained support, faction/health/pack contract blockers, material-consuming autonomous work, player needs preserved during pulses, voluntary withdrawal, supply transfer/request limits, care and dismissal, business failure and reserve conservation, local-stock restocking and reputation prices, infrastructure costs, once-only combat loot, shared guarding damage, parley/disengagement/registered ballistics, NPC/player combat target rejection, source-character history boundaries, model NPC-catalog validation, full restart persistence, released-seat cleanup and failed ownership rollback.

The original checks cover seeded regional generation, typed intentions, rejection of unsupported/negated/chained requests, observation costs, movement and needs, stock depletion and traces, repairs, autonomous ecology, traveler migration, negotiation, remote observation limits, legacy contracts, six-seat capacity, redacted tokens, bounded indices and discovered sites, recovery, host pause, stale revisions, idle pausing, concurrent serialized actions, and seat release.

HTTP tests start a real local server. Local-narrator tests use mocks to verify loopback restrictions, reviewed action/target validation, mapped destinations, contract kinds, characterization context, and omission of session tokens. No actual model inference is claimed.

**The Node interface smoke test passed with the real HTTP host and a minimal DOM harness.** It exercises comprehensive character creation, the registered character sheet, two companion agreements, generated lore and task proposals, contextual check display, a business purchase, public water operation, a guard/parley encounter, 49 local map cells, atlas destinations and stepwise routes, saved dialogue, delivery acceptance and abandonment, expedition start, unknown-input retention, movement, projection restrictions, literal chat text, pause, disconnect, character-builder restoration, and resume. It verifies interface logic and API integration; it is not a real-browser or pixel-layout test.

The host environment has no runnable Chromium/Firefox executable. Real-browser visual playtesting remains unverified. No native Windows launch, multi-device LAN/internet session, accessibility conformance audit, human balance test, actual local-model inference, or production-load test is claimed. Model prose may embellish incorrectly despite having no state-writing authority.

## Repeat the checks

Run inside the game folder:

```text
python -m unittest discover -s tests -v
node tests/ui-smoke.cjs
```

Node is only required for the developer interface test. Playing requires Python 3.10+ and a browser; no third-party Python packages are needed.

## Human playtest

1. Create a new atlas world with appearance, voice, biography, goals and boundaries. Review the character sheet before beginning. Export and re-import a creation template in a separate draft.
2. Begin, ask the encampment custodian about place and history, then inspect the recorded dialogue. Verify the characterization is consistent.
3. Open the route atlas. Compare the original photographs, confidence notes, landmark names and services. Plan a nearby route and verify planning does not move the player. Walk a sector and confirm position, route length and needs change.
4. Visit Black.Dot Outpost, register, and inspect the credential and blueprint effect. Try another verified exchange and confirm slot/cost limits.
5. Accept each commitment type over separate journeys. Use the commitment route button, reach the exact target, perform required work, and fulfill. Verify materials, rewards, standing, care tier and history. Abandon one and inspect its cost.
6. Enter a storm route, inspect any conditions and check penalties, attempt field care, and visit an appropriate clinic. At WN_MED, compare access before and after its delivery commitment. At RESID, compare free provision and care.
7. Gather, plant and repair; revisit and confirm scene traces and changing habitat. Pause/resume the shared clock and observe an ecological pulse without personal starvation.
8. Address residents in each region and on generated routes. Verify contact memory stays specific to the speaker and descriptions remain consistent after moving.
9. Join with a second browser/computer. Confirm separate character/need records, shared habitat and standing, party transmissions, and visible co-located appearances.
10. Stop and restart the host. Resume the saved seat and confirm route, description, conversations, commitment, equipment, and conditions persist. Open a legacy v0.1 save and confirm its original position/layout remain.
11. If a local model is available, separately test prose expansion and interpretation. Check character fidelity, map boundaries, observation cycle labeling, rejected invalid targets, and explicit review before any action.
