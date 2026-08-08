import json, os

def parse_gba_to_intermediate(macro_list):
    """
    Étape 1 : GBA -> Cinematic Intermediate Format (CIF)
    Extrait la chorégraphie et sépare l'ancien texte.
    """
    cif = []
    text_counter = 1
    
    for m in macro_list:
        if 'CAMERA_INIT_PAN' in m:
            cif.append({"type": "CameraInit", "target": "hero"})
        elif 'BGM_SWITCH' in m:
            cif.append({"type": "MusicChange", "bgm": m.split('(')[1].split(')')[0]})
        elif 'FLASH_TO' in m:
            cif.append({"type": "ScreenFlash", "color": "white", "frames": 10})
        elif 'CALL_SCRIPT(SHOCK_FUNC)' in m:
            cif.append({"type": "CameraShake", "intensity": "high", "frames": 20})
        elif 'SELECT_ANIMATION' in m:
            cif.append({"type": "Animation", "actor": "Target", "anim_id": m.split('(')[1].split(')')[0]})
        elif 'MSG_' in m:
            cif.append({
                "type": "Dialog", 
                "speaker": "Unknown", 
                "old_text_ignored": "Oui, narrative d'origine supprimée.",
                "new_era_key": f"NEW_ERA_SCENE_DIALOGUE_{text_counter:03d}"
            })
            text_counter += 1
            
    return cif

def generate_pmdo_lua(cif_data, scene_name):
    """
    Étape 2 : CIF -> Lua PMDO/RogueEssence
    Génère un script conforme à l'API RogueEssence (GAME, GROUND, UI).
    """
    lua = f"--- Remake Framework PMDO - Scene: {scene_name}\n"
    lua += f"local {scene_name} = {{}}\n\n"
    lua += f"function {scene_name}.PlayCutscene()\n"
    lua += "  GAME:CutsceneMode(true)\n\n"
    
    for action in cif_data:
        if action["type"] == "CameraInit":
            lua += "  -- Translation GBA: CAMERA_INIT_PAN()\n"
            lua += "  local center_ent = GAME:GetPlayerPartyMember(0)\n"
            lua += "  GAME:MoveCamera(center_ent.MapLoc.X, center_ent.MapLoc.Y, 1)\n\n"
        elif action["type"] == "MusicChange":
            track = action["bgm"].replace("MUS_", "").replace("_", " ").title()
            lua += f"  -- Translation GBA: BGM_SWITCH\n"
            lua += f"  GAME:PlayBGM('{track}', true)\n\n"
        elif action["type"] == "ScreenFlash":
            lua += f"  -- Translation GBA: FLASH_TO\n"
            lua += f"  GAME:FadeOut(true, {action['frames']})\n\n"
        elif action["type"] == "CameraShake":
            lua += f"  -- Translation GBA: SHOCK_FUNC\n"
            lua += f"  SOUND:PlayBattleSE('EVT_Roar')\n"
            lua += f"  GAME:WaitFrames({action['frames']})\n\n"
        elif action["type"] == "Animation":
            lua += f"  -- Translation GBA: SELECT_ANIMATION({action['anim_id']})\n"
            lua += f"  GROUND:CharSetAction(target_ent, RogueEssence.Ground.Animations.AttackAction())\n\n"
        elif action["type"] == "Dialog":
            lua += f"  -- PMD Red MSG_ macro replaced with New Era localized string\n"
            lua += f"  UI:WaitShowDialogue(STRINGS:FormatKey(\"{action['new_era_key']}\"))\n\n"
            
    lua += "  GAME:CutsceneMode(false)\n"
    lua += "end\n\n"
    lua += f"return {scene_name}\n"
    return lua

if __name__ == "__main__":
    # Test avec la cinématique de destruction de la météorite (Rayquaza)
    test_gba_macros = [
        "CAMERA_INIT_PAN()",
        "BGM_SWITCH(MUS_RAYQUAZAS_DOMAIN)",
        "MSG_NPC(NPC_RAYQUAZA, \"Take charge of your destiny!\")",
        "FLASH_TO(TRUE, PALUTIL_KIND_05, 8, RGB_U32(0xFF, 0xFF, 0xFF))",
        "CALL_SCRIPT(SHOCK_FUNC)",
        "SELECT_ANIMATION(24)"
    ]
    
    print("--- 1. Analyse et génération du Cinematic Intermediate Format (CIF) ---")
    cif = parse_gba_to_intermediate(test_gba_macros)
    print(json.dumps(cif, indent=2))
    
    print("\n--- 2. Génération du Script Lua PMDO ---")
    lua_out = generate_pmdo_lua(cif, "rayquaza_climax")
    print(lua_out)
