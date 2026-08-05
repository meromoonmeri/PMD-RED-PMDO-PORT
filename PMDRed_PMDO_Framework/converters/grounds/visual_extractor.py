import os, struct, io, json
from PIL import Image

def parse_bpl(p):
    with open(p, 'rb') as f: d = f.read()
    n = d[0]; pals = []; off = 4
    for _ in range(n):
        cols = [(0,0,0,0)]
        for c in range(15):
            cols.append((d[off], d[off+1], d[off+2], 255))
            off += 4
        pals.append(cols)
    return pals

def parse_bpc(p):
    with open(p, 'rb') as f: d = f.read()
    cw, chh, nt = struct.unpack_from('<HHH', d, 0)
    nc, = struct.unpack_from('<H', d, 14)
    tiles = [bytes(32)] + [d[16+i*32:16+(i+1)*32] for i in range(nt-1)]
    off = 16 + (nt-1)*32; n = cw * chh
    chunks = [[0]*n]
    for i in range(nc-1):
        chunks.append(list(struct.unpack_from(f'<{n}H', d, off)))
        off += n*2
    return cw, chh, tiles, chunks

def parse_bpa(p):
    """
    Returns (num_tiles_per_frame, num_frames, frames_tiles)
    frames_tiles is a list of lists of tile data (each tile is 32 bytes)
    """
    if not os.path.exists(p):
        return 0, 0, []
        
    with open(p, 'rb') as f: d = f.read()
    
    # We found that offset 28 is where tile data starts for T01P011.bpa
    # Let's dynamically find the offset by assuming the end of the file is tile data
    # and the first two shorts are tiles_per_frame and num_frames.
    tiles_per_frame, num_frames = struct.unpack_from('<HH', d, 0)
    
    if tiles_per_frame == 0 or num_frames == 0:
        return 0, 0, []
        
    expected_tile_data_size = tiles_per_frame * num_frames * 32
    header_size = len(d) - expected_tile_data_size
    
    if header_size < 0:
        print(f"Warning: BPA file {p} has invalid size.")
        return 0, 0, []
        
    off = header_size
    frames = []
    for f in range(num_frames):
        frame_tiles = []
        for t in range(tiles_per_frame):
            frame_tiles.append(d[off:off+32])
            off += 32
        frames.append(frame_tiles)
        
    return tiles_per_frame, num_frames, frames

def decode_bma(p):
    with open(p, 'rb') as f: d = f.read()
    Wt, Ht, tw, th, Wc, Hc = d[:6]
    nL, hD, hC = struct.unpack_from('<HhH', d, 6)
    src = 12; STRIDE = 64; layers = []
    for li in range(nL):
        dst = []
        for j in range(Hc):
            row = []
            prev = dst[(j-1)*STRIDE:j*STRIDE] if j > 0 else [0]*STRIDE
            k = 0
            while k < Wc:
                cmd = d[src]; src += 1
                if cmd >= 0xC0:
                    for l in range(cmd - 0xC0 + 1):
                        v = d[src] | (d[src+1]<<8) | (d[src+2]<<16); src += 3
                        a, b = v & 0xFFF, (v >> 12) & 0xFFF
                        if j > 0: a ^= prev[len(row)]; b ^= prev[len(row)+1]
                        row += [a, b]
                    k += (cmd - 0xBF) * 2
                elif cmd >= 0x80:
                    v = d[src] | (d[src+1]<<8) | (d[src+2]<<16); src += 3
                    for l in range(cmd - 0x80 + 1):
                        a, b = v & 0xFFF, (v >> 12) & 0xFFF
                        if j > 0: a ^= prev[len(row)]; b ^= prev[len(row)+1]
                        row += [a, b]
                    k += (cmd - 0x7F) * 2
                else:
                    for l in range(cmd + 1):
                        if j > 0: row += [prev[len(row)], prev[len(row)+1]]
                        else: row += [0, 0]
                    k += (cmd + 1) * 2
            row = row[:STRIDE] + [0]*(STRIDE - len(row))
            dst += row
        layers.append(dst)
    return Wt, Ht, Wc, Hc, nL, hC, layers

def render_gba_map(base_name, pmdred_dir, output_dir):
    bpl_path = os.path.join(pmdred_dir, f'{base_name}.bpl')
    bpc_name = base_name
    if not os.path.exists(os.path.join(pmdred_dir, f'{bpc_name}c.bpc')):
        bpc_name = base_name[:-1] 
    bpc_path = os.path.join(pmdred_dir, f'{bpc_name}c.bpc')
    bma_path = os.path.join(pmdred_dir, f'{base_name}m.bma')
    bpa_path = os.path.join(pmdred_dir, f'{bpc_name}1.bpa')
    
    if not all(os.path.exists(p) for p in [bpl_path, bpc_path, bma_path]):
        raise Exception(f"Missing GBA asset files for {base_name}.")
        
    base_pals = parse_bpl(bpl_path)
    cw, chh, base_tiles, chunks = parse_bpc(bpc_path)
    Wt, Ht, Wc, Hc, nL, hC, layers = decode_bma(bma_path)
    
    tpf, n_frames, anim_frames = parse_bpa(bpa_path)
    if n_frames == 0:
        n_frames = 1
        anim_frames = [[]]
    else:
        print(f"[{base_name}] BPA Animations found: {n_frames} frames, {tpf} tiles per frame.")

    generated_images = []
    
    for frame_idx in range(n_frames):
        # Build the complete tile array for this frame
        current_tiles = list(base_tiles)
        current_tiles.extend(anim_frames[frame_idx])
        
        img = Image.new('RGBA', (Wt * 8, Ht * 8), (0, 0, 0, 255))
        
        for lay in reversed(layers):
            for cy in range(Hc):
                for cx in range(Wc):
                    cid = lay[cy * 64 + cx]
                    if cid <= 0 or cid >= len(chunks): continue
                    for i, ent in enumerate(chunks[cid]):
                        ti = ent & 0x3FF; hf = (ent >> 10) & 1; vf = (ent >> 11) & 1; pi = (ent >> 12) & 0xF
                        if ti == 0 or ti >= len(current_tiles): continue
                        tx, ty = cx * 3 + i % 3, cy * 3 + i // 3
                        if tx * 8 + 8 > Wt * 8 or ty * 8 + 8 > Ht * 8: continue
                        
                        td = current_tiles[ti]
                        pal = base_pals[pi % len(base_pals)]
                        
                        for y in range(8):
                            for x in range(4):
                                b = td[y * 4 + x]
                                for k2, ci in enumerate((b & 0xF, b >> 4)):
                                    if ci == 0: continue
                                    xx = x * 2 + k2; yy = y
                                    if hf: xx = 7 - xx
                                    if vf: yy = 7 - yy
                                    img.putpixel((tx * 8 + xx, ty * 8 + yy), pal[ci])
                                    
        out_png = os.path.join(output_dir, f"{base_name}_Frame_{frame_idx}.png")
        img.save(out_png)
        generated_images.append(out_png)
        
    return generated_images

if __name__ == "__main__":
    pmd_dir = '/tmp/pmd-red/data/map_bg'
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'Visual_Renders')
    os.makedirs(out_dir, exist_ok=True)
    
    test_map = 'T01P01' # Place Pokémon (with fountain/flags animation)
    try:
        print(f"Extraction Pixel-Perfect avec ANIMATIONS BPA pour {test_map}...")
        imgs = render_gba_map(test_map, pmd_dir, out_dir)
        for i in imgs:
            print(f"✅ Rendu généré : {i}")
            
        test_map_2 = 'T01P02A' # Whiscash Pond
        print(f"Extraction Pixel-Perfect avec ANIMATIONS BPA pour {test_map_2}...")
        imgs2 = render_gba_map(test_map_2, pmd_dir, out_dir)
        for i in imgs2:
            print(f"✅ Rendu généré : {i}")
            
    except Exception as e:
        print(f"Error: {e}")
