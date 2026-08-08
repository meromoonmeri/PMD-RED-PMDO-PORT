#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recover_all_maps.py — Export pixel-perfect de TOUTES les maps PMD Red restantes
=================================================================================
Suite de recover_33_maps.py : après les 33 cartes canoniques (Arc Fugitif,
Ch6-10, Villes), on exporte les 212 cartes restantes de pret/pmd-red avec le
même pipeline 1:1 et la même sauvegarde continue (commit + push + purge).

Le manifeste est construit DYNAMIQUEMENT depuis map_dependencies.json
(245 entrées), qui donne les noms de fichiers EXACTS par carte — les triplets
bpl/bpc/bma ne partagent pas toujours la même base (ex: T01P02A + T01P02c +
T01P02Am). Les 33 cartes déjà exportées (par recover_33_maps.py) sont sautées.

Noms : asset = bpl.lower() (ex 't01p01'). Les positions d'entités sont lues
dans le station header quand il existe (src/data/ground/ground_data_*.h) ;
sinon, repli = Main_Entrance_Marker au centre de la zone marchable (le rendu
et la collision restent 1:1).

Usage :
  python3 tools/recover_all_maps.py                (toutes les restantes)
  python3 tools/recover_all_maps.py t01p01 ...     (sous-ensemble par bpl)
Prérequis : identiques à recover_33_maps.py (pret/pmd-red dans /tmp/pmd-red,
skytemple-files, git auth configurée).
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
from pmdred_lib import parse_bpl, parse_bpc, decode_bma, get_collision, BASE  # noqa: E402
from PIL import Image

PMDRED = '/tmp/pmd-red'
OUT_TILES = os.path.join(REPO, 'output', 'Tiles')
OUT_GROUNDS = os.path.join(REPO, 'output', 'Grounds')
DEP = json.load(open(os.path.join(REPO, 'map_dependencies.json')))

# Les 33 sources déjà exportées par recover_33_maps.py (par bpl)
ALREADY_EXPORTED = {
    'D01P01', 'D02P01', 'D03P01', 'D04P01', 'D04P02', 'D05P01', 'D06P01',
    'D07P01', 'D08P01', 'D08P02', 'D09P01', 'D10P01', 'D11P01', 'D12P01',
    'D12P02', 'D12P04', 'D13P01', 'D13P02', 'D13P03', 'D14P01', 'D15P01',
    'D16P01', 'D17P01', 'D18P01', 'D19P01', 'D20P01', 'D21P01', 'D22P01',
    'D23P01', 'D24P01', 'D24P02', 'D25P01', 'T00P01',
}

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


# --- rendu avec noms de fichiers EXPLICITES (bpl/bpc/bma differents) --------
def render_ext(bpl, bpc, bma, transparent_bg=False):
    pals = parse_bpl(f'{BASE}/{bpl}.bpl')
    cw, chh, tiles, chunks = parse_bpc(f'{BASE}/{bpc}.bpc')
    Wt, Ht, Wc, Hc, nL, hC, layers = decode_bma(f'{BASE}/{bma}.bma')
    bg = (0, 0, 0, 0) if transparent_bg else (0, 0, 0, 255)
    img = Image.new('RGBA', (Wt * 8, Ht * 8), bg)
    for lay in reversed(layers):
        for cy in range(Hc):
            for cx in range(Wc):
                cid = lay[cy * 64 + cx]
                if cid <= 0 or cid >= len(chunks):
                    continue
                for i, ent in enumerate(chunks[cid]):
                    ti = ent & 0x3FF
                    hf = (ent >> 10) & 1
                    vf = (ent >> 11) & 1
                    pi = (ent >> 12) & 0xF
                    if ti == 0 or ti >= len(tiles):
                        continue
                    tx, ty = cx * 3 + i % 3, cy * 3 + i // 3
                    if tx * 8 + 8 > Wt * 8 or ty * 8 + 8 > Ht * 8:
                        continue
                    td = tiles[ti]
                    pal = pals[pi % len(pals)]
                    for y in range(8):
                        for x in range(4):
                            b = td[y * 4 + x]
                            for k2, ci in enumerate((b & 0xF, b >> 4)):
                                if ci == 0:
                                    continue
                                xx = x * 2 + k2
                                yy = y
                                if hf:
                                    xx = 7 - xx
                                if vf:
                                    yy = 7 - yy
                                img.putpixel((tx * 8 + xx, ty * 8 + yy), pal[ci])
    return img, Wt, Ht


def station_path(bpl):
    return os.path.join(PMDRED, 'src', 'data', 'ground',
                        f'ground_data_{bpl.lower()}_station.h')


LIVES_RE = re.compile(
    r'/\*\s*\d+\s*\*/\s*\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
    r'\s*\{\s*(\d+)\s*,\s*(\d+)\s*,')
BLOCK_RE = re.compile(
    r'static const struct (GroundLivesData|GroundEffectData)'
    r'\s+(\w+)\[\]\s*=\s*\{(.*?)\n\};', re.S)


def parse_station(bpl):
    """(lives, effs) depuis le header ; ([], []) si absent."""
    p = station_path(bpl)
    if not os.path.isfile(p):
        return [], []
    txt = open(p, encoding='utf-8', errors='replace').read()
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


def convert(mid, bpl, bpc, bma):
    """Génère .tile + .rsground pour une carte, retourne les infos."""
    asset = bpl.lower()
    img, W, H = render_ext(bpl, bpc, bma)
    bg = Image.new('RGBA', img.size, (0, 0, 0, 255))
    bg.alpha_composite(img)
    img = bg
    coll, cw, ch = get_collision(f'{BASE}/{bma}.bma')
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
    assert (cw, ch) == (W, H), f'{asset}: collision {cw}x{ch} != rendu {W}x{H}'
    lives, effs = parse_station(bpl)

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
        if walk:
            # centre géométrique de la carte, puis walkable le plus proche
            gx = W // 2
            gy = H // 2
            hero = min(walk, key=lambda p: (p[0]-gx)**2 + (p[1]-gy)**2)
            markers.insert(0, mk_marker('Main_Entrance_Marker', hero[0]*T, hero[1]*T, 0))

    comment = (f'PMD Red {bpl} ({mid}). Pixel-perfect export 1:1 from '
               f'pret/pmd-red (bpl {bpl}, bpc {bpc}, bma {bma}). '
               + ('Entity positions from ground_data_station.h. '
                  if lives or effs else 'No station header: fallback marker '
                  'at walkable center. ')
               + ('Collision derived from visible area (source BMA has no '
                  'collision layer).' if coll_derived else 'Collision from '
                  'source BMA.'))
    make_rsground(asset, asset.upper(), asset.upper(), comment, '', sheet, W, H,
                  coll, markers, spawners, ground_path)

    reach, walk_n, on_walk = flood_stats(coll, W, H,
                                         (hero[0] if hero else 0),
                                         (hero[1] if hero else 0))
    print(f'{bpl} ({mid}) -> {asset:20s} {W}x{H}  tiles={n_ent}({n_uniq}u)  '
          f'lives={len(lives)} effs={len(effs)}  flood={reach}/{walk_n}'
          f'{"  !! HERO SUR MUR" if (hero and not on_walk) else ""}')
    return {'src': bpl, 'mid': mid, 'asset': asset, 'W': W, 'H': H,
            'tile': tile_path, 'ground': ground_path,
            'lives': lives, 'effs': effs, 'reach': reach, 'walk': walk_n,
            'hero_on_walk': on_walk, 'coll_derived': coll_derived}


def git(*args, check=True):
    return subprocess.run(['git'] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def save_and_purge(src, info):
    files = [info['tile'], info['ground']]
    git('update-index', '--no-skip-worktree', *files, check=False)
    git('add', '-A')
    cp = git('commit', '-m', f'feat: Export carte {src}', check=False)
    if cp.returncode != 0:
        if 'nothing to commit' in (cp.stdout + cp.stderr):
            print(f'  deja a jour: {src}')
        else:
            print(f'  !! COMMIT ECHOUE pour {src}:\n{(cp.stdout+cp.stderr)[-800:]}')
            sys.exit(2)
    p = git('push', 'origin', 'master', check=False)
    if p.returncode != 0:
        print(f'  !! PUSH ECHOUE pour {src}:\n{p.stderr[-800:]}')
        sys.exit(2)
    print(f'  pushed origin/master: {src}')
    for f in files:
        if os.path.exists(f):
            os.remove(f)
    git('update-index', '--skip-worktree', *files)
    print(f'  purge locale + skip-worktree: {os.path.basename(files[0])}, '
          f'{os.path.basename(files[1])}')


def already_on_origin():
    out = git('ls-tree', '-r', '--name-only', 'origin/master', check=False)
    grounds = set()
    for line in (out.stdout or '').splitlines():
        line = line.strip()
        if line.startswith('output/Grounds/') and line.endswith('.rsground'):
            grounds.add(os.path.basename(line)[:-9])
    return grounds


def main():
    force = '--force' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--force']
    on_origin = already_on_origin()
    targets = args
    if targets:
        wanted = {t.lower() for t in targets}
        entries = [(mid, e) for mid, e in DEP.items() if e['bpl'].lower() in wanted]
    else:
        entries = [(mid, e) for mid, e in DEP.items()
                   if e['bpl'] not in ALREADY_EXPORTED]
    entries.sort(key=lambda x: x[1]['bpl'])
    print(f'EXPORT {len(entries)} MAPS -> {REPO} (deja sur origin: '
          f'{len(on_origin)})')
    print('=' * 70)
    results, skipped = [], []
    for mid, e in entries:
        bpl, bpc, bma = e['bpl'], e['bpc'], e['bma']
        asset = bpl.lower()
        if asset in on_origin and not force:
            print(f'--- {bpl} ({mid}) --- deja exporte, skip')
            skipped.append(bpl)
            continue
        print(f'--- {bpl} ({mid}) ---')
        info = convert(mid, bpl, bpc, bma)
        save_and_purge(bpl, info)
        results.append(info)
    bad = [r for r in results if not r['hero_on_walk'] or r['reach'] == 0]
    print('=' * 70)
    print(f'{len(results)} cartes exportees ce run (+{len(skipped)} deja faites), '
          f'{len(bad)} anomalies')
    for r in bad:
        print('  !!', r['src'], r['asset'],
              'hero sur mur' if not r['hero_on_walk'] else 'flood 0')


if __name__ == '__main__':
    main()
