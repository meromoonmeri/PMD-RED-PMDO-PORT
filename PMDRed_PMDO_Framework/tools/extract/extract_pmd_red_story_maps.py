import os, sys, re, json
sys.path.insert(0, os.path.abspath('repo/tools'))
import convert_pmdred_batch

# Dictionnaire de correspondance scénaristique Red Rescue Team -> New Era 
# (Les événements se passent 30 ans plus tard).
story_maps = {
    # 1. Bois Petit (Tiny Woods)
    'D01P01': ('bois_petit_entree', 'Tiny Woods Entry', 'Entrée du Bois Petit (30 ans plus tard)', 'MUS_TINY_WOODS', 'Vestige de la première mission de sauvetage. Les arbres ont poussé.'),
    'D01P02': ('bois_petit_fond', 'Tiny Woods End', 'Fond du Bois Petit (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Vestige.'),

    # 2. Grotte Éclair (Thunderwave Cave)
    'D02P01': ('grotte_eclair_entree', 'Thunderwave Cave Entry', 'Entrée de la Grotte Éclair (30 ans plus tard)', 'MUS_THUNDERWAVE_CAVE', 'Fermée par des éboulements, devenue un nid statique.'),
    'D02P02': ('grotte_eclair_fond', 'Thunderwave Cave End', 'Fond de la Grotte Éclair (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Vestige.'),

    # 3. Mont Acier (Mt. Steel)
    'D03P01': ('mont_acier_entree', 'Mt Steel Entry', 'Entrée du Mont Acier (30 ans plus tard)', 'MUS_MT_STEEL', 'Exploité par la Fédération, minéralisé.'),
    'D03P02': ('mont_acier_sommet', 'Mt Steel Peak', 'Sommet du Mont Acier (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Lieu de la bataille mythique contre Airmure.'),

    # 4. Bois Sinistre (Sinister Woods)
    'D04P01': ('bois_sinistre_entree', 'Sinister Woods Entry', 'Entrée du Bois Sinistre (30 ans plus tard)', 'MUS_SINISTER_WOODS', 'Toujours aussi lugubre, envahi de ronces.'),
    'D04P02': ('bois_sinistre_fond', 'Sinister Woods End', 'Cœur du Bois Sinistre (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Là où Gengar avait piégé l\'Équipe.'),

    # 5. Ravin Silencieux (Silent Chasm)
    'D05P01': ('ravin_silencieux_entree', 'Silent Chasm Entry', 'Entrée du Ravin Silencieux (30 ans plus tard)', 'MUS_SILENT_CHASM', 'Le brouillard s\'est épaissi depuis l\'effondrement.'),
    'D05P02': ('ravin_silencieux_fond', 'Silent Chasm End', 'Fond du Ravin Silencieux (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Où Jumpluff avait disparu.'),

    # 6. Mont Foudre (Mt. Thunder)
    'D06P01': ('mont_foudre_entree', 'Mt Thunder Entry', 'Entrée du Mont Foudre (30 ans plus tard)', 'MUS_MT_THUNDER', 'Vestige foudroyé.'),
    'D06P02': ('mont_foudre_relais', 'Mt Thunder Mid', 'Relais du Mont Foudre (30 ans plus tard)', 'MUS_MT_THUNDER', 'Zone de repos calcinée.'),
    'D06P03': ('mont_foudre_sommet', 'Mt Thunder Peak', 'Sommet du Mont Foudre (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Ancien domaine d\'Électhor.'),

    # 7. Grand Canyon (Great Canyon)
    'D07P01': ('grand_canyon_entree', 'Great Canyon Entry', 'Entrée du Grand Canyon (30 ans plus tard)', 'MUS_GREAT_CANYON', 'Lieu asséché, érosion visible.'),
    'D07P02': ('grand_canyon_sommet', 'Great Canyon Peak', 'Colline des Anciens (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'L\'observatoire de Xatu, abandonné.'),

    # 8. Grotte Lapis (Lapis Cave) - Arc Fugitif
    'D08P01': ('grotte_lapis_entree', 'Lapis Cave Entry', 'Entrée de la Grotte Lapis (30 ans plus tard)', 'MUS_LAPIS_CAVE', 'Arc Fugitif New Era. Joyaux ternis.'),
    'D08P02': ('grotte_lapis_fond', 'Lapis Cave End', 'Fond de la Grotte Lapis (30 ans plus tard)', 'MUS_THERES_TROUBLE', 'Lieu d\'embuscade.'),

    # 9. Mont Brasier (Mt. Blaze) - Arc Fugitif
    'D09P01': ('mont_brasier_entree', 'Mt Blaze Entry', 'Entrée du Mont Brasier (30 ans plus tard)', 'MUS_MT_BLAZE', 'Lave refroidie en obsidienne.'),
    'D09P02': ('mont_brasier_relais', 'Mt Blaze Mid', 'Relais du Mont Brasier (30 ans plus tard)', 'MUS_MT_BLAZE', 'Bivouac volcanique.'),
    'D09P03': ('mont_brasier_sommet', 'Mt Blaze Peak', 'Sommet du Mont Brasier (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Domaine de Sulfura, cratère inactif.'),

    # 10. Forêt Givrée (Frosty Forest) - Arc Fugitif
    'D10P01': ('foret_givree_entree', 'Frosty Forest Entry', 'Entrée de la Forêt Givrée (30 ans plus tard)', 'MUS_ESCAPE_THROUGH_THE_SNOW', 'Glaces persistantes.'),
    'D10P02': ('foret_givree_relais', 'Frosty Forest Mid', 'Relais de la Forêt Givrée (30 ans plus tard)', 'MUS_FROSTY_FOREST', 'Point de survie.'),
    'D10P03': ('foret_givree_fond', 'Frosty Forest End', 'Fond de la Forêt Givrée (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Embuscade d\'Artikodin / Absol.'),

    # 11. Mont Gel (Mt. Freeze) - Arc Fugitif
    'D11P01': ('mont_gel_entree', 'Mt Freeze Entry', 'Entrée du Mont Gel (30 ans plus tard)', 'MUS_ESCAPE_THROUGH_THE_SNOW', 'Froid mordant perpétuel.'),
    'D11P02': ('mont_gel_relais', 'Mt Freeze Mid', 'Relais du Mont Gel (30 ans plus tard)', 'MUS_MT_FREEZE', 'Abri de fortune dans le blizzard.'),
    'D11P03': ('mont_gel_sommet', 'Mt Freeze Peak', 'Sommet du Mont Gel (30 ans plus tard)', 'MUS_LEGEND_OF_NINETALES', 'Autel de Feunard.'),

    # 12. Caverne Magma (Magma Cavern)
    'D12P01': ('caverne_magma_entree', 'Magma Cavern Entry', 'Entrée Caverne Magma (30 ans plus tard)', 'MUS_MAGMA_CAVERN', 'Chaleur insoutenable.'),
    'D12P02': ('caverne_magma_relais', 'Magma Cavern Mid', 'Relais Caverne Magma (30 ans plus tard)', 'MUS_MAGMA_CAVERN', 'Lave bouillonnante.'),
    'D12P03': ('caverne_magma_fosse', 'Magma Cavern Pit', 'Fosse Caverne Magma (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Antichambre de Groudon.'),
    'D12P04': ('caverne_magma_fond', 'Magma Cavern End', 'Fond Caverne Magma (30 ans plus tard)', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Lieu de la bataille primordiale.'),

    # 13. Tour Céleste (Sky Tower)
    'D13P01': ('tour_celeste_entree', 'Sky Tower Entry', 'Entrée de la Tour Céleste (30 ans plus tard)', 'MUS_SKY_TOWER', 'L\'ascension vers les nuages.'),
    'D13P02': ('tour_celeste_relais', 'Sky Tower Mid', 'Relais de la Tour Céleste (30 ans plus tard)', 'MUS_SKY_TOWER', 'Bivouac aérien.'),
    'D13P03': ('tour_celeste_sommet', 'Sky Tower Summit', 'Sommet de la Tour Céleste (30 ans plus tard)', 'MUS_RAYQUAZAS_DOMAIN', 'L\'autel où la météorite a été brisée.'),

    # VILLES ET HUBS HISTORIQUES (Transformés ou abandonnés)
    'T01P01': ('place_pokemon_ruines', 'Pokemon Square Ruins', 'Place Pokémon (30 ans plus tard)', 'MUS_POKEMON_SQUARE', 'L\'ancienne Place Pokémon, aujourd\'hui relique historique du monde d\'avant.'),
    'T01P02B': ('etang_barbicha', 'Whiscash Pond', 'Étang Barbicha (30 ans plus tard)', 'MUS_WHISCASH_POND', 'Barbicha n\'est plus, mais l\'étang demeure sacré.'),
    'T01P05': ('dojo_makuhita_ruines', 'Makuhita Dojo Ruins', 'Ruines du Dojo Makuhita', 'MUS_MAKUHITA_DOJO', 'Le dojo a été détruit par les récents séismes.'),
    'T00P01': ('base_equipe_sauvetage', 'Rescue Team Base', 'Ancienne Base de l\'Équipe de Secours', 'MUS_TEAM_BASE', 'Le mythique QG du Héros d\'antan, envahi par la végétation.')
}

convert_pmdred_batch.MANIFEST.update(story_maps)

results = []
print("Extraction et Reconstruction Canonique 30 Ans Plus Tard...")
for src in story_maps.keys():
    try:
        res = convert_pmdred_batch.convert(src)
        results.append(f"✅ {src} -> {res['asset']}.rsground ({story_maps[src][4]})")
    except Exception as e:
        results.append(f"❌ {src} -> Erreur: {e}")

with open(os.path.join("repo", "docs", "PMD_RED_NEW_ERA_CONTINUITY.md"), "w") as f:
    f.write("# Continuité PMD Red -> New Era (30 Ans Plus Tard)\n\n")
    f.write("> Extraction exhaustive des lieux canoniques de l'histoire principale pour intégration aux cinématiques et à l'Arc Fugitifs de New Era.\n\n")
    for r in results:
        f.write(f"- {r}\n")

print("Conversion terminée. Rapport généré dans docs/PMD_RED_NEW_ERA_CONTINUITY.md")
