import os, json, sys

def test_ground_maps(ground_dir):
    errors = 0
    maps = 0
    for f in os.listdir(ground_dir):
        if not f.endswith('.rsground'): continue
        maps += 1
        filepath = os.path.join(ground_dir, f)
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f_in:
                data = json.load(f_in)
                obj = data.get('Object', {})
                w = len(obj.get('Layers', [{}])[0].get('Tiles', []))
                obs = len(obj.get('obstacles', []))
                if w != obs:
                    print(f"❌ {f} : Dimension mismatch (Tiles {w} != Obstacles {obs})")
                    errors += 1
        except Exception as e:
            print(f"❌ {f} : Corrupted JSON - {e}")
            errors += 1
    
    print(f"Validated {maps} maps. {errors} errors found.")
    return errors == 0

if __name__ == '__main__':
    print("Running PMDO Conversion Tests...")
    d = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'Ground')
    if os.path.exists(d):
        success = test_ground_maps(d)
        sys.exit(0 if success else 1)
    else:
        print("Data/Ground directory not populated yet.")
        sys.exit(0)
