# Fort Énigma — L'Appel du Gardien

Jeu d'aventure et d'énigmes qui tient dans **un seul fichier HTML**, sans
serveur ni dépendance : `index.html` s'ouvre directement dans un navigateur.

Le joueur traverse dix univers (Fort de Pierre, Atelier à Vapeur, Quartier
Néon…), affronte des épreuves chronométrées et tente d'ouvrir le Coffre au
Trésor. Le Gardien propose en fin de partie de forger de nouvelles salles,
qui rejoignent aussitôt le jeu.

---

## Démarrer

Aucune installation. Ouvrez `index.html` dans un navigateur récent.

Pour servir le fichier localement :

```bash
python3 -m http.server 8000
# puis http://localhost:8000/index.html
```

---

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | le jeu entier — code, styles, illustrations et sons |
| `outils/verifier.js` | teste le jeu en conditions réelles (navigateur sans interface) |
| `outils/reparer.py` | audite et répare le fichier hors navigateur |
| `.github/workflows/verification.yml` | lance les deux à chaque envoi |

Le fichier pèse environ 9 Mo : les onze illustrations sont encodées à
l'intérieur, ce qui permet de jouer sans connexion.

---

## Les trois filets de sécurité

Ils ne se recouvrent pas : chacun voit ce que les autres ne peuvent pas voir.

### 1. `outils/reparer.py` — sur le fichier

```bash
python3 outils/reparer.py index.html            # audit seul
python3 outils/reparer.py index.html --reparer  # corrige, avec sauvegarde .bak
```

Neuf règles issues de pannes réellement rencontrées : commentaire CSS hors
`<style>` (qui s'affiche comme du texte), décor étiré par un
`background-size:100% 100%`, balises non appariées, minuteurs trop rapides,
poids du fichier…

**Limite :** liste fermée de défauts connus. Ce qu'il ne connaît pas, il ne
le voit pas.

### 2. `outils/verifier.js` — sur le jeu qui tourne

```bash
npm install puppeteer
node outils/verifier.js index.html
```

Onze contrôles sur quatre formats d'écran (Android, iPhone, petit écran,
ordinateur) : chevauchements entre la carte et les éléments flottants,
débordements, proportions des décors, réactivité, erreurs JavaScript, carnet
d'observation, création des salles acceptées, distinction réelle des
mécaniques de jeu.

Sortie lisible et code de retour `1` en cas de défaut — donc utilisable en
intégration continue.

### 3. Le Gardien technique — pendant la partie

Intégré au jeu, sans réseau. Il capture les erreurs, vérifie les sauvegardes,
détecte les écrans vides et les épreuves figées, puis répare seul selon une
escalade : redessin → libération des minuteurs → retour à l'accueil.

**Appui long sur le chronomètre** pour ouvrir son rapport (écran, appareil,
journal des incidents). Ce rapport est copiable : c'est lui qu'il faut joindre
à un signalement de bug.

---

## La Salle des Machines

Panneau de développement : **trois clics rapides sur l'horloge numérique**.
Il donne accès aux raccourcis (toutes les clés, saut au trésor, doublons,
choix de l'univers et de la météo).

Il est **masqué en production**. Le triple clic n'ouvre rien sur un domaine
public. Il reste accessible :

- en local (`file://`, `localhost`, réseau privé) ;
- sur un aperçu de branche (Netlify, Vercel) ;
- en ajoutant `?atelier=ouvert` à l'adresse — actif pour la session ;
- en console : `__fortAtelier.ouvrir()`.

Sans cela, n'importe quel joueur pourrait se donner toutes les clés.

---

## Intégrité des sauvegardes

Un jeu qui tourne dans le navigateur **ne peut pas être rendu intrichable** :
le code est téléchargé chez le joueur, donc lisible et modifiable. Obscurcir
le code ne ferait que gêner le débogage sans arrêter personne.

Le jeu ne protège donc pas — il **détecte**. Chaque sauvegarde porte une
empreinte ; une progression modifiée à la main devient visible :

- le jeu reste entièrement jouable ;
- un discret ⚠ apparaît près du chronomètre ;
- les classements portent la mention « scores non certifiés ».

En console : `__fortIntegrite.etat()` pour l'état, `__fortIntegrite.reinitialiser()`
pour repartir sur des bases saines.

La seule protection réelle serait un serveur validant les scores — c'est un
autre projet.

---

## Signaler un problème

1. Appui long sur le chronomètre → **Copier le rapport**.
2. Ouvrir une issue en collant ce rapport.
3. Préciser le moment exact (chargement, changement d'écran, en continu) et
   joindre une capture si l'anomalie est visuelle.

---

## Modifier le jeu

Tout est dans `index.html`. Les correctifs successifs sont regroupés en blocs
`<style>` identifiés en fin de fichier (`fort-frame-anchor`,
`fort-decors-univers`, `fort-themes-epreuves`, `fort-anti-flash`…), chacun
commenté avec le défaut qu'il corrige.

Après toute modification :

```bash
python3 outils/reparer.py index.html && node outils/verifier.js index.html
```

Les illustrations sont encodées en WebP dans des variables CSS
(`--decor-univers`) : remplacer une image revient à remplacer sa chaîne
base64 dans le bloc `fort-decors-univers`.

---

## Publier

### En une commande

```bash
./publier.sh                    # vérifie puis pousse
./publier.sh "mon message"      # avec un message de commit
./publier.sh --test-seul        # vérifie sans rien publier
```

**Rien n'est poussé si une vérification échoue** : c'est ce qui évite de
republier une régression. Le script refuse aussi de démarrer si le dépôt
distant n'est pas configuré, et prévient si le fichier devient trop lourd
pour GitHub.

### Où héberger

Le jeu est un fichier statique : tout hébergeur convient. Les configurations
sont déjà dans le dépôt.

| Plateforme | Fichier fourni | Mise à jour |
|---|---|---|
| **GitHub Pages** | `.github/workflows/publication.yml` | automatique après vérification réussie |
| **Netlify** | `netlify.toml` | automatique à chaque push |
| **Vercel** | `vercel.json` | automatique à chaque push |
| **Replit** | `.replit`, `replit.nix` | onglet Git → Pull, puis Deploy |

GitHub Pages est le choix le plus simple ici : la publication ne se déclenche
que si la vérification a réussi, et il n'y a aucun compte supplémentaire à
créer. Netlify et Vercel apportent surtout un réseau de diffusion plus rapide
— utile vu les 5,5 Mo du fichier.

Aucune de ces plateformes ne « corrige le code » : ce rôle revient aux outils
du dossier `outils/` et au Gardien technique intégré au jeu.

---

## Licence

Projet personnel. Les illustrations ont été générées pour ce jeu ; les
Doublons et le Coffre au Trésor sont des créations originales.
