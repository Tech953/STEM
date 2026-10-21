# Stem 0.5.0

A self-hosted text adventure for 1–6 players, now using the shared **Field Guide 1.0** creature, check, encounter, combat, progression and material-condition foundation.

## Play

1. Extract the whole ZIP. The host needs Python 3.10 or newer; no third-party packages or model are needed.
2. On Windows, run **Start-Windows.bat** in this folder. On macOS/Linux, run `python3 server.py`.
3. Open **http://localhost:8776**. Create a character and room; invite your group, then begin the expedition.
4. Open **FIELD GUIDE / SHARED RULES** to review exact chances, costs, encounters, equipment and Growth.

Use the existing route atlas for mapped travel, or write intentions. New commands include **full rest**, **breather**, **spend a watch** and **end turn**. The field panel supplies targeted AP controls. The current character sheet remains valid after Growth and reconnect.

## What changed

- A 48-profile catalog with world-specific weighted encounter tables, persistent scene identities and recorded seeded draws.
- Four check grades; exact d20 percentages; skill, context, relationship, reputation, fatigue and trained support components.
- Local hidden-hex distances and AP turns, finite attacks/ammo, separate Health/Energy damage and one-time salvage.
- Earned XP, once-per-situation awards, session caps, Growth and rank-3 mastery.
- Real provision costs, safe-rest timing, weapon wear, repairs, replacements and voluntary companion agreements.
- Existing map interpretation, dialogue records, CRT settings, world lore and saves retained.

The full current controls, migration procedure, formulas and remaining extensions are in [FIELD-GUIDE-UPDATE.md](FIELD-GUIDE-UPDATE.md). Test evidence is in [FIELD-GUIDE-VALIDATION.md](FIELD-GUIDE-VALIDATION.md).

## Existing campaigns

Old databases load using their original rules. The host can select **ADOPT FIELD GUIDE 1.0** to upgrade after reviewing the update guide. Existing characters, earned XP, inventory, routes, histories and agreements are preserved. Stop the host and back up its save database first. New rooms use the Field Guide by default; API fixtures can explicitly select `ruleset: "legacy"`.

## Play together

Run one host for the group. Other players on the same LAN open `http://HOST-LAN-IP:8776` and use the same room code. They need both the host address and code. The code does not locate a server. Keep the host running. Remote play requires your own private network connection or a properly configured HTTPS host; this ZIP does not deploy a public service.

Session credentials persist in the browser's existing storage. **Exit/Disconnect** preserves the seat; **Leave** releases it. Resume using the same browser and server address. Do not distribute live databases or room credentials.

## Development

Run `python3 -m unittest discover -s tests -q` for Python tests.
Run `node tests/test_field_ui.cjs .` for the HTTP/DOM interface harness (Node 18+).

`field_rules.py`, `creature_catalog.json` and `static/field-guide.js` are identical across both releases; each ZIP includes its own copies. Numerical outcomes are server-authoritative. The interfaces never submit accepted rolls, earned XP, ammo or inventory totals.

These are source prototypes with launchers. No compiled Windows executable is claimed. Prior documentation remains under its original filenames; use the Field Guide update as the current rules authority. The earlier README is preserved in `README-HISTORY.md`.
