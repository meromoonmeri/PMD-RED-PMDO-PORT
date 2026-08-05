# Prompt — Auto-réflexion & Audit exhaustif (méthode maîtresse, avec outils)

## Principe fondateur

**Rien n'est présumé acquis.** Ce prompt part du même constat que celui déjà posé sur la fin du chapitre 5 : un contenu peut sembler correct sur le papier (un plan de cinématique détaillé, un prompt de conception rigoureux) et pourtant être défaillant dans son implémentation réelle (carte 100 % walkable, PNJ qui se chevauchent, code recopié d'un autre patron sans adaptation). L'auto-réflexion n'est donc jamais une formalité de fin de tâche : c'est une boucle continue, appliquée avant, pendant et après chaque production.

Ce document est la **méthode maîtresse** du projet : il ne remplace aucun des documents déjà produits, il les orchestre en un seul protocole d'audit exhaustif, avec la documentation et les outils à mobiliser à chaque étape.

---

## Boucle d'auto-réflexion — à appliquer à chaque tâche, sans exception

1. **Avant de commencer** : qu'est-ce que je crois déjà savoir sur cette zone/scène/personnage, et cette croyance est-elle vérifiée ou simplement supposée ? Si elle est supposée, la vérifier avant d'écrire quoi que ce soit (cf. exigence de connaissance exhaustive du projet).
2. **Pendant la production** : à chaque décision (position, dialogue, collision, transition), suis-je en train d'appliquer un template déjà validé, ou suis-je en train d'improviser une nouvelle convention non documentée ?
3. **Après la production** : si je devais auditer ce que je viens de produire comme si je découvrais le travail de quelqu'un d'autre, quelles questions poserais-je en premier — et est-ce que je peux y répondre avec certitude, ou seulement avec l'impression que « ça devrait être bon » ?

Cette troisième étape est la plus souvent sautée, et c'est celle qui a laissé passer les défauts déjà détectés sur la fin du chapitre 5. Elle est donc explicitement obligatoire ci-dessous, domaine par domaine.

---

## Documentation et outils à mobiliser

### Moteur et systèmes
- RogueEssence (moteur) : https://github.com/RogueCollab/RogueEssence
- Documentation Lua : https://github.com/RogueCollab/RogueEssence/tree/master/RogueEssence/Lua
- RogueElements (génération procédurale) : https://github.com/audinowho/RogueElements
- PMDC (systèmes de combat) : https://github.com/PMDCollab/PMDC

### Contenu et assets
- PMDODump : https://github.com/audinowho/PMDODump
- PMDODump — Docs et DataAsset : https://github.com/audinowho/PMDODump/tree/master/DataAsset/Docs
- PMDO-Explorers-Maps : https://github.com/slothplaysnecro/PMDO-Explorers-Maps
- DumpAsset : https://github.com/audinowho/DumpAsset
- PMDCollab/RawAsset : https://github.com/PMDCollab/RawAsset
- PMDCollab (organisation) : https://github.com/PMDCollab

### Tutoriels et wiki
- PMDOTutorial, Lesson 1 — Starting Hub Map : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.1
- PMDOTutorial, Lesson 2 — Ground Maps In-Depth : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.2
- PMDOTutorial, Lesson 3 — Dungeon Maps : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.3
- PMDOTutorial, Lesson 5 — Multi-Floor Generation : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.5
- PMDOTutorial, Lesson 6 — Cutscenes : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.6
- PMDOTutorial, Lesson 7 — Boss Battle : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.7
- PMDOTutorial, toutes releases : https://github.com/audinowho/PMDOTutorial/releases
- Floor Generation Overview : https://wiki.pmdo.pmdcollab.org/Floor_Generation_Overview
- Text Guide : https://wiki.pmdo.pmdcollab.org/Text_Guide
- Scripting Cheat Sheet : https://wiki.pmdo.pmdcollab.org/Scripting_Cheat_Sheet
- Script Reference : https://wiki.pmdo.pmdcollab.org/Script_Reference

### Décompilations et remakes de référence
- pret/pmd-red (Red Rescue Team) et son port RogueEssence `rogue-rescue-team` : https://github.com/pret/pmd-red / https://github.com/jtjanecek/rogue-rescue-team
- pret/pmd-sky (Explorers of Sky) : https://github.com/pret/pmd-sky
- UsernameFodder/pmdsky-debug : https://github.com/UsernameFodder/pmdsky-debug
- ExplorersOfSkyOrigins : https://github.com/slothplaysnecro/ExplorersOfSkyOrigins
- Organisation SkyTemple (skytemple, skytemple-files)

### Mods et projets de référence
- ProjectEoN : https://github.com/Logical321/ProjectEoN
- Halcyon (mod d'origine du projet) : https://github.com/Palikadude/Halcyon
- ZMDO : https://github.com/RaoKurai/ZMDO
- minior-game-jam : https://github.com/CregALeg/minior-game-jam

### Outils internes déjà spécifiés pour ce projet
- Outil de prévisualisation avancée du Ground & logique spatiale (`outil_previsualisation_ground_logique_spatiale.md`) — à utiliser pour tout audit de collision/positionnement.
- Générateur de map/tileset cohérent (`outil_generateur_map_tileset.md`).
- Générateur d'entrance de donjon (`outil_generateur_entrance_donjon.md`).
- Outil de conversion d'assets décompilés (`outil_conversion_assets_pmdsky.md`, étendu au format GBA de Rescue Team quand nécessaire, cf. `plan_narratif_chapitre5_a_10_rayquaza.md`).

---

## Audit exhaustif — domaine par domaine

Pour chaque scène, map ou chapitre soumis à cet audit, dérouler l'intégralité des domaines suivants. Ne jamais valider un domaine sur la base d'une impression : chaque ligne doit pouvoir être justifiée par une vérification concrète.

### 1. Logique spatiale (murs, collisions, walkability)
Référence : `prompt_logique_spatiale_obligatoire.md`.
- Chaque élément visuellement solide (bâtiment, rocher, eau, rive, tronc d'arbre, falaise) a-t-il une collision fonctionnelle réellement associée, catégorisée selon la grille déjà posée ?
- Aucune zone n'est-elle walkable par défaut sans décision explicite ?
- Les positions de scène déjà scriptées restent-elles valides une fois les collisions vérifiées ?

### 2. Positionnement et mise en scène
Référence : `prompt_mise_en_scene_optimise.md` (sections 2.1 à 2.9), template de référence : **camp du Tunnel** pour les coordonnées et distances.
- Chaque personnage a-t-il une position de départ logique, sans superposition ni chevauchement de sprite ?
- L'orientation de chaque personnage correspond-elle à sa position réelle par rapport au foyer d'attention (pas une rotation uniforme) ?
- Les déplacements sont-ils justifiés narrativement, sans collision ni trajectoire impossible ?
- Le dosage des réactions est-il respecté (pas de sur-jeu systématique, pas de figement) ?

### 3. Narration et développement des personnages
Référence : structure en beats déjà validée du **campement du Mont Windsep**.
- La scène suit-elle un déroulé en actes/beats comparable en détail à ce standard ?
- Chaque personnage présent a-t-il une fonction narrative dans la scène, cohérente avec sa personnalité déjà établie ailleurs dans le projet ?
- La causalité narrative est-elle respectée (rien d'introduit n'est mis en retrait sans explication) ?
- Les callbacks (ex. Kino qui s'endort) sont-ils choisis consciemment, pas laissés au hasard ?

### 4. Transitions et OST
Référence : `prompt_mise_en_scene_optimise.md`, section 2.7 et gestion des OST.
- Chaque fondu correspond-il à un changement de configuration majeur, pas une simple ponctuation ?
- Chaque acte/segment a-t-il sa propre identité sonore, sans piste unique du début à la fin ?
- Le silence est-il utilisé comme un outil de mise en scène assumé quand c'est pertinent ?

### 5. Boss et mini-boss
Référence : `boss_miniboss_narration_voix.md`, `arenes_boss_arc_tournoi.md`.
- Le boss a-t-il une justification narrative complète (qui, pourquoi ici, que veut-il, enjeu, issue) ?
- La Voix n'intervient-elle que si elle est réellement indispensable ?
- L'arène est-elle construite manuellement, cohérente avec le biome et la personnalité du légendaire ?

### 6. Triptyque du donjon et géométrie unique
Référence : `prompt_triptyque_entrance_relais_arene.md`, `prompt_geometrie_rescue_team_chapitre6.md`.
- L'entrance (si elle existe), le ou les relais et l'arène forment-ils un ensemble cohérent, avec des indices progressifs vers le légendaire ?
- Le donjon possède-t-il une géométrie de salles qui lui est propre, non dupliquée d'un autre donjon du projet ?
- Le registre de suivi anti-duplication a-t-il été consulté et mis à jour ?

### 7. Structure de chapitre
Référence : `structure_narrative_donjons_par_chapitre.md`, `prompt_chapitres_5_a_12_arc_fugitif.md`.
- Le chapitre respecte-t-il 3 à 5 donjons répartis en sous-arcs cohérents ?
- Les journées job board sont-elles justifiées par le rythme, pas systématisées ?
- Le fil rouge narratif du chapitre (ou du fil transversal en cours, ex. perturbations) est-il explicitement filé sans rupture ?

### 8. Monde vivant
Référence : `systeme_raid_ville_vivante.md`.
- Les PNJ ont-ils des positions et des dialogues cohérents avec les événements récents de l'histoire ?
- Le job board est-il fonctionnel et cohérent avec la ville concernée ?

### 9. Audit VFX et assets
Référence : section « Contraintes techniques obligatoires » de `prompt_boss_tornadus_chapitre5.md`.
- L'inventaire des VFX et assets existants a-t-il été fait avant toute création nouvelle ?
- Chaque nouvel asset est-il justifié par l'absence d'équivalent recensé ?

### 10. Continuité globale du projet
Référence : `PROMPT_ULTIME_new_era.md`, registres de suivi déjà institués.
- Le contenu produit est-il cohérent avec tout ce qui a déjà été écrit (personnages, événements, foreshadowing) ?
- Le foreshadowing semé est-il tracé pour un paiement futur vérifiable ?
- Une erreur récurrente déjà identifiée ailleurs (ex. vestige de code d'un autre patron) a-t-elle été spécifiquement recherchée ici ?

---

## Format du rapport d'audit exhaustif

```
=== AUTO-RÉFLEXION PRÉALABLE ===
Ce que je présume déjà savoir :
Ce qui a été vérifié / ce qui reste supposé :

=== AUDIT PAR DOMAINE ===
1. Logique spatiale :        [conforme / à corriger — détail]
2. Positionnement/mise en scène : [conforme / à corriger — détail]
3. Narration/personnages :   [conforme / à corriger — détail]
4. Transitions/OST :         [conforme / à corriger — détail]
5. Boss/mini-boss :          [conforme / à corriger / sans objet]
6. Triptyque/géométrie :     [conforme / à corriger / sans objet]
7. Structure de chapitre :   [conforme / à corriger / sans objet]
8. Monde vivant :            [conforme / à corriger / sans objet]
9. VFX/assets :               [conforme / à corriger / sans objet]
10. Continuité globale :     [conforme / à corriger — détail]

=== CORRECTIONS RECOMMANDÉES ===
(par domaine, avec référence explicite au template ou document appliqué)

=== VALIDATION FINALE ===
Test de crédibilité : un joueur attentif trouverait-il quelque chose
d'étrange dans ce contenu ? [oui/non — détail si oui]
```

---

## Auto-questionnement final — le doute comme méthode

- Ai-je audité ce contenu comme si je le découvrais pour la première fois, ou l'ai-je survolé parce qu'il « semblait » déjà bien fait ?
- Pour chaque décision technique ou narrative, puis-je citer le document ou le template précis qui la justifie — ou est-ce une improvisation non tracée ?
- Si un audit indépendant était mené demain sur ce même contenu, obtiendrait-il le même résultat que le mien ?
- Ai-je cherché les erreurs récurrentes déjà connues du projet (vestiges de code, gabarits recopiés, walkability par défaut) avant de conclure que ce contenu en est exempt ?

> Tant qu'une seule de ces questions n'a pas de réponse vérifiée, l'audit n'est pas terminé.
