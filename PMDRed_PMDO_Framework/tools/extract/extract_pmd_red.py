import os, re, json

PMDRED = '/tmp/pmd-red'
OUTPUT_DIR = 'pmd_red_extraction'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Parse constants/ground_map.h
map_ids = {}
with open(os.path.join(PMDRED, 'include', 'constants', 'ground_map.h'), 'r') as f:
    in_enum = False
    for line in f:
        if 'enum GroundMapID' in line:
            in_enum = True
            continue
        if in_enum and '}' in line:
            break
        if in_enum and 'MAP_' in line:
            m = re.search(r'(MAP_[A-Z0-9_]+)', line)
            if m:
                map_ids[m.group(1)] = len(map_ids)

# 2. Parse src/ground_files_table.c and map_files_table.c to find DxxPxx / Map IDs
file_to_mapid = {}
with open(os.path.join(PMDRED, 'src', 'map_files_table.c'), 'r') as f:
    content = f.read()
    # matches: [MAP_FILE_ID_POKEMON_SQUARE] = { .bplFileName = "T01P01", ... }
    blocks = re.findall(r'\[(MAP_FILE_ID_[A-Z0-9_]+|MAP_[A-Z0-9_]+)\]\s*=\s*\{([^}]*)\}', content)
    for map_id, block in blocks:
        bpl = re.search(r'\.bplFileName\s*=\s*"([^"]+)"', block)
        if bpl:
            file_to_mapid[bpl.group(1)] = map_id

# 3. Find all station files for NPC/spawns/scripts
ground_data_files = []
ground_data_dir = os.path.join(PMDRED, 'src', 'data', 'ground')
for fname in os.listdir(ground_data_dir):
    if fname.endswith('_station.h'):
        ground_data_files.append(fname)

index_data = []

# Analyze each file
for bpl in sorted(os.listdir(os.path.join(PMDRED, 'data', 'map_bg'))):
    if not bpl.endswith('.bpl'):
        continue
    base = bpl[:-4]
    
    map_id = file_to_mapid.get(base, 'UNKNOWN')
    
    station_file = f'ground_data_{base.lower()}_station.h'
    has_station = os.path.exists(os.path.join(ground_data_dir, station_file))
    
    # Try to find lives and effects
    lives_count = 0
    effs_count = 0
    bgm = 'Unknown'
    if has_station:
        with open(os.path.join(ground_data_dir, station_file), 'r', encoding='utf-8', errors='replace') as f:
            station_text = f.read()
            lives_count = len(re.findall(r'GroundLivesData', station_text)) // 2 # approx
            effs_count = len(re.findall(r'GroundEffectData', station_text)) // 2
            
            # Find BGM
            bgm_match = re.search(r'BGM_SWITCH\((MUS_[A-Z0-9_]+)\)', station_text)
            if bgm_match:
                bgm = bgm_match.group(1)

    index_data.append({
        'bpl_file': base,
        'map_id': map_id,
        'has_scripts': has_station,
        'approx_entities': lives_count,
        'approx_cutscenes': effs_count,
        'bgm': bgm
    })

# Write JSON Index
with open(os.path.join(OUTPUT_DIR, 'pmd_red_index.json'), 'w') as f:
    json.dump(index_data, f, indent=2)

# Generate Markdown Report, focusing on Fugitive Arc
with open(os.path.join(OUTPUT_DIR, 'PMD_RED_EXTRACTION_REPORT.md'), 'w') as f:
    f.write("# Extraction Exhaustive : Pokémon Donjon Mystère Red Rescue Team\n\n")
    f.write(f"Nombre total de cartes Ground trouvées : {len(index_data)}\n\n")
    
    f.write("## 1. Cartes de l'Arc des Fugitifs (Fugitive Arc)\n")
    fugitive_keywords = ['LAPIS', 'BLAZE', 'FROSTY', 'FREEZE']
    fugitives = [d for d in index_data if any(k in d['map_id'] for k in fugitive_keywords)]
    
    for d in fugitives:
        f.write(f"- **{d['map_id']}** (`{d['bpl_file']}`) | BGM: {d['bgm']} | Scripts: {'Oui' if d['has_scripts'] else 'Non'} | Entités: {d['approx_entities']}\n")
    
    f.write("\n## 2. Arènes de Boss\n")
    boss_keywords = ['BOSS', 'PEAK', 'SUMMIT', 'PIT', 'END', 'DEEP', 'REACH']
    bosses = [d for d in index_data if any(k in d['map_id'] for k in boss_keywords) and d not in fugitives]
    
    for d in bosses:
        f.write(f"- **{d['map_id']}** (`{d['bpl_file']}`) | BGM: {d['bgm']}\n")
        
    f.write("\n## 3. Entrées de Donjons\n")
    entries = [d for d in index_data if 'ENTRY' in d['map_id'] and d not in fugitives]
    for d in entries:
        f.write(f"- **{d['map_id']}** (`{d['bpl_file']}`) | BGM: {d['bgm']}\n")

print(f"Extraction terminee. Resultats generes dans {OUTPUT_DIR}/PMD_RED_EXTRACTION_REPORT.md")
