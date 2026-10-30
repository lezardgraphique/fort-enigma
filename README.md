# Fort Énigma — L'Appel du Gardien

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
- **Le début de partie** se passe dans le **hall des portes** : une galerie voûtée sous les constellations, avec une porte lumineuse par monde (tour, roue, engrenage, flocon, ancre, masque, feuille, soleil, éclair, lune). Le Gardien avance vers la grande porte entrouverte sur les étoiles.
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
