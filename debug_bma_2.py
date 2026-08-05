import struct
p = '/tmp/pmd-red/data/map_bg/T01P01m.bma'
with open(p, 'rb') as f:
    d = f.read()

Wt, Ht, tw, th, Wc, Hc = d[:6]
nL, hD, hC = struct.unpack_from('<HhH', d, 6)
src = 12
STRIDE = 64
layers = []
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

# Print some cids
for cy in range(5):
    row_cids = [layers[0][cy * 64 + cx] for cx in range(10)]
    print(f"Row {cy}: {row_cids}")

print(f"Total src parsed: {src} out of {len(d)}")
zero_chunks = sum(1 for cid in layers[0] if cid == 0)
print(f"Total zero chunks in layer 0: {zero_chunks}")
