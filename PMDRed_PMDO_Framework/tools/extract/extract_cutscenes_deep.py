import os, sys, re, json

repo_dir = os.path.abspath('repo')
pmdred_dir = '/tmp/pmd-red'
report_path = os.path.join(repo_dir, 'docs', 'CINEMATIC_ASSET_DATABASE.md')

def scan_file_for_macros(filepath):
    if not os.path.exists(filepath):
        return []
    macros = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            # Capture specific technical macros
            for target in ['FLASH_TO', 'FLASH_FROM', 'BGM_SWITCH', 'BGM_FADEOUT', 'CAMERA_PAN', 'CAMERA_INIT_PAN', 'SE_PLAY', 'SCREEN_SHAKE', 'CALL_SCRIPT']:
                if target in line:
                    macros.append(line)
    return macros

scenes_to_extract = [
    {
        'id': 'RAYQUAZA_METEOR_HYPERBEAM',
        'desc': 'Apparition de Rayquaza, chargement de l\'Ultralaser et destruction de la météorite',
        'files': ['src/data/ground/ground_data_d13p03_station.h']
    },
    {
        'id': 'METEOR_PANIC_SQUARE',
        'desc': 'Panique sur la place Pokémon, caméras frénétiques et flashs sombres',
        'files': ['src/data/ground/ground_data_t01p01_station.h']
    },
    {
        'id': 'ARTICUNO_AMBUSH',
        'desc': 'Rencontre Artikodin et intervention Absol, flashs aveuglants',
        'files': ['src/data/ground/ground_data_d10p03_station.h']
    }
]

with open(report_path, 'w', encoding='utf-8') as out:
    out.write("# CINEMATIC ASSET DATABASE (Extraction Complète PMD Red)\n\n")
    out.write("> **Bibliothèque réutilisable pour la mise en scène dans New Era**\n")
    out.write("> Les scripts narratifs originaux sont exclus. Ce document catalogue la manière de manipuler la caméra, les palettes, et les animations pour recréer l'intensité des cinématiques 30 ans plus tard.\n\n")

    for s in scenes_to_extract:
        out.write(f"## [{s['id']}] {s['desc']}\n")
        
        all_macros = []
        for file in s['files']:
            all_macros.extend(scan_file_for_macros(os.path.join(pmdred_dir, file)))
            
        # Classify
        bgm = [m for m in all_macros if 'BGM_' in m]
        flashes = [m for m in all_macros if 'FLASH_' in m]
        cameras = [m for m in all_macros if 'CAMERA_' in m]
        scripts = [m for m in all_macros if 'CALL_SCRIPT' in m]
        
        out.write("### SCENE_CAMERA_DATA\n")
        out.write("```c\n")
        for m in cameras:
            out.write(f"{m}\n")
        out.write("```\n")
        
        out.write("### EFFECTS & PARTICLES (VFX Palette Swaps)\n")
        out.write("*(Les explosions comme l'Ultralaser ou la Météorite utilisent principalement des surcharges de couleur plein écran `FLASH_TO` combinées à des tremblements, plutôt que de vraies particules 3D)*\n")
        out.write("```c\n")
        for m in flashes:
            out.write(f"{m}\n")
        out.write("```\n")
        
        out.write("### ANIMATIONS & SHAKES\n")
        out.write("```c\n")
        for m in scripts:
            out.write(f"{m}\n")
        out.write("```\n")
        
        out.write("### AUDIO_SCENE_DATA\n")
        out.write("```c\n")
        unique_bgm = list(set(bgm))
        for m in unique_bgm:
            out.write(f"{m}\n")
        out.write("```\n")
        out.write("---\n")

print("Base de données complète extraite : repo/docs/CINEMATIC_ASSET_DATABASE.md")
