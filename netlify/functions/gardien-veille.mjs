// ============================================================
// Fort Énigma -- la VIGIE du Gardien (tourne seule, toutes les heures)
// ------------------------------------------------------------
// Sans joueur ni développeur, le Gardien vérifie lui-même que le Fort
// tient debout :
//   - le jeu, version.json et le mode hors connexion répondent ;
//   - la sauvegarde partagée et la voix du Gardien (IA) répondent ;
//   - la clé de l'IA est bien configurée ;
//   - les incidents remontés par les joueurs (rapport.mjs) ne
//     s'emballent pas (même panne répétée, avalanche d'erreurs).
// Il écrit l'état du Fort (lu par le jeu via /api/etat) et, quand un
// NOUVEAU problème apparaît, il donne l'alerte :
//   - toujours dans les journaux Netlify : ligne « [ALERTE-FORT] … » ;
//   - et, si GITHUB_ALERTES_TOKEN est configuré, en ouvrant un ticket
//     GitHub (au plus une fois par problème et par jour).
// ============================================================
import { jour, magasin, modifier } from "../lib/vigie.mjs";

export const config = { schedule: "@hourly" };

const SEUIL_ERREURS = 40;    // incidents / 24 h au-delà desquels on s'inquiète
const SEUIL_REPETE = 8;      // même incident répété

function env(k) { try { return Netlify.env.get(k); } catch (e) { return process.env[k]; } }

async function sonder(url, attendu, ms = 8000) {
  const c = new AbortController(), t = setTimeout(() => c.abort(), ms), t0 = Date.now();
  try {
    const r = await fetch(url, { signal: c.signal, headers: { "user-agent": "Fort-Enigma-Vigie" } });
    const corps = await r.text();
    return { ok: attendu(r, corps), statut: r.status, ms: Date.now() - t0 };
  } catch (e) { return { ok: false, statut: 0, ms: Date.now() - t0 }; }
  finally { clearTimeout(t); }
}

export async function verifier({ base, cleIA, incidents, sonde = sonder }) {
  const p = [];
  const ajoute = (code, gravite, texte) => p.push({ code, gravite, texte });
  const [site, ver, sw, sauv, ia] = await Promise.all([
    sonde(base + "/", (r, c) => r.status === 200 && /Fort/.test(c)),
    sonde(base + "/version.json", (r, c) => { try { return r.status === 200 && !!JSON.parse(c).version; } catch (e) { return false; } }),
    sonde(base + "/sw.js", (r) => r.status === 200),
    sonde(base + "/.netlify/functions/sauvegarde?id=" + "0".repeat(64), (r, c) => r.status === 404 && /"t"/.test(c)),
    sonde(base + "/api/gardien", (r) => r.status === 405),
  ]);
  if (!site.ok) ajoute("site", "panne", "Le Fort ne répond plus (page d'accueil, statut " + site.statut + ").");
  else if (site.ms > 6000) ajoute("lenteur", "attention", "Le Fort répond lentement (" + site.ms + " ms).");
  if (!ver.ok) ajoute("version", "attention", "version.json est illisible : les mises à jour automatiques sont bloquées.");
  if (!sw.ok) ajoute("horsligne", "attention", "Le service du mode hors connexion (sw.js) ne répond pas.");
  if (!sauv.ok) ajoute("sauvegarde", "panne", "La sauvegarde partagée PC ↔ mobile ne répond pas (statut " + sauv.statut + ").");
  if (!ia.ok) ajoute("gardien-ia", "panne", "La voix du Gardien (IA) ne répond pas (statut " + ia.statut + ").");
  else if (!cleIA) ajoute("gardien-ia", "attention", "La clé ANTHROPIC_API_KEY n'est pas configurée : le Gardien reste muet.");

  const total = incidents && incidents.total || 0;
  const sigs = Object.values(incidents && incidents.sig || {}).sort((a, b) => b.n - a.n);
  if (total >= SEUIL_ERREURS) ajoute("incidents", "attention", total + " incidents réparés chez les joueurs en 24 h (le plus fréquent : " + (sigs[0] ? sigs[0].type + " « " + sigs[0].msg.slice(0, 80) + " »" : "?") + ").");
  for (const s of sigs.slice(0, 3)) {
    if (s.n >= SEUIL_REPETE && s.type !== "joueur") ajoute("repete:" + (s.kind || s.type), "attention", "Panne répétée " + s.n + " fois : " + s.type + (s.kind ? " sur « " + s.kind + " »" : "") + " — « " + s.msg.slice(0, 90) + " ».");
  }
  const signalements = sigs.filter((s) => s.type === "joueur");
  if (signalements.length) ajoute("signalements", "info", signalements.length + " signalement(s) de joueurs : « " + signalements[0].msg.slice(0, 100) + " ».");

  const niveau = p.some((x) => x.gravite === "panne") ? "panne" : p.some((x) => x.gravite === "attention") ? "attention" : "ok";
  return { niveau, problemes: p, mesures: { site: site.ms, sauvegarde: sauv.ms, gardien: ia.ms }, incidents24h: total };
}

async function ticketGitHub(token, depot, titre, corps) {
  try {
    const r = await fetch("https://api.github.com/repos/" + depot + "/issues", {
      method: "POST",
      headers: { authorization: "Bearer " + token, accept: "application/vnd.github+json", "user-agent": "Fort-Enigma-Vigie", "content-type": "application/json" },
      body: JSON.stringify({ title: titre, body: corps, labels: ["alerte-gardien"] }),
    });
    return r.status;
  } catch (e) { return 0; }
}

export default async () => {
  const t = Date.now();
  try {
    const store = await magasin("vigie");
    const base = (env("URL") || "https://fort-enigma.netlify.app").replace(/\/$/, "");
    const [a, b] = await Promise.all([store.get("jour-" + jour(t), { type: "json" }), store.get("jour-" + jour(t - 864e5), { type: "json" })]);
    const inc = { total: (a && a.total || 0) + (b && b.total || 0) * 0.5 | 0, sig: Object.assign({}, b && b.sig, a && a.sig) };
    const etat = await verifier({ base, cleIA: !!env("ANTHROPIC_API_KEY"), incidents: inc });
    const avant = await store.get("etat", { type: "json" });
    for (const p of etat.problemes) p.depuis = (avant && (avant.problemes || []).find((x) => x.code === p.code) || {}).depuis || t;
    etat.verifie = t;
    await store.setJSON("etat", etat);

    // alerte uniquement pour les problèmes NOUVEAUX (pas déjà signalés depuis 24 h)
    const nouveaux = etat.problemes.filter((p) => p.gravite !== "info");
    if (nouveaux.length) {
      const envoyees = (await store.get("alertes", { type: "json" })) || {};
      const aSignaler = nouveaux.filter((p) => !envoyees[p.code] || t - envoyees[p.code] > 864e5);
      if (aSignaler.length) {
        for (const p of aSignaler) console.error("[ALERTE-FORT]", p.gravite.toUpperCase(), p.code, "—", p.texte);
        const token = env("GITHUB_ALERTES_TOKEN");
        if (token) {
          const depot = env("GITHUB_ALERTES_DEPOT") || "lezardgraphique/fort-enigma";
          await ticketGitHub(token, depot, "🚨 Le Gardien signale : " + aSignaler.map((p) => p.code).join(", "),
            "La vigie du Gardien a détecté :\n\n" + aSignaler.map((p) => "- **" + p.gravite + "** — " + p.texte).join("\n") +
            "\n\nÉtat complet : " + base + "/api/etat\n\n_Ticket ouvert automatiquement par la vigie (gardien-veille)._");
        }
        await modifier(store, "alertes", (d) => { aSignaler.forEach((p) => { d[p.code] = t; }); return d; }, {});
      }
    } else if (avant && avant.niveau !== "ok") console.log("[FORT-RETABLI] Tout est rentré dans l'ordre.");
    return new Response("ok");
  } catch (e) {
    console.error("[ALERTE-FORT] PANNE vigie — la vigie elle-même a échoué :", e && e.message);
    return new Response("erreur", { status: 500 });
  }
};
