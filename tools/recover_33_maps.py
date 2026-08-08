#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recover_33_maps.py — Récupération d'urgence des 33 maps canoniques PMD Red
=============================================================================
Mission : reconstruire les 33 cartes Pixel-Perfect (Arc Fugitif, chapitres 6-10,
villes) purgées par erreur du disque local, et les téléverser sur
meromoonmeri/PMD-RED-PMDO-PORT avec sauvegarde continue.

Pipeline : identique à tools/convert_pmdred_batch.py de New Era (validé sur la
zone pilote autel_celeste / D13P03) :
  - décodage BPL (palettes) / BPC (tuiles+chunks) / BMA (layout+collision) GBA
  - rendu identity-mapped 1:1 (aucune transformation spatiale)
  - collision : couche BMA d'origine (skytemple-files), fallback « tuile noire »
    documenté si hasCollision=0
  - positions d'entités lues dans src/data/ground/ground_data_*_station.h
    (kind 0 -> Main_Entrance_Marker ; 4/34/10/11 -> TEAMMATE_n ;
     kind>=80 -> Boss_Marker ; effets -> Cutscene_Marker)
  - écriture : Content->output/Tiles/{Sheet}.tile + output/Grounds/{asset}.rsground

STRATÉGIE DE SAUVEGARDE EN CONTINU (par carte) :
  1. générer .tile + .rsground
  2. git add -A
  3. git commit -m "feat: Export carte {id}"
  4. git push origin master
  5. os.remove() des fichiers locaux générés  -> disque sandbox libéré
  6. git update-index --skip-worktree <fichiers>  -> git ne voit plus leur
     absence ; ils restent commités dans la branche et dans l'historique.

Usage :
  python3 tools/recover_33_maps.py            (les 33 cartes)
  python3 tools/recover_33_maps.py D13P03     (sous-ensemble)
Prérequis : pret/pmd-red clone dans /tmp/pmd-red ; skytemple-files ; git auth
configure sur l'origin (token) ; git user configuré.
"""
import copy
import io
import json
import os
import re
import struct
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'tools'))
from pmdred_lib import render, get_collision, BASE  # noqa: E402

PMDRED = '/tmp/pmd-red'
OUT_TILES = os.path.join(REPO, 'output', 'Tiles')
OUT_GROUNDS = os.path.join(REPO, 'output', 'Grounds')

# ---------------------------------------------------------------------------
# MANIFESTE — 33 CARTES EXACTES (Arc Fugitif, Chapitres 6 à 10, Villes)
# src -> (asset, nom EN, nom FR, musique, usage)
# Les 30 premières proviennent du manifeste canonique New Era (lot 2 + lot 3).
# + D04P02 (Sinister Woods END, Arc Fugitif), D13P03 (Sky Tower END, climax
#   Rayquaza) et T00P01 (Pokémon Square, « Villes »).
# ---------------------------------------------------------------------------
MANIFEST = {
    # --- Lot 2 : entrées / fonds de donjon (Chapitres 1-10) ---
    'D01P01': ('foret_tendre_oree',     'Tender Forest Edge',   'Orée de la Forêt Tendre',
               'Friend Area Forest.ogg', 'reserve entree donjon palier 1'),
    'D02P01': ('grotte_statique_seuil', 'Static Cave Mouth',    'Seuil de la Grotte Statique',
               'Friend Area Cave.ogg',  'reserve entree donjon electrique'),
    'D03P01': ('pic_ferreux_pied',      'Ironclad Foothill',    'Pied du Pic Ferreux',
               'Mt. Horn.ogg',          'reserve entree donjon minier'),
    'D04P01': ('bois_sombres_oree',     'Duskwood Edge',        'Orée des Bois Sombres',
               'Mystifying Forest.ogg', 'entree Sinister Woods (Ch6 New Era)'),
    'D05P01': ('gouffre_muet_bord',     'Silent Rim',           'Bord du Gouffre Muet',
               'Growing Anxiety.ogg',   'reserve entree gouffre'),
    'D06P01': ('mont_grondant_pied',    'Thunderous Foothill',  'Pied du Mont Grondant',
               'Rising Fear.ogg',       'reserve entree donjon orage'),
    'D07P01': ('grand_canyon_porte',    'Vast Canyon Gate',     'Porte du Grand Canyon',
               'Canyon Camp.ogg',       'reserve canyon post-ch10'),
    'D08P01': ('grotte_lazuli_seuil',   'Lazuli Cave Mouth',    'Seuil de la Grotte Lazuli',
               'Water Cave.ogg',        'reserve entree grotte bleue'),
    'D08P02': ('grotte_lazuli_fond',    'Lazuli Cave Depths',   'Fond de la Grotte Lazuli',
               'Lower Spring Cave.ogg', 'reserve salle finale grotte bleue'),
    'D09P01': ('mont_cendre_pied',      'Cinder Foothill',      'Pied du Mont Cendré',
               'Deep Dark Crater.ogg',  'reserve entree donjon feu'),
    'D10P01': ('foret_givree_oree',     'Frostwood Edge',       'Orée de la Forêt Givrée',
               'Snow Camp.ogg',         'entree candidate Sentier Glaciaire (ch8)'),
    'D11P01': ('mont_gele_pied',        'Frozen Foothill',      'Pied du Mont Gelé',
               'Summit.ogg',            'entree candidate Sentier Enneigé (ch10)'),
    'D12P01': ('gorge_ardente_porte',   'Magmatic Gate',        'Porte de la Gorge Ardente',
               'In the Depths of the Pit.ogg', 'reserve arc Groudon (ch5)'),
    'D13P01': ('parvis_celeste',        'Celestial Forecourt',  'Parvis Céleste',
               'Sky Peak Prairie.ogg',  'entree Sky Tower (Ch10 New Era)'),
    'D22P01': ('vallon_perdu',          'Lost Hollow',          'Vallon Perdu',
               'Sympathy.ogg',          'reserve scene de sauvetage'),
    'D23P01': ('sanctuaire_voeu',       'Wishing Sanctum',      'Sanctuaire du Vœu',
               'Star Cave.ogg',         'salle finale Grotte du Voeu (Jirachi)'),
    'D24P01': ('caverne_trouble_fond',  'Murkdepth Hall',       'Fond de la Caverne Trouble',
               'Mysterious Passage.ogg', 'reserve salle de sceau'),
    'D24P02': ('caverne_trouble_autel', 'Murkdepth Altar',      'Autel de la Caverne Trouble',
               'Luminous Spring.ogg',   'reserve autel de sceau'),
    # --- Lot 3 : arènes de cinématique de boss ---
    'D12P02': ('gorge_ardente_coeur',   'Magmatic Heart',       'Cœur de la Gorge Ardente',
               'In the Depths of the Pit.ogg', 'cinematique mi-parcours arc Groudon'),
    'D12P04': ('fosse_ardente',         'Blazing Pit',          'Fosse Ardente',
               'In the Depths of the Pit.ogg', 'arene Groudon'),
    'D13P02': ('palier_celeste',        'Celestial Landing',    'Palier Céleste',
               'Sky Peak Cave.ogg',     'relais Sky Tower'),
    'D14P01': ('abime_tempetes',        'Storm Abyss',          'Abîme des Tempêtes',
               'On the Beach at Dusk.ogg', 'arene Kyogre'),
    'D15P01': ('fosse_argentee',        'Silver Deep',          'Fosse Argentée',
               'Water Cave.ogg',        'arene Lugia'),
    'D16P01': ('champ_braises',         'Ember Reach',          'Champ des Braises',
               'Deep Dark Crater.ogg',  'arene Moltres'),
    'D17P01': ('champ_foudre',          'Stormbolt Reach',      'Champ de la Foudre',
               'Rising Fear.ogg',       'arene Raikou'),
    'D18P01': ('champ_vent_boreal',     'Northgale Reach',      'Champ du Vent Boréal',
               'Snow Camp.ogg',         'arene Articuno'),
    'D19P01': ('sommet_aurore',         'Dawnlit Summit',       'Sommet de l’Aurore',
               'Summit.ogg',            'arene Ho-Oh'),
    'D20P01': ('antre_occident',        'Westward Den',         'Antre de l’Occident',
               'Growing Anxiety.ogg',   'arene Mewtwo'),
    'D21P01': ('cretes_boreales',       'Northern Crests',      'Crêtes Boréales',
               'Mt. Travail.ogg',       'arene Latios/Latias'),
    'D25P01': ('bois_des_plaintes',     'Wailing Woods',        'Bois des Plaintes',
               'Mystifying Forest.ogg', 'arene Suicune'),
    # --- Arc Fugitif / Villes (complément pour 33) ---
    'D04P02': ('bois_sombres_fond',     'Duskwood Depths',      'Fond des Bois Sombres',
               'In the Depths of the Pit.ogg', 'Sinister Woods END (boss)'),
    'D13P03': ('tour_ciel_sommet',      'Sky Tower Summit',     'Sommet de la Tour du Ciel',
               'Rayquazas Domain.ogg',  'Sky Tower END (climax Rayquaza, Ch10)'),
    'T00P01': ('place_pokemon',         'Pokemon Square',       'Place Pokémon',
               'Pokemon Square.ogg',    'ville principale (Pokemon Square)'),
}

# Gabarit de spawner TEAMMATE_n (extrait de New Era searing_tunnel_midpoint)
TEAMMATE_TEMPLATE = {
    "NPCName": "Teammate1", "NPCChar": {
        "Nickname": "", "OriginalUUID": "", "OriginalTeam": "",
        "BaseForm": {"Species": "missingno", "Form": 0, "Skin": "normal", "Gender": 0},
        "Level": 0, "EXP": 0, "MaxHPBonus": 0, "AtkBonus": 0, "DefBonus": 0,
        "MAtkBonus": 0, "MDefBonus": 0, "SpeedBonus": 0,
        "BaseSkills": [{"SkillNum": "", "Charges": 0, "CanForget": True} for _ in range(4)],
        "BaseIntrinsics": ["none"], "FormIntrinsicSlot": -1, "Relearnables": {},
        "Discriminator": 0, "MetAt": "", "MetLoc": {"ID": "", "StructID": {"Segment": -1, "ID": -1},
        "EntryPoint": -1}, "DefeatAt": "", "DefeatLoc": {"ID": "", "StructID": {"Segment": -1,
        "ID": -1}, "EntryPoint": -1}, "IsFounder": False, "IsPartner": False,
        "NameLocked": False, "IsFavorite": False, "Unrecruitable": False,
        "ActionEvents": [], "ScriptVars": None},
    "EntName": "TEAMMATE_1", "Direction": 4, "EntEnabled": True, "EntOrder": 0,
    "InteractOrder": 0, "triggerType": 0, "EntityCallbacks": [0],
    "Collider": {"X": 220, "Y": 352, "Width": 16, "Height": 16},
}


def station_path(src):
    return os.path.join(PMDRED, 'src', 'data', 'ground',
                        f'ground_data_{src.lower()}_station.h')


LIVES_RE = re.compile(
    r'/\*\s*\d+\s*\*/\s*\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
    r'\s*\{\s*(\d+)\s*,\s*(\d+)\s*,')
BLOCK_RE = re.compile(
    r'static const struct (GroundLivesData|GroundEffectData)'
    r'\s+(\w+)\[\]\s*=\s*\{(.*?)\n\};', re.S)


def parse_station(src):
    txt = open(station_path(src), encoding='utf-8', errors='replace').read()
    lives_blocks, effs_blocks = [], []
    for kind, name, body in BLOCK_RE.findall(txt):
        entries = [(int(m[0]), int(m[4]), int(m[5])) for m in LIVES_RE.findall(body)]
        if not entries:
            continue
        (lives_blocks if kind == 'GroundLivesData' else effs_blocks).append(entries)
    lives = next((b for b in lives_blocks if any(k == 0 for k, _, _ in b)),
                 lives_blocks[0] if lives_blocks else [])
    effs = effs_blocks[0] if effs_blocks else []
    return lives, [(x, y) for _, x, y in effs]


def write_tile_file(img, out_path, tile_size=8):
    W, H = img.size
    cols, rows = W // tile_size, H // tile_size
    entries = []
    for y in range(rows):
        for x in range(cols):
            t = img.crop((x*tile_size, y*tile_size, (x+1)*tile_size, (y+1)*tile_size))
            buf = io.BytesIO()
            t.save(buf, 'PNG', optimize=True)
            entries.append(((x | (y << 32)), buf.getvalue()))
    uniq, order = {}, []
    for key, png in entries:
        if png not in uniq:
            uniq[png] = None
            order.append(png)
    header_size = 8 + len(entries) * 16
    offsets, pos = {}, header_size
    for h in order:
        offsets[h] = pos
        pos += 8 + len(h)
    out = bytearray()
    out += struct.pack('<II', tile_size, len(entries))
    for key, png in entries:
        out += struct.pack('<QQ', key, offsets[png])
    for h in order:
        out += struct.pack('<Q', len(h)) + h
    open(out_path, 'wb').write(bytes(out))
    return len(entries), len(order)


def mk_marker(nm, x, y, direction=4):
    return {"EntName": nm, "Direction": direction, "EntEnabled": True,
            "EntOrder": 0, "InteractOrder": 0, "triggerType": 0,
            "Collider": {"X": x, "Y": y, "Width": 16, "Height": 16}}


def mk_spawner(nm, x, y):
    s = copy.deepcopy(TEAMMATE_TEMPLATE)
    s['NPCName'] = 'Teammate' + nm[-1]
    s['EntName'] = nm
    s['Collider'] = {"X": x, "Y": y, "Width": 16, "Height": 16}
    return s


def make_rsground(name, name_en, name_fr, comment, music, sheet, W, H, collision,
                  markers, spawners, out_path):
    def tile(x, y):
        return {"AutoTileset": "", "Associates": [],
                "Layers": [{"Frames": [{"Sheet": sheet, "TexLoc": {"X": x, "Y": y}}],
                            "FrameLength": 60}],
                "NeighborCode": -1}
    tiles = [[tile(x, y) for y in range(H)] for x in range(W)]
    obstacles = [[{"Bounds": {"X": x*8, "Y": y*8, "Width": 8, "Height": 8},
                   "Tags": 1 if collision[y*W + x] else 0}
                  for y in range(H)] for x in range(W)]
    d = {
        "Version": "0.8.9.0",
        "Object": {
            "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
            "TexSize": 1,
            "Name": {"DefaultText": name_en, "LocalTexts": {"fr": name_fr}},
            "Released": False,
            "Comment": comment,
            "obstacles": obstacles,
            "rand": {"$type": "RogueElements.ReRandom, RogueElements",
                     "FirstSeed": 0, "s": [16294208416658607535, 7960286522194355700,
                                           4876170194715417726, 12554865158188930543]},
            "Status": {},
            "Background": {"$type": "RogueEssence.Dungeon.MapBG, RogueEssence",
                           "MapLoc": {"X": 0, "Y": 0},
                           "BGAnim": {"AnimIndex": "", "FrameTime": 1,
                                      "StartFrame": -1, "EndFrame": -1,
                                      "AnimDir": -1, "Alpha": 255, "AnimFlip": 0},
                           "BGMovement": {"X": 0, "Y": 0},
                           "RepeatX": False, "RepeatY": False},
            "BlankBG": {"AutoTileset": "", "Associates": [], "Layers": [],
                        "NeighborCode": -1},
            "Layers": [{"Name": "Base", "Layer": 0, "Visible": True,
                        "Tiles": tiles}],
            "AssetName": name,
            "Music": music,
            "EdgeView": 1,
            "NoSwitching": False,
            "ViewCenter": None,
            "ViewOffset": {"X": 0, "Y": 0},
            "ActiveChar": None,
            "Decorations": [{"Name": "New Deco", "Layer": 0, "Visible": True,
                             "Anims": []}],
            "Entities": [{"Name": "New EntLayer", "Visible": True,
                          "MapChars": [],
                          "GroundObjects": [],
                          "Spawners": spawners,
                          "Markers": markers}],
        },
    }
    with io.open(out_path, 'w', encoding='utf-8-sig') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def sheet_name(asset):
    return ''.join(p.capitalize() for p in asset.split('_')) + '_Base'


def flood_stats(collision, W, H, sx, sy):
    from collections import deque
    walk = {(x, y) for x in range(W) for y in range(H) if not collision[y*W + x]}
    if (sx, sy) not in walk:
        return 0, len(walk), False
    seen, q = {(sx, sy)}, deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x+dx, y+dy)
            if n in walk and n not in seen:
                seen.add(n)
                q.append(n)
    return len(seen), len(walk), True


def convert(src):
    """Génère .tile + .rsground dans output/ et renvoie les infos."""
    asset, name_en, name_fr, music, usage = MANIFEST[src]
    img, W, H = render(src, None)
    from PIL import Image
    bg = Image.new('RGBA', img.size, (0, 0, 0, 255))
    bg.alpha_composite(img)
    img = bg
    coll, cw, ch = get_collision(f'{BASE}/{src}m.bma')
    coll_derived = False
    if coll is None:
        coll_derived = True
        cw, ch = W, H
        px = img.load()
        coll = []
        for y in range(H):
            for x in range(W):
                black = all(px[x*8+i, y*8+j][:3] == (0, 0, 0)
                            for i in (0, 3, 7) for j in (0, 3, 7))
                coll.append(1 if black else 0)
    assert (cw, ch) == (W, H), f'{src}: collision {cw}x{ch} != rendu {W}x{H}'
    lives, effs = parse_station(src)

    sheet = sheet_name(asset)
    os.makedirs(OUT_TILES, exist_ok=True)
    os.makedirs(OUT_GROUNDS, exist_ok=True)
    tile_path = os.path.join(OUT_TILES, f'{sheet}.tile')
    ground_path = os.path.join(OUT_GROUNDS, f'{asset}.rsground')
    n_ent, n_uniq = write_tile_file(img, tile_path)

    T = 8
    markers, spawners = [], []
    mates = 0
    boss_done = False
    npc_i = 0
    hero = None
    for kind, x, y in lives:
        if kind == 0 and hero is None:
            hero = (x, y)
            markers.append(mk_marker('Main_Entrance_Marker', x*T, y*T, 0))
        elif kind in (4, 34, 10, 11) and mates < 3:
            mates += 1
            spawners.append(mk_spawner(f'TEAMMATE_{mates}', x*T, y*T))
        elif kind >= 80 and not boss_done:
            boss_done = True
            markers.append(mk_marker('Boss_Marker', x*T, y*T, 4))
        else:
            npc_i += 1
            markers.append(mk_marker(f'PNJ_Marker_{npc_i}', x*T, y*T, 4))
    for i, (x, y) in enumerate(effs):
        markers.append(mk_marker(f'Cutscene_Marker_{i+1}' if i else 'Cutscene_Marker',
                                 x*T, y*T, 4))
    if hero is None:
        walk = [(x, y) for x in range(W) for y in range(H) if not coll[y*W + x]]
        cx = sum(p[0] for p in walk)//len(walk)
        cy = sum(p[1] for p in walk)//len(walk)
        hero = (cx, cy)
        markers.insert(0, mk_marker('Main_Entrance_Marker', cx*T, cy*T, 0))

    comment = (f'PMD Red {src} -> {asset}. Imported 1:1 from pret/pmd-red. '
               f'Geometry, collision and entity positions preserved from '
               f'ground_data_{src.lower()}_station.h. Usage: {usage}.'
               + (' Collision derived from visible area (source BMA has no '
                  'collision layer).' if coll_derived else ''))
    make_rsground(asset, name_en, name_fr, comment, music, sheet, W, H, coll,
                  markers, spawners, ground_path)

    reach, walk_n, on_walk = flood_stats(coll, W, H, hero[0], hero[1])
    print(f'{src} -> {asset:24s} {W}x{H}  tiles={n_ent}({n_uniq}u)  '
          f'lives={len(lives)} effs={len(effs)}  '
          f'flood={reach}/{walk_n}{"" if on_walk else "  !! HERO SUR MUR"}')
    return {'src': src, 'asset': asset, 'fr': name_fr, 'W': W, 'H': H,
            'tile': tile_path, 'ground': ground_path,
            'lives': lives, 'effs': effs, 'reach': reach, 'walk': walk_n,
            'hero_on_walk': on_walk, 'usage': usage, 'music': music,
            'coll_derived': coll_derived}


def git(*args, check=True):
    return subprocess.run(['git'] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def save_and_purge(src, info):
    """git add -A && commit && push origin master && os.remove + skip-worktree."""
    files = [info['tile'], info['ground']]
    # Re-execution : si les fichiers sont deja skip-worktree (export precedente),
    # on retire le flag pour permettre un eventuel re-add ; sinon git add -A
    # les ignorerait et le commit echouerait sur « nothing to commit ».
    git('update-index', '--no-skip-worktree', *files, check=False)
    git('add', '-A')
    cp = git('commit', '-m', f'feat: Export carte {src}', check=False)
    if cp.returncode != 0:
        if 'nothing to commit' in (cp.stdout + cp.stderr):
            # deja exporte (meme contenu) : on purge et on considere OK
            print(f'  deja a jour: {src}')
        else:
            print(f'  !! COMMIT ECHOUE pour {src}:\n{(cp.stdout+cp.stderr)[-800:]}')
            sys.exit(2)
    p = git('push', 'origin', 'master', check=False)
    if p.returncode != 0:
        print(f'  !! PUSH ECHOUE pour {src}:\n{p.stderr[-800:]}')
        sys.exit(2)
    print(f'  pushed origin/master: {src}')
    # Purge du disque local : les fichiers restent commités (branche + historique)
    for f in files:
        if os.path.exists(f):
            os.remove(f)
    git('update-index', '--skip-worktree', *files)
    print(f'  purge locale + skip-worktree: {os.path.basename(files[0])}, '
          f'{os.path.basename(files[1])}')


def main():
    targets = sys.argv[1:] or list(MANIFEST)
    print(f'RECUPERATION {len(targets)} MAPS -> {REPO}')
    print('=' * 70)
    results = []
    for src in targets:
        if src not in MANIFEST:
            print(f'!! inconnu: {src}')
            continue
        print(f'--- {src} ({MANIFEST[src][1]}) ---')
        info = convert(src)
        save_and_purge(src, info)
        results.append(info)
    bad = [r for r in results if not r['hero_on_walk'] or r['reach'] == 0]
    print('=' * 70)
    print(f'{len(results)} cartes converties + poussees, {len(bad)} anomalies')
    for r in bad:
        print('  !!', r['src'], r['asset'], 'hero sur mur' if not r['hero_on_walk'] else 'flood 0')
    print('Disque :', sum(os.path.getsize(r['tile']) + os.path.getsize(r['ground'])
                          for r in results if os.path.exists(r['tile'])),
          'octets restants (0 = tout purge)')


if __name__ == '__main__':
    main()
