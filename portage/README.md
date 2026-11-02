# Fort Énigma en application

Le jeu reste **un seul fichier** (`index.html`). Ce dossier l'emballe en applications installables, sans le réécrire.

| Cible | Outil | Résultat |
|---|---|---|
| Windows, macOS, Linux | [Tauri 2](https://tauri.app) | `.msi` / `.exe`, `.dmg`, `.AppImage` / `.deb` (≈ 10 Mo, utilise le moteur web du système) |
| Android | [Capacitor 8](https://capacitorjs.com) | `.apk` |
| iOS | Capacitor 8 | projet Xcode à construire sur un Mac |

## Le plus simple : laisser GitHub construire

Onglet **Actions** → **Applications (PC et Android)** → **Run workflow**. On peut aussi pousser une étiquette, par exemple `git tag v1.0 && git push --tags`.

Au bout d'une quinzaine de minutes, les installateurs sont à télécharger en bas de la page de l'exécution, dans la rubrique **Artifacts**.

## Sur ta machine

```bash
cd portage
npm ci
npm run pc                    # ouvre le jeu dans une fenêtre (Rust + Tauri requis)
npm run pc:construire         # installateur PC pour ton système
npm run android:creer         # une seule fois (Android Studio / SDK requis)
npm run android:construire    # .apk de test
npm run ios:creer             # une seule fois, sur un Mac avec Xcode
npm run ios:synchroniser      # puis ouvrir ios/App dans Xcode
```

`preparer.mjs` copie dans `www/` le jeu, ses décors, ses icônes et `version.json`. La version de l'application suit celle du jeu (`1.<mois>.<jour×100+heure>`).

## Ce qui change dans l'application

- **Hors connexion** : le jeu complet est embarqué et fonctionne sans Internet.
- **Services en ligne** : la voix du Gardien, la sauvegarde PC ↔ mobile, la vigie et l'état du Fort sont appelés sur `https://fort-enigma.netlify.app`. C'est le module `fort-natif` du jeu qui s'en charge. Les fonctions Netlify n'autorisent que les origines des applications (`tauri://localhost`, `http(s)://tauri.localhost`, `capacitor://localhost`, `https://localhost`), en plus du site.
- **Mises à jour** : l'application ne se met pas à jour toute seule comme le site. Le Gardien signale qu'une nouvelle version est sortie, et il faut réinstaller.
- **Permissions** : aucune permission système n'est demandée (`src-tauri/capabilities/default.json` est vide).

## Pour publier dans les boutiques

- **Windows / macOS** : les installateurs ne sont pas signés, donc Windows SmartScreen ou macOS Gatekeeper afficheront un avertissement. Pour l'éviter, il faut un certificat de signature de code (Windows) et un compte Apple Developer avec notarisation (macOS), à ajouter en secrets GitHub.
- **Android / Play Store** : l'APK construit est une version de test. Pour le Play Store, il faut une clé de signature (*keystore*) et `./gradlew bundleRelease`, qui produit un `.aab`.
- **iOS / App Store** : il faut un Mac, Xcode et un compte Apple Developer. Apple refuse les applications qui ne sont qu'un site web emballé (règle 4.2). Le jeu embarqué, son fonctionnement hors connexion et la sauvegarde aident, mais rien n'est garanti.
