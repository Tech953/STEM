# Field Guide integration validation

Thorns 0.6.0 / Stem 0.5.0 · 18 October 2026

## Result

- **Thorns: 69 Python tests pass**, including 36 existing compatibility tests and 33 shared Field Guide tests.
- **Stem: 114 Python tests pass**, including 81 existing compatibility tests and 33 shared Field Guide tests.
- **20 new client interface flows pass** across both games using their complete client scripts, real HTTP and a DOM harness. The controlled scene is a test fixture, not a production spawn override.
- Both existing contact/expedition interface harnesses also pass.
- JavaScript syntax checks pass for all changed production client scripts.

## Coverage

The new suites run independently against each game's real server and save model. They cover legal starting packs/bulk, all 48 profile identities, world-frame filtering, 230 bonus/DC combinations with all twenty die faces per game, saved RNG continuation, 240 seeded encounter/budget cases per game, reroll prevention, natural 1/20, grade percentages, XP/session/goal caps, Growth, mastery, old-XP adoption, legacy pack preservation, provisioning, full rest, treatment failure costs, AP order, absence of per-action counterattacks, Energy-only attacks, anchored targets, finite ammo, morale, finite salvage, wear/repair/replacement, NPC readiness/support costs/party limits/voluntary dismissal, inactive seats, host authority, contract escrow/one-time payout and a departing combat seat.

The interface harness exercises creation, start, personal provision cost, fixed initiative, hidden-hex approach, AP attack, finite salvage, weapon wear/repair, shared-watch time and poll persistence in each client. The pre-existing suites remain explicit **legacy-rules fixtures**, preserving their original behavioral assertions; the new suites test the new default rules separately.

## Practical limits

A rendered Chromium session was unavailable: no browser binary was installed and the attempted runtime download returned an incomplete archive. This is **not a screenshot, browser-layout, mobile-layout or accessibility certification**. The DOM/HTTP tests verify action wiring, rendering logic, state changes and persistence. Windows launchers/build recipe are preserved and the Thorns bundler now includes the new JSON catalog, but no Windows executable was compiled or tested on Windows here.

Exact odds validate a specified roll and fixed analytic model. They do not establish full-fight win rates or human playtest balance. Encounter costs remain the guide's explicit planning heuristic. Manual targeted attacks, detailed cover/opaque scenery, draw/reload states, a selectable permadeath mode and some profile-specific narrative powers remain extensions. Whole-monument destruction and new hyper-realistic art are not claimed by this mechanics release.

## Reproduce

Thorns: `python3 -m unittest discover -q`, `node test_field_ui.cjs .`, `node test_contact_ui.cjs`.

Stem: `python3 -m unittest discover -s tests -q`, `node tests/test_field_ui.cjs .`, `node tests/ui-smoke.cjs`.

Python runtime has no third-party dependencies. Node 18+ is needed only for the HTTP/DOM test harnesses.
