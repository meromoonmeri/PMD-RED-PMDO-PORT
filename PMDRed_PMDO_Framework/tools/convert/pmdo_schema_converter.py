import os, json

def generate_pmdo_monster_schema(gba_monster_id, name, hp, atk, defend, spatk, spdef, speed, types, abilities):
    """
    Simulates the conversion of a PMD Red C-struct into a RogueEssence PMDC MonsterData JSON.
    """
    pmdo_monster = {
        "$type": "PMDC.Data.MonsterData, PMDC",
        "Name": {
            "DefaultText": name,
            "LocalTexts": {}
        },
        "Released": True,
        "Comment": f"Converted from PMD Red ID: {gba_monster_id}",
        "Title": { "DefaultText": "Pokémon", "LocalTexts": {} },
        "IndexNum": gba_monster_id,
        "ExpYield": 50, # Example base
        "JoinRate": 10, # Example base
        "Forms": [
            {
                "$type": "RogueEssence.Data.BaseMonsterForm, RogueEssence",
                "FormName": { "DefaultText": "", "LocalTexts": {} },
                "Element1": types[0] if len(types) > 0 else "none",
                "Element2": types[1] if len(types) > 1 else "none",
                "Intrinsic1": abilities[0] if len(abilities) > 0 else "none",
                "Intrinsic2": abilities[1] if len(abilities) > 1 else "none",
                "Intrinsic3": "none",
                "LevelSkills": [],
                "BaseStatHP": hp,
                "BaseStatAttack": atk,
                "BaseStatDefense": defend,
                "BaseStatSpAtk": spatk,
                "BaseStatSpDef": spdef,
                "BaseStatSpeed": speed
            }
        ]
    }
    return pmdo_monster

def generate_pmdo_skill_schema(gba_skill_id, name, power, hit_rate, pp, element, category):
    """
    Simulates the conversion of a PMD Red move into a RogueEssence PMDC SkillData JSON.
    """
    pmdo_skill = {
        "$type": "PMDC.Data.SkillData, PMDC",
        "Name": {
            "DefaultText": name,
            "LocalTexts": {}
        },
        "Desc": {
            "DefaultText": "Converted skill.",
            "LocalTexts": {}
        },
        "Released": True,
        "Comment": f"Converted from PMD Red ID: {gba_skill_id}",
        "Element": element,
        "Category": category,
        "BaseCharges": pp,
        "BaseHitRate": hit_rate,
        "HitRateStat": "RogueEssence.Data.Stat.Accuracy",
        "Data": {
            "$type": "RogueEssence.Data.BattleData, RogueEssence",
            "ActionType": 0,
            "Element": element,
            "Category": category,
            "HitRate": hit_rate,
            "SkillStates": [],
            "BeforeEffects": [],
            "BeforeHitEffects": [],
            "OnHits": [
                {
                    "$type": "PMDC.Dungeon.DamageAnimEvent, PMDC",
                    "Damage": power
                }
            ],
            "OnEffects": []
        }
    }
    return pmdo_skill

def output_samples(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Convert Bulbasaur
    bulba = generate_pmdo_monster_schema(1, "Bulbasaur", 45, 49, 49, 65, 65, 45, ["grass", "poison"], ["overgrow"])
    with open(os.path.join(output_dir, "monster_001.json"), 'w', encoding='utf-8') as f:
        json.dump(bulba, f, indent=2, ensure_ascii=False)
        
    # 2. Convert Tackle
    tackle = generate_pmdo_skill_schema(33, "Tackle", 40, 100, 35, "normal", "Physical")
    with open(os.path.join(output_dir, "skill_033.json"), 'w', encoding='utf-8') as f:
        json.dump(tackle, f, indent=2, ensure_ascii=False)
        
    print(f"Sample data correctly mapped to PMDC / RogueEssence structures in {output_dir}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'PMDC_Converted')
    output_samples(out_dir)
