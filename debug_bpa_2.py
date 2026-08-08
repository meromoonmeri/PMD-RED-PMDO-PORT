import struct
p = '/tmp/pmd-red/data/map_bg/T01P011.bpa'
with open(p, 'rb') as f: d = f.read()

shorts = struct.unpack_from('<16H', d, 0)
print("Header as unsigned shorts:")
print(shorts)
