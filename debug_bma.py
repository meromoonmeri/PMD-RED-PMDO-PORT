import struct
import os

p = '/tmp/pmd-red/data/map_bg/T01P01m.bma'
if not os.path.exists(p):
    p = '/tmp/pmd-red/data/map_bg/T00P01m.bma'

with open(p, 'rb') as f:
    d = f.read()

Wt, Ht, tw, th, Wc, Hc = d[:6]
nL, hD, hC = struct.unpack_from('<HhH', d, 6)

print(f"Wt={Wt}, Ht={Ht}, tw={tw}, th={th}, Wc={Wc}, Hc={Hc}")
print(f"nL={nL}, hD={hD}, hC={hC}")
print(f"Wt*tw = {Wt*tw} (Wc={Wc}) => chunks ? No, Wt is tiles. 40 * 3 = 120 ? Wt is tiles, Wc is chunks.")
print(f"Usually chunk is 3x3 tiles. Wt={Wt}, Wc={Wc}. Wt/Wc = {Wt/Wc if Wc else 0}")
