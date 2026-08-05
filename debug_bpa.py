import struct, os
p = '/tmp/pmd-red/data/map_bg/T01P011.bpa'
if not os.path.exists(p):
    print("No BPA file")
else:
    with open(p, 'rb') as f: d = f.read()
    print(f"BPA File size: {len(d)}")
    # Try unpacking as tiles?
    print("Hex dump:")
    print(" ".join(f"{x:02X}" for x in d[:64]))
