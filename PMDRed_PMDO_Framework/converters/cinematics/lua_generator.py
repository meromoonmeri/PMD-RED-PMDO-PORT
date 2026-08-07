import json, os

def cif_to_lua(cif_model):
    """
    Traduit le modèle CIF en script Lua PMDO strict.
    """
    scene_name = cif_model.get('scene_id', 'unknown_scene')
    
    lua = f"--- Framework Remake: {scene_name}\n"
    lua += f"local {scene_name} = {{}}\n\n"
    lua += f"function {scene_name}.Cutscene()\n"
    lua += "  GAME:CutsceneMode(true)\n\n"
    
    for evt in cif_model.get('events', []):
        evt_type = evt.get('type')
        if evt_type == "CameraMove":
            if evt.get('target') == 'Player':
                lua += "  GAME:MoveCamera(0, 0, 1, false) -- Focus retour joueur\n"
            else:
                lua += f"  -- [TODO] GAME:MoveCamera(TargetX, TargetY, Speed) -- Macro originelle : {evt.get('raw', 'INIT_PAN')}\n"
        
        elif evt_type == "ScreenFlash":
            if evt.get('mode') == 'FadeOut':
                lua += f"  GAME:FadeOut(true, {evt.get('frames')})\n"
            else:
                lua += f"  GAME:FadeIn({evt.get('frames')})\n"
                
        elif evt_type == "ScreenShake":
            lua += f"  SOUND:PlayBattleSE('EVT_Roar')\n"
            lua += f"  GAME:WaitFrames({evt.get('frames')}) -- Remplacement du SHOCK_FUNC GBA\n"
            
        elif evt_type == "MusicChange":
            track = evt.get('track').replace('MUS_', '').replace('_', ' ').title()
            lua += f"  GAME:PlayBGM('{track}', true)\n"
            
        elif evt_type == "MusicFade":
            lua += f"  GAME:FadeOutBGM({evt.get('frames')})\n"
            
        elif evt_type == "MusicStop":
            lua += f"  GAME:FadeOutBGM(30)\n"
            
        elif evt_type == "Animation":
            lua += f"  -- [TODO] GROUND:CharSetAction(ent, Anim_ID_{evt.get('anim_id')})\n"
            
        elif evt_type == "Wait":
            lua += f"  GAME:WaitFrames({evt.get('frames')})\n"
            
        elif evt_type == "DialogPlaceholder":
            lua += f"  UI:WaitShowDialogue(STRINGS:FormatKey(\"{evt.get('key')}\"))\n"
            
        lua += "\n"
        
    lua += "  GAME:CutsceneMode(false)\n"
    lua += "end\n\n"
    lua += f"return {scene_name}\n"
    
    return lua

if __name__ == "__main__":
    in_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'intermediate', 'cinematics', 'd13p03.json')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'Scripts', 'scene')
    os.makedirs(out_dir, exist_ok=True)
    
    if os.path.exists(in_file):
        with open(in_file, 'r') as f:
            cif_model = json.load(f)
            
        lua_code = cif_to_lua(cif_model)
        out_file = os.path.join(out_dir, "d13p03.lua")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(lua_code)
        print(f"Lua généré : {out_file}")
