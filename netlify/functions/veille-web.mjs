// ============================================================
// Fort Énigma -- la VEILLE du Gardien sur le web (une fois par jour)
// ------------------------------------------------------------
// Le Gardien source lui-même le web (outil de recherche de l'API
// Claude) pour rester à la pointe : nouveautés et tendances des jeux
// d'énigmes, escape games et casse-tête. Il en garde un court carnet
// (titre, résumé, source) que le joueur lit DANS le jeu (☰ → État du
// Fort) et dont le Gardien se sert pour converser.
// Coût maîtrisé : une seule requête par jour, 3 recherches au plus.
// ============================================================
import { magasin, propre } from "../lib/vigie.mjs";

export const config = { schedule: "@daily" };

const MODELES = ["claude-haiku-5-5", "claude-haiku-4-5-20251001"];
const CONSIGNE = `Tu es le Gardien de Fort Énigma, un jeu web d'énigmes et de mini-jeux (escape game familial).
Fais une courte veille sur le web : trouve 3 nouveautés ou tendances RÉCENTES (dernières semaines) dans les jeux d'énigmes,
casse-tête, escape games ou jeux de logique, qui pourraient inspirer le Fort. Pas de contenu choquant ni politique.
Réponds UNIQUEMENT par un tableau JSON de 3 objets : [{"titre": "6 à 10 mots", "resume": "une phrase de 15 à 30 mots en français", "source": "https://…"}]`;

function env(k) { try { return Netlify.env.get(k); } catch (e) { return process.env[k]; } }

export async function interroger(apiKey, appel = fetch) {
  for (const modele of MODELES) {
    const c = new AbortController(), t = setTimeout(() => c.abort(), 26000);
    try {
      const r = await appel("https://api.anthropic.com/v1/messages", {
        method: "POST", signal: c.signal,
        headers: { "content-type": "application/json", "x-api-key": apiKey, "anthropic-version": "2023-06-01" },
        body: JSON.stringify({ model: modele, max_tokens: 900, messages: [{ role: "user", content: CONSIGNE }],
          tools: [{ type: "web_search_20250305", name: "web_search", max_uses: 3 }] }),
      });
      const raw = await r.text();
      if (r.status === 404 || (r.status === 400 && /model/i.test(raw))) continue;
      if (r.status < 200 || r.status >= 300) { console.error("veille-web : API", r.status, raw.slice(0, 200)); return null; }
      const data = JSON.parse(raw);
      const texte = (data.content || []).filter((b) => b && b.type === "text").map((b) => b.text).join("\n");
      const m = texte.match(/\[[\s\S]*\]/);
      const liste = m ? JSON.parse(m[0]) : [];
      return (Array.isArray(liste) ? liste : []).slice(0, 3).map((x) => ({
        titre: propre(x && x.titre, 90), resume: propre(x && x.resume, 260),
        source: /^https:\/\/[^\s"<>]{4,300}$/.test(x && x.source || "") ? x.source : "",
      })).filter((x) => x.titre && x.resume);
    } catch (e) { console.error("veille-web :", e && e.name); return null; }
    finally { clearTimeout(t); }
  }
  return null;
}

export default async () => {
  const apiKey = env("ANTHROPIC_API_KEY");
  if (!apiKey) return new Response("pas de clé");
  const liste = await interroger(apiKey);
  if (!liste || !liste.length) { console.warn("[ALERTE-FORT] ATTENTION veille-web — la veille du web n'a rien rapporté aujourd'hui."); return new Response("vide"); }
  const store = await magasin("vigie");
  await store.setJSON("veille", { t: Date.now(), liste });
  return new Response("ok");
};
