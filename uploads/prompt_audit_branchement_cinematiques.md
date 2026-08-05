# Prompt — Audit exhaustif du branchement des cinématiques (déclenchement, textes de transition)

## Constat de départ — deux défauts détectés en test en jeu

1. **Cinématique post-victoire absente** : après la défaite d'Absol, aucune cinématique ne se lance. Le trigger de fin de combat ne déclenche rien, ou pointe vers une cinématique qui n'existe pas/n'est pas branchée correctement.
2. **Texte de transition suspect** : une cinématique de transition en écran noir affiche *« Nous avions traversé la Stepped ! »* — ce texte contient un élément non identifié (« la Stepped ») qui n'est ni un nom de lieu français cohérent, ni une traduction reconnaissable. C'est très probablement un **vestige de patron recopié** (nom de variable, placeholder de template, ou reliquat d'un texte source non traduit/non adapté) — exactement le même type de défaut déjà détecté ailleurs dans le projet (commentaire contradictoire de `ch_5.lua`, vestige du patron Mont/Tunnel).

**Ce que ces deux défauts ont en commun** : ils ne sont pas de simples fautes isolées, ce sont des signes que le **branchement** des cinématiques (déclenchement correct au bon moment, texte correctement rempli et traduit) n'a pas été vérifié après implémentation — exactement le type d'erreur que `prompt_auto_reflexion_audit_exhaustif.md` et `prompt_correction_fin_chapitre5_templates.md` mettent déjà en garde de ne jamais présumer corrigé sans audit réel.

**Principe de travail** : ne pas se limiter à corriger ces deux cas précis. Auditer **l'ensemble des cinématiques du projet** pour la même classe de défaut, avant de considérer la question close.

---

## Documentation à consulter en priorité pour cet audit

- PMDOTutorial, Lesson 6 — Cutscenes (MapScene, Cutscene, Coroutine, triggers) : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.6
- PMDOTutorial, Lesson 7 — Boss Battle (déclenchement post-combat, scripts de victoire) : https://github.com/audinowho/PMDOTutorial/releases/tag/v0.7
- Script Reference : https://wiki.pmdo.pmdcollab.org/Script_Reference
- Scripting Cheat Sheet : https://wiki.pmdo.pmdcollab.org/Scripting_Cheat_Sheet
- Text Guide (gestion des strings, clés de traduction) : https://wiki.pmdo.pmdcollab.org/Text_Guide
- Documentation Lua RogueEssence : https://github.com/RogueCollab/RogueEssence/tree/master/RogueEssence/Lua

Étudier en priorité la façon dont un combat de boss déclenche sa cinématique de victoire (quel événement l'appelle, quelle condition doit être remplie) et la façon dont les clés de texte de transition sont censées être remplies (`strings.fr.resx` vs texte codé en dur, cf. règle déjà posée sur la séparation anglais/français).

---

## Objectif principal

Auditer, pour **chaque boss et chaque transition de cinématique déjà implémentés dans le projet**, deux points précis :

### A. Déclenchement post-victoire
- La cinématique prévue après la victoire se lance-t-elle réellement, ou le trigger est-il cassé/absent/mal référencé ?
- Le script de fin de combat appelle-t-il la bonne cinématique (pas une cinématique d'un autre boss recopiée par erreur, pas une référence à un nom de scène qui n'existe plus) ?
- Si aucune cinématique de victoire n'a jamais été écrite pour ce boss, est-ce un oubli (à corriger) ou une absence volontaire et déjà justifiée ailleurs dans le projet ?

### B. Texte des transitions en écran noir
- Chaque texte de transition affiché est-il un texte français idiomatique et complet, sans reliquat de nom de variable, de placeholder ou de terme non traduit ?
- Le texte correspond-il réellement à l'événement narratif qu'il décrit (pas un texte générique recopié d'une autre transition sans adaptation au contexte, cf. règle déjà posée sur les textes de narration qui doivent toujours être adaptés au contexte, jamais copiés automatiquement) ?
- Le texte provient-il bien de `strings.fr.resx` via le système de Strings/TextData, ou a-t-il été codé en dur quelque part (ce qui expliquerait plus facilement ce genre de fuite de placeholder) ?

---

## Recherche spécifique — l'anomalie « la Stepped »

Avant de la corriger isolément, déterminer son origine exacte :
1. Rechercher la chaîne « Stepped » (et ses variantes probables : `Stepped`, `stepped_zone`, nom de variable anglais non traduit) dans l'ensemble des fichiers de script et de strings du projet.
2. Si elle apparaît à plusieurs endroits, c'est la confirmation qu'il s'agit d'un **template recopié** plutôt qu'une erreur isolée — traiter alors chaque occurrence, pas seulement celle détectée après Absol.
3. Identifier le nom de lieu ou l'expression française qu'elle était censée remplacer (probablement un nom de donjon ou de segment non renseigné dans la clé de texte au moment de la duplication du script).
4. Une fois l'origine confirmée, corriger la clé de texte avec la formulation française idiomatique adaptée au contexte réel de cette transition (cf. règle déjà posée : jamais un texte copié automatiquement d'une autre scène).

---

## Audit systématique — tous les boss et toutes les transitions déjà implémentés

Ne pas se limiter à Absol. Passer en revue, avec la même méthode, chaque boss/mini-boss et chaque transition déjà scriptés dans le projet, notamment ceux déjà couverts par les documents de conception existants :
- Tornadus (chapitre 5, Mont Windsep)
- Regigigas (Ruines Tordues)
- Absol (déclencheur du bug initial — localisation exacte dans le projet à confirmer, chapitre à préciser)
- Tout autre boss/mini-boss déjà implémenté mais non encore documenté dans les prompts de conception de ce projet

Pour chacun, vérifier les points A et B ci-dessus, et consigner le résultat même si aucun défaut n'est trouvé — l'absence de vérification documentée équivaut à une absence de vérification, conformément au principe déjà posé dans `audit_rigueur_totale_coherence_exhaustive.md`.

---

## Format du rapport d'audit

```
=== AUDIT BRANCHEMENT CINÉMATIQUE ===

Boss / transition concerné :
Chapitre / donjon :

--- A. Déclenchement post-victoire ---
Cinématique prévue :
Se déclenche réellement en jeu : [oui/non]
Trigger vérifié (référence de code) :
Problème détecté :
Correction :

--- B. Texte de transition ---
Texte affiché actuellement :
Source du texte (strings.fr.resx / codé en dur / autre) :
Anomalie détectée (placeholder, terme non traduit, texte générique non adapté) :
Correction (texte français idiomatique proposé) :

--- Occurrences liées détectées ailleurs dans le projet ---
(lister toute autre scène partageant la même anomalie, ex. même
placeholder recopié, même absence de trigger de victoire)
```

---

## Validation finale

Avant de considérer cette mission terminée :
1. Chaque boss déjà implémenté dans le projet a-t-il été vérifié pour le point A (déclenchement) ?
2. Chaque transition en écran noir déjà implémentée a-t-elle été vérifiée pour le point B (texte) ?
3. L'anomalie « la Stepped » a-t-elle été recherchée exhaustivement, pas seulement corrigée à l'endroit où elle a été repérée ?
4. Les corrections apportées ont-elles été retestées en jeu (pas seulement relues dans le code) ?
5. Le suivi de continuité du projet a-t-il été mis à jour pour tracer cette classe de défaut comme erreur récurrente déjà rencontrée (vestige de patron non adapté), conformément au principe déjà posé : améliorer le processus de duplication de scène pour que ce type d'erreur ne se reproduise plus, plutôt que de la corriger scène par scène indéfiniment.

## Règle absolue

Ne jamais présumer qu'un boss ou une transition « fonctionne probablement » parce que son plan de cinématique est bien écrit sur le papier. Seul un test en jeu, ou une vérification de code équivalente, constitue une validation. C'est exactement ce qui a permis à ces deux défauts de passer inaperçus jusqu'au test en jeu sur Absol.

---

## Auto-questionnement avant de clore cette mission

- Ai-je vérifié le déclenchement réel de la cinématique de victoire pour chaque boss du projet, ou seulement pour Absol ?
- L'anomalie de texte a-t-elle été recherchée comme un motif potentiellement récurrent, avant d'être traitée comme un cas isolé ?
- Chaque correction a-t-elle été revalidée en jeu, pas seulement dans le script ?
- Cette classe de défaut (vestige de patron non adapté) a-t-elle été consignée pour éviter sa réapparition sur les prochains boss/donjons du projet (Rayquaza et la Tour Céleste notamment, dont l'implémentation reste à venir) ?

> Si l'une de ces questions révèle une incohérence ou une vérification manquante, la mission n'est pas terminée.
