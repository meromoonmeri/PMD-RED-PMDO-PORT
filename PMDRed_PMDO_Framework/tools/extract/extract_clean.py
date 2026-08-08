import os, sys
sys.path.insert(0, os.path.abspath('tools/convert'))
import convert_pmdred_batch

story_maps = {
    'D01P01': ('bois_petit_entree', 'Tiny Woods Entry', 'Entrée du Bois Petit', 'MUS_TINY_WOODS', 'Arc'),
    'D01P02': ('bois_petit_fond', 'Tiny Woods End', 'Fond du Bois Petit', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D02P01': ('grotte_eclair_entree', 'Thunderwave Cave Entry', 'Entrée de la Grotte Éclair', 'MUS_THUNDERWAVE_CAVE', 'Arc'),
    'D02P02': ('grotte_eclair_fond', 'Thunderwave Cave End', 'Fond de la Grotte Éclair', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D03P01': ('mont_acier_entree', 'Mt Steel Entry', 'Entrée du Mont Acier', 'MUS_MT_STEEL', 'Arc'),
    'D03P02': ('mont_acier_sommet', 'Mt Steel Peak', 'Sommet du Mont Acier', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D04P01': ('bois_sinistre_entree', 'Sinister Woods Entry', 'Entrée du Bois Sinistre', 'MUS_SINISTER_WOODS', 'Arc'),
    'D04P02': ('bois_sinistre_fond', 'Sinister Woods End', 'Cœur du Bois Sinistre', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D05P01': ('ravin_silencieux_entree', 'Silent Chasm Entry', 'Entrée du Ravin Silencieux', 'MUS_SILENT_CHASM', 'Arc'),
    'D05P02': ('ravin_silencieux_fond', 'Silent Chasm End', 'Fond du Ravin Silencieux', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D06P01': ('mont_foudre_entree', 'Mt Thunder Entry', 'Entrée du Mont Foudre', 'MUS_MT_THUNDER', 'Arc'),
    'D06P02': ('mont_foudre_relais', 'Mt Thunder Mid', 'Relais du Mont Foudre', 'MUS_MT_THUNDER', 'Arc'),
    'D06P03': ('mont_foudre_sommet', 'Mt Thunder Peak', 'Sommet du Mont Foudre', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D07P01': ('grand_canyon_entree', 'Great Canyon Entry', 'Entrée du Grand Canyon', 'MUS_GREAT_CANYON', 'Arc'),
    'D08P01': ('grotte_lapis_entree', 'Lapis Cave Entry', 'Entrée de la Grotte Lapis', 'MUS_LAPIS_CAVE', 'Arc'),
    'D08P02': ('grotte_lapis_fond', 'Lapis Cave End', 'Fond de la Grotte Lapis', 'MUS_THERES_TROUBLE', 'Arc'),
    'D09P01': ('mont_brasier_entree', 'Mt Blaze Entry', 'Entrée du Mont Brasier', 'MUS_MT_BLAZE', 'Arc'),
    'D09P02': ('mont_brasier_relais', 'Mt Blaze Mid', 'Relais du Mont Brasier', 'MUS_MT_BLAZE', 'Arc'),
    'D09P03': ('mont_brasier_sommet', 'Mt Blaze Peak', 'Sommet du Mont Brasier', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D10P01': ('foret_givree_entree', 'Frosty Forest Entry', 'Entrée de la Forêt Givrée', 'MUS_ESCAPE_THROUGH_THE_SNOW', 'Arc'),
    'D10P02': ('foret_givree_relais', 'Frosty Forest Mid', 'Relais de la Forêt Givrée', 'MUS_FROSTY_FOREST', 'Arc'),
    'D10P03': ('foret_givree_fond', 'Frosty Forest End', 'Fond de la Forêt Givrée', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D11P01': ('mont_gel_entree', 'Mt Freeze Entry', 'Entrée du Mont Gel', 'MUS_ESCAPE_THROUGH_THE_SNOW', 'Arc'),
    'D11P02': ('mont_gel_relais', 'Mt Freeze Mid', 'Relais du Mont Gel', 'MUS_MT_FREEZE', 'Arc'),
    'D11P03': ('mont_gel_sommet', 'Mt Freeze Peak', 'Sommet du Mont Gel', 'MUS_LEGEND_OF_NINETALES', 'Arc'),
    'D12P01': ('caverne_magma_entree', 'Magma Cavern Entry', 'Entrée Caverne Magma', 'MUS_MAGMA_CAVERN', 'Arc'),
    'D12P02': ('caverne_magma_relais', 'Magma Cavern Mid', 'Relais Caverne Magma', 'MUS_MAGMA_CAVERN', 'Arc'),
    'D12P04': ('caverne_magma_fond', 'Magma Cavern End', 'Fond Caverne Magma', 'MUS_IN_THE_DEPTHS_OF_THE_PIT', 'Arc'),
    'D13P01': ('tour_celeste_entree', 'Sky Tower Entry', 'Entrée de la Tour Céleste', 'MUS_SKY_TOWER', 'Arc'),
    'D13P02': ('tour_celeste_relais', 'Sky Tower Mid', 'Relais de la Tour Céleste', 'MUS_SKY_TOWER', 'Arc'),
    'D13P03': ('tour_celeste_sommet', 'Sky Tower Summit', 'Sommet de la Tour Céleste', 'MUS_RAYQUAZAS_DOMAIN', 'Arc'),
    'T01P01': ('place_pokemon_ruines', 'Pokemon Square Ruins', 'Place Pokémon', 'MUS_POKEMON_SQUARE', 'Arc'),
    'T01P05': ('dojo_makuhita_ruines', 'Makuhita Dojo Ruins', 'Ruines du Dojo Makuhita', 'MUS_MAKUHITA_DOJO', 'Arc'),
    'T00P01': ('base_equipe_sauvetage', 'Rescue Team Base', 'Ancienne Base de l\'Équipe de Secours', 'MUS_TEAM_BASE', 'Arc')
}

convert_pmdred_batch.MANIFEST.clear()
convert_pmdred_batch.MANIFEST.update(story_maps)

print("Extraction PMD Red Pure...")
for src in story_maps.keys():
    try:
        convert_pmdred_batch.convert(src)
    except Exception as e:
        pass
print("Done")
