import struct
import os

p = '/tmp/pmd-red/data/map_bg/T01P01c.bpc'
if not os.path.exists(p):
    # try another
    p = '/tmp/pmd-red/data/map_bg/T00P01c.bpc'

with open(p, 'rb') as f:
    d = f.read()

cw, chh, nt = struct.unpack_from('<HHH', d, 0)
unk1, unk2, unk3, unk4 = struct.unpack_from('<HHHH', d, 6)
nc, = struct.unpack_from('<H', d, 14)

print(f"File size: {len(d)}")
print(f"Chunk W: {cw}, Chunk H: {chh}")
print(f"Num tiles (nt): {nt}")
print(f"Num chunks (nc): {nc}")
print(f"Header unknowns: {unk1}, {unk2}, {unk3}, {unk4}")

# Calculate expected chunk offset
tile_data_size = nt * 32
chunk_data_size = nc * (cw * chh * 2)
print(f"Expected tile data size: {tile_data_size}")
print(f"Expected chunk data size: {chunk_data_size}")
print(f"Expected total size (16 + {tile_data_size} + {chunk_data_size}): {16 + tile_data_size + chunk_data_size}")

