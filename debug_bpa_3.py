import struct
p = '/tmp/pmd-red/data/map_bg/T01P01c.bpc'
with open(p, 'rb') as f: d = f.read()
cw, chh, nt = struct.unpack_from('<HHH', d, 0)
nc, = struct.unpack_from('<H', d, 14)
off = 16 + (nt-1)*32
chunks = [[0]*9]
for i in range(nc-1):
    chunks.append(list(struct.unpack_from('<9H', d, off)))
    off += 18

max_ti = 0
for cid, chunk in enumerate(chunks):
    if cid == 0: continue
    for ent in chunk:
        ti = ent & 0x3FF
        if ti > max_ti:
            max_ti = ti
print(f"Max tile index used in map: {max_ti} (nt={nt})")
