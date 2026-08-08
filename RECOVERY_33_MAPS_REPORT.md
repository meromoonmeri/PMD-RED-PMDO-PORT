# Récupération d'urgence — 33 Maps Canoniques PMD Red

**Dépôt** : `meromoonmeri/PMD-RED-PMDO-PORT` (branche `master`)
**Date** : 2026-08-06
**Objectif** : reconstruire les 33 cartes Pixel-Perfect purgées du disque local et
les téléverser de façon indélébile, avec sauvegarde continue par carte.

---

## 1. Stratégie de sauvegarde en continu (appliquée)

Pour CHAQUE carte, le script `tools/recover_33_maps.py` :

1. génère `output/Tiles/{Sheet}.tile` + `output/Grounds/{asset}.rsground` ;
2. `git add -A` ;
3. `git commit -m "feat: Export carte {src}"` ;
4. `git push origin master` ;
5. `os.remove()` des deux fichiers locaux — le disque sandbox est libéré ;
6. `git update-index --skip-worktree <fichiers>` — git ne voit plus leur
   absence : ils restent commités dans la branche et dans l'historique.

Résultat : **33 blobs .rsground + 33 blobs .tile sur GitHub**, `0 octet` de
copie de travail locale (working tree propre, repo local ~23 Mo = objets git).

## 2. Manifeste des 33 cartes (Arc Fugitif, Chapitres 6-10, Villes)

| Source pmd-red | Asset | FR | Dim. | Tuiles (uniques) | Flood | Commit |
|---|---|---|---|---|---|---|
| D01P01 | foret_tendre_oree | Orée de la Forêt Tendre | 54×45 | 2430 (253) | 2430/2430 | 104808b |
| D02P01 | grotte_statique_seuil | Seuil de la Grotte Statique | 48×39 | 1872 (767) | 978/978 | e7b3fe4 |
| D03P01 | pic_ferreux_pied | Pied du Pic Ferreux | 45×39 | 1755 (1167) | 344/344 | 83aa107 |
| D04P01 | bois_sombres_oree | Orée des Bois Sombres | 57×48 | 2736 (265) | 292/292 | e24e81d |
| D04P02 | bois_sombres_fond | Fond des Bois Sombres | 69×72 | 4968 (10) | 758/758 | b562e99 |
| D05P01 | gouffre_muet_bord | Bord du Gouffre Muet | 84×30 | 2520 (367) | 215/215 | 7e5a5a4 |
| D06P01 | mont_grondant_pied | Pied du Mont Grondant | 51×36 | 1836 (1096) | 733/733 | 7559014 |
| D07P01 | grand_canyon_porte | Porte du Grand Canyon | 57×30 | 1710 (1157) | 659/659 | 51a542b |
| D08P01 | grotte_lazuli_seuil | Seuil de la Grotte Lazuli | 45×36 | 1620 (1240) | 412/412 | 57014a3 |
| D08P02 | grotte_lazuli_fond | Fond de la Grotte Lazuli | 45×36 | 1620 (1236) | 412/412 | f561bd6 |
| D09P01 | mont_cendre_pied | Pied du Mont Cendré | 45×39 | 1755 (1301) | 438/438 | 94706c9 |
| D10P01 | foret_givree_oree | Orée de la Forêt Givrée | 33×42 | 1386 (864) | 140/140 | aa9ae8a |
| D11P01 | mont_gele_pied | Pied du Mont Gelé | 33×36 | 1188 (908) | 340/340 | dd090ec |
| D12P01 | gorge_ardente_porte | Porte de la Gorge Ardente | 51×42 | 2142 (1015) | 1083/1083 | 583b38b |
| D12P02 | gorge_ardente_coeur | Cœur de la Gorge Ardente | 57×57 | 3249 (19) | 657/657 | 54ab5ff |
| D12P04 | fosse_ardente | Fosse Ardente | 63×63 | 3969 (2) | 650/650 | a0c9ac3 |
| D13P01 | parvis_celeste | Parvis Céleste | 51×36 | 1836 (1079) | 551/551 | b294711 |
| D13P02 | palier_celeste | Palier Céleste | 57×57 | 3249 (19) | 657/657 | b70e8ea |
| D13P03 | tour_ciel_sommet | Sommet de la Tour du Ciel | 69×75 | 5175 (2) | 750/750 | 29b2a84 |
| D14P01 | abime_tempetes | Abîme des Tempêtes | 66×63 | 4158 (2) | 868/868 | 5dcbafe |
| D15P01 | fosse_argentee | Fosse Argentée | 69×75 | 5175 (2) | 4347/4347 | 3e36524 |
| D16P01 | champ_braises | Champ des Braises | 45×45 | 2025 (19) | 558/594 ⚠ | ed867f3 |
| D17P01 | champ_foudre | Champ de la Foudre | 48×45 | 2160 (19) | 657/657 | afe86c3 |
| D18P01 | champ_vent_boreal | Champ du Vent Boréal | 45×42 | 1890 (19) | 378/378 | 6aec794 |
| D19P01 | sommet_aurore | Sommet de l'Aurore | 66×63 | 4158 (2) | 856/856 | 125628c |
| D20P01 | antre_occident | Antre de l'Occident | 45×42 | 1890 (10) | 1080/1080 | dbbff3d |
| D21P01 | cretes_boreales | Crêtes Boréales | 63×60 | 3780 (6) | 3078/3078 | 2deea9a |
| D22P01 | vallon_perdu | Vallon Perdu | 51×45 | 2295 (1112) | 2295/2295 | 787587c |
| D23P01 | sanctuaire_voeu | Sanctuaire du Vœu | 45×42 | 1890 (10) | 702/702 | 0385cda |
| D24P01 | caverne_trouble_fond | Fond de la Caverne Trouble | 51×48 | 2448 (1287) | 1378/1378 | ae7c3e5 |
| D24P02 | caverne_trouble_autel | Autel de la Caverne Trouble | 51×36 | 1836 (1211) | 778/778 | 0ab2331 |
| D25P01 | bois_des_plaintes | Bois des Plaintes | 45×42 | 1890 (19) | 618/618 | b5c0f40 |
| T00P01 | place_pokemon | Place Pokémon | 144×111 | 15984 (496) | 9096/9096 | 4c3dca6 |

⚠ D16P01 : 36 cases non connexes dans la carte d'origine (îlots de lave isolés),
conservées 1:1, aucune entité dessus — comportement fidèle à la source.

## 3. Contrôles de qualité (par carte, intégrés au pipeline)

- **Rendu identity-mapped 1:1** : tuile GBA (x,y) → `TexLoc{X:x,Y:y}`, aucune
  transformation spatiale (règle documentée Partie 6 du projet New Era).
- **Collision** : couche BMA d'origine (skytemple-files), `Tags` par cellule ;
  fallback « tuile entièrement noire = bloquée » si `hasCollision=0`
  (documenté dans le `Comment` de chaque .rsground).
- **Positions d'entités** : lues dans `src/data/ground/ground_data_*_station.h`
  de pret/pmd-red (kind 0 → `Main_Entrance_Marker` ; 4/34/10/11 →
  `TEAMMATE_n` ; ≥80 → `Boss_Marker` ; effets → `Cutscene_Marker`).
- **Flood-fill** : chaque carte valide que le héros atteint toutes les cases
  marchables (0 anomalie « hero sur mur »).
- **Structure** : `AssetName` == nom du fichier, `Layers[0].Tiles` cohérent
  avec la grille `obstacles`, JSON parseable (format RogueEssence 0.8.9).

## 4. Outils livrés dans le dépôt

- `tools/pmdred_lib.py` — décodeurs BPL/BPC/BMA + rendu (transcrits des
  sources pret/pmd-red, validés sur la zone pilote D13P03).
- `tools/recover_33_maps.py` — pipeline complet : manifeste 33 cartes,
  conversion 1:1, sauvegarde continue (commit+push+purge+skip-worktree),
  re-exécutable (les cartes déjà exportées sont détectées « déjà à jour »).

## 5. État final

- `origin/master` : **33 .rsground + 33 .tile** (dossiers `output/Grounds/`,
  `output/Tiles/`) + outils + ce rapport.
- Working tree local : propre. Copie de travail purgée (0 octet restant).
- 33 commits `feat: Export carte {src}` + 2 commits outillage/nettoyage.
