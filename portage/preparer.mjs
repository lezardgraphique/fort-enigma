// Fort Énigma — prépare le dossier www/ embarqué dans les applications.
// Le jeu est le même fichier que sur le site : on copie index.html, ses décors,
// ses icônes et version.json. (Pas de service worker : l'application a déjà
// tous ses fichiers sur l'appareil.)
import { cpSync, mkdirSync, rmSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ici = dirname(fileURLToPath(import.meta.url));
const racine = join(ici, "..");
const www = join(ici, "www");
rmSync(www, { recursive: true, force: true });
mkdirSync(www, { recursive: true });

const fichiers = ["index.html", "version.json", "manifest.webmanifest", "favicon.ico", "favicon-16.png", "favicon-32.png",
  "icone-192.png", "icone-512.png", "icone-masquable-512.png", "apercu.jpg", "cle-fort-enigma.png", "cle-fort-enigma-transparent.png"];
for (const f of fichiers) if (existsSync(join(racine, f))) cpSync(join(racine, f), join(www, f));
cpSync(join(racine, "decors"), join(www, "decors"), { recursive: true });

// la version de l'application suit celle du jeu : 1.<mois depuis 2026>.<jour×100+heure>
try {
  const v = JSON.parse(readFileSync(join(racine, "version.json"), "utf8")).version || "";
  const m = v.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/);
  if (m) {
    // compatible avec les installateurs Windows (MSI : 255.255.65535 au plus)
    const version = `1.${(+m[1] - 2026) * 12 + +m[2]}.${+m[3] * 100 + +m[4]}`;
    const conf = join(ici, "src-tauri", "tauri.conf.json");
    const c = JSON.parse(readFileSync(conf, "utf8")); c.version = version; writeFileSync(conf, JSON.stringify(c, null, 2) + "\n");
    console.log("version de l'application :", version);
  }
} catch (e) { console.warn("version non mise à jour :", e.message); }
console.log("www/ prêt :", fichiers.length, "fichiers + decors/");
