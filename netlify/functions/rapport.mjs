// ============================================================
// Fort Énigma -- rapports d'incidents envoyés par le jeu
// ------------------------------------------------------------
// Quand le Gardien répare quelque chose dans le navigateur d'un joueur
// (erreur, écran vide, sablier figé, épreuve mise en maintenance…), le
// jeu en envoie ici un résumé ANONYME : type, court message nettoyé,
// écran, épreuve, version. Aucune donnée personnelle, aucun identifiant.
// Les incidents sont comptés par jour et par signature (Netlify Blobs) ;
// la vigie horaire (gardien-veille) les analyse et donne l'alerte.
//   POST /api/rapport  { version, incidents: [{ type, msg, ecran, kind }] }
// ============================================================
import { json, origineOk, propre, jour, magasin, modifier, preflight, avecCors } from "../lib/vigie.mjs";

export const config = {
  path: "/api/rapport",
  rateLimit: { windowLimit: 12, windowSize: 60, aggregateBy: ["ip", "domain"] },
};

const TYPES = /^(erreur|promesse|maintenance|scell|repli|r[ée]par|r[ée]veil|sablier|rendu|veille|reseau|joueur|lenteur)/;
const MAX = 16000;

export async function traiter(req, store) {
  if (req.method !== "POST") return json({ erreur: "méthode non permise" }, 405);
  if (!origineOk(req)) return json({ erreur: "origine refusée" }, 403);
  if (!/^application\/json\b/i.test(req.headers.get("content-type") || "")) return json({ erreur: "JSON attendu" }, 415);
  if (Number(req.headers.get("content-length") || 0) > MAX) return json({ erreur: "trop lourd" }, 413);
  const brut = await req.text();
  if (brut.length > MAX) return json({ erreur: "trop lourd" }, 413);
  let c; try { c = JSON.parse(brut); } catch (e) { return json({ erreur: "JSON invalide" }, 400); }
  if (!c || typeof c !== "object" || !Array.isArray(c.incidents)) return json({ erreur: "format invalide" }, 400);
  const version = propre(c.version, 24);
  const liste = c.incidents.slice(0, 20).map((i) => {
    if (!i || typeof i !== "object") return null;
    const type = propre(i.type, 20).toLowerCase();
    if (!TYPES.test(type)) return null;
    return { type, msg: propre(i.msg, type === "joueur" ? 300 : 160), ecran: propre(i.ecran, 30), kind: propre(i.kind, 30) };
  }).filter(Boolean);
  if (!liste.length) return json({ ok: true, retenus: 0 });

  const t = Date.now();
  await modifier(store, "jour-" + jour(t), (d) => {
    d.total = (d.total || 0) + liste.length;
    d.sig = d.sig || {};
    for (const i of liste) {
      const sig = (i.type + "|" + i.kind + "|" + i.msg.slice(0, 80)).slice(0, 140);
      const e = d.sig[sig] || (d.sig[sig] = { n: 0, type: i.type, msg: i.msg, ecran: i.ecran, kind: i.kind, version, premier: t });
      e.n++; e.dernier = t; e.version = version || e.version;
    }
    // on garde les 120 signatures les plus fréquentes
    const k = Object.keys(d.sig);
    if (k.length > 120) k.sort((a, b) => d.sig[a].n - d.sig[b].n).slice(0, k.length - 120).forEach((x) => delete d.sig[x]);
    return d;
  }, { total: 0, sig: {} });
  if (liste.some((i) => i.type === "joueur")) console.warn("[SIGNALEMENT-FORT]", liste.filter((i) => i.type === "joueur").map((i) => i.msg).join(" | ").slice(0, 300));
  return json({ ok: true, retenus: liste.length });
}

export default async (req) => {
  const p = preflight(req); if (p) return p;
  try { return avecCors(req, await traiter(req, await magasin("vigie"))); }
  catch (e) { console.error("rapport : échec", e && e.name); return json({ erreur: "indisponible" }, 503); }
};
