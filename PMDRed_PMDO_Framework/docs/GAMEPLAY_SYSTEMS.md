# Gameplay Systems & Conversion Guide

## 1. Mécaniques d'Exploration PMDO vs PMD Red
Dans RogueEssence (PMDO), la génération de donjons est gérée par le composant `RogueElements`, beaucoup plus avancé que l'algorithme GBA.
Le système GBA utilisait des "Room generators" basiques. PMDO utilise des `FloorPlan` modifiables.

## 2. Le Recrutement
- **PMD Red** : Géré par le système des "Friend Areas" (Zones d'Accueil). Un Pokémon battu avec la bonne taille corporelle et le bon taux pouvait demander à rejoindre, à condition d'avoir acheté sa zone au Club Grodoudou.
- **RogueEssence** : Utilise le système moderne d'Assemblage (Chimecho Assembly). Le joueur interagit directement avec un menu en ville pour modifier son équipe. Le portage nécessitera soit d'adapter l'Assemblage pour utiliser les `.rsground` des Zones d'Accueil extraites, soit d'abandonner la mécanique de visite physique.

## 3. Météo et Effets de Terrain
- **GBA** : Géré via des surcouches graphiques matérielles (OAM Blending).
- **PMDO** : Géré par l'objet `MapStatus`. Les effets (Pluie, Grêle, Tempête de Sable) appliquent automatiquement des masques de particules et des modificateurs de statistiques globaux au niveau de l'étage (`Floor`).
