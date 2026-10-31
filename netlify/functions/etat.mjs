// ============================================================
// Fort Énigma -- état du Fort, lu par le jeu (☰ → État du Fort)
//   GET /api/etat -> { niveau, problemes, verifie, incidents24h, veille }
// Données publiques et sans secret : textes de la vigie et carnet de
// veille du web. Mis en cache une minute.
// ============================================================
import { json, magasin } from "../lib/vigie.mjs";

export const config = { path: "/api/etat", rateLimit: { windowLimit: 30, windowSize: 60, aggregateBy: ["ip", "domain"] } };

export async function traiter(req, store) {
  if (req.method !== "GET") return json({ erreur: "méthode non permise" }, 405);
  const [etat, veille] = await Promise.all([store.get("etat", { type: "json" }), store.get("veille", { type: "json" })]);
  const e = etat || { niveau: "inconnu", problemes: [] };
  return json({
    niveau: e.niveau, verifie: e.verifie || null, incidents24h: e.incidents24h || 0,
    problemes: (e.problemes || []).filter((p) => p.gravite !== "info").map((p) => ({ code: p.code, gravite: p.gravite, texte: p.texte, depuis: p.depuis })),
    veille: veille ? { t: veille.t, liste: veille.liste || [] } : null,
  }, 200, "public, max-age=60");
}

export default async (req) => {
  try { return await traiter(req, await magasin("vigie")); }
  catch (e) { return json({ niveau: "inconnu", problemes: [], veille: null }, 200, "no-store"); }
};
