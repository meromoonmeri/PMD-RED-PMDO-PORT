import os, sys, re, json

def extract_choreography_to_cif(station_file_path):
    """
    Extrait l'âme de la mise en scène (timing, musique, fx) dans un Modèle Intermédiaire (CIF),
    conformément aux règles de CinematicModel.
    """
    if not os.path.exists(station_file_path):
        return None
        
    cif = {"scene_id": os.path.basename(station_file_path).replace('ground_data_', '').replace('_station.h', ''),
           "events": []}
           
    text_skip_counter = 1
    
    with open(station_file_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if 'CAMERA_PAN' in line:
                cif['events'].append({"type": "CameraMove", "target": "PanOffset", "raw": line})
            elif 'CAMERA_INIT_PAN' in line:
                cif['events'].append({"type": "CameraMove", "target": "InitialFocus"})
            elif 'CAMERA_END_PAN' in line:
                cif['events'].append({"type": "CameraMove", "target": "Player"})
            elif 'FLASH_TO' in line:
                m = re.search(r'FLASH_TO\([^,]+,[^,]+,\s*(\d+)', line)
                frames = m.group(1) if m else "10"
                cif['events'].append({"type": "ScreenFlash", "mode": "FadeOut", "frames": int(frames)})
            elif 'FLASH_FROM' in line:
                m = re.search(r'FLASH_FROM\([^,]+,[^,]+,\s*(\d+)', line)
                frames = m.group(1) if m else "10"
                cif['events'].append({"type": "ScreenFlash", "mode": "FadeIn", "frames": int(frames)})
            elif 'CALL_SCRIPT(SHOCK_FUNC)' in line:
                cif['events'].append({"type": "ScreenShake", "intensity": "high", "frames": 30})
            elif 'BGM_SWITCH' in line:
                m = re.search(r'BGM_SWITCH\((.*?)\)', line)
                if m: cif['events'].append({"type": "MusicChange", "track": m.group(1)})
            elif 'BGM_FADEOUT' in line:
                m = re.search(r'BGM_FADEOUT\((.*?)\)', line)
                frames = m.group(1) if m else "60"
                cif['events'].append({"type": "MusicFade", "frames": int(frames)})
            elif 'BGM_STOP' in line:
                cif['events'].append({"type": "MusicStop"})
            elif 'SELECT_ANIMATION' in line:
                m = re.search(r'SELECT_ANIMATION\((.*?)\)', line)
                if m: cif['events'].append({"type": "Animation", "anim_id": m.group(1)})
            elif 'WAIT' in line:
                m = re.search(r'WAIT\((.*?)\)', line)
                if m: cif['events'].append({"type": "Wait", "frames": int(m.group(1))})
            elif 'MSG_' in line:
                cif['events'].append({"type": "DialogPlaceholder", "key": f"NEW_ERA_DLG_{text_skip_counter:03d}"})
                text_skip_counter += 1
                
    return cif

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'intermediate', 'cinematics')
    os.makedirs(out_dir, exist_ok=True)
    
    # Test unitaire d'extraction
    test_path = '/tmp/pmd-red/src/data/ground/ground_data_d13p03_station.h'
    cif = extract_choreography_to_cif(test_path)
    if cif:
        out_file = os.path.join(out_dir, f"{cif['scene_id']}.json")
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(cif, f, indent=2)
        print(f"CIF Extrait : {out_file}")
