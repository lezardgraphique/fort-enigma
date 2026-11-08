# Panneaux de la place et fêtes foraines

Ce dossier appartient au créateur du jeu : les joueurs ne peuvent rien y changer.

## Ajouter une affiche

1. Dépose l'image ici, au format 2:1 (idéal : 1200 × 600), en `.webp`, `.jpg` ou `.png`, avec un nom simple sans espaces (`soiree-enigmes.webp`).
2. Ajoute-la dans `annonces.json` :

```json
{ "image": "pubs/soiree-enigmes.webp", "texte": "Soirée énigmes, vendredi 21 h", "du": "2026-11-20", "au": "2026-11-28", "lien": "https://…" }
```

`texte` est lu par les lecteurs d'écran ; `du`, `au` (AAAA-MM-JJ) et `lien` (https) sont facultatifs. Les affiches tournent toutes les 7 secondes ; deux panneaux au plus sont plantés, là où les allées entre les étals le permettent.

## Le dernier post Instagram

`{ "source": "instagram", "compte": "thomas_lzg" }` affiche le dernier post du compte, fourni par la fonction Netlify `instagram` (mise à jour toutes les heures). Tant que la clé d'accès n'est pas réglée, le panneau montre une affiche qui renvoie au profil.

Réglage, une seule fois : compte Instagram professionnel (créateur ou entreprise), application Meta avec la permission `instagram_business_basic`, puis variable d'environnement `INSTAGRAM_TOKEN` dans Netlify (jeton longue durée). La fonction prolonge le jeton toute seule chaque semaine.

## Les fêtes

`foires` liste les périodes (MM-JJ, elles peuvent enjamber le Nouvel An). `"type": "noel"` remplace le chapiteau par un sapin et les fanions par une guirlande d'ampoules. Pour voir la fête hors saison : `?foraine=1`.
