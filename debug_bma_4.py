import struct
p = '/tmp/pmd-red/data/map_bg/T01P01m.bma'
with open(p, 'rb') as f: d = f.read()

Wt, Ht, tw, th, Wc, Hc = d[:6]
nL, hD, hC = struct.unpack_from('<HhH', d, 6)
src = 12
STRIDE = 64
# Skip layer 1 decode
def skip_decode(src):
    for j in range(Hc):
        k = 0
        while k < Wc:
            cmd = d[src]; src += 1
            if cmd >= 0xC0:
                src += 3 * (cmd - 0xC0 + 1)
                k += (cmd - 0xBF) * 2
            elif cmd >= 0x80:
                src += 3
                k += (cmd - 0x7F) * 2
            else:
                k += (cmd + 1) * 2
    return src

src = skip_decode(src)
print(f"Bytes left: {len(d) - src}")
if len(d) - src > 0:
    print("Hex dump of remaining:")
    print(" ".join(f"{x:02X}" for x in d[src:src+64]))
    
