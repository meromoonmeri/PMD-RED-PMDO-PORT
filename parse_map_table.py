import re, json

with open('/tmp/pmd-red/src/map_files_table.c', 'r', encoding='utf-8') as f:
    txt = f.read()

maps = {}
# Find each ID
matches = re.finditer(r'\[(MAP_FILE_ID_[A-Z0-9_]+)\]\s*=\s*\{', txt)
indices = [m.start() for m in matches] + [len(txt)]

for i, m in enumerate(re.finditer(r'\[(MAP_FILE_ID_[A-Z0-9_]+)\]\s*=\s*\{', txt)):
    map_id = m.group(1)
    block = txt[indices[i]:indices[i+1]]
    
    bpl = re.search(r'\.bplFileName\s*=\s*"([^"]+)"', block)
    bpc = re.search(r'\.bpcFileName\s*=\s*"([^"]+)"', block)
    bma = re.search(r'\.bmaFileName\s*=\s*"([^"]+)"', block)
    
    bpa_list = []
    bpa_block = re.search(r'\.bpaFileNames\s*=\s*\{([^}]+)\}', block)
    if bpa_block:
        bpa_list = re.findall(r'"([^"]+)"', bpa_block.group(1))

    if bpl and bpc and bma:
        maps[map_id] = {
            'bpl': bpl.group(1),
            'bpc': bpc.group(1),
            'bma': bma.group(1),
            'bpa': bpa_list
        }

with open('/home/user/map_dependencies.json', 'w') as f:
    json.dump(maps, f, indent=2)

print(f"Extracted {len(maps)} map configurations.")
bpa_counts = [len(m['bpa']) for m in maps.values()]
print(f"Max BPAs used by a single map: {max(bpa_counts) if bpa_counts else 0}")
