# Doctrine officielle — PMDRed → PMDO

Toute génération `.tile`, `.rsground` ou `.rsmap` doit dépendre exclusivement de données et de code issus de `pret/pmd-red`.

Les PNG RTRB, Spriters Resource, captures et sorties d’émulateur sont des oracles de validation uniquement. Ils sont interdits dans le graphe de génération.

Une carte n’est conforme que si elle fournit : manifeste de provenance, hashes des entrées, rendu généré, référence émulateur séparée, comparaison pixel par pixel, rapport de frames/palettes/couches et sérialisation PMDO valide.

Cible finale : 245/245 cartes, zéro exception.
