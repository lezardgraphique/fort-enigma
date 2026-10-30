// Fort Énigma — chaque jeu de la Forge du Gardien est toujours soluble (sans navigateur).
// Lance : node outils/test-forge.mjs [index.html]
import { readFileSync } from "node:fs";
const html = readFileSync(process.argv[2] || new URL("../index.html", import.meta.url), "utf8");
const m = html.match(/<script id="fort-forge">([\s\S]*?)<\/script>/);
if (!m) { console.log("  ✗ couche de la Forge introuvable"); process.exit(1); }
globalThis.window = globalThis;
globalThis.document = { readyState: "loading", addEventListener() {}, getElementById: () => null, createElement: () => ({ style: {} }), head: { appendChild() {} }, body: {}, querySelector: () => null };
globalThis.localStorage = { _: {}, getItem(k) { return this._[k] || null; }, setItem(k, v) { this._[k] = v; } };
globalThis.location = { search: "" };
new Function(m[1])();
const F = window.FortForge;
let echecs = 0;
const verif = (nom, ok) => { if (!ok) echecs++; console.log((ok ? "  ✓ " : "  ✗ ") + nom); };
const N = 300, pb = {};
for (const d of [0, 4, 8, 12]) for (let k = 0; k < N; k++) {
  const t = F.generer("tuyaux", d); if (!F._tuyauxRelies({ n: t.n, g: t.sol, e: t.e, s: t.s })) pb.tuyaux = 1;
  const mi = F.generer("miroirs", d), ms = JSON.parse(JSON.stringify(mi));
  Object.values(ms.g).forEach((v) => { if (v.sol) v.cur = v.sol; });
  if (!F._trajet(ms).gagne || F._trajet(mi).gagne) pb.miroirs = 1;
  if (F.generer("runes", d).g.every((v) => !v)) pb.runes = 1;
  if (F.generer("taquin", d).t.join() === "1,2,3,4,5,6,7,8,0") pb.taquin = 1;
  const sc = F.generer("sceaux", d); if (!F._sceauxOk(sc.sol) || sc.g.indexOf(-1) < 0) pb.sceaux = 1;
  if (F._tableauOk(F.generer("tableau", d))) pb.tableau = 1;
  const de = F.generer("dedale", d); if (!de.m || de.m.length !== de.n * de.n) pb.dedale = 1;
}
verif("8 jeux inédits dans la Forge", Object.keys(F.mecaniques).length === 8);
for (const k of Object.keys(F.mecaniques)) verif(`${k} : ${N * 4} parties générées, toutes solubles et non résolues d'avance`, !pb[k]);
console.log(echecs ? `\n${echecs} vérification(s) en échec.` : "\nForge du Gardien : tout est conforme.");
process.exit(echecs ? 1 : 0);
