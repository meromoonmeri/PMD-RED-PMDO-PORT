import json

def log_validation(source, target, status, missing=[]):
    """
    Règle fondamentale de validation :
    SOURCE / TARGET / STATUS / MISSING
    """
    print(f"SOURCE: {source}")
    print(f"TARGET: {target}")
    print(f"STATUS: {status}")
    if missing:
        print(f"MISSING: {', '.join(missing)}")
    else:
        print("MISSING: None")
    print("-" * 40)

if __name__ == "__main__":
    print("=== DÉMONSTRATION DU VALIDATEUR ===")
    
    # 1. Validation d'une map convertie complètement
    log_validation(
        source="pmd-red/data/map_bg/D13P03 (Tour Céleste Sommet)",
        target="Data/Ground/tour_celeste_sommet.rsground",
        status="SUCCESS",
        missing=[]
    )
    
    # 2. Validation d'un donjon (Génération PMDO)
    log_validation(
        source="pmd-red/src/dungeon_pokemon.c (Spawn List)",
        target="Data/Dungeon/tour_celeste.xml (FloorPlan)",
        status="SUCCESS",
        missing=[]
    )
    
    # 3. Validation Cinématique
    log_validation(
        source="pmd-red/src/data/ground_data_d13p03_station.h (Rayquaza Cinematic)",
        target="Data/Cinematics/rayquaza_climax.lua",
        status="PARTIAL",
        missing=["Adaptation manuelle des coordonnées X/Y exactes de la caméra", "Écriture du texte dans strings.fr.resx"]
    )
