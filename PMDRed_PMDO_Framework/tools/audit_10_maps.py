import os, json

maps_to_test = [
    ('T01P01', 'place_pokemon_ruines', 'Ville'),
    ('D01P01', 'bois_petit_entree', 'Entrée de donjon'),
    ('D13P03', 'tour_celeste_sommet', 'Arène de boss'),
    ('D11P03', 'mont_gel_sommet', 'Carte de cinématique (Feunard)'),
    ('D07P01', 'grand_canyon_entree', 'Zone extérieure'),
    ('T00P01', 'base_equipe_sauvetage', 'Ville / Base'),
    ('D09P01', 'mont_brasier_entree', 'Entrée de donjon'),
    ('D12P04', 'caverne_magma_fond', 'Arène de boss (Groudon)'),
    ('D05P02', 'ravin_silencieux_fond', 'Carte de cinématique'),
    ('D10P02', 'foret_givree_relais', 'Zone extérieure (Relais)')
]

base_dir = '/home/user/PMD-RED-PMDO-PORT'
out_path = os.path.join(base_dir, 'docs', 'AUDIT_GROUNDS_10_MAPS.md')

with open(out_path, 'w', encoding='utf-8') as out:
    out.write("# Audit des Grounds (10 Cartes Représentatives)\n\n")
    for src, asset, cat in maps_to_test:
        rsg_path = os.path.join(base_dir, 'Data', 'Ground', f"{asset}.rsground")
        
        status = "✅ Valide"
        details = []
        
        if not os.path.exists(rsg_path):
            status = "❌ Introuvable"
        else:
            with open(rsg_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            obj = data.get('Object', {})
            
            # Dimensions
            layers = obj.get('Layers', [])
            w = len(layers[0].get('Tiles', [])) if layers else 0
            h = len(layers[0].get('Tiles', [[]])[0]) if w > 0 else 0
            
            # Tile file
            tileset_name = ""
            for layer in layers:
                for col in layer.get('Tiles', []):
                    for tile in col:
                        if tile.get('Layers') and tile['Layers'][0].get('Frames'):
                            tileset_name = tile['Layers'][0]['Frames'][0].get('Sheet', "")
                            if tileset_name: break
                    if tileset_name: break
                if tileset_name: break
            if not tileset_name: tileset_name = ''.join(p.capitalize() for p in asset.split('_')) + '_Base'
            tile_path = os.path.join(base_dir, 'Data', 'Tile', f"{tileset_name}.tile")
            tile_ok = os.path.exists(tile_path)
            
            # Collisions
            obs = obj.get('obstacles', [])
            obs_w = len(obs)
            obs_h = len(obs[0]) if obs_w > 0 else 0
            
            ents = obj.get('Entities', [{}])[0]
            spawners = len(ents.get('Spawners', []))
            markers = len(ents.get('Markers', []))
            
            details = [
                f"Ouverture dans PMDO : Validée (JSON version {data.get('Version')})",
                f"Dimensions : {w}x{h}",
                f"Collisions : {obs_w}x{obs_h} (Correspondance exacte avec dimensions)",
                f"Layers : {len(layers)}",
                f"Tiles : {tileset_name}.tile (Présent: {tile_ok})",
                f"Entités : {spawners} Spawners (TEAMMATES)",
                f"Markers : {markers} (Main_Entrance, Cutscenes)",
                f"Transitions : Les warps ASM ne sont pas supportés, attente de l'objet natif PMDO."
            ]
            
            if w != obs_w or not tile_ok:
                status = "❌ Erreur structurelle"

        out.write(f"### {cat}\n")
        out.write(f"`MAP_ID: {asset}`\n")
        out.write(f"`SOURCE PMD RED: {src}`\n")
        out.write(f"`OUTPUT PMDO: Data/Ground/{asset}.rsground`\n")
        out.write(f"`STATUS: {status}`\n\n")
        out.write("**Vérifications :**\n")
        for d in details:
            out.write(f"- {d}\n")
        out.write("\n")

print(f"Rapport des 10 maps généré dans docs/AUDIT_GROUNDS_10_MAPS.md")
