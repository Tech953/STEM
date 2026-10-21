# Map photographs → playable Stem atlas

The supplied overview and Witches Needle inset are converted into game data, rather than used only as background images. Named sites, terrain, barriers, traversal, generated scene identity, service access, residents, and contract targets all read from `geography.py`.

## What was converted

| Image feature | Playable interpretation | Certainty |
|---|---|---|
| Western Witches Needle / THORNS labels | Tower anchor, encampment spawn, and district approaches | Readable labels; coordinates approximate |
| The Vines enclosure | Southwestern woodland habitat | Label and broad enclosure interpreted from image |
| The Harvet branching woodland | Eastern woodland and extraction/recovery destination | Readable label; footprint approximate |
| Amp Lands / northern branching marks | Northern plain and woodland survey anchor | Label interpreted; route extent approximate |
| Label read as Ind.Crux | A northern route marker with a board | Spelling and purpose provisional |
| Eastern mountains / construction | CITY_CLOUD_S approach, base, ED.NET, middle and upper boundaries | Mountains visible; document topology supplies names |
| Northern water and a meandering line | Impassable water/channel sectors | Broad feature inferred; not surveyed hydrology |
| Southern curling marks and tent forms | AETHERGALE dustland and checkpoint encounters | Region/checkpoint identities supplied by documents |
| Northeastern chain-linked spiral | Northern Spiral Observation | Shape retained; label not confidently read |
| Needle inset rings, linking line, blocks and plots | Greatweb and district approach cluster | Shape visible; exact district assignments inferred |

Three river crossings are **playability interpretations**, not verified labeled bridges from the drawing. RED>GATE> and district interiors use documentary constraints; their atlas coordinates are inferred. District and checkpoint names should not be mistaken for labels independently recovered from the photograph.

## Coordinate and route model

The atlas uses a north-up game convention after interpreting the photographed page orientation. X increases east and Y increases south. Bounds are X −18…+18 and Y −12…+12; spawn is [−10, 3]. Each sector is abstract. The original drawing does not establish reliable distances, elevations, a complete road network, or exact cardinal orientation.

A route joins passable north/east/south/west sectors. Breadth-first search finds a shortest connection count. It does not optimize terrain cost, weather safety, or provisions. Planning is free; walking is not. Woodland, dustland, and mountain paths take two cycles, ordinary ground and named approaches one. Water, map edges, and the lower eastern RED>GATE> barrier reject physical movement. All 28 landmarks have a land route from spawn in this interpretation.

The Needle’s vertical structure is represented by adjacent district **approaches**, rather than a reconstruction of every floor. PEAK.EN_PERCEPT and GRAVESITE are observation boundaries, not accessible interiors. CITY_CLOUD_S service encounters are sequel adaptations of the mountain approach; they do not establish a canonically unrestricted pilgrimage road.

## Landmark register

Each entry below is also available in the game’s destination selector with its description and services.

| Landmark | Sector [X, Y] | Services | Source / interpretation confidence |
|---|---|---|---|
| The THORNS Encampment | [-10, 3] | shelter, board, craft | overview: labeled encampment; WN_TOWER / Bio-Plast Encampment; high label / approximate placement |
| The Arcturion | [-11, 0] | shelter, board, register, trade | DOCX: WN_REZ; inset: settlement approach; interpreted |
| Witches Needle | [-12, -3] | board, lesson | overview: Witches Needle; inset: tower and ring structures; high label / approximate placement |
| Greatweb Approach | [-12, -1] | repair, survey | inset: rings and connecting line; DOCX: Greatweb; interpreted |
| Undercroft.Beta | [-14, 1] | salvage, shelter | inset: lower approach; DOCX: Undercroft.Beta; interpreted |
| The Lower_Burgs | [-14, -2] | shelter, trade, craft | inset: grouped settlement blocks; DOCX: Lower_Burgs; interpreted |
| Black.Dot Outpost | [-10, -2] | register, mods | DOCX: Black.Dot outposts; inset placement interpretation; interpreted |
| SPIDREsec Pilgrim Rail | [-13, 2] | mods, board | DOCX: SPIDREsec; inset infrastructure approach; interpreted |
| MOD_OP Exchange | [-11, -4] | mods, craft, trade | DOCX: MOD_OP; district placement interpretation; interpreted |
| WN_MED Contract Desk | [-10, -4] | medical_contract | DOCX: WN_MED; district placement interpretation; interpreted |
| The Harvet Woodland | [13, 5] | board, survey, salvage | overview: The Harvet label; DOCX: The Harvet; high label / approximate placement |
| The Vines | [-13, 9] | forage, survey | overview: The Vines label; high label / approximate placement |
| Ind.Crux Route Marker | [-6, -5] | board, survey | overview: label read approximately as Ind.Crux; provisional transcription |
| Amp Lands | [0, -8] | forage, survey | overview: Amp Lands label; high label / approximate placement |
| FOOTHILL CUSP | [0, -3] | shelter, board, trade, care | DOCX: FOOTHILL CUSP; overview: northern settlement below woodland; interpreted |
| UPPER RUNEHILLS Approach | [2, -5] | lesson, craft | DOCX: UPPER RUNEHILLS; mountain/settlement interpretation; interpreted |
| GRAVESITE Boundary | [4, -6] | survey | DOCX: GRAVESITE; map placement inferred; interpreted |
| base.EN_KHO | [6, 0] | shelter, salvage, board | overview: eastern mountain settlement; DOCX: base.EN_KHO; interpreted |
| ED.NET | [7, -1] | lesson, survey | DOCX: ED.NET; eastern mountain placement interpretation; interpreted |
| Plat.EN_MID Approach | [8, 1] | salvage, mods | DOCX: Plat.EN_MID; mountains on overview; interpreted |
| PEAK.EN_PERCEPT Boundary | [9, -2] | survey | DOCX: PEAK.EN_PERCEPT; upper mountain placement interpretation; interpreted |
| CHECKPOINT.triad | [-2, 5] | shelter, board, trade | DOCX: CHECKPOINT.triad; overview: tent forms near southern open land; interpreted |
| CHECKPOINT.RESID | [2, 8] | shelter, free_provision, care | DOCX: CHECKPOINT.RESID; southern dustland waypoint inferred; interpreted |
| CHECKPOINT.GALE | [5, 6] | survey, board, craft | DOCX: CHECKPOINT.GALE; overview: southern swirl field; interpreted |
| CHECKPOINT.CASC | [8, 9] | shelter, survey | DOCX: CHECKPOINT.CASC; eastern dustland placement inferred; interpreted |
| CHECKPOINT.UNDERTOW | [12, 10] | shelter, board, remote | DOCX: CHECKPOINT.UNDERTOW; southern/eastern border interpretation; interpreted |
| RED>GATE> Observation Line | [14, 11] | remote, survey | DOCX: RED>GATE>; inferred border placement; interpreted |
| Northern Spiral Observation | [11, -8] | survey | overview: northeastern spiral feature; visible shape / uncertain label |

## Map use in play

Open **World Route Atlas**, select a named place or a gold point, and plan a route. The line and player marker show actual saved route/position data. Use **Travel Next Sector** to walk. The orange commitment ring and **Plan Commitment Route** lead to an accepted task’s exact coordinates, including a generated restoration sector next to a landmark. A manual move cancels the route.

Every named destination supplies a persistent custodian and local dialogue. Seeded ecology, weather, provisions, and travelers are generated between these anchors. Their changes affect the descriptions and survival consequences, while the geographic register stays stable.

The original overview and inset remain accessible under **Inspect the source drawings**. They are served unchanged from `reference/maps/world-reference-1.jpg` and `world-reference-2.jpg`. The converted atlas is generated as `static/atlas.svg`; its landmarks and paths are interactive overlays. Keep the photograph, document provenance, and inferred sector data distinct when revising the map.

## Future precision

A clearer scan, explicit north arrow, distance scale, and confirmed transcription of unclear labels would support more exact revision. Until then, the geographic conversion is a reviewable playable interpretation. No unreadable label is treated as a recovered canonical name.
