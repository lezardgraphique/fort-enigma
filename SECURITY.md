# Sécurité — Fort Énigma

## Signaler une faille

Ouvrez un signalement privé via l'onglet **Security → Report a vulnerability** du dépôt GitHub (ne publiez pas le détail dans une issue publique). Réponse visée sous 7 jours.

## Mesures en place

**Navigateur (index.html)**
- Politique de sécurité du contenu (CSP) stricte : aucune ressource externe sauf les API météo listées ; `object-src`, `frame-src`, `form-action`, `base-uri` fermés ; `upgrade-insecure-requests`.
- Toutes les saisies (noms de joueurs et d'équipes, ville, messages au Gardien) sont neutralisées avant affichage ; les réponses des API tierces (météo, géolocalisation) et du Gardien sont échappées.
- Les données relues depuis le stockage local passent par `__deepSanitize` ; les sauvegardes corrompues sont réparées au démarrage.
- Aucun `eval`, aucun `new Function`, aucun code construit à partir de données (les boutons de propositions utilisent des attributs de données).
- La « Salle des machines » (outils de test qui permettent de tricher) n'est accessible qu'avec `?machines=1` dans l'adresse.

**Serveur (netlify/functions/gardien-chat.mjs, route `/api/gardien`)**
- Clé API uniquement côté serveur (variable `ANTHROPIC_API_KEY`), jamais dans le dépôt (vérifié à chaque envoi).
- Limitation de débit Netlify : 20 requêtes / minute / IP.
- Origines autorisées : sites du projet et développement local ; JSON obligatoire ; taille ≤ 24 Ko ; messages validés ; contexte réduit à une liste blanche de champs courts ; aucune erreur interne renvoyée au client.

**En-têtes HTTP (netlify.toml)** : HSTS, `nosniff`, `Referrer-Policy`, `Permissions-Policy` restrictive, `Cross-Origin-Opener-Policy` et `Cross-Origin-Resource-Policy` en same-origin, `frame-ancestors` limité à Netlify.

**Contrôles automatiques** : `outils/test-securite.mjs` (fonction du Gardien), recherche de clé API, CodeQL, `outils/verifier.js` et `outils/reparer.py` à chaque envoi.

## Limite connue

Le jeu tient en un seul fichier avec des scripts intégrés : la CSP doit autoriser `'unsafe-inline'` pour les scripts. Le risque est compensé par l'échappement systématique des données affichées.
