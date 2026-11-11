// Fort Énigma — tests de sécurité des fonctions serveur (sans réseau, sans clé).
// Lance : node outils/test-securite.mjs   (code de sortie 1 si une vérification échoue)
// Le Gardien n'utilise plus aucune API d'IA : il répond dans le jeu avec sa mémoire du Fort.
const H = { "content-type": "application/json", origin: "https://fort-enigma.netlify.app" };
const corps = (o) => JSON.stringify(o);
let echecs = 0;
// ---- sauvegarde partagée entre appareils (faux magasin en mémoire) ----
const sv = await import(new URL("../netlify/functions/sauvegarde.mjs", import.meta.url));
const mem = new Map(); let ne = 0;
const magasin = {
  async get(k) { const v = mem.get(k); return v ? JSON.parse(v.s) : null; },
  async getWithMetadata(k) { const v = mem.get(k); return v ? { data: JSON.parse(v.s), etag: v.e } : null; },
  async setJSON(k, o, c = {}) { const v = mem.get(k); if (c.onlyIfMatch && (!v || v.e !== c.onlyIfMatch)) return { modified: false }; if (c.onlyIfNew && v) return { modified: false }; mem.set(k, { s: JSON.stringify(o), e: "e" + ++ne }); return { modified: true }; },
  async delete(k) { mem.delete(k); },
};
const ID = "a".repeat(64), base = "https://fort-enigma.netlify.app/.netlify/functions/sauvegarde";
async function sauv(nom, url, init, statut, verif) {
  const r = await sv.traiter(new Request(url, init), magasin);
  const t = await r.text();
  const ok = r.status === statut && (!verif || verif(t));
  if (!ok) echecs++;
  console.log((ok ? "  ✓ " : "  ✗ ") + "sauvegarde : " + nom + " → " + r.status);
}
const paquet = (o) => JSON.stringify({ id: ID, rev: 0, iv: "AAAAAAAAAAAAAAAA", d: "QUJD", ...o });
if (!(sv.config && sv.config.rateLimit && sv.config.rateLimit.windowLimit <= 60)) { echecs++; console.log("  ✗ sauvegarde : rateLimit absent"); } else console.log("  ✓ sauvegarde : rateLimit " + sv.config.rateLimit.windowLimit + "/" + sv.config.rateLimit.windowSize + "s");
await sauv("identifiant invalide refusé", base + "?id=../../x", { method: "GET" }, 400);
await sauv("inconnue → 404 sans contenu", base + "?id=" + ID, { method: "GET" }, 404, (t) => !JSON.parse(t).d);
await sauv("écriture d'une origine étrangère refusée", base, { method: "PUT", headers: { ...H, origin: "https://exemple-malveillant.com" }, body: paquet() }, 403);
await sauv("écriture sans origine refusée", base, { method: "PUT", headers: { "content-type": "application/json" }, body: paquet() }, 403);
await sauv("type de contenu vérifié", base, { method: "PUT", headers: { ...H, "content-type": "text/plain" }, body: paquet() }, 415);
await sauv("taille bornée", base, { method: "PUT", headers: H, body: paquet({ d: "A".repeat(500000) }) }, 413);
await sauv("format strict (base64)", base, { method: "PUT", headers: H, body: paquet({ d: "<script>" }) }, 400);
await sauv("première écriture", base, { method: "PUT", headers: H, body: paquet() }, 200, (t) => JSON.parse(t).rev === 1);
await sauv("écriture périmée refusée (conflit)", base, { method: "PUT", headers: H, body: paquet({ rev: 0 }) }, 409);
await sauv("lecture du paquet chiffré", base + "?id=" + ID, { method: "GET" }, 200, (t) => { const j = JSON.parse(t); return j.rev === 1 && j.d === "QUJD" && !("id" in j); });
await sauv("effacement d'une origine étrangère refusé", base + "?id=" + ID, { method: "DELETE", headers: { origin: "https://exemple-malveillant.com" } }, 403);
await sauv("effacement par le jeu", base + "?id=" + ID, { method: "DELETE", headers: { origin: "https://fort-enigma.netlify.app" } }, 200);
await sauv("méthode inconnue refusée", base, { method: "POST", headers: H, body: paquet() }, 405);
// ---- vigie : rapports, état, contrôles ----
const rp = await import(new URL("../netlify/functions/rapport.mjs", import.meta.url));
const et = await import(new URL("../netlify/functions/etat.mjs", import.meta.url));
const vg = await import(new URL("../netlify/functions/gardien-veille.mjs", import.meta.url));
const vl0 = await import(new URL("../netlify/lib/vigie.mjs", import.meta.url));
async function vig(nom, mod, url, init, statut, verif) {
  const r = await mod.traiter(new Request(url, init), magasin); const t = await r.text();
  const ok = r.status === statut && (!verif || verif(t)); if (!ok) echecs++;
  console.log((ok ? "  ✓ " : "  ✗ ") + "vigie : " + nom + " → " + r.status);
}
const RP = "https://fort-enigma.netlify.app/api/rapport";
await vig("rapport d'une origine étrangère refusé", rp, RP, { method: "POST", headers: { ...H, origin: "https://exemple-malveillant.com" }, body: corps({ incidents: [] }) }, 403);
await vig("rapport : types inconnus ignorés", rp, RP, { method: "POST", headers: H, body: corps({ incidents: [{ type: "<script>", msg: "x" }] }) }, 200, (t) => JSON.parse(t).retenus === 0);
await vig("rapport : message nettoyé (pas de lien, de balise ni de jeton)", rp, RP, { method: "POST", headers: H, body: corps({ version: "v1", incidents: [{ type: "erreur", msg: "<b>boom</b> https://x.y/secret " + "sk-" + "ant-api03-" + "A".repeat(40), ecran: "accueil", kind: "riddle" }] }) }, 200,
  () => { const d = [...mem.entries()].find(([k]) => k.startsWith("jour-")); const sig = d && Object.values(JSON.parse(d[1].s).sig)[0]; return sig && !/[<>]|https?:|sk-ant-api03-A{20}/.test(sig.msg); });
await vig("rapport : taille bornée", rp, RP, { method: "POST", headers: H, body: corps({ incidents: [{ type: "erreur", msg: "a".repeat(20000) }] }) }, 413);
await vig("état : lecture publique sans secret", et, "https://fort-enigma.netlify.app/api/etat", { method: "GET" }, 200, (t) => JSON.parse(t).niveau === "inconnu");
const tout = { ok: true, statut: 200, ms: 100 };
const sain = await vg.verifier({ base: "https://f", incidents: { total: 2, sig: {} }, sonde: async () => tout });
const malade = await vg.verifier({ base: "https://f", incidents: { total: 60, sig: { a: { n: 12, type: "maintenance", kind: "memory", msg: "boom" } } },
  sonde: async (u) => /sauvegarde/.test(u) ? { ok: false, statut: 502, ms: 50 } : tout });
const okV = sain.niveau === "ok" && malade.niveau === "panne" && malade.problemes.some((p) => p.code === "sauvegarde") && malade.problemes.some((p) => p.code === "repete:memory") && malade.problemes.some((p) => p.code === "incidents");
if (!okV) echecs++; console.log((okV ? "  ✓ " : "  ✗ ") + "vigie : détecte panne, panne répétée et avalanche d'incidents");
const T0 = 1e13;
const notes = await vg.verifier({ base: "https://f", cleStatut: 200, maintenant: T0, incidents: { total: 0, sig: {} }, sonde: async () => tout,
  serveur: { blobs: { gravite: "panne", texte: "Le stockage ne répond plus", dernier: T0 - 6e5, n: 3 }, vieux: { gravite: "panne", texte: "ancien", dernier: T0 - 864e5 } } });
const okN = notes.niveau === "panne" && notes.problemes.some((p) => p.code === "serveur:blobs" && /3 fois/.test(p.texte)) && !notes.problemes.some((p) => p.code === "serveur:vieux");
if (!okN) echecs++; console.log((okN ? "  ✓ " : "  ✗ ") + "vigie : reprend les pannes signalées par les services (2 dernières heures)");
const errV = console.error; let lignes = []; console.error = (...a) => lignes.push(a.join(" "));
vl0._oublierAlertes();
const a1 = await vl0.alerteServeur("essai", "panne", "boom", { store: magasin, maintenant: T0 });
const a2 = await vl0.alerteServeur("essai", "panne", "boom", { store: magasin, maintenant: T0 + 6e4 });
const a3 = await vl0.alerteServeur("essai", "panne", "boom", { store: magasin, maintenant: T0 + 7e5 });
console.error = errV;
const noteS = mem.get("serveur"); const okA = a1 && !a2 && a3 && lignes.length === 2 && /^\[ALERTE-FORT\] PANNE essai/.test(lignes[0]) && noteS && JSON.parse(noteS.s).essai.n === 2;
if (!okA) echecs++; console.log((okA ? "  ✓ " : "  ✗ ") + "service : alerte immédiate « [ALERTE-FORT] », sans répétition pendant 10 min, notée pour la vigie");
const sched = vg.config && vg.config.schedule === "@hourly";
if (!sched) echecs++; console.log((sched ? "  ✓ " : "  ✗ ") + "vigie : tourne seule toutes les heures");

// ---- application installée (Tauri / Capacitor) : CORS limité à ses origines ----
async function cors(nom, fn, init, statut, verif) {
  const r = await fn(new Request("https://fort-enigma.netlify.app/api/x", init)); const ok = r.status === statut && (!verif || verif(r)); if (!ok) echecs++;
  console.log((ok ? "  ✓ " : "  ✗ ") + "application : " + nom + " → " + r.status);
}
const vlc = await import(new URL("../netlify/lib/vigie.mjs", import.meta.url));
const servi = async (req) => vlc.preflight(req) || vlc.avecCors(req, vlc.json({ ok: true }));
await cors("pré-vérification depuis l'appli mobile", servi, { method: "OPTIONS", headers: { origin: "capacitor://localhost" } }, 204, (r) => r.headers.get("access-control-allow-origin") === "capacitor://localhost");
await cors("pré-vérification depuis un site étranger refusée", servi, { method: "OPTIONS", headers: { origin: "https://exemple-malveillant.com" } }, 403);
await cors("réponse lisible par l'appli PC", servi, { method: "POST", headers: { ...H, origin: "tauri://localhost" }, body: "{}" }, 200, (r) => r.headers.get("access-control-allow-origin") === "tauri://localhost");
await cors("aucun CORS pour un site étranger", servi, { method: "POST", headers: { ...H, origin: "https://exemple-malveillant.com" }, body: "{}" }, 200, (r) => !r.headers.get("access-control-allow-origin"));
const vl = await import(new URL("../netlify/lib/vigie.mjs", import.meta.url));
const pf = vl.preflight(new Request("https://f/api/rapport", { method: "OPTIONS", headers: { origin: "http://tauri.localhost" } }));
const okp = pf && pf.status === 204 && pf.headers.get("access-control-allow-origin") === "http://tauri.localhost"; if (!okp) echecs++;
console.log((okp ? "  ✓ " : "  ✗ ") + "application : services de la vigie et de la sauvegarde ouverts à l'appli");

import { readdirSync, readFileSync } from "node:fs";
const dossier = new URL("../netlify/", import.meta.url);
const fichiers = ["functions", "lib"].flatMap((d) => readdirSync(new URL(d + "/", dossier)).filter((f) => f.endsWith(".mjs")).map((f) => readFileSync(new URL(d + "/" + f, dossier), "utf8")));
const sansIA = fichiers.every((t) => !/ANTHROPIC|anthropic\.com|x-api-key/i.test(t));
if (!sansIA) echecs++; console.log((sansIA ? "  ✓ " : "  ✗ ") + "autonomie : aucune fonction n'appelle d'API d'IA ni ne lit de clé");

console.log(echecs ? `\n${echecs} vérification(s) de sécurité en échec.` : "\nSécurité des fonctions : tout est conforme.");
process.exit(echecs ? 1 : 0);
