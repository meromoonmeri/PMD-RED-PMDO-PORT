import os, sys, re, json

def parse_station_to_cif(station_file_path):
    """
    Lit un fichier _station.h de PMD Red et génère une liste brute CIF (Cinematic Intermediate Format)
    """
    if not os.path.exists(station_file_path):
        return None
        
    cif = {"scene": os.path.basename(station_file_path).replace('ground_data_', '').replace('_station.h', ''),
           "camera": [], "effects": [], "audio": [], "animations": [], "raw_sequence": []}
           
    with open(station_file_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if 'CAMERA_PAN' in line:
                m = re.search(r'CAMERA_PAN\((.*?)\)', line)
                if m: cif['camera'].append({"command": "PAN", "args": m.group(1)})
                cif['raw_sequence'].append({"type": "Camera", "action": "PAN", "raw": line})
            elif 'CAMERA_INIT_PAN' in line:
                cif['camera'].append({"command": "INIT_PAN"})
                cif['raw_sequence'].append({"type": "Camera", "action": "INIT_PAN"})
            elif 'CAMERA_END_PAN' in line:
                cif['camera'].append({"command": "END_PAN"})
                cif['raw_sequence'].append({"type": "Camera", "action": "END_PAN"})
            elif 'FLASH_TO' in line:
                m = re.search(r'FLASH_TO\(([^,]+),[^,]+,\s*(\d+)', line)
                frames = m.group(2) if m else 10
                cif['effects'].append({"type": "FLASH_TO", "frames": int(frames)})
                cif['raw_sequence'].append({"type": "Effect", "action": "FLASH_TO", "frames": int(frames)})
            elif 'FLASH_FROM' in line:
                m = re.search(r'FLASH_FROM\(([^,]+),[^,]+,\s*(\d+)', line)
                frames = m.group(2) if m else 10
                cif['effects'].append({"type": "FLASH_FROM", "frames": int(frames)})
                cif['raw_sequence'].append({"type": "Effect", "action": "FLASH_FROM", "frames": int(frames)})
            elif 'CALL_SCRIPT(SHOCK_FUNC)' in line:
                cif['effects'].append({"type": "SCREEN_SHAKE"})
                cif['raw_sequence'].append({"type": "Effect", "action": "SHAKE"})
            elif 'BGM_SWITCH' in line:
                m = re.search(r'BGM_SWITCH\((.*?)\)', line)
                if m:
                    cif['audio'].append({"command": "SWITCH", "track": m.group(1)})
                    cif['raw_sequence'].append({"type": "Audio", "action": "SWITCH", "track": m.group(1)})
            elif 'BGM_FADEOUT' in line:
                m = re.search(r'BGM_FADEOUT\((.*?)\)', line)
                frames = m.group(1) if m else 60
                cif['audio'].append({"command": "FADEOUT", "frames": int(frames)})
                cif['raw_sequence'].append({"type": "Audio", "action": "FADEOUT", "frames": int(frames)})
            elif 'BGM_STOP' in line:
                cif['audio'].append({"command": "STOP"})
                cif['raw_sequence'].append({"type": "Audio", "action": "STOP"})
            elif 'SELECT_ANIMATION' in line:
                m = re.search(r'SELECT_ANIMATION\((.*?)\)', line)
                if m:
                    cif['animations'].append({"anim_id": m.group(1)})
                    cif['raw_sequence'].append({"type": "Animation", "anim_id": m.group(1)})
                    
    return cif

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'cinematics_cif')
    os.makedirs(out_dir, exist_ok=True)
    
    # Extraction réelle du climax (Rayquaza & Meteorite)
    pmd_dir = '/tmp/pmd-red/src/data/ground'
    targets = ['ground_data_d13p03_station.h', 'ground_data_a04p01_station.h', 'ground_data_t01p01_station.h']
    
    print("--- REAL EXTRACTION: GBA -> CIF ---")
    for t in targets:
        cif = parse_station_to_cif(os.path.join(pmd_dir, t))
        if cif:
            out_file = os.path.join(out_dir, f"{cif['scene']}.cif.json")
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(cif, f, indent=2)
            print(f"✅ CIF Extracted: {out_file} (Camera: {len(cif['camera'])}, VFX: {len(cif['effects'])})")
