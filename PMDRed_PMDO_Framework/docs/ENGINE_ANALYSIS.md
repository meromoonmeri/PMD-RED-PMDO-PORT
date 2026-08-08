# PMD Red Engine Analysis

## Architecture du Moteur Original (GBA)

Pokémon Donjon Mystère : Équipe de Secours Rouge utilise un moteur de jeu structuré en plusieurs sous-systèmes écrits en C et Assembleur.

### 1. Gestion des Cartes (Grounds)
Les "Grounds" (villes, intérieurs, arènes de boss) ne sont pas des donjons procéduraux.
Le jeu les gère via trois fichiers principaux :
- **BPL (Background Palette)** : Palettes 15-bits indexées.
- **BPC (Background Character/Chunks)** : Les tuiles brutes et leurs assemblages en blocs (chunks).
- **BMA (Background Map)** : La matrice de la carte. Elle contient l'agencement des chunks et, crucialement, une couche cachée de 1-bit représentant les **Collisions** (marchable/bloquant).

### 2. Gestion des Entités (Station Scripts)
Contrairement aux moteurs modernes orientés objets, PMD Red gère ses entités (Héros, PNJ) via des structures mémoire statiques (`_station.h`).
- `GroundLivesData` : Définit la position X/Y exacte, le sprite à utiliser et l'ID de script du personnage au chargement de la map.
- `GroundEffectData` : Définit les points invisibles sur la carte utilisés comme ancrages pour la caméra ou les effets visuels pendant les cinématiques.

### 3. Cinématiques et Scripts
Le système d'événements repose sur des listes de commandes (macros C) lues séquentiellement :
- `SELECT_ANIMATION(id)` : Joue une animation précalculée (ex: choc, attaque, saut).
- `CAMERA_PAN(x, y, speed)` : Manipule le registre de scrolling GBA pour déplacer la vue.
- `FLASH_TO(TRUE, PAL_KIND, frames, RGB)` : Modifie temporairement la palette de l'écran (très utilisé pour simuler des explosions ou des lasers, comme l'Ultralaser de Rayquaza, sans utiliser de vraies particules).
- `BGM_SWITCH / BGM_FADEOUT` : Contrôle granulaire du processeur audio (AgbGbs).

### 4. Différences majeures avec RogueEssence (PMDO)
- **Transitions de map (Warps)** : PMD Red hardcode les sorties de map dans les scripts C (`ground_script.c`). RogueEssence utilise des objets physiques interactifs (`GroundObject` avec une hitbox).
- **Tuiles animées (BPA)** : PMD Red utilise un fichier séparé (`.bpa`) pour animer l'eau ou le feu via un cycle de palettes. RogueEssence intègre l'animation directement dans chaque tuile du fichier `.tile`.

