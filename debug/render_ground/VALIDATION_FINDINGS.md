# Offline Ground validation findings

Renderer: `PMDRed_PMDO_Framework/tools/render_pmdo_ground.py`

## Execution

- 263 `.rsground` files discovered in `output/Grounds/`
- 263 PNG files rendered from native `.rsground` + `.tile`
- 0 serialization, missing-sheet, or TexLoc errors
- RogueEssence was not executed
- No emulator/pixel oracle comparison was performed

## D09P03

`debug/render_ground/d09p03.png` renders as a mostly uniform burgundy silhouette surrounded by black. The offline renderer successfully resolved every referenced `.tile` entry, therefore this is not a missing-sheet or PMDO loading error in the renderer.

D09P03 is one of the known dungeon-backed maps requiring the ROM-extracted `mapparam` and `bXXfon/pal/cel/cex/canm` material pipeline. Its current visual asset must be classified as **conversion incomplete/corrupt**, not as a RogueEssence integration failure.

The PNG is diagnostic evidence only. It must not be used as an input to regenerate a Ground or tileset.
