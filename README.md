# Fort Énigma — L'Appel du Gardien

Jeu d'aventure et d'énigmes qui tient dans **un seul fichier HTML**, sans
serveur ni dépendance : `index.html` s'ouvre directement dans un navigateur.

Le joueur traverse dix univers (Fort de Pierre, Atelier à Vapeur, Quartier
Néon…), affronte vingt épreuves chronométrées et tente d'ouvrir le Coffre au
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

Le fichier pèse environ 2,5 Mo : les illustrations de chaque univers sont
encodées à l'intérieur (WebP/AVIF compressés), ce qui permet de jouer sans
connexion.

---

## Les épreuves

Vingt épreuves tirées au sort (`ALL_KINDS` dans `index.html`). Chaque univers
les habille à sa façon (titre, décor), mais la mécanique reste la même.

| Clé | Épreuve | Remarque |
|---|---|---|
| `riddle` | Énigme du Gardien des Clés | |
| `math` | Calcul Éclair | |
| `anagram` | Anagramme du Trésor | |
| `memory` | Mémoire des Symboles | |
| `labyrinth` | Le Labyrinthe des Égarés | |
| `seal` | Le Sceau des Anciens | |
| `morpion` | Morpion du Gardien | |
| `bingo` | Bingo des Chiffres | |
| `remparts` | La Course des Remparts | |
| `cartes` | Le Pari du Panda | |
| `weights` | Le Poids du Passé | |
| `crossbow` | Le Tir de l'Arbalète | |
| `reflex` | Les Auto-tamponneuses | boucle à pas fixe |
| `wire` | Le Fil d'Argent | boucle à pas fixe |
| `equilibre` | L'Équilibre du Passeur | boucle à pas fixe, sans duel |
| `echo` | L'Écho du Fort | sans duel |
| `lueurs` | Les Lueurs du Jour | uniquement au petit matin |
| `marche` | Le Marché de Midi | uniquement l'après-midi |
| `astres` | Les Astres de la Nuit | uniquement le soir et la nuit |
| `atelier` | Atelier du Gardien | seulement si une proposition a été forgée ; sans duel |

Certains univers écartent quelques épreuves (`UNIVERSE_KIND_EXCLUDE`).
`roulette` (Machine à Doublons) et `padlock` (Le Verrou des Soupirs) existent
dans le code mais ne font pas partie du tirage.

**Avant d'ajouter une épreuve**, vérifier qu'elle ne double pas une existante
par sa *mécanique* et non par son titre. Deux épreuves ont été retirées pour
cette raison : L'Écho des Cloches (un Simon, identique à Mémoire des
Symboles) et Le Pendule du Sacrifice (arrêter un indicateur mobile, comme
Le Tir de l'Arbalète).

---

## Le moteur (FortEngine)

Premier script du document, il sert toutes les autres parties du jeu :

1. **Boucle à pas de temps fixe** (60 pas simulés par seconde). La vitesse de
   jeu est la même de 24 à 240 Hz et ne ralentit plus quand l'appareil perd
   des images. `FortEngine.loop({ update, render })` ; les épreuves qui
   bougent en continu l'utilisent (voir la colonne « boucle à pas fixe »).
2. **Gouverneur d'animations.** Les animations CSS infinies invisibles
   (opacité nulle, parent masqué) sont mises en pause, sans aucun effet
   visuel. Selon le palier, le décor est allégé.
3. **Ordonnanceur de minuteurs.** Les minuteurs de fond (500 ms et plus) sont
   regroupés sur un seul, exécutés par tranches et ralentis en arrière-plan.
4. **Moniteur de fluidité** (mode Auto uniquement). Il mesure les images
   lentes et règle le palier, avec hystérésis pour éviter les va-et-vient.

| Palier | Nom |
|---|---|
| 0 | plein |
| 1 | équilibré |
| 2 | économe |
| 3 | minimal |

Le réglage de qualité du joueur est respecté : **Max** force le palier 0,
**Éco** le palier 2, **Auto** laisse le moniteur décider.

Paramètres d'adresse utiles au développement :

- `?perf=1` : affiche le compteur de fluidité et le palier courant ;
- `?fxtier=N` (0 à 3) : impose un palier.

En console : `FortEngine.stats()` (images, tâches longues, animations actives
et en pause), `FortEngine.setTier(n)`.

**Limite connue :** les mesures ont été faites dans Chromium sans GPU
(rendu logiciel). Le gain de fluidité visuelle sur un vrai téléphone reste à
constater avec `?perf=1`.

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
commenté avec le défaut qu'il corrige. Les plus récents concernent
l'affichage : `fort-transition-card-style` (carte de transition en verre
dépoli), `fort-cards-tablette-pc` (largeur fluide des cartes),
`fort-paysage-mobile` (téléphone en mode paysage), `fort-multi-plateforme`
(écrans très étroits, zones tactiles) et `fort-moteur-paliers` (allègement
du décor selon le palier du moteur).

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
créer. Netlify apporte en plus les fonctions serverless utilisées par le Gardien IA
(voir `netlify/functions/`) ; Vercel n'expose pas encore d'équivalent pour
cette fonction précise.

Aucune de ces plateformes ne « corrige le code » : ce rôle revient aux outils
du dossier `outils/` et au Gardien technique intégré au jeu.

### Automatiser réellement les deux côtés (GitHub → Netlify)

Le tableau ci-dessus dit « automatique à chaque push » pour Netlify — mais
cela suppose que Netlify et GitHub soient déjà reliés. Voici comment le
faire une bonne fois pour toutes :

1. **Relier le dépôt à Netlify** (à faire une seule fois) : sur
   [app.netlify.com](https://app.netlify.com), *Add new site → Import an
   existing project → Deploy with GitHub*, puis choisir ce dépôt. Netlify
   lit automatiquement `netlify.toml` : rien à configurer à la main.
   Une fois relié, **chaque `git push` sur `main` déclenche un déploiement
   Netlify sans aucune action de ta part** — c'est Netlify qui écoute
   GitHub, pas l'inverse.

2. **Ajouter la clé du Gardien IA** : Netlify → *Site settings →
   Environment variables → Add a variable* → nom `ANTHROPIC_API_KEY`,
   valeur ta clé Anthropic. Sans elle, le Gardien reste sur son répertoire
   de secours local (voir `netlify/functions/gardien-chat.mjs`) — le jeu
   fonctionne quand même, juste sans IA réelle.
   `.env.example` documente cette variable pour un test en local avec
   `netlify dev` ; ne jamais committer le fichier `.env` réel (déjà exclu
   par `.gitignore`).

3. **Empêcher qu'une régression parte en ligne** : sur GitHub, *Settings →
   Branches → Add branch protection rule* pour `main`, cocher *Require
   status checks to pass before merging* et sélectionner le check
   **Vérification du jeu**. Résultat concret : une pull request qui casse
   le jeu (audit `reparer.py`, fonction du Gardien, ou test `verifier.js`
   en échec) ne peut plus être fusionnée dans `main` — et comme Netlify
   déploie depuis `main`, une régression ne peut plus se retrouver en
   ligne par ce chemin. GitHub Pages, lui, applique déjà cette règle tout
   seul (voir `publication.yml`, qui ne se déclenche qu'après un succès de
   `verification.yml`) ; cette étape GitHub étend la même protection au
   déploiement Netlify.

4. **Le filet anti-fuite de clé** : `verification.yml` scanne désormais
   le dépôt à chaque push et bloque le pipeline si un texte ressemblant à
   une clé API Anthropic (`sk-ant-...`) s'y trouve — utile si quelqu'un
   colle une vraie clé dans le code par erreur au lieu de la mettre en
   variable d'environnement.

### Vérifier que GitHub et Netlify sont synchronisés

`main` est la seule source de vérité : Netlify ne garde rien qui ne soit pas
dans ce dépôt (hors variables d'environnement, qui sont volontairement
absentes du code). Pour le contrôler :

1. Dans Netlify, *Deploys*, ouvrir le déploiement de production : il indique
   le commit dont il est issu.
2. Comparer avec `git rev-parse HEAD` (ou le dernier commit de `main` sur
   GitHub). Les deux doivent être identiques.

`main--fort-enigma.netlify.app` n'est pas un second site : c'est l'adresse
du déploiement de la branche `main` du même projet.

---

## Licence

Projet personnel. Les illustrations ont été générées pour ce jeu ; les
Doublons et le Coffre au Trésor sont des créations originales.
