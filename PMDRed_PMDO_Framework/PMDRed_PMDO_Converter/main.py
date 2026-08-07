import json, os, sys

def run_pipeline():
    print("=====================================================")
    print(" FRAMEWORK REMAKE PMD RED -> PMDO (ROGUEESSENCE)")
    print("=====================================================")
    
    # 1. Base Intermédiaire (Systems)
    db_path = os.path.join(os.path.dirname(__file__), 'compatibility_database', 'systems.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        systems = json.load(f)
        
    print("\n--- ANALYSE DE LA POLITIQUE DE CONVERSION ---")
    for sys_name, data in systems.items():
        print(f"[{sys_name.upper()}] Action: {data['action']}")
        print(f"    -> Règle : {data['conversion_rule']}")
        
    print("\n--- EXÉCUTION DU COMPILATEUR CINÉMATIQUE (Démo CIF) ---")
    os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'converters', 'cinematics', 'cinematic_compiler.py')}")
    
    print("\n--- VALIDATION FINALE OBLIGATOIRE ---")
    os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'validator', 'conversion_validator.py')}")

if __name__ == "__main__":
    run_pipeline()
