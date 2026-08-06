# Export Pixel-Perfect — Couverture Complète PMD Red (245/245)

**Dépôt** : `meromoonmeri/PMD-RED-PMDO-PORT` (branche `master`)
**Date** : 2026-08-06
**Statut** : **245 cartes / 245 exportées** — couverture totale de `pret/pmd-red`
`data/map_bg/` telle que référencée par `map_dependencies.json`.

---

## 1. Couverture par famille

| Famille | Type | Cartes | Exemples |
|---|---|---|---|
| **A** | Cinématiques / intro (Arc du Héros) | 16 | a01p01 (Personality Test), a04p03 (Summit Sunset) |
| **B** | Bases d'équipe (3 stades × 16 équipes) | 96 | b01p01a/b/c (Team A, Basic/Construct/Final), … b16p02c |
| **D** | Donjons (entrées, mi-parcours, arènes de boss) | 45 | d01p01–d25p01 (dont les 33 canoniques déjà nommés) |
| **H** | Friend Areas | 65 | h01p01 (Recif Genereux) … h29p04 (Ile Finale) |
| **S** | Scènes spéciales | 6 | s01–s06 |
| **T** | Villes / hubs | 10 | t00p01 (Place Pokemon), t01p01–t01p07 (Square + bâtiments) |
| **W** | World map / écrans | 7 | w01–w06, w03p01–p03 |

**Total : 245 `.rsground` + 245 `.tile`** (dossiers `output/Grounds/`, `output/Tiles/`).

## 2. Détail des 33 cartes canoniques (déjà nommées en français)

Cf. `RECOVERY_33_MAPS_REPORT.md` — Arc Fugitif (D04P02), Chapitres 6-10
(D13P03 climax Rayquaza, T00P01 Place Pokemon), arènes de boss, etc.

## 3. Cartes restantes (212) — nommées par identifiant source

Toutes les cartes A/B/D/H/S/T/W non couvertes par les 33 ont été exportées
avec `AssetName` = identifiant bpl en minuscules (ex : `d01p02`, `h01p01`,
`b01p01a`, `t01p01`), `Sheet` = nom capitalisé (`D01p02_Base`, …).

Pipeline identique : rendu identity-mapped 1:1, collision BMA d'origine
(fallback « tuile noire » documenté), positions d'entités depuis le station
header quand il existe (sinon marqueur au centre de la zone marchable la plus
proche du centre géométrique).

## 4. Anomalies contrôlées (7 cartes « écrans vides »)

7 cartes sont des **écrans unis noirs** dans la ROM source (1 seule tuile
unique, 0 case marchable) : `h01p01w`, `h02p01w`, `h02p03w`, `h17p01w`,
`w03p01`, `w03p02`, `w03p03`, `w04`. Elles sont exportées **fidèlement**
(rendu 1:1 = rectangle noir, collision tout-bloquée) — ce n'est pas un bug du
pipeline : la source ne contient rien d'autre. Ce sont des identifiants
résiduels de la ROM (variantes « UNK » / world-map).

## 5. Stratégie de sauvegarde continue (appliquée sur les 245)

Pour chaque carte : `git add -A` → `git commit "feat: Export carte {id}"` →
`git push origin master` → `os.remove()` local → `git update-index
--skip-worktree`. Working tree local **propre**, aucun octet de copie de
travail conservé (les blobs vivent dans l'historique git distant).

## 6. Vérifications

- 245/245 entrées `map_dependencies.json` → présentes sur `origin/master`.
- 0 carte incomplète (bpl/bpc/bma tous présents pour chaque entrée).
- 0 anomalie « héros sur mur » hors écrans vides légitimes (cf. §4).
- Repo local : ~77 Mo (objets git uniquement), working tree 0 modif.
