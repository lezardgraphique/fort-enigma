# Fort Énigma — L'Appel du Gardien

[![Soutenir sur Ko-fi](https://img.shields.io/badge/Ko--fi-Soutenir-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/thomaslzg75)

Jeu d'aventure et d'énigmes qui tient dans **un seul fichier HTML**, sans
serveur ni dépendance : `index.html` s'ouvre directement dans un navigateur.

Le joueur traverse dix univers (Fort de Pierre, Atelier à Vapeur, Quartier
Néon…), affronte dix-neuf épreuves chronométrées et tente d'ouvrir le Coffre au
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

Dix-neuf épreuves tirées au sort (`ALL_KINDS` dans `index.html`). Chaque univers
les habille à sa façon (titre, décor), mais la mécanique reste la même, sauf
pour `astres` (voir plus bas). Chaque épreuve affiche, sous son texte
d'ambiance, une ligne **« 🎯 comment jouer »** : c'est la consigne `sub` du
générateur, conservée dans `howto` quand `applyThemedMeta` la remplace.

| Clé | Épreuve | Remarque |
|---|---|---|
| `riddle` | Énigme du Gardien des Clés | |
| `math` | Calcul Éclair | |
| `anagram` | Anagramme du Trésor | |
| `memory` | Mémoire des Symboles | |
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
| `astres` | Les Astres de la Nuit | uniquement le soir et la nuit ; une mécanique propre à chaque univers |
| `atelier` | Atelier du Gardien | seulement si une proposition a été forgée ; sans duel ; jeu de rythme unique |

Certains univers écartent quelques épreuves (`UNIVERSE_KIND_EXCLUDE`).
`roulette` (Machine à Doublons) et `padlock` (Le Verrou des Soupirs) existent
dans le code mais ne font pas partie du tirage.

**Les Astres de la Nuit** sont le seul jeu dont la mécanique change selon
l'univers, et chaque variante n'existe que dans un seul :

| Univers | Jeu de nuit |
|---|---|
| Crique des Pirates | repérer l'étoile différente |
| Manoir Hanté | retrouver les paires |
| Fête Foraine | suivre le bon gobelet |
| Veillée Nocturne | compter les étoiles filantes |

Les autres univers n'ont pas de jeu de nuit (`UNIVERSE_KIND_EXCLUDE`).

**Avant d'ajouter une épreuve**, vérifier qu'elle ne double pas une existante
par sa *mécanique* et non par son titre. Ont été retirés pour cette raison :
L'Écho des Cloches (un Simon, identique à Mémoire des Symboles), Le Pendule du
Sacrifice (comme Le Tir de l'Arbalète), Le Labyrinthe des Égarés (observer puis
reproduire, comme Mémoire des Symboles), quatre variantes d'Astres (Chœur =
mémoire, Rouages = Sceau, Braise = Équilibre, Veilleur = Fil d'Argent) et trois
mécaniques de l'Atelier (glisse = Arbalète, balance = Équilibre, frappes =
Remparts).

### Difficulté

Le niveau d'une épreuve (`escalate`) dépend de la progression de la partie, de
l'heure, du niveau du joueur et de son historique sur ce jeu. Il est étiqueté
NOVICE (moins de 3), GARDIEN (3 à 5) ou MAÎTRE (6 et plus). Règles à respecter
pour tout nouveau jeu : il doit rester **faisable à chaque niveau** (vérifier
avec un joueur simulé de temps de réaction réaliste, pas seulement avec des
bornes plausibles) et ne jamais punir plus vite que le temps de réaction humain.
Exemples déjà appliqués : l'aléa de niveau est plafonné à +1 et seulement après
deux épreuves ; le Bingo garantit une ligne gagnante ; le Fil d'Argent laisse un
délai de réaction (520 ms au niveau 0, 400 ms au plus bas) avant la décharge.

### Les cartes à collectionner

Dix cartes, une par univers, enregistrées dans `fort-cartes-collection`
(localStorage). On les gagne en ouvrant le Coffre au Trésor (environ une chance
sur trois) ou en achetant une Carte mystère au Marché du Fort (50 💰). La galerie
s'ouvre depuis le bouton « 🃏 Mes cartes » de l'accueil (`window.__fortCartes.ouvrir()`),
et chaque nouvelle carte déclenche une révélation. Collection complète : Pactole
du Gardien, +300 💰, versé une seule fois. La monnaie du Marché est exposée par
`window.bank()` / `window.setBank()` : ne pas les renommer, plusieurs scripts les
appellent depuis l'extérieur.

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

**Adresse du jeu : https://fort-enigma.netlify.app** — c'est la seule à
utiliser et à partager. Les adresses de type `main--fort-enigma.netlify.app`
(branche) ou `<id>--fort-enigma.netlify.app` (déploiement) affichées par
Netlify répondent « Site not found » pour ce projet ; elles sont redirigées
vers l'adresse principale (voir `netlify.toml`).

---

## Licence

Projet personnel. Les illustrations ont été générées pour ce jeu ; les
Doublons et le Coffre au Trésor sont des créations originales.

## Style des cartes et couche plateforme

- **Cartes** : fond bleu nuit, bordure fine or, badge de catégorie, titre doré, emblème à droite (style du prototype « Trois concepts d'épreuves »).
- **Couche plateforme** (`<script id="fort-plateforme">`) : navigation clavier / manette (flèches, croix, A/B, Échap, T/Start), vibrations, 13 succès sauvegardés (`fort-succes-v1`), transitions et profondeur des cartes, écran maintenu allumé, plein écran. Réglages dans la fenêtre 🏆. Désactivation : `?plat=0`.

## La Veillée (refonte)

Couche `<script id="fort-veillee">` par-dessus le jeu (désactivable avec `?veillee=0`) :
- **Lanternes** : les clés deviennent des lanternes qui s'allument ; la lumière suit la couleur de l'univers.
- **Ferveur** : chaque réussite alimente une flamme (×1 à ×4) qui rapporte des pièces ; un échec la fait retomber de moitié.
- **Défi de la veillée** : un objectif par partie, avec récompense en pièces.
- **Maîtrise** : chaque carte indique Inédit (+5 pièces), En progrès, Maîtrisé ou Redoutable.
- **Bilan du Gardien** en fin de partie, avec records (`fort-veillee-records`).

## Décor vivant et mode hors connexion

- **Décor vivant** (`<script id="fort-decor">`, désactivable avec `?decor=0`) : particules sur deux plans de profondeur (braises, embruns, neige, pluie, lucioles, sable, vapeur, confettis, étoiles filantes), parallaxe à la souris ou à l'inclinaison du téléphone, lumière animée par univers (torches, lune, aurore, néons, rayons), brume rampante et éclairs d'orage. La météo réelle et l'heure s'y ajoutent. Le cadre devient une vitre qui laisse voir le décor peint. Gouverné par FortEngine.
- **Hors connexion** : `sw.js` (service worker) + `manifest.webmanifest` + icônes `icone-*.png`. Le jeu se charge et se joue sans réseau ; il est installable comme une application. La météo et le chat du Gardien reprennent dès que la connexion revient.

## Le Gardien (v2) : guide, mécanicien et veilleur

`<script id="fort-gardien">` — onglet 🕯️ sur le bord gauche, bouton « Parler au Gardien », ou touche **G**.
- **Hors connexion** : répond à toutes les questions sur le jeu (règles, les 19 épreuves avec méthode et astuce, clés, doublons, coffre, univers, modes, horloge, difficulté, Ferveur, défi, succès, réglages, manette, hors ligne, statistiques) à partir de l'état réel de la partie. Ne donne jamais la solution d'une épreuve.
- **Agit** : débloquer l'écran, relancer l'épreuve, retour accueil, mode fluide / tous les effets, son, réparation des sauvegardes, réglages par défaut, mise à jour, diagnostic.
- **Veille** : journal des erreurs, auto-réparation des écrans plantés, neutralisation des voiles invisibles qui bloquent les clics, réparation des sauvegardes abîmées au démarrage.
- **En ligne** : la fonction `gardien-chat` reçoit le contexte de la partie et peut déclencher les mêmes actions (`[[action:…]]`) ; repli local instantané en cas de silence.

## Allègement

Le décor vivant remplace les systèmes de particules DOM du jeu (fées, braises), les calques de décor invisibles sont mis en pause, les animations coûteuses (filtres, ombres animées, flou, mélange de calques) sont retirées, et les épreuves tournent avec un décor allégé.

## Décor stable (anti-clignotement)

- Plus d'éclairs, d'étoiles filantes ni de lumières qui vacillent : la lumière d'ambiance de chaque univers est fixe et passe derrière le cadre.
- Les animations du jeu qui faisaient varier brusquement la lumière (torches, ampoules, lanternes, étoiles, éclairs) sont arrêtées sur leur état stable.
- Le cadre ne joue plus qu'une seule animation d'entrée (avant, une seconde le refaisait disparaître) ; plus de fondu global de l'écran ni de cartes qui réapparaissent à chaque rafraîchissement.
- Les particules ne passent plus devant l'interface, et les bulles d'aide du décor ne recouvrent plus les cartes.

## Fond simple et fluide

`<script id="fort-fond">` (désactivable avec `?fond=0`) : un seul tableau peint en plein écran — la scène de l'accueil, puis le décor de l'univers en cours — avec un fondu enchaîné doux quand l'univers change. Toutes les couches animées de l'ancien décor (ciel, vagues, nuages, fées, braises, oiseaux, guirlandes, château 3D, éléments saisonniers, particules) sont retirées ; la salle du trésor reste. Le cadre entre sans passer par la transparence, le « Fort qui tremble » ne flashe plus, et les messages du Gardien s'affichent en haut pendant une épreuve.

## Le Fil d'Argent (v3)

`<script id="fort-filargent">` : une clé (ou une bourse en défi bonus) pend à un fil d'argent. Maintenir (doigt, souris, Espace ou Entrée) chauffe le fil, relâcher le refroidit. Tant que la chaleur reste dans la zone dorée, le fil fond ; fondu, il lâche la clé dans le coffre. La zone rouge fait surchauffer le fil : une surchauffe est pardonnée, la seconde fait perdre la clé. Plus le niveau monte, plus la zone est étroite, la chauffe rapide et la fonte longue (courants d'air à partir du niveau 4).

## Mise en page « décor d'abord »

`<script id="fort-format">` — inspirée des jeux mobiles d'aventure (Monument Valley, The Room) et des règles de la « zone du pouce » :
- le décor peint occupe tout l'écran ; une seule barre fine en haut (clés, pièces, son) ;
- tout le jeu tient dans **un panneau** : en bas de l'écran sur téléphone (à portée de pouce), sur le côté droit sur ordinateur et tablette à l'horizontale ;
- les boutons secondaires (succès, Gardien, registre) sont regroupés en petites pastilles ; plus de lanternes, coins dorés ni guirlandes sur les cadres ;
- l'en-tête des épreuves est resserré : toutes les commandes des 19 épreuves sont visibles sans défiler sur un téléphone de 360×640 ;
- un téléphone tenu à l'horizontale propose de revenir à la verticale (avec « Continuer à l'horizontale »).

## Aperçu du lien

`apercu.jpg` (1200×630) + balises Open Graph / Twitter dans `index.html` : le lien partagé affiche la miniature du jeu.

## Décors haute définition et nettoyage de l'affichage

- **Décors nets sur téléphone** : les décors d'univers (900×491) n'étaient vus que par une bande centrale agrandie ~5× sur un écran vertical. Chaque décor a maintenant une version verticale recadrée, débruitée puis agrandie ×4 par super-résolution (EDSR, OpenCV), utilisée automatiquement sur écran vertical (`<script id="fort-decors-hd">`). Les trois portraits de l'accueil sont agrandis ×2 de la même façon. Fichier : ~4,8 Mo.
- **Plus de chevauchements** : un seul bouton ☰ en haut à droite regroupe Succès, Gardien et Registre ; message du Gardien sous la barre du haut, entièrement à l'écran ; rangée Marché / Contrat / Gardien de l'accueil calculée pour ne jamais toucher le panneau ; bandeaux de succès et de récompense empilés sans se recouvrir.
- **Plus de textes coupés** : accueil compacté (titre sur une ligne, horloge, météo et réglage graphique retirés de l'accueil, boutons secondaires en trois colonnes), en-tête du choix d'épreuve resserré, clé de défilement décorative retirée.

## Décors HD (originaux) et travelling

Les décors de 8 univers (Fort, Fête foraine, Atelier, Nordique, Pirates, Manoir, Jungle, Désert) et le port de l'accueil reprennent les **images originales** (1376–1408 × 768) au lieu des versions 900 px compressées : en paysage, l'original propre ; à la verticale, un recadrage agrandi ×2 par super-résolution (1074×1536). Néon et Veillée nocturne gardent la version agrandie précédente faute d'original. Un **travelling très lent** (zoom 6 % + léger glissement sur 48 s, sans variation de lumière) anime le fond ; il se coupe avec « réduire les animations » ou les effets de profondeur. Fichier : ~7,4 Mo, gardé sur l'appareil après le premier chargement.

## Sécurité

Voir [SECURITY.md](SECURITY.md). En bref : saisies et réponses externes échappées, CSP et en-têtes durcis, fonction du Gardien protégée (route `/api/gardien`, limite de 20 requêtes/minute/IP, origines autorisées, validation stricte, aucune fuite d'erreur), Salle des machines réservée à `?machines=1`, tests automatiques (`node outils/test-securite.mjs`).


## Fêtes et saisons

Aux dates clés, le Fort change de couleurs (cadre, titre, bouton « Jouer en solo », clés) et s'anime discrètement derrière le panneau, avec une petite bannière sur l'accueil :

| Fête | Période | Animation |
|---|---|---|
| Halloween | 20 oct. → 2 nov. | chauves-souris, citrouilles, fantômes qui traversent le ciel |
| Noël | 1er → 30 déc. | neige lente |
| Nouvel An | 31 déc. → 2 janv. | paillettes dorées |
| Saint-Valentin | 10 → 15 févr. | cœurs qui montent |
| Pâques | 3 jours avant → lundi de Pâques (date calculée) | fleurs et œufs |
| 1er Mai | 30 avr. → 1er mai | brins de muguet |
| Fête de la musique | 21 juin | notes qui montent |
| 14 Juillet | 13 → 14 juil. | bouquets bleu-blanc-rouge |

**Décorations de fête.** Des objets dessinés dans le style des décors sont posés sur le bord haut de la carte, à l'accueil comme dans les univers. À l'horizontale, ils se posent au sol, à gauche de l'écran.

| Fête | Décorations |
|---|---|
| Noël | sapin illuminé avec son étoile, cadeaux, liseré de neige sur la carte |
| Halloween | citrouilles sculptées et lumineuses, guirlande orange et violette |
| Nouvel An | ballons dorés, guirlande d'étoiles |
| Saint-Valentin | ballons-cœurs, guirlande de cœurs |
| Pâques | paniers d'œufs, fanions pastel |
| 1er Mai | pots de muguet |
| Fête de la musique | guitare, lampion, guirlande de notes |
| 14 Juillet | lampions bleu-blanc-rouge, fanions tricolores |

Ces décorations sont statiques : elles ne clignotent pas et ne coûtent rien pendant le jeu.

Animations en `transform` uniquement (aucun flash de lumière), coupées avec « réduire les animations » ou le mode calme. Tester une fête : `?fete=noel` (ou `halloween`, `nouvelan`, `valentin`, `paques`, `muguet`, `musique`, `quatorze`) ; désactiver : `?fete=0`.

L'accueil répartit aussi ses blocs sur toute la hauteur de la carte (plus de vide en bas, la pastille « Offre-moi un café » n'est plus coupée).

## Direction artistique : la Porte des Mondes

Tous les décors suivent la même ligne directrice et sont des illustrations originales, dessinées pour le jeu. Ils n'utilisent aucune image extérieure et ne sont soumis à aucun droit d'auteur tiers. Ils sont rendus en haute définition : 1290×2048 en vertical et 2048×1152 en horizontal.

- **L'accueil** montre le château sur sa colline, sa **grande porte magique** à runes, la ville qui descend vers le port, les navires et le **marché** du quai avec ses étals rayés, ses guirlandes de lanternes, ses passants et le Gardien à la lanterne. La scène existe de jour, au coucher du soleil et de nuit, selon l'heure.
- **Le début de partie** se passe dans le **hall des portes** : une galerie voûtée sous les constellations, dans la pierre chaude du Fort. Chaque porte est une arche de pierre (avec sa clé de voûte runique et son emblème) **qui laisse voir le monde où elle mène**, tel qu'on le retrouvera dans la partie. Le seuil de chaque porte brille de la couleur de son monde, comme la porte du jeu. Le Gardien avance vers la grande porte entrouverte sur les étoiles. La carte du récit reprend la carte sombre et dorée de l'accueil.
- **Les vignettes des portes d'univers** sont tirées des mêmes décors.
- **Dans le jeu**, chaque monde se voit **à travers la même porte du Fort** : une arche de pierre avec une clé de voûte en forme de clé et des runes gravées (`portail.js`). Les runes et le seuil prennent la couleur de l'univers. La porte est dessinée une seule fois à la taille de l'écran, puis gardée comme une simple image : elle ne coûte rien pendant le jeu et n'est pas redessinée quand la barre d'adresse du téléphone apparaît ou disparaît. Le décor qui glisse lentement derrière elle donne de la profondeur.
- **Les 10 mondes** partagent la même facture : aplats dégradés, lumière du soir ou de nuit, liserés de lumière, halos doux, brume, grain de pierre et vignette. Ce sont le Fort de Pierre, la Fête Foraine, l'Atelier à Vapeur, la Salle Nordique, la Crique des Pirates, le Manoir Hanté, la Jungle de Jade, le Temple des Sables, le Quartier Néon et la Veillée Nocturne.
- L'image d'aperçu du lien (`apercu.jpg`) et les textures des cases viennent du même atelier.

### Revue de direction artistique

Les décors ont été revus en deux passes avec une IA dédiée à la direction artistique. Elle a établi un diagnostic et une note par décor, une charte et des corrections précises. La charte appliquée est la suivante :

- une seule source de lumière principale par scène (`S.lumiere`), placée dans la zone visible ;
- trois plans de valeur : lointain clair, sujet le plus contrasté, premier plan sombre ;
- un sol commun `S.sol()` (motif en perspective, flaque de lumière, premier plan assombri) ;
- des ombres de contact et des ombres portées (`S.ombre`, `S.ombre_portee`) ;
- une brume organique ;
- un éclairage d'ambiance (`S.eclairage`) et une vignette commune, centrée sur la partie de l'image qui reste visible au-dessus des cartes et du panneau ;
- des particules plafonnées, une texture discrète et le sujet placé au-dessus des cartes sur téléphone.

Effet des corrections, d'après la revue :

- le Pirate passe de 4,5 à 6/10 ;
- la Foraine passe de 5 à 6,5/10 ;
- le Désert passe de 5,5 à 7/10 ;
- le Fort passe de 6,5 à 7,5/10 ;
- les autres décors gagnent de 0,5 à 1 point.

Les sources se trouvent dans `outils/decors/` :

- `atelier.py` : la boîte à outils commune ;
- `mondes.py` : les mondes et l'accueil ;
- `neon.py`, `nocturne.py` : ces deux mondes ;
- `lot.py` : génère et rend un lot, par exemple `python3 lot.py fort,pirate PL` ;
- `apercu.py` : crée l'image d'aperçu.

Les dessins sont déterministes, ce qui permet de les retoucher puis de les régénérer à l'identique.

## La Forge du Gardien : de vrais jeux inédits

Avant, les salles proposées par le Gardien collaient un nouveau nom sur une poignée de petites mécaniques, elles-mêmes proches d'épreuves existantes. On rejouait donc les mêmes jeux sous d'autres noms. Désormais, chaque salle acceptée reçoit des **jeux réellement nouveaux**, absents des 19 épreuves du Fort :

| Jeu | Principe |
|---|---|
| 🔆 Les Runes à éteindre | chaque rune bascule aussi ses voisines ; il faut toutes les éteindre |
| 🧩 La Mosaïque brisée | faire glisser les pièces pour reformer la suite 1 → 8 |
| 🔗 Les Conduits | tourner les conduits pour relier l'entrée à la sortie |
| 🌀 Le Dédale | labyrinthe généré, à parcourir au doigt ou aux flèches |
| 🏛️ Les Trois Piliers | tours de Hanoï, 3 ou 4 disques |
| 🔦 Le Rayon des Miroirs | faire pivoter les miroirs pour guider le rayon jusqu'au cristal |
| 🖼️ Le Tableau caché | picross : remplir la grille d'après les nombres |
| 🔯 Le Carré des Sceaux | sudoku 4×4 à symboles |

- Chaque partie est générée au hasard et toujours soluble. `outils/test-forge.mjs`, exécuté par la CI, en génère 1 200 par jeu pour le vérifier.
- La difficulté suit celle du Fort.
- Le Gardien attribue d'abord les jeux que le joueur ne possède pas encore, et jamais deux fois le même dans une salle.
- Les salles déjà acceptées sont converties automatiquement.
- **En ligne**, le Gardien écrit lui-même le récit de la salle et le nom de ses jeux (`/api/gardien`, mode `forge`). L'IA n'écrit que du texte, en JSON strict, nettoyé côté serveur puis dans le navigateur. Les jeux restent choisis dans une liste blanche de mécaniques déjà codées.
- Désactivation : `?forge=0`.

## Le Gardien met le Fort à jour

- À chaque publication, la construction écrit `version.json` avec la version et la liste des nouveautés.
- Au lancement, toutes les 20 minutes et au retour du réseau, le Gardien compare cette version avec la sienne.
- S'il en trouve une plus récente, il l'annonce avec les nouveautés et propose **« Mettre à jour le Fort »**. Il récupère alors la nouvelle version et recharge le jeu, sans toucher à la progression.
- Après une mise à jour, il présente une fois les nouveautés.
- Désactivation : `?maj=0`.

## Décors des salles du Gardien

Les salles que propose le Gardien ont maintenant leur propre décor, dans la même facture que les dix mondes. Avant, elles affichaient le château de l'accueil.

- **Décors dédiés** (14, dans `decors/`) : Bibliothèque Interdite, Atlantide Engloutie, Far West, Cirque Mystique, Station Orbitale, Temple Maya, Carnaval Vénitien, Cité, Crypte, Labyrinthe, Jardin, Ruche, Laboratoire, Palais.
- **Salles aux noms composés** (« Crypte Maudite des Cendres », « Ruche Radiante de Jade »…) : le premier mot choisit le décor.
  - Tombeau et Prison utilisent la Crypte.
  - Archives utilise la Bibliothèque, Canyon le Far West et Temple le Temple Maya.
  - Forge, Observatoire et Bastion reprennent l'Atelier à Vapeur, la Veillée Nocturne et le Fort de Pierre.
  - Cité Cyberpunk reprend le Quartier Néon.
- **Teinte** : la matière du nom (de Glace, de Jade, des Cendres, de Plasma…) teinte légèrement la salle.
- **Porte magique** : elle prend la couleur de la salle.
- **Chargement** : ces décors ne sont pas intégrés au fichier du jeu. Ils se chargent à l'entrée de la salle, puis restent disponibles hors connexion. S'ils manquent (aperçu sans les fichiers), le Fort reprend son décor d'accueil.
- **Sources** : `outils/decors/mondes2.py`.

## Le passage du seuil

Quand la partie mène d'un univers à un autre, on franchit vraiment une porte. Le passage dure environ 1,8 s, et on peut le passer en touchant l'écran :

- l'arche de pierre se rapproche, comme si l'on avançait ;
- une carte de passage indique d'où l'on vient (« Tu quittes la Crique des Pirates ») et le monde où l'on entre (icône, nom et ambiance) ;
- elle montre aussi le **chemin dans le Fort** : les portes déjà franchies, la salle actuelle (« Salle 3 sur 8 ») et celles qui restent ;
- pendant ce temps, le décor du nouveau monde s'installe derrière.

La première salle s'ouvre de la même façon à la fin de l'introduction. Les animations se limitent à des déplacements et des fondus, sans flash de lumière. Elles sont raccourcies si l'appareil demande de réduire les animations. Désactivation : `?seuil=0`.

## Les habitants du Fort et la salle du Coffre

- **Drapeau du donjon** : le bord droit du fanion est désormais fixé au mât et la pointe flotte au vent.
- **Port animé** (couche `fort-persos`, désactivable avec `?persos=0`) : sur les écrans de menu, les auvents des étals ondulent, des passants marchent sur le quai, le Panda tient son étal et le Gardien veille sur son perchoir. Leurs positions viennent des ancres enregistrées au rendu du décor (`peint/out/accueil_*.json`, injectées dans `window.__decorsAncres`).
- **Les personnages reviennent** : le Gardien, le Panda, le Parieur et le Voleur apparaissent, dessinés et animés (respiration, clignement, lanterne, pièce, clés), avec une bulle tirée de leur **chronique**. Chaque rencontre fait avancer leur histoire, et le compteur est mémorisé dans le navigateur (`fort-chronique`).
- **Salle du Coffre** : la chambre forte (arches, runes, coffre sur son estrade, dix serrures) sert de décor à la salle du trésor, à ses transitions et aux écrans bonus.
- Le Gardien (`gardien-chat.mjs`) connaît la même histoire et reste cohérent avec elle.

## Sauvegarde partagée entre PC et mobile

- Menu **☰ → Sauvegarde PC ↔ mobile** (ou touche **S** sur PC). Un premier appareil crée un **code de voyage** de 16 caractères. Les autres appareils le récupèrent en scannant le **QR code**, en ouvrant le lien (`#relier=…`) ou en saisissant le code.
- La synchronisation est ensuite automatique : au lancement, quelques secondes après chaque progrès, au retour sur l'onglet et au retour du réseau. Pendant une épreuve, rien n'est appliqué : les nouveautés attendent le prochain menu.
- **Chiffrement de bout en bout** : le navigateur chiffre la progression (AES-GCM, clé tirée du code par PBKDF2) avant l'envoi. La fonction `netlify/functions/sauvegarde.mjs` ne stocke qu'un paquet illisible dans Netlify Blobs, sous une empreinte opaque du code. Elle applique les mêmes garde-fous que le Gardien : même origine pour écrire, JSON uniquement, taille bornée, limite de débit et écriture conditionnelle (pas d'écrasement en cas de conflit). Les tests sont dans `outils/test-securite.mjs`.
- **Fusion clé par clé** : la modification la plus récente gagne, avec l'horloge recalée sur celle du serveur. Le Tableau des Légendes réunit les deux appareils. Si les deux appareils ont déjà joué au moment de les relier, le joueur choisit la progression à garder.
- Désactivation : `?synchro=0`. Le QR code est généré par *qrcode-generator* (Kazuhiko Arase, licence MIT), intégré au fichier.

## Confort sur PC

- **Raccourcis clavier** (avec une souris) :
  - **1–6** pour répondre (le numéro s'affiche sur chaque réponse) ;
  - **Entrée** pour l'action principale ;
  - **Échap** pour fermer une fenêtre ou revenir ;
  - **F** pour le plein écran ;
  - **G** pour parler au Gardien ;
  - **S** pour la sauvegarde ;
  - **?** pour l'aide, aussi accessible dans le menu ☰.
- Survols dorés et focus clavier visible.
- Grands écrans (à partir de 1500×860) : la carte grandit avec l'écran (zoom jusqu'à ×1,5). Les écrans de lecture (règles, histoire, légendes…) s'élargissent.
- Le décor suit légèrement la souris. Cet effet est désactivé si « réduire les animations » est actif ou avec `?relief=0`.
- Désactivation de tout ce confort PC : `?pc=0`.

## Ambiance des fêtes

La couche `fort-ambiance` complète « Fêtes et saisons » pendant chaque fête. Elle se désactive avec `?ambiance=0`, et `?fete=0` coupe toutes les fêtes. Pour tester une fête : `?fete=halloween`, `noel`, `nouvelan`, `valentin`, `paques`, `muguet`, `musique` ou `quatorze`.

- **Ciel et lumière** : chaque fête recolore le décor et y ajoute un effet.

  | Fête | Effet |
  |---|---|
  | Halloween | brume violette au sol |
  | Noël | neige qui tombe en deux couches, neige posée sur le port |
  | Nouvel An, 14 Juillet | feux d'artifice au-dessus du château |
  | Fête de la musique | faisceaux de concert |
  | Pâques, 1er Mai | rais de soleil |
  | Saint-Valentin | halos roses |
- **Coins de la carte** : toiles d'araignée et araignée qui descend à Halloween, givre à Noël.
- **Les habitants se déguisent** : le Gardien, le Panda et le Voleur portent un chapeau de saison.

  | Fête | Chapeau |
  |---|---|
  | Halloween | sorcière |
  | Noël | bonnet |
  | Nouvel An | cotillon |
  | Saint-Valentin | cœurs |
  | Pâques | couronne de fleurs |
  | 1er Mai | brins de muguet |
  | Fête de la musique | casque audio |
  | 14 Juillet | bicorne |

  Le Parieur garde son haut-de-forme, mais son ruban prend les couleurs de la fête. À sa première rencontre de la fête, chacun dit une réplique de saison.
- **Chasse de saison** : le Gardien cache 5 objets dans le décor, jamais pendant une épreuve. Les trouver tous donne un titre de saison, affiché dans la bannière de la fête.

  | Fête | Objets cachés |
  |---|---|
  | Halloween | citrouilles |
  | Noël | boules de Noël |
  | Nouvel An | étoiles d'or |
  | Saint-Valentin | cœurs |
  | Pâques | œufs |
  | 1er Mai | brins de muguet |
  | Fête de la musique | notes perdues |
  | 14 Juillet | cocardes |

  La progression suit la sauvegarde partagée entre appareils.
- **Contraintes d'animation** : tout s'anime en transform et opacité, lentement et sans flash. Rien ne bouge en mode calme ni si « réduire les animations » est actif.
- **Correctif** : le jeu déclare `GuardianSpirit` en `const`, que les couches ne voyaient pas via `window`. Un petit pont (`fort-pont`) l'expose désormais. Les annonces du Gardien des couches (mise à jour du Fort, sauvegarde, astuces PC, fêtes) s'affichent donc enfin.

## Un Gardien autonome, une épreuve une seule fois

- **Le Gardien décide seul.**
  - Quand il imagine une salle, il ne demande plus « Accepter / Refuser ». Il la bâtit lui-même avec **un seul jeu inédit** de la Forge, puis l'annonce.
  - Il ne donne jamais à une salle un jeu qu'une autre possède déjà. Une fois ses 8 inventions placées, il renonce seul aux nouvelles idées.
  - Il bâtit au plus une salle par jour, et note tout dans son journal.
  - Il installe aussi les **mises à jour du Fort** lui-même, toujours entre deux parties. Il ne fait qu'une tentative automatique par version et par session, donc jamais de boucle de rechargement.
- **Essai d'un nouveau jeu** : un seul jeu (celui de la salle), une seule tentative. Ensuite, le Gardien ramène automatiquement au Fort.
- **Une épreuve, une seule fois par partie** (couche `fort-unique`, désactivable avec `?unique=0`) :
  - aucune répétition, même dans un autre univers, en duel ou en défi bonus ;
  - le bouton « Rejouer » est retiré. Il pouvait aussi figer le jeu, car il transmettait un niveau de difficulté invalide ;
  - chaque salle du Gardien fait jouer son propre jeu, et l'atelier n'apparaît plus dans les autres univers.
- `outils/verifier.js` contrôle désormais :
  - l'essai unique avec retour automatique ;
  - l'absence de répétition sur plusieurs parties simulées ;
  - l'autonomie du Gardien.

## La vigie du Gardien : autonomie, alertes et veille du web

Le Gardien veille désormais sur le Fort **sans joueur ni développeur** :

| Pièce | Rôle |
|---|---|
| `netlify/functions/gardien-veille.mjs` (**toutes les heures**, tâche planifiée Netlify) | Vérifie le jeu, `version.json`, le mode hors connexion, la sauvegarde, la voix du Gardien et la présence de la clé de l'IA. Analyse aussi les incidents remontés par les joueurs (pannes répétées, avalanche d'erreurs). Il écrit l'état du Fort et **donne l'alerte** pour tout nouveau problème. |
| `netlify/functions/rapport.mjs` (`/api/rapport`) | Reçoit des joueurs des résumés **anonymes** des réparations faites par le Gardien, ainsi que les signalements « Un souci ? ». Les messages sont nettoyés (pas de lien, de balise ni de jeton), bornés et limités en débit. |
| `netlify/functions/etat.mjs` (`/api/etat`) | Donne l'état public du Fort, lu par le jeu. |
| `netlify/functions/veille-web.mjs` (**une fois par jour**) | Le Gardien **source le web** grâce à l'outil de recherche de l'API Claude. Il garde un carnet de 3 nouveautés du monde des énigmes, avec leur source. |
| Couche `fort-vigie` (`?vigie=0` pour la couper) | Envoie les incidents. Si une panne se répète sur l'appareil, elle prévient le joueur. Si la vigie signale une panne générale, elle prévient le joueur une fois en lui disant ce que ça change pour lui. Elle ajoute aussi l'entrée **☰ → État du Fort** : services, interventions, nouvelles du monde des énigmes et signalement d'un souci. |

**Alertes** :
- Chaque nouveau problème écrit une ligne `[ALERTE-FORT]` dans les journaux des fonctions Netlify.
- Les signalements des joueurs écrivent une ligne `[SIGNALEMENT-FORT]`.
- En option, définir `GITHUB_ALERTES_TOKEN` (jeton GitHub limité aux *Issues* du dépôt) dans les variables d'environnement Netlify. La vigie ouvre alors un ticket GitHub, au plus une fois par problème et par jour. `GITHUB_ALERTES_DEPOT` permet d'utiliser un autre dépôt.

**Recherche web dans la conversation** :
- Le Gardien peut faire une recherche sur le web, une seule par réponse, uniquement si le joueur demande une information réelle et récente. Il ne s'en sert jamais pour les épreuves du Fort.
- Les sources s'affichent sous sa réponse, et le joueur reste dans le jeu.
- Si la recherche web n'est pas activée sur le compte Anthropic, ou si elle est trop lente, le Gardien répond sans elle.
- Coût : environ 10 $ pour 1 000 recherches, en plus des jetons.

## Registre du Fort

☰ → « Registre du Fort » ouvre un vrai registre, partout (couche `fort-registre`, désactivable avec `?registre=0`) :

- **En partie** :
  - l'univers et la salle en cours (n / total) ;
  - le trousseau de clés gagnées et perdues ;
  - les doublons ;
  - les épreuves déjà franchies.
- **Toujours** :
  - ta légende (parties jouées, coffres ouverts, record, niveau, titres) ;
  - la chasse de saison ;
  - les salles bâties par le Gardien, avec leur jeu.

Auparavant, cette entrée ne faisait qu'afficher un petit encart, invisible hors partie : rien ne se passait sur l'accueil. `outils/verifier.js` vérifie désormais que le Registre s'ouvre.

## Entrée dans les mondes

La carte de passage d'un univers à l'autre (« Devant toi, la porte de… ») ne se ferme plus toute seule. On n'entre dans le monde qu'en cliquant sur **« Entrer dans … ▸ »**, ou avec Entrée ou Espace au clavier. Un toucher à côté ne fait rien, et la carte se referme si l'on revient à un menu.

## Saisons et changement automatique des décorations

- **Entre les fêtes, le Fort suit les saisons** :

  | Saison | Période | Décor |
  |---|---|---|
  | Automne | 23 sept. → 30 nov. | feuilles qui tombent, guirlande de feuilles, citrouille, brume dorée |
  | Hiver | 1er déc. → 19 mars | flocons, bonhomme de neige, neige posée, givre aux coins de la carte |
  | Printemps | 20 mars → 20 juin | pétales, pots de fleurs, guirlande pastel, rais de soleil |
  | Été | 22 juin → 22 sept. | lucioles, soleil, lampion, lumière chaude |

  Les fêtes gardent la priorité sur les saisons pendant leurs dates.
- **Changement automatique** :
  - le Fort revérifie le calendrier toutes les 10 minutes et à chaque retour sur l'onglet ;
  - quand la fête ou la saison change, le Gardien l'annonce (« Le Fort change de parure : Hiver au Fort ») et recharge le décor ;
  - ce rechargement n'a lieu que sur un menu, jamais en pleine partie, et une seule fois par session ;
  - une fête imposée par l'adresse (`?fete=…`) ne change pas.
- Pour tester une saison : `?fete=automne`, `hiver`, `printemps` ou `ete`.

## Le temps qu'il fait

Couche `fort-meteo`, désactivable avec `?meteo=0` ou dans ⚙️ Réglages PC.

- Chaque monde a son climat, et le temps y change pendant la partie : environ toutes les 3 minutes, il peut évoluer. Par exemple clair → nuageux → pluie → orage → pluie → nuageux, puis un **arc-en-ciel** quand la pluie cesse en journée.

  | Monde | Temps les plus fréquents |
  |---|---|
  | La Crique | pluie, orage, vent |
  | Néon | pluie |
  | Jungle | pluie, brouillard |
  | Désert | soleil, **vent de sable** |
  | Manoir | brouillard, orage |
  | Nord | neige, vent |
- **Sur le port de l'accueil**, le temps suit la **vraie météo de chez le joueur** quand elle est connue. Sinon, il suit la saison. En hiver, la pluie se change souvent en neige.
- Les salles intérieures (Coffre, salles du Gardien) restent à l'abri.
- La carte d'entrée dans un monde, le Registre et le carnet de route annoncent le temps qu'il fait. Le Gardien commente l'orage, la neige, le brouillard, le vent de sable et l'arc-en-ciel.
- **Animation** : uniquement transform et opacité, avec des motifs en tuile qui glissent d'une hauteur de motif. L'orage ne gronde que par des éclairs lointains, petits et brefs, jamais en éclairant l'écran.
- **Version allégée sur téléphone** : un seul rideau de pluie, pas de ronds dans les flaques.

## Sur PC : ce que font les bons jeux PC

- **Échap** ouvre le **Menu du Fort** quand il n'y a rien à fermer, et jamais en pleine épreuve, où le temps continue de courir. Le menu propose :
  - reprendre ;
  - le Registre ;
  - le mode photo ;
  - les réglages ;
  - les raccourcis ;
  - le plein écran ;
  - l'abandon de la partie, avec confirmation.
- **⚙️ Réglages PC** (touche O ou menu ☰), chaque réglage étant expliqué au survol :
  - taille de l'interface : Auto ou de 90 à 150 % ;
  - carnet de route ;
  - curseur du Fort (une clé dorée) ;
  - météo animée ;
  - compteur d'images (img/s et pire image).
- **Raccourcis personnalisables** : clique sur la touche, puis appuie sur la nouvelle. Les réglages et les touches suivent la sauvegarde PC ↔ mobile.

  | Touche | Action |
  |---|---|
  | F | plein écran |
  | P | mode photo |
  | R | Registre |
  | G | Gardien |
  | S | sauvegarde |
  | E | État du Fort |
  | O | réglages |
  | ? | aide |
- **Mode photo** : l'interface s'efface pour admirer le décor, qui suit la souris.
- **Carnet de route** : sur grand écran et en partie, un encadré en bas à gauche affiche le monde, la salle, le trousseau, les doublons et le temps.
- **Écrans ultra-larges** : la carte se rapproche du centre.

## Applications (PC et mobile)

Le dossier `portage/` emballe le jeu en applications installables, sans le réécrire :
- **Tauri 2** pour Windows, macOS et Linux ;
- **Capacitor 8** pour Android, et iOS sur un Mac.

Pour les construire : onglet **Actions** de GitHub → **Applications (PC et Android)** → **Run workflow**, puis récupérer les installateurs dans la rubrique « Artifacts ». Tous les détails sont dans `portage/README.md`.

Dans l'application, le jeu est embarqué et marche hors connexion. Le module `fort-natif` envoie les appels aux services en ligne vers le site, et les fonctions Netlify n'acceptent que les origines des applications, grâce à des règles d'accès entre origines (CORS) testées dans `outils/test-securite.mjs`.

## Guide des épreuves

Couche `fort-guide`, désactivable avec `?guide=0`.

- On l'ouvre depuis ☰ → **Guide des épreuves**, avec la touche **H** sur PC, ou depuis les Règles.
- Il couvre toutes les épreuves du Fort et les 8 jeux de la Forge, avec pour chacune :
  - le but ;
  - comment jouer ;
  - l'astuce du Gardien ;
  - le moment de la journée où elle apparaît ;
  - la salle qui l'abrite ;
  - le nombre de parties où tu l'as jouée.
- On peut chercher par nom et filtrer : épreuves du Fort, jeux de la Forge, jamais jouées.
- **Dans chaque épreuve**, le bouton « ❔ Comment jouer » ouvre l'aide de cette épreuve dans la carte, sans la couvrir. Le sablier continue de tourner. La toute première fois qu'on rencontre une épreuve, l'aide s'ouvre d'elle-même.

## Temps aléatoire

Le temps de chaque monde est **tiré au hasard à chaque entrée** selon son climat et la saison. Il change ensuite à **intervalles irréguliers**, entre 1 et 2 minutes et demie. Sur le port, la vraie météo du joueur devient seulement plus probable, elle n'est plus imposée. Le temps annoncé sur la carte d'entrée est toujours celui que l'on trouve en entrant.

## Panneaux de la place et fêtes foraines

Couche `fort-panneaux` (écran d'accueil), réglée par le créateur dans `pubs/annonces.json` : les joueurs ne peuvent rien y changer. Le mode d'emploi est dans `pubs/LISEZMOI.md`.

- **Panneaux sur pied**, comme les panneaux d'arène de League of Legends. Ils sont plantés sur les pavés, dans les allées entre les étals : deux montants, ou un seul mât si l'allée est étroite. Leurs poteaux ne touchent jamais un étal ni un lampadaire, et sur téléphone, la carte d'accueil cache leur pied comme elle cache les étals. Ils montrent les images du dossier `pubs/` (format 2:1), en fondu toutes les 7 s, et un appui ouvre le lien choisi. Il y a deux panneaux au plus.
- **Dernier post Instagram** : `{"source":"instagram","compte":"thomas_lzg"}`. Les fonctions `netlify/functions/instagram.mjs` (accès) et `instagram-maj.mjs` (planifiée, toutes les heures) récupèrent le dernier post et le gardent dans Netlify Blobs. Le jeu ne contacte jamais Instagram, et l'image est servie par le site lui-même. Il faut un compte Instagram professionnel et la variable `INSTAGRAM_TOKEN` dans Netlify ; le jeton est prolongé chaque semaine. Sans jeton, le panneau montre une affiche qui renvoie au profil.
- **Fêtes saisonnières**, derrière les étals : grande roue, chapiteau à l'enseigne de la fête, carrousel, et fanions tendus de mât en mât (printemps, Saint-Jean, Toussaint). Pour le marché de Noël, un sapin décoré remplace le chapiteau et une guirlande d'ampoules remplace les fanions.
- **Cohérence du décor** : les étals et les lampadaires sont peints dans l'image de fond. Un masque découpe donc les manèges à leur place, pour qu'ils passent derrière. Les lampadaires sont retrouvés dans l'image elle-même (jour, crépuscule, nuit, téléphone ou PC). La nuit, les manèges s'assombrissent avec la ville, et seules les ampoules restent vives.
- **Attractions animées** : la grande roue tourne. Le carrousel tourne aussi : ses chevaux défilent en boucle sur le plateau. Les ampoules du carrousel et du chapiteau s'allument en chenillard. Des visiteurs traversent la place et entrent sous le chapiteau, et la nuit, son entrée rougeoie. Ces animations restent actives en mode allégé (transform et opacity seulement).
- **Carrousel en rotation** : chaque cheval suit une orbite autour du mât. Devant le mât, il est plus grand, éclairé et va vers la droite ; derrière, il est plus petit, dans l'ombre, et revient vers la gauche. Chaque cheval a une animation au nom unique, pour que le régulateur d'animations du jeu ne fige pas un seul cheval.
- **Visiteurs du chapiteau**, jamais la même scène deux fois : ils arrivent à intervalles irréguliers (plus espacés la nuit), de gauche ou de droite, chacun à son pas. On croise des adultes, des femmes en robe, des chapeaux, parfois un parent suivi de son enfant. Certains hésitent devant l'entrée, d'autres ressortent. Le rideau ne s'écarte que lorsqu'une personne est sur le seuil, puis se referme derrière elle.
- **Marchand de l'étal de gauche** : il passe derrière son auvent, à la taille des autres marchands, et seules sa tête et ses épaules dépassent du comptoir.
- **Derrière les étals** : le Gardien fait sa ronde derrière les étals, plus loin et un peu plus petit, découpé par le même masque que les manèges. Le Panda, à la taille des autres marchands, se tient sous son auvent, le corps caché par le comptoir.
- **Les plans du décor, du fond vers l'avant** :
  1. le ciel et le château ;
  2. la petite herse de la porte la nuit, désormais derrière tout le reste ;
  3. les maisons et leurs fenêtres ;
  4. les manèges (roue, chapiteau ou sapin, carrousel) et les fanions ;
  5. le Gardien en ronde ;
  6. les panneaux, plantés dans les allées ;
  7. le Panda sous son auvent ;
  8. les étals, les marchands et les passants.
- **Placement des manèges** : ils ne se chevauchent jamais. Le chapiteau se met face à une allée, loin de la roue, en laissant de la place au carrousel. Le carrousel prend la place libre la moins cachée par un panneau, quitte à rapetisser un peu (il paraît alors plus loin). S'il n'y a vraiment pas de place, il n'y a pas de carrousel. Un panneau évite d'abord les manèges, puis le chapiteau. Les fanions vont de mât en mât, de gauche à droite.
- **Immobile par rapport aux étals** : le fond zoome lentement et suit la souris. Le décor est donc calculé dans le repère propre du marché, et le cadrage est figé tant que la fenêtre ne change pas. Manèges, panneaux et découpes restent collés aux étals au lieu d'être recalculés en continu.
- Animations : transform et opacity seulement. Le mouvement réduit est respecté. Options : `?panneaux=0` pour désactiver, `?foraine=1` pour forcer la fête.

## L'effraction du soir et la Foire secrète

Couches `fort-effraction` et `fort-foire`. Elles ne concernent que les parties commencées le soir ou la nuit, quand le Fort est fermé.

**Un passage différent chaque soir.** Le mode d'effraction est tiré à partir de la date. Tous les joueurs ont donc le même passage la même nuit, et jamais deux soirs de suite le même. L'accueil l'annonce (« 🌙 Ce soir, on entre par… »), et l'introduction comme son bouton s'adaptent.

| Passage | Le jeu |
|---|---|
| 🔒 Les grilles du Fort | le dialogue avec le Contrebandier, comme avant |
| 🌊 La poterne de la mer | avancer de rocher en rocher quand la vague se retire (5 passages, 3 faux pas permis) |
| 🪜 L'échelle du rempart | maintenir pour grimper, lâcher quand la sentinelle se retourne |
| 🛒 La charrette du Contrebandier | retenir sa couverture, puis répondre aux 3 questions du garde (9 s chacune) |
| 🕯️ Le souterrain oublié | un dédale 5 × 5 à la lanterne, avant que l'huile s'épuise |

Les soirs d'orage, la poterne est noyée : on passe par le souterrain. Gain : 6 doublons, plus 3 par faux pas évité. En cas d'échec, le Gardien attend le joueur en duel, comme avant. L'effraction revient à chaque nouvelle partie de nuit (le drapeau vit sur la partie). Test : `?effraction=poterne|rempart|charrette|souterrain|grilles`.

**La Foire secrète du Gardien (nuit seulement).** Une fois entré, le joueur découvre que le Gardien tient une foire clandestine derrière les remparts :

- chaque monde devient une attraction, avec la même épreuve et la même salle (le Galion Tanguant, le Train Fantôme, le Palais des Glaces, la Grande Roue des Étoiles…) ;
- la planche de BD devient l'affiche de l'attraction : bandeau rayé « La Foire secrète · attraction n° X », billets des attractions déjà faites, boutons « Monter dans l'attraction ▸ » et « Une autre attraction ↻ » ;
- des guirlandes et une grande roue qui tourne lentement veillent sur la partie (transform et opacity seulement) ;
- la salle du trésor affiche le plan de la foire parcourue cette nuit-là.

Le jour, rien ne change. Désactivation : `?foire=0`.

## Dépendances à jour

- **Applications (`portage/`)** : Capacitor passe de 8.5.3 à 8.6.0. Cela corrige l'alerte Dependabot (paquet `uuid` vulnérable, tiré par `xcode`). `glob`, `minimatch` et `rimraf` sont aussi mis à jour. `npm audit` : 0 vulnérabilité.
- **Tests (racine)** : Puppeteer passe de 23 à 25.16, ce qui ferme 10 alertes de gravité haute sur ses dépendances (`extract-zip`, `basic-ftp`, `zod`…). La CI de vérification tourne désormais sous Node 22, version requise par Puppeteer 25.

## Conformité W3C

Le code est vérifié avec le **Nu Html Checker** du W3C (`vnu.jar`, le moteur de validator.w3.org), lancé en local sur deux cibles :

- **`index.html` tel que publié** : 0 erreur, 0 avertissement (il y en avait 373).
- **Le DOM rendu de 22 écrans** (accueil, règles, histoire, choix, sept épreuves, résultat, effraction, voleur, trésor, plateau, menu…), capturé dans Chromium puis validé : de 166 erreurs à 0 erreur réelle.

Ce qui a été corrigé :

- les 30 feuilles `<style>` posées dans `<body>` rejoignent `<head>`, dans le même ordre ;
- deux valeurs CSS fautives : une durée `NaNs` (remplacée par `.01ms`) et un raccourci `mask` (écrit en propriétés détaillées) ;
- `"Palatino Linotype"` entre guillemets doubles cassait les attributs `style="…"` ; la famille s'écrit désormais sans guillemets, ce qui est du CSS valide ;
- les cartes d'épreuve sont des `<button>` : leur contenu passe de `<div>` à `<span>` affichés en bloc, sans changement visuel ;
- plus de `role="button"` redondant sur un vrai bouton, ni d'`aria-hidden` doublant `hidden` ;
- `@property --pp-m` devient `CSS.registerProperty()`, son équivalent JavaScript ;
- `vector-effect` passe du CSS à l'attribut SVG du fil d'argent.

Trois signalements restants sont des limites connues du validateur, pas des défauts :

- `clip-path: inset(… round 0 0 50% 50%)` sur le cadre des portraits : syntaxe valide de CSS Shapes, mais le validateur CSS n'accepte qu'un seul rayon ;
- « meta charset après 1024 octets » : n'apparaît que dans la sérialisation du DOM rendu, à cause des styles posés en ligne sur `<html>` à l'exécution ; le fichier publié déclare son encodage dès les premiers octets ;
- « image bloquée par img-src » (simple info) : la CSP autorise `data:` explicitement. Le validateur émet la même info sur un document minimal de deux lignes avec la même CSP.

Pour relancer : `java -jar vnu.jar index.html` (paquet npm `vnu-jar`, Java 11 ou plus).

## Le livre du Fort : règles, histoire, plateau

Couche `livre.js` (`window.FortLivre`, désactivation `?livre=0`) :

- **Règles du jeu** réécrites et à jour : le but en une phrase, une frise (Entrer → épreuves → défis bonus → Coffre) et neuf chapitres repliables — une partie pas à pas (planche de BD, refus d'une porte), les épreuves (une fois par partie, jeux liés à l'heure, 💡 Aide à 3 doublons, duels), clés et doublons, le Coffre (gain d'au moins 5 doublons, retour sans clé), le Fort la nuit (effraction, Contrebandier), les habitants (portraits), les modes de jeu, un Fort vivant (saisons, météo, décor, menu ☰), astuces. L'ancienne contradiction sur les défis bonus est levée. Le bouton du Guide des épreuves reste en tête.
- **Histoire du Fort** : neuf chapitres cohérents avec le jeu actuel (le Gardien encapuchonné à la lanterne et au bâton-clé, le Marché du port et le Panda, le Parieur et le Voleur, les grilles de la nuit et le Contrebandier, le Coffre), un portrait par chapitre, le texte entier sans « Lire la suite », des points cliquables, ← → au clavier, et « Jouer en solo » au dernier chapitre.
- **Mode Plateau** : légende des cases sous le plateau (repliable, l'état est mémorisé), info-bulle sur chaque case, icônes de cases agrandies, nom du joueur réduit au centre ; panneau élargi sur PC.

## Le Fort fermé la nuit

Le soir et la nuit (`isFortClosed`, 18 h – 6 h), le Fort est réellement fermé à l'image (couche `nuit.js`, `window.FortNuit`) :

- **Effraction** (rencontre du Contrebandier aux grilles) : voile de nuit sur la muraille peinte, lune à la place du soleil couchant, porte close (battants de bois, herse baissée, chaîne et cadenas qui se balance, mince lueur sous la porte) et lanterne d'une sentinelle qui fait sa ronde sur le chemin de ronde.
- **Accueil** : la porte lumineuse du château est remplacée par une petite herse fermée.
- **Début de partie cohérent** : le soir et la nuit, l'introduction montre le château de l'extérieur, porte close (texte adapté : « Le Fort a fermé ses portes pour la nuit… », bouton « Approcher des grilles 🌙 »). Le bouton mène directement à l'effraction devant la muraille du Fort (et non plus après l'entrée dans un monde). Réussie, « la grille s'entrouvre » puis la planche de BD ouvre le premier monde ; ratée, on est traîné à l'intérieur et la première épreuve devient un duel contre le Gardien. L'effraction a toujours le décor de la muraille (univers « fort ») et la carte de passage du seuil n'y apparaît plus. En journée, rien ne change.
- Repères de porte mesurés sur chaque image (paysage 2048×1152 et portrait 1290×2048), placés avec le même calcul « cover » que le décor. En journée, rien ne change. Désactivation : `?nuitfort=0`.

## Nouvelle épreuve : le Bonneteau du Panda

Le Panda glisse un doublon sous un de ses bols à thé, le montre une seconde, puis mélange les bols : il faut suivre le bon et le toucher (touches 1 à 4 sur PC). Couche `bonneteau.js` (`makeBonneteau` / `bonneteauHtml` / `attachBonneteau`), branchée dans `ALL_KINDS`, `buildChallenge`, l'affichage et le branchement des épreuves, `KIND_META`, les types de clés et les étiquettes.

- **Difficulté** : de 5 à 14 passes de plus en plus rapides (560 → 230 ms), **feintes** dès le niveau 3 (deux bols se croisent puis reviennent), **4e bol** dès le niveau 5. Temps : durée du mélange + 6 à 11 s pour choisir.
- Le tirage est fait d'avance et la position finale calculée ; un test rejoue 300 tirages pour vérifier qu'elle correspond.
- **Aide** (💡) : indique le bon bol, qui brille à la fin du mélange. Fiche dans le Guide des épreuves et réponse du Gardien.
- Le Panda entre en scène pendant l'épreuve. Pas de duel sur cette épreuve. Une seule fois par partie, comme les autres.

## Le marché du port s'anime

Sur l'accueil (couche `personnages.js`) :
- **Étals** : en plus des auvents qui ondulent, une lanterne se balance au coin de chaque étal (allumée la nuit) et un marchand s'active derrière un comptoir sur trois.
- **Passants** : chacun suit un trajet d'étal en étal et **s'arrête devant les stands** (2 à 5 s), se retourne quand il change de sens, et ne marque le pas qu'en marchant. Trajets calculés à partir des étals du décor (`@keyframes` générées).
- **Le bâton du Gardien** devient un bâton-clé : bois noueux, bague dorée, surmonté de l'anneau d'une clé qui luit doucement, et tenu par une main (il ne flotte plus à côté de la robe). Même dessin partout où le Gardien apparaît en pied (port, rencontres, planche de BD).
- **Le Panda** s'affaire derrière son comptoir (il se déplace, se penche, revient) ; **le Gardien** fait sa ronde sur le quai avec des haltes et fait demi-tour, sans masquer l'étal du Panda.
- **Marche** : les passants ont deux jambes et deux bras qui se balancent en opposition, le corps monte à chaque pas, et tout se fige quand ils s'arrêtent devant un étal (variable `--pp-m`). Certains portent un chapeau.
- **La nuit** (21 h – 6 h) le marché s'assoupit : moins de passants (2 à 3), plus lents, aux haltes plus longues ; un seul marchand, qui somnole ; le Panda pique du nez et laisse s'envoler des « z » ; le Gardien fait une ronde plus lente ; auvents et lanternes bougent à peine.
- Sobriété : trois passants en portrait, lanternes et marchands immobiles sur les appareils modestes, tout s'arrête si « réduire les animations » est demandé.

## Correctifs : choix respectés et confort sur PC

- **Le jeu choisi est celui qui se lance.** La couche « une épreuve, une seule fois » remplaçait au lancement tout jeu déjà joué, y compris celui que le joueur venait de choisir sur une carte (ex. « Le Pari du Panda » → « Le Fil d'Argent »). Désormais, un jeu choisi sur une carte (épreuve ou défi bonus) n'est jamais remplacé, et la liste des jeux joués est recalée avant de proposer les cartes, qui ne montrent donc plus de jeu déjà fait. Une épreuve annoncée en duel (« Relever le défi ») est aussi celle qui se joue : elle n'est plus échangée au moment de la relancer.
- **PC** : le panneau grandit dès 1100 px de large (×1,05 en 1366×768, ×1,2 en 1536×864, ×1,45 en 1920×1080 ; l'accueil plafonne à ×1,15 et s'élargit pour garder « Fort Énigma » sur une ligne). Les épreuves et les choix disposent d'un panneau plus large (560 px avant zoom). La salle du Coffre passe en deux colonnes (code à gauche, pavé et « Valider » à droite) : le bouton n'est plus coupé. La planche de BD s'agrandit sur les grands écrans.
- **Carnet de route retiré** (PC) : ce petit encart fixé en bas à gauche répétait la barre du haut (salle, clés, doublons), la météo et le Registre, et chevauchait les cartes posées à gauche (introduction, personnages). L'option a aussi disparu des Réglages PC. Le titre de l'introduction tient sur une ligne en grand écran.

## La planche du passage

À chaque entrée dans un monde, une planche de bande dessinée en trois cases **remplace la carte d'entrée** (couche `bd.js`, `window.FortBD`) : le Gardien à la lanterne avec un récitatif et une réplique propre au monde, la clé qui tourne dans la serrure avec son onomatopée (« CLAC ! », « KLONK ! »…), puis la porte en bois qui s'ouvre sur l'image du monde et son nom.

- **Entrer dans le monde ▸** (ou la touche Entrée) lance la salle.
- **Un autre monde ↻** : une fois par salle. Le Gardien choisit alors d'office une autre porte ; la nouvelle planche n'offre plus que « Entrer ».
- La carte d'entrée du jeu et la carte du seuil sont masquées pendant la planche (la carte reste en place, invisible, pour que la surveillance technique ne croie pas l'écran vide).
- Pas de planche en mode plateau ni pendant l'essai d'un jeu inédit : la carte classique y reste. Désactivation : `?bd=0` (absente sous navigateur automatisé, sauf `?bd=1`).

## Accueil allégé

- La carte d'accueil ne garde que l'essentiel : titre, phrase d'ambiance, horloge et météo, bannière (centrée) de fête, les trois modes de jeu, Règles / Légendes / Mes cartes et le lien « café ». L'horloge et la météo restent affichées côte à côte : la pastille montre le temps qu'il fait sur le Fort (la vraie météo locale si elle est connue), et un toucher dessus ouvre la saisie de la ville. Le compteur de parties et le doublon d'ambiance « Il fait nuit » sont retirés de la carte.
- **Titres du Gardien**, **Histoire du Fort** et **Qualité graphique** (Max → Auto → Éco, rechargement) passent dans le menu ☰, visibles hors partie seulement.
- Le **Panda du port** est découpé au niveau du comptoir de son étal : il le tient au lieu de flotter devant.
- Les **décors vivants** ne réagissent plus sur l'accueil ; ailleurs, la phrase n'apparaît qu'au premier toucher d'un lieu (ensuite, une simple onde).

## Fin de partie et décors vivants

- **Aucune clé gagnée** : en solo, l'écran « Le Destin est scellé » propose seulement **🏠 Retour à l'accueil** (la partie est inscrite au Tableau des légendes comme un échec). En soirée ou au plateau, l'équipe passe son tour de Coffre.
- **Le Coffre ouvert renferme un gain** : 5 doublons, +1 s'il reste plus de 30 s au sablier, +2 s'il en reste plus de 60. Le gain s'affiche sur l'écran de victoire.
- **Décors vivants** : toucher le décor (hors carte et boutons) sur l'accueil, les entrées de monde et les écrans de choix fait réagir la scène : une onde, des éclats et une phrase propre à chaque univers et à la météo. Une fois par lieu visité, il y a 30 % de chances d'y trouver un doublon caché (3 par partie au plus, pas en mode plateau). Couche `fin.js`, `window.FortFin`.

## Visages et Fil d'Argent

- **Le Contrebandier** (rencontre aux grilles, la nuit) a un portrait dessiné dans la facture du Panda et du Gardien : tricorne galonné, bandeau sur l'œil, cicatrice, pipe fumante, anneau d'or, éclairé par une lanterne (couche `visages.js`, `window.FortVisages`).
- **Le Voleur des Ombres** remplace son emoji par un portrait (capuche pointue, masque, yeux qui guettent, clé dérobée) ; sa silhouette en pied est redessinée dans le même esprit.
- **Le Fil d'Argent** est tracé en courbe : l'objet y est accroché par un anneau, la bourse est un vrai dessin noué par son cordon. Le fil ploie sous le poids, se dilate et rougit en chauffant, s'amincit en fondant, vibre en surchauffe puis se rompt en deux.

## Personnages : sans duellistes

Les personnages du Fort sont le Gardien, le Panda, le Parieur et le Voleur. Les duellistes ont été retirés : un duel oppose désormais au Gardien ou au Panda (une ancienne partie qui avait tiré les duellistes affronte le Gardien). Avant un duel, c'est l'adversaire réel qui entre en scène, avec sa propre réplique.

## Météo : fond propre

Les couches de météo inactives sont retirées de l'affichage (et non plus seulement rendues transparentes), ce qui supprime les lignes « fantômes » vues sur certains téléphones. Le vent et le sable sont dessinés en courtes rafales répétées, sans lignes sur toute la largeur. L'orage ne déclenche plus l'éclair blanc plein écran du décor.

## Bouton « Aide » : la solution

Couche `fort-aide`, désactivable avec `?aide=0`.

Dans chaque épreuve, un seul bouton **💡 Aide** montre la solution. Il coûte **3 doublons**.

| Épreuves | Ce que montre l'aide |
|---|---|
| Énigme, Écho | la bonne réponse, surlignée |
| Calcul, Anagramme | le résultat, le mot |
| Mémoire | la séquence |
| Sceau | combien de fois tourner chaque roue |
| Poids | les poids à prendre, surlignés |
| Marché | l'ordre des nombres |
| Astres | le nombre d'étoiles dorées |
| Pari du Panda | la carte la plus forte |
| Bingo | tes numéros qui vont sortir |
| Morpion | la case à jouer |
| Course, arbalète, fil d'argent, équilibre, lueurs, auto-tamponneuses | la technique exacte, avec les chiffres utiles |

Pour les jeux de la Forge, l'aide calcule la vraie solution :

| Jeu | Méthode | Ce que montre l'aide |
|---|---|---|
| Runes | calcul exact (algèbre linéaire) | les runes à toucher |
| Mosaïque | recherche du plus court chemin | les pièces à faire glisser |
| Dédale | plus court chemin | le chemin, surligné |
| Trois piliers | suite de coups optimale | les coups à jouer |
| Conduits | solution de la grille | rotations à faire, case par case |
| Miroirs | solution de la grille | les miroirs à tourner |
| Tableau | solution de la grille | les cases à remplir |
| Sceaux | solution de la grille | le sceau de chaque case |

Chaque solution a été suivie jusqu'à la victoire dans les tests.

Comme la solution est toujours à portée de main, les épreuves **montent d'un cran de difficulté**. Le guide des épreuves reste disponible dans le menu ☰.

## Le Panda du quai, les habitations et l'aide visuelle

- **Le Panda du Marché** (accueil, derrière le deuxième étal) a été redessiné : pelage ombré, gilet bordé d'or, lunettes rondes, brin de bambou et doublon épinglé. On peut le toucher : il répond dans sa propre bulle, avec des répliques qui changent selon le moment de la journée (petit matin, matin, après-midi, soir, nuit) et selon le profil du joueur (prénom, parties, record, coffres, épreuves rangées au grenier). La nuit, il somnole et se réveille au premier toucher.
- **Les habitations du quai** (`<script id="fort-habitations">`, désactivable avec `?habitations=0`) : le jeu lit la silhouette de la première rangée de façades dans le décor peint, puis ajoute des fenêtres, des volets, des portes et un liseré de lumière sur les toits le jour, des fenêtres qui vacillent (et s'éteignent de temps en temps) le soir et la nuit, et quelques cheminées qui fument. Les animations sont coupées en mode calme ou si « réduire les animations » est activé.
- **L'aide visuelle des épreuves** (`<script id="fort-aide-visuelle">`, `?aide-visuelle=0`) : quand une épreuve a été ratée au moins 2 fois (la moitié des essais, ou les 2 derniers), une fiche s'affiche sous la consigne : les gestes en pictogrammes, la règle et une astuce. Un toucher la referme.
- **Grenier plus réactif** : une épreuve est rangée au grenier (elle ne revient plus dans les parties) dès 3 échecs avec au moins 75 % d'échecs, ou 3 échecs sur les 4 dernières tentatives. L'ancienne règle (5 échecs à 60 %) reste valable. Au moins 10 épreuves restent toujours en jeu, et une épreuve rangée revient quand une nouvelle idée de l'Atelier est façonnée.

## Appareils Apple (iPhone, iPad, Mac)

Couche `fort-apple` (en tête de page, s'active seulement sur Safari et sur iOS) :

- **Son** : Safari met le contexte audio en pause (« suspendu » ou « interrompu ») après un appel, l'écran verrouillé ou un passage dans une autre appli, et ne le relance jamais seul. Les contextes sont gardés en liste et réveillés au premier geste, au retour dans le jeu et au focus. Le commutateur silencieux de l'iPhone coupe toujours le son du jeu (choix d'Apple, volontairement conservé).
- **Pas de zoom involontaire** : `touch-action: manipulation` (le double-tap ne zoome plus, le pincement reste) et champs de saisie à 16 px minimum sur iPhone/iPad (en dessous, Safari zoome en tapant).
- **Toucher fiable** : iOS n'envoie pas toujours le clic jusqu'au document sur une carte ou une vignette ; chaque bloc posé dans la page reçoit un écouteur vide qui le rend « cliquable ».
- **Clavier** : la page est remise en place quand le clavier se ferme (Safari la laissait parfois décalée).
- **Appui long** : plus de menu « Enregistrer l'image » ni de sélection de texte sur les boutons et le décor.
- **Compatibilité** : préfixes `-webkit-` ajoutés là où ils manquaient (`backdrop-filter`, `mask-image`, `user-select`) pour Safari avant la version 18 ; une expression régulière à « lookbehind » (inconnue d'iOS avant 16.4, qui bloquait tout un script) a été réécrite ; le Gardien explique que l'iPhone n'a pas de plein écran (ajouter le jeu à l'écran d'accueil).

## Safari 15 (iPad / iPhone sous iOS 15) et annonces de mise à jour

- **Safari 15.6** : tout le code du jeu est en JavaScript ES2021 (vérifié script par script) ; les couleurs `color-mix()` (Safari 16.2+) ont une couleur de repli ; préfixes `-webkit-` ajoutés pour `appearance` et `backface-visibility` ; le plein écran préfixé de l'iPad (`webkitRequestFullscreen`) reçoit les noms standard, donc le bouton ⛶ et la touche F marchent sur iPad.
- **Annonces du Gardien** : deux lignes courtes au plus, visibles 5 s après une mise à jour (3,5 s pendant l'installation). `window.__FORT_VERSION` et `__FORT_NOUVEAUTES` dans `index.html` doivent rester identiques à `version.json` à chaque publication, sinon le Gardien croit toujours à une nouvelle version.
- **Décor de la fête** : les panneaux sont choisis en premier dans une allée dégagée et entièrement visible ; le chapiteau puis le carrousel se placent autour (le panneau, puis le chapiteau, rapetissent un peu si la place manque ; sans place, pas de panneau). Un panneau ne masque plus jamais un manège. Les décorations de saison posées sur la carte (citrouille, feuilles) s'effacent pendant une fête foraine, et ne flottent plus au milieu de la place sur un écran bas. Le guichet du chapiteau est dessiné (plus de rectangle noir) et l'enseigne du sapin de Noël n'est plus cachée par les étals.

## Décor sur iPhone / iPad (Safari) : vérifications et sources

- **Le décor sautait en faisant défiler** : sur iOS, la barre d'adresse de Safari se replie et réapparaît pendant le défilement, ce qui change la hauteur de la fenêtre et déclenche des événements `resize` ([WebKit bug 141832](https://bugs.webkit.org/show_bug.cgi?id=141832), [explication](https://johnkavanagh.co.uk/articles/understanding-phantom-window-resize-events-in-ios/)). La place des manèges était recalculée à chaque fois. Elle est maintenant retenue par rapport aux étals et gardée tant que seules les dimensions verticales changent (même largeur, même orientation, même fête).
- **Petit panneau** (téléphone) : seule l'image est affichée (un texte de 7 px était coupé en plein mot). La guirlande de feuilles posée sur la carte s'efface pendant une fête foraine.
- **Compatibilité Safari 15.6 (iPadOS 15)**, vérifiée automatiquement avec les données MDN (`@mdn/browser-compat-data`) sur toutes les feuilles de style réellement chargées et tous les scripts :
  - fonctions récentes, avec repli : `color-mix()` (Safari 16.2, [source](https://web-platform-dx.github.io/web-features-explorer/features/color-mix)), `CSS.registerProperty` (16.4, [source](https://web-platform-dx.github.io/web-features-explorer/features/registered-custom-properties)), plein écran standard (16.4 ; version `webkit` utilisée avant), `CompressionStream` (16.4), `requestIdleCallback` et `navigator.vibrate` (absents) : tous testés avant usage ;
  - fonctions présentes depuis Safari 15.4 ([notes WebKit 15.4](https://webkit.org/blog/12445/new-webkit-features-in-safari-15-4/)) : `svh`/`dvh`, `:has()`, masques sans préfixe, `appearance`, `backface-visibility` ; propriétés `scale`/`translate` depuis Safari 14.1 ([web.dev](https://web.dev/articles/css-individual-transform-properties)) ;
  - restent sans effet sur Safari 15, sans conséquence : `overscroll-behavior` (16), `scrollbar-width` (18.2), `text-wrap: balance` (17.5).
- **Capture avec le vrai moteur de Safari** : `outils/capture-webkit.py` (WebKitGTK), voir l'en-tête du fichier.

## Fluidité sur iPad / iPhone anciens (iOS 15)

- **Décor « cassé » sur les appareils peu puissants** : le régulateur d'animations (FortEngine) mettait en pause une animation sur deux ou sur quatre parmi celles qui portent le même nom. Sur la place, cela figeait une partie des nacelles de la grande roue (qui penchaient pendant que la roue tournait), la moitié des ampoules du chapiteau et les jambes de certains passants (qui glissaient). Le décor de la place (`.pf-calque`, `.pf-arriere`, `.pp-port`) est désormais traité en bloc : tout ou rien ; au palier minimal, seules les lumières purement décoratives s'arrêtent, entièrement.
- **iOS 15 et plus ancien** (classe `ios-ancien`, d'après « Version/NN » ou « OS NN_ » du navigateur) : ces appareils ne peuvent pas passer à iPadOS 16 (iPad Air 2, iPad mini 4 : [liste Apple relayée par iPhone in Canada](https://www.iphoneincanada.ca/ipad/ipados-16-compatible-devices-list-ipad-air-2-ipad-mini-4-dropped/)). Palier « économe » fixe dès le départ (plus de va-et-vient du palier, qui relançait les styles), flou d'arrière-plan des cartes coupé (recalculé à chaque image derrière une carte pendant que le décor bouge) et fond fixe (pas de travelling). Les manèges continuent de tourner.

## Roue et personnages figés sur iPad (iPadOS 15)

- **Personnages** : en mode calme (palier ≥ 2, donc tous les iPad sous iOS 15 depuis la v62), une règle arrêtait toutes les animations des passants, du Gardien, du Panda et des marchands. Ils bougent de nouveau dans tous les modes ; seuls les auvents et les lanternes, purement décoratifs, s'arrêtent en mode calme. Seul « réduire les animations » du système les fige.
- **Grande roue** : elle tournait par la propriété CSS `rotate` appliquée à un groupe SVG, à l'intérieur d'un dessin filtré et masqué. Safari doit alors redessiner tout le dessin à chaque image, et les transformations CSS sur les éléments SVG y sont fragiles ([WebKit bug 183237](https://bugs.webkit.org/show_bug.cgi?id=183237), [bug 250387](https://bugs.webkit.org/show_bug.cgi?id=250387)). La roue est maintenant faite de calques HTML tournés par `transform` (pris en charge directement par le processeur graphique) : pieds fixes, jante et rayons qui tournent, douze nacelles qui tournent autour du moyeu en restant droites (deux rotations opposées synchronisées), moyeu. Vérifié avec le moteur WebKit : les nacelles avancent bien entre deux mesures.

## Carrousel, fanions et ampoules : pensés pour le moteur de Safari

Pas d'application iPad possible sans Mac (Xcode n'existe que sur macOS) : la fluidité se gagne côté web, en suivant la façon dont WebKit affiche les animations.

- **Carrousel** : les douze chevaux (six devant le mât, six derrière) sont des calques HTML déplacés par `transform`, dans un repère de 220 × 165 px mis à l'échelle une seule fois. Les chevaux du fond sont assombris par un filtre posé sur leur dessin fixe, jamais sur un calque qui bouge (un filtre sur un parent animé oblige à tout refiltrer à chaque image).
- **Fanions** : animés par `transform: rotate()` au lieu de la propriété `rotate` sur des éléments SVG.
- **Ampoules du chapiteau et du carrousel, lueur de l'entrée** : elles sont dessinées à l'intérieur du dessin SVG ; les faire clignoter force Safari à redessiner tout le chapiteau en continu. Sur iOS 15 (`ios-ancien`), elles restent allumées, fixes.
- Contrôle : avec le moteur WebKit et l'identité d'un iPad sous iOS 15, les chevaux, les nacelles et les passants avancent entre deux mesures prises à 3 s d'intervalle.

## Compteur de fluidité (?perf=1)

Le compteur affichait « fps 0 » quand le palier est imposé (iOS 15, réglage manuel, `?fxtier`), car la mesure n'avait lieu qu'en mode automatique. Avec `?perf=1`, la mesure tourne toujours (sans changer le palier imposé) et une ligne indique l'appareil : iOS, navigateur (Safari ou Chrome), taille d'écran et densité, et si le mode `ios-ancien` est actif. Sur iOS 15, une seule des deux nappes de pluie est affichée.
