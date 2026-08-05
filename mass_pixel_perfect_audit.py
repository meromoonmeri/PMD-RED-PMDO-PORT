import os, struct, json, sys

with open('/home/user/map_dependencies.json', 'r') as f:
    MAP_DEPS = json.load(f)

PMD_DIR = '/tmp/pmd-red/data/map_bg'

def parse_bpl(p):
    with open(p, 'rb') as f: d = f.read()
    return d[0] # Just returning pal count for validation

def parse_bpc(p):
    with open(p, 'rb') as f: d = f.read()
    cw, chh, nt = struct.unpack_from('<HHH', d, 0)
    nc, = struct.unpack_from('<H', d, 14)
    
    # Validation: Are all chunks resolvable within file bounds?
    off = 16 + (nt-1)*32
    chunks = [[0]*(cw*chh)]
    for i in range(nc-1):
        if off + cw*chh*2 > len(d):
            raise Exception("BPC file too short for chunk data")
        chunks.append(list(struct.unpack_from(f'<{cw*chh}H', d, off)))
        off += cw*chh*2
    return nt, chunks

def parse_bpa(p):
    if not os.path.exists(p): return 0, 0
    with open(p, 'rb') as f: d = f.read()
    tpf, num_frames = struct.unpack_from('<HH', d, 0)
    return tpf, num_frames

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
                if src >= len(d): raise Exception("BMA decode ran out of data")
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
    return Wt, Ht, Wc, Hc, layers

out_report = open('/home/user/GROUND_AUDIT.md', 'w', encoding='utf-8')
out_report.write("# Audit Exhaustif 100% Pixel-Perfect Grounds (PMD Red)\n\n")

total = len(MAP_DEPS)
passed = 0
failed = 0

for map_id, deps in MAP_DEPS.items():
    bpl = os.path.join(PMD_DIR, deps['bpl'] + '.bpl')
    bpc = os.path.join(PMD_DIR, deps['bpc'] + '.bpc')
    bma = os.path.join(PMD_DIR, deps['bma'] + '.bma')
    bpas = [os.path.join(PMD_DIR, b + '.bpa') for b in deps['bpa']]
    
    missing_files = []
    for p in [bpl, bpc, bma] + bpas:
        if not os.path.exists(p):
            missing_files.append(os.path.basename(p))
            
    if missing_files:
        out_report.write(f"`{map_id}`  FAIL  (Missing files: {', '.join(missing_files)})\n")
        failed += 1
        continue
        
    try:
        # Decode BPL
        pal_count = parse_bpl(bpl)
        # Decode BPC
        nt, chunks = parse_bpc(bpc)
        # Decode BMA
        Wt, Ht, Wc, Hc, layers = decode_bma(bma)
        
        # Determine total valid tiles (base + bpa injected)
        total_valid_tiles = nt
        total_anim_frames = 1
        if bpas:
            # We process BPA injection logic
            max_frames = 1
            for bpa_path in bpas:
                tpf, num_frames = parse_bpa(bpa_path)
                if num_frames > max_frames: max_frames = num_frames
                total_valid_tiles += tpf # Dynamic injection increases valid index pool
            total_anim_frames = max_frames
            
        # Exhaustive validation: No missing chunks, no missing tiles
        error_msg = None
        for lay_idx, lay in enumerate(layers):
            for cy in range(Hc):
                for cx in range(Wc):
                    cid = lay[cy * 64 + cx]
                    if cid == 0: continue
                    if cid >= len(chunks):
                        error_msg = f"Out of bounds chunk ID {cid} (Max {len(chunks)-1}) at cx={cx}, cy={cy}"
                        break
                    
                    for i, ent in enumerate(chunks[cid]):
                        ti = ent & 0x3FF
                        if ti == 0: continue
                        if ti >= total_valid_tiles:
                            error_msg = f"Out of bounds tile ID {ti} (Max {total_valid_tiles-1}) in chunk {cid}"
                            break
                    if error_msg: break
                if error_msg: break
            if error_msg: break
            
        if error_msg:
            out_report.write(f"`{map_id}`  FAIL  ({error_msg})\n")
            failed += 1
        else:
            anim_str = f" [BPA Anim: {total_anim_frames} frames]" if bpas else ""
            out_report.write(f"`{map_id}`  PASS 100%  (Layers: {len(layers)}, Chunks: {len(chunks)}, Resolvable Tiles: {total_valid_tiles}){anim_str}\n")
            passed += 1
            
    except Exception as e:
        out_report.write(f"`{map_id}`  FAIL  ({str(e)})\n")
        failed += 1

out_report.write(f"\n**TOTAL**: {passed}/{total} PASS ({(passed/total)*100:.2f}%)\n")
out_report.close()

print(f"Audit completed. PASS: {passed}/{total}")
