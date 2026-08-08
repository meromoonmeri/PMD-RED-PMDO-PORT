import json, os

def cif_to_lua(cif_data, scene_name):
    """
    Génère un script Lua PMDO jouable (Cutscene) à partir des données CIF.
    """
    lua = f"--- PMDO AUTOMATIC CONVERSION\n"
    lua += f"--- Source Scene: {cif_data.get('scene', scene_name)}\n\n"
    lua += f"local {scene_name} = {{}}\n\n"
    lua += f"function {scene_name}.Cutscene()\n"
    lua += "  GAME:CutsceneMode(true)\n\n"
    
    text_counter = 1
    
    for action in cif_data.get('raw_sequence', []):
        if action['type'] == 'Audio':
            if action['action'] == 'SWITCH':
                track = action['track'].replace('MUS_', '').replace('_', ' ').title()
                lua += f"  GAME:PlayBGM('{track}', true)\n"
            elif action['action'] == 'FADEOUT':
                lua += f"  GAME:FadeOutBGM({action['frames']})\n"
            elif action['action'] == 'STOP':
                lua += f"  GAME:FadeOutBGM(60)\n  GAME:WaitFrames(60)\n"
        elif action['type'] == 'Effect':
            if action['action'] == 'FLASH_TO':
                lua += f"  GAME:FadeOut(true, {action['frames']}) -- FLASH_TO equivalent\n"
            elif action['action'] == 'FLASH_FROM':
                lua += f"  GAME:FadeIn({action['frames']}) -- FLASH_FROM equivalent\n"
            elif action['action'] == 'SHAKE':
                lua += f"  SOUND:PlayBattleSE('EVT_Roar')\n  GAME:WaitFrames(20) -- SCREEN_SHAKE equivalent\n"
        elif action['type'] == 'Camera':
            if action['action'] == 'INIT_PAN':
                lua += f"  -- [PMDO] TODO: GAME:MoveCamera(HeroX, HeroY, 1)\n"
            elif action['action'] == 'PAN':
                lua += f"  -- [PMDO] TODO: CAMERA_PAN {action.get('raw')}\n"
        elif action['type'] == 'Animation':
            lua += f"  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:{action['anim_id']})\n"

    lua += "\n  GAME:CutsceneMode(false)\n"
    lua += "end\n\n"
    lua += f"return {scene_name}\n"
    return lua

if __name__ == "__main__":
    in_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'cinematics_cif')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'PMDO_Project', 'Scripts', 'scene')
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- REAL COMPILATION: CIF -> LUA ---")
    for f in os.listdir(in_dir):
        if not f.endswith('.cif.json'): continue
        with open(os.path.join(in_dir, f), 'r') as fp:
            cif = json.load(fp)
            
        scene_name = cif['scene']
        lua = cif_to_lua(cif, scene_name)
        
        out_path = os.path.join(out_dir, f"{scene_name}.lua")
        with open(out_path, 'w', encoding='utf-8') as fout:
            fout.write(lua)
        print(f"✅ LUA Generated: {out_path}")
