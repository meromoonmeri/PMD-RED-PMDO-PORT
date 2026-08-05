import os, json

def convert_to_floorplan(dungeon_data, name):
    """
    Génère un squelette XML compatible RogueElements.FloorPlan
    La GBA n'a pas de système XML, on crée la passerelle.
    """
    xml = f"<!-- RogueElements FloorPlan / PMDO Dungeon Pack Generator -->\n"
    xml += f"<!-- Source: PMD Red ({name}) -->\n"
    xml += "<FloorPlan>\n"
    xml += f"  <Name>{name.title().replace('_', ' ')}</Name>\n"
    xml += "  <Spawns>\n"
    
    unique_spawns = list(set(dungeon_data.get('spawns', [])))
    for sp in unique_spawns:
        xml += "    <MobSpawn>\n"
        xml += f"      <Species>{sp.lower()}</Species>\n"
        xml += "      <Rate>10</Rate>\n"
        xml += "    </MobSpawn>\n"
        
    xml += "  </Spawns>\n"
    xml += "</FloorPlan>\n"
    return xml

if __name__ == "__main__":
    in_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'intermediate', 'dungeons', 'dungeons.json')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'Dungeons')
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 2. CONVERSION DUNGEON -> XML ---")
    if os.path.exists(in_file):
        with open(in_file, 'r') as f:
            data = json.load(f)
            
        for k, v in data.items():
            if len(v['spawns']) > 0:
                xml = convert_to_floorplan(v, k.replace('DUNGEON_', ''))
                out_path = os.path.join(out_dir, f"{k.replace('DUNGEON_', '').lower()}.xml")
                with open(out_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(xml)
                print(f"✅ FloorPlan XML généré: {out_path}")
    else:
        print("Erreur: Parseur C/ASM manquant ou JSON introuvable.")
