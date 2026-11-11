// ============================================================
// Fort Énigma -- état du Fort, lu par le jeu (☰ → État du Fort)
//   GET /api/etat -> { niveau, problemes, verifie, incidents24h, veille }
// Données publiques et sans secret : textes de la vigie. Mis en cache
// une minute. (La veille du web, qui passait par l'API Claude, est retirée.)
// ============================================================
import { json, magasin, preflight, avecCors } from "../lib/vigie.mjs";

export const config = { path: "/api/etat", rateLimit: { windowLimit: 30, windowSize: 60, aggregateBy: ["ip", "domain"] } };

export async function traiter(req, store) {
  if (req.method !== "GET") return json({ erreur: "méthode non permise" }, 405);
  const etat = await store.get("etat", { type: "json" });
  const e = etat || { niveau: "inconnu", problemes: [] };
  return json({
    niveau: e.niveau, verifie: e.verifie || null, incidents24h: e.incidents24h || 0,
    problemes: (e.problemes || []).filter((p) => p.gravite !== "info").map((p) => ({ code: p.code, gravite: p.gravite, texte: p.texte, depuis: p.depuis })),
    veille: null,
  }, 200, "public, max-age=60");
}

export default async (req) => {
  const p = preflight(req); if (p) return p;
  try { return avecCors(req, await traiter(req, await magasin("vigie"))); }
  catch (e) { return json({ niveau: "inconnu", problemes: [], veille: null }, 200, "no-store"); }
};
