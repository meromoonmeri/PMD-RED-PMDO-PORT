import json

def generate_mapping_strategy():
    print("--- NEW ERA : MAPPING CANONIQUE (RED/SKY -> NEW ERA) ---")
    
    # Stratégie de fusion basée sur tes instructions
    mapping = {
        "Gloomy Forest (Forêt Lugubre)": {
            "new_era_chapter": 6,
            "origin_game": "PMD Red",
            "origin_dungeon": "Sinister Woods",
            "grounds_to_import": [
                {"src": "d04p01_entree", "new_era_rsground": "gloomy_forest_entrance"},
                {"src": "d04p02_fond", "new_era_rsground": "gloomy_forest_boss"}
            ],
            "note": "Remplacement canonique de l'architecture. Les arbres lugubres de Sinister Woods serviront de base pour le boss du Chapitre 6."
        },
        "Sky Tower (Tour Céleste)": {
            "new_era_chapter": 10,
            "origin_game": "PMD Red",
            "origin_dungeon": "Sky Tower",
            "grounds_to_import": [
                {"src": "d13p01_entree", "new_era_rsground": "sky_tower_entrance"},
                {"src": "d13p02_relais", "new_era_rsground": "sky_tower_midpoint"},
                {"src": "d13p03_sommet", "new_era_rsground": "sky_tower_summit"}
            ],
            "cinematics_to_import": [
                {"src": "d13p03.lua", "event": "Apparition Rayquaza + Ultralaser"}
            ],
            "vfx_to_import": [
                "VFX_Rayquaza_Hyperbeam_Core",
                "VFX_Meteor_Fragment"
            ],
            "note": "Reprise à 100% de l'ambiance GBA. Le Lua généré dans le Framework PMD Red va être injecté dans New Era pour rejouer l'explosion de la Météorite pixel par pixel."
        }
    }
    
    print(json.dumps(mapping, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    generate_mapping_strategy()
