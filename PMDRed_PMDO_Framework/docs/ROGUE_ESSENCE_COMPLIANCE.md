# Conformité et Intégration RogueEssence / PMDC

Ce document établit la passerelle d'architecture définitive entre le code source GBA (`pret/pmd-red`) et les standards natifs du moteur **RogueEssence / PMDC**, conformément à la documentation officielle.

## 1. Moteur de Base et Systèmes de Combat (`PMDC`)
*Référence : [PMDCollab/PMDC](https://github.com/PMDCollab/PMDC)*

Le moteur PMDC gère tout le gameplay. Il ne faut **pas** recréer ces systèmes, mais extraire les données de `pmd-red` pour les mouler dans le format JSON de PMDC :

| Donnée PMD Red (C/ASM) | Format PMDC Cible (JSON) | Action de Conversion |
| :--- | :--- | :--- |
| `monster_data` | `PMDC.Data.MonsterData` | Conversion des stats de base, types, et du taux de recrutement en `BaseHP`, `BaseAtk`, `JoinRate`. |
| `move_data` | `PMDC.Data.SkillData` | Extraction de la puissance (Power), Précision (HitRate) et PP. L'IA de ciblage est ignorée car PMDO utilise `AITactics`. |
| `item_data` | `PMDC.Data.ItemData` | Conversion en `ItemData` avec les tags PMDC (`UsageType`, `Price`, `MaxStack`). |

## 2. Génération Procédurale (`RogueElements`)
*Référence : [audinowho/RogueElements](https://github.com/audinowho/RogueElements)*

PMD Red génère ses donjons avec un algorithme codé en dur (`dungeon_generator.c`).
Dans le portage, cet algorithme est **totalement ignoré**. Nous extrayons uniquement les paramètres pour alimenter le moteur `RogueElements` :

*   **Structure d'un étage (Floor)** : Converti en `RogueElements.FloorPlan`.
*   **Rencontres sauvages** : Extraction des tableaux de spawn (`dungeon_pokemon.c`) convertis en `RogueEssence.Data.SpawnList<MobSpawn>`.
*   **Items au sol** : Converti en `RogueEssence.Data.SpawnList<ItemSpawn>`.

## 3. Cartes Ground et Scènes (`PMDOTutorial`)
*Références : Leçon 2 (Ground Maps), Leçon 6 (Cutscenes), Script Reference.*

Les cartes GBA (BPL/BMA) sont converties en `.rsground` et exploitées via Lua :
*   **Hitboxes et Murs** : La couche BMA est extraite cellule par cellule pour générer la grille `Object.obstacles` (`Tags: 1` = mur).
*   **Entités (PNJ, Héros)** : Les `GroundLivesData` de la GBA sont convertis en `RogueEssence.Ground.GroundChar` et `GroundSpawner`.
*   **Triggers / Événements** : Les événements d'origine sont désactivés. RogueEssence attend un fichier `init.lua` contenant `GAME:CutsceneMode()` et `GROUND:CharSetAction()`. Le convertisseur prépare les balises pour l'intégration de la nouvelle histoire.

## 4. Interfaces et Textes (Text Guide)
*Référence : [Scripting Cheat Sheet & Text Guide](https://wiki.pmdo.pmdcollab.org/Scripting_Cheat_Sheet)*

Les dialogues GBA utilisaient des macros C (`MSG_NORMAL`). 
*   **Conversion** : L'outil ignore les textes GBA pour laisser place au système de localisation natif de RogueEssence. Tous les textes seront insérés dans les fichiers `strings.resx` et `strings.fr.resx` avec appel via `UI:WaitShowDialogue()`.

## Résumé de l'Approche
L'outil d'extraction ne tente jamais de "forcer" un vieux système GBA dans PMDO. Il agit comme un prisme : il lit le code de 2005 et recrache des structures de données XML/JSON et Lua qui **obéissent strictement à l'architecture C# de RogueEssence.**
