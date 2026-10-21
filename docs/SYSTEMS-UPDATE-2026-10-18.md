# Thorns and Stem — systems update

Updated releases: **Thorns 0.6.0** and **Stem 0.5.0**.

The Creature and Stat Guide now drives live, persistent field gameplay through the same shared rules module in both games. The original Thorns voting chapter, Stem route atlas, source drawings, local memory, optional state-bound narrator and CRT settings remain available.

| Area | Integration |
| --- | --- |
| Catalog | All 48 guide profiles, original baseline numbers, variants, intent, descriptions, peaceful routes, limits and source notes. |
| Encounters | Regional weighted habitat tables, saved scene IDs, four-cycle watches, fixed budgets and evidence-only outcomes for oversized profiles. Long Tar/Spirit Rush frames remain gated. |
| Checks | Four outcome grades, exact d20 percentages, bounded practice/context/standing/trust/attitude/support/conditions/fatigue. |
| Tactical play | Hidden-hex distance, fixed initiative, real AP turns, own-turn enemy actions, finite stored attacks, weapon wear, separate Health/Energy channels, morale and nonviolent passage. |
| Progress | Earned-XP ledger, once-per-resolution awards, session/goal caps, Growth and rank-3 mastery. |
| Provisions | Actual personal supplies, cycle-before-recovery ordering, full-rest reservations, material repair/replacement and finite scene salvage. |
| Contracts | Real reward escrow, unique paid IDs and preserved active commitments during migration. |
| Companions | Thorns gains two persistent traveling designations and scoped support/guard/rest. Stem retains its fuller task infrastructure with party limits, readiness, actual support/ration costs, lore and histories. |
| Compatibility | New rooms use the guide. Existing campaigns retain their old rules until host adoption; old XP, inventory, identity, route and history are carried forward. |

**Verification:** 183 Python tests pass (69 Thorns / 114 Stem), plus 20 new HTTP/DOM interface flows and both pre-existing interface harnesses. Per-game exact probability and seeded-generation checks run inside those tests. Shared engine/data/client files are byte-identical across releases; original map image bytes are preserved.

Both ZIPs include source code, data, launchers, the full update guide, migration instructions, validation notes and reproducible tests. Extract each ZIP completely and open its README.

**Remaining limits:** these are text-game source prototypes. No Windows EXE or new sprite/3D asset set was built. Rendered-browser/mobile layout could not be verified in this runtime; interface checks use real HTTP with a DOM harness. Detailed targeted attacks, cover/occlusion, draw/reload states, selectable permadeath and some authored profile-specific powers remain future extensions. Exact roll analytics do not replace playtesting. The guide's numerical/gameplay rules were integrated; comparison books do not replace world canon or its d20 system.
