#!/usr/bin/env node
/* ============================================================
   Fort Énigma — vérificateur automatique d'affichage
   ------------------------------------------------------------
   Usage :  node verifier.js [chemin/vers/index.html]
   Contrôle, sur 4 formats d'écran :
     1. chevauchements entre la carte et les élements flottants
     2. débordements hors de l'écran
     3. déformation des décors (ratio non respecté)
     4. réactivité : écritures DOM inutiles au repos
     5. erreurs JavaScript au chargement
   Sortie : rapport lisible + code retour 1 si un défaut est vu.
   ============================================================ */
'use strict';
const path = require('path');
/* Puppeteer est cherche a l'endroit standard ; on accepte aussi un chemin
   fourni par l'environnement, pour les machines ou il est installe ailleurs. */
let puppeteer;
try {
  puppeteer = require('puppeteer');
} catch (_) {
  try {
    if (!process.env.PUPPETEER_PATH) throw new Error('PUPPETEER_PATH non defini');
    puppeteer = require(process.env.PUPPETEER_PATH);
  } catch (__) {
    console.error('Puppeteer est introuvable. Installez-le : npm install puppeteer');
    console.error('(ou definissez PUPPETEER_PATH vers une installation existante)');
    process.exit(2);
  }
}
/* Sans chemin explicite, Puppeteer utilise le navigateur qu'il a telecharge :
   c'est le cas normal en integration continue. */
const CHROME = process.env.CHROME_PATH || null;

const FICHIER = path.resolve(process.argv[2] || './index.html');
const FORMATS = [
  { w: 412, h: 915, nom: 'Android' },
  { w: 390, h: 844, nom: 'iPhone' },
  { w: 360, h: 640, nom: 'Petit' },
  { w: 1880, h: 830, nom: 'Desktop' },
];
const UNIVERS = ['fort', 'foraine', 'steampunk', 'nordique', 'pirate',
                 'manoir', 'jungle', 'desert', 'neon', 'nocturne'];

let defauts = 0;
const ko = (m) => { defauts++; console.log('   ✗ ' + m); };
const ok = (m) => console.log('   ✓ ' + m);

/* éléments flottants qui ne doivent jamais recouvrir la carte */
const FLOTTANTS = 'footer.credits,#fortV2Menu,'
  + '#fortDailyContract,#fortV2Hud,.gardien-toast,.clue-journal,.master-chat';

async function controlerFormat(navigateur, vp) {
  const page = await navigateur.newPage();
  const erreurs = [];
  page.on('pageerror', (e) => erreurs.push(e.message.slice(0, 90)));
  await page.setViewport({ width: vp.w, height: vp.h });
  await page.goto('file://' + FICHIER, { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 2800));

  console.log(`\n── ${vp.nom} (${vp.w}×${vp.h}) ──────────────`);

  /* 1 & 2 — chevauchements et débordements, écran par écran */
  for (const ecran of ['accueil', 'regles', 'legendes']) {
    const r = await page.evaluate((e, selFlottants) => {
      try { go(e); } catch (_) {}
      const boites = [];
      const ajoute = (nom, el) => {
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
        const b = el.getBoundingClientRect();
        if (b.width < 2 || b.height < 2) return;
        boites.push({ nom, t: b.top, b: b.bottom, l: b.left, r: b.right });
      };
      const carte = document.querySelector('.frame');
      if (carte) ajoute('carte', carte);
      document.querySelectorAll(selFlottants).forEach((el) =>
        ajoute(el.id || String(el.className).split(' ')[0], el));
      const croisements = [];
      for (let i = 0; i < boites.length; i++) {
        for (let j = i + 1; j < boites.length; j++) {
          const a = boites[i], c = boites[j];
          if (a.t < c.b && c.t < a.b && a.l < c.r && c.l < a.r)
            croisements.push(a.nom + ' ↔ ' + c.nom);
        }
      }
      const cr = carte ? carte.getBoundingClientRect() : null;
      return {
        croisements,
        deborde: cr ? (cr.bottom > innerHeight + 1 || cr.top < -1) : false,
      };
    }, ecran, FLOTTANTS);

    if (r.croisements.length) ko(`${ecran} : ${r.croisements.join(', ')}`);
    if (r.deborde) ko(`${ecran} : la carte déborde de l'écran`);
    if (!r.croisements.length && !r.deborde) ok(`${ecran} : aucun chevauchement, aucun débordement`);
  }

  /* 3 — décors : le ratio doit être respecté (cover, jamais 100% 100%) */
  const decors = await page.evaluate(async (univers) => {
    const mauvais = [];
    for (const u of univers) {
      state.mode = 'solo'; state.solo = newRun(6, 'T', false); state._universe = u;
      const c = buildChallenge('riddle', state.solo, 2);
      applyThemedMeta(c, u); launchChallenge(c);
      await new Promise((r) => setTimeout(r, 200));
      const cs = getComputedStyle(document.getElementById('roomLayer'), '::before');
      if (!/cover|contain/.test(cs.backgroundSize)) mauvais.push(u + ' (' + cs.backgroundSize + ')');
    }
    return mauvais;
  }, UNIVERS);
  if (decors.length) ko('décors déformés : ' + decors.join(', '));
  else ok('les 10 décors gardent leurs proportions');

  /* 4 — réactivité : peu d'écritures DOM quand rien ne se passe */
  const mutations = await page.evaluate(() => new Promise((res) => {
    let n = 0;
    const o = new MutationObserver((m) => { n += m.length; });
    o.observe(document.body, { childList: true, subtree: true, attributes: true, characterData: true });
    setTimeout(() => { o.disconnect(); res(n); }, 3000);
  }));
  const parSeconde = Math.round(mutations / 3);
  /* ~15/s proviennent de l'animation de marche du Gardien (voulue).
     Au-dela de 60/s, c'est le signe d'une boucle qui reecrit inutilement. */
  if (parSeconde > 60) ko(`réactivité : ${parSeconde} écritures DOM/s au repos (seuil 60)`);
  else ok(`réactivité : ${parSeconde} écritures DOM/s au repos`);

  /* 5 — erreurs JavaScript */
  if (erreurs.length) ko('erreurs JS : ' + [...new Set(erreurs)].join(' | '));
  else ok('aucune erreur JavaScript');

  /* 6 — jeux acceptes : creation immediate + essai jouable */
  const jeux = await page.evaluate(async () => {
    localStorage.setItem('fort-proposals-seen', JSON.stringify([{
      name: 'Salle de Controle', emoji: '🧪', decided: false,
      trials: [{ icon: '⚙️', name: 'Essai Un' }, { icon: '🔔', name: 'Essai Deux' }],
    }]));
    localStorage.setItem('fort-propositions-acceptees', '[]');
    if (typeof window.__acceptSuggestion !== 'function') return { err: 'acceptation indisponible' };
    window.__acceptSuggestion('Salle de Controle');
    for (let i = 0; i < 25; i++) {
      if (document.querySelector('#nouvelleEpreuve.ouvert')) break;
      await new Promise((r) => setTimeout(r, 120));
    }
    const w = JSON.parse(localStorage.getItem('fort-propositions-acceptees') || '[]');
    const panneau = !!document.querySelector('#nouvelleEpreuve.ouvert');
    const btn = document.querySelector('#nouvelleEpreuve .ne-essayer');
    if (btn) btn.click();
    await new Promise((r) => setTimeout(r, 1100));
    const enEssai = document.body.dataset.screen === 'epreuve'
      && !!document.getElementById('bandeauEssai');
    // un seul test : l'épreuve terminée, le Gardien ramène seul au Fort
    try { resolveChallenge(true); } catch (_) {}
    await new Promise((r) => setTimeout(r, 3600));
    const w2 = JSON.parse(localStorage.getItem('fort-propositions-acceptees') || '[]');
    return { enJeu: w.filter((x) => x.compiled).length, panneau, enEssai,
             unJeu: w2.every((x) => (x.trials || []).length === 1),
             retour: document.body.dataset.screen };
  });
  if (jeux.err) ko(jeux.err);
  else {
    if (jeux.enJeu < 1) ko('jeu accepte : pas cree immediatement');
    if (!jeux.panneau) ko('jeu accepte : panneau d\'annonce absent');
    if (!jeux.enEssai) ko('jeu accepte : l\'essai ne se lance pas');
    if (jeux.retour !== 'accueil') ko('essai : pas de retour automatique au Fort apres le test');
    if (!jeux.unJeu) ko('salle du Gardien : plus d\'un jeu propose');
    if (jeux.enJeu >= 1 && jeux.panneau && jeux.enEssai && jeux.retour === 'accueil' && jeux.unJeu)
      ok('salle du Gardien : un seul jeu, un seul essai, retour automatique');
  }

  /* 7 — anti-clignotement : fond sombre des la premiere image */
  const flash = await page.evaluate(() => ({
    fond: getComputedStyle(document.documentElement).backgroundColor,
    theme: getComputedStyle(document.documentElement).colorScheme,
  }));
  const sombre = /rgba?\(\s*(\d+)/.exec(flash.fond);
  if (!sombre || +sombre[1] > 60) ko('fond de page clair : risque de flash blanc');
  else if (flash.theme !== 'dark') ko('color-scheme non declare en sombre');
  else ok('anti-clignotement : fond sombre + theme sombre declares');

  /* 8 — les jeux forges doivent etre REELLEMENT differents entre eux */
  const meca = await page.evaluate(async () => {
    localStorage.setItem('fort-propositions-acceptees', '[]');
    const noms = ['A', 'B', 'C'];
    localStorage.setItem('fort-proposals-seen', JSON.stringify(noms.map((n) => ({
      name: 'Salle ' + n, emoji: '🧪', decided: false,
      trials: [{ icon: '⚙️', name: n + '1' }, { icon: '🔔', name: n + '2' }],
    }))));
    for (const n of noms) {
      window.__acceptSuggestion('Salle ' + n);
      await new Promise((r) => setTimeout(r, 200));
    }
    await new Promise((r) => setTimeout(r, 1700));
    const w = JSON.parse(localStorage.getItem('fort-propositions-acceptees') || '[]');
    const mechs = w.flatMap((p) => (p.trials || []).map((t) => t.mech)).filter(Boolean);
    /* et chaque mecanique inedite doit produire une interface jouable */
    const jouables = {};
    const nouvelles = ['runes', 'taquin', 'tuyaux', 'dedale', 'piliers', 'miroirs', 'tableau', 'sceaux'];
    for (const m of nouvelles) {
      localStorage.setItem('fort-propositions-acceptees', JSON.stringify([{
        date: 't', universe: 'Test', emoji: '🧪', compiled: true,
        trials: [{ icon: '⚙️', name: 'E', mech: m }],
      }]));
      state.mode = 'solo'; state.solo = newRun(1, 'T', false);
      const c = makeAtelier(state.solo, 2);
      c.difficulty = getDiffLevel(2);
      launchChallenge(c);
      await new Promise((r) => setTimeout(r, 450));
      jouables[m] = !!document.querySelector('#fgZone .fg-c, #fgZone .fg-mur, #fgZone .fg-pilier');
    }
    try { go('accueil'); } catch (_) {}
    return { total: mechs.length, distinctes: new Set(mechs).size, jouables,
             rebaptises: mechs.filter((x) => nouvelles.indexOf(x) < 0) };
  });
  if (meca.distinctes < meca.total)
    ko(`jeux forges : ${meca.distinctes} mecaniques pour ${meca.total} epreuves (doublons)`);
  else ok(`jeux forges : ${meca.total} epreuves, ${meca.distinctes} mecaniques differentes`);
  const muettes = Object.entries(meca.jouables).filter(([, v]) => !v).map(([k]) => k);
  if (muettes.length) ko('mecaniques sans interface : ' + muettes.join(', '));
  else ok('les ' + Object.keys(meca.jouables).length + ' jeux de la Forge sont jouables');
  if (meca.rebaptises.length) ko('jeux forges : anciens jeux rebaptises (' + meca.rebaptises.join(', ') + ')');
  else ok('jeux forges : uniquement des jeux inedits, aucun ancien jeu rebaptise');


  /* 9 — une epreuve ne revient jamais deux fois dans une partie (univers, duel, bonus) */
  const uni = await page.evaluate(async () => {
    localStorage.setItem('fort-propositions-acceptees', JSON.stringify([
      { universe: 'Salle U', emoji: '🧪', compiled: true, trials: [{ name: 'R', icon: 'x', mech: 'runes' }] }]));
    try { registerAcceptedProposals(); } catch (_) {}
    let doublons = 0; const exemples = [];
    for (let p = 0; p < 6; p++) {
      state.mode = 'solo'; state.solo = newRun(8, 'T', false); const run = state.solo, vus = [];
      for (let i = 0; i < 8; i++) {
        state._universe = nextUniverse(run);
        const c = genChallenge(run);
        try { launchChallenge(c); } catch (_) {}
        try { stopActiveTimer(); } catch (_) {}
        const a = c.isDuel ? c : state.activeChallenge;
        vus.push(a.kind + (a.kind === 'atelier' ? ':' + a.data.mech : ''));
        run.doneCount++;
      }
      state.bonusMode = true;
      try { launchChallenge(buildChallenge(vus[0].split(':')[0], run, 3)); } catch (_) {}
      try { stopActiveTimer(); } catch (_) {}
      vus.push(state.activeChallenge.kind + (state.activeChallenge.kind === 'atelier' ? ':' + state.activeChallenge.data.mech : ''));
      state.bonusMode = false;
      const d = vus.length - new Set(vus).size;
      if (d) { doublons += d; exemples.push(vus.join(',')); }
    }
    try { go('accueil'); } catch (_) {}
    return { doublons, exemples, rejouer: getComputedStyle(document.documentElement).getPropertyValue('--x') };
  });
  if (uni.doublons) ko('epreuves repetees dans une partie : ' + uni.exemples.slice(0, 2).join(' | '));
  else ok('chaque epreuve n\'apparait qu\'une fois par partie (univers, duel et bonus compris)');

  /* 10 — le Gardien est autonome : il batit seul une salle, avec un seul jeu inedit */
  const auto = await page.evaluate(async () => {
    localStorage.setItem('fort-propositions-acceptees', '[]');
    localStorage.removeItem('fort-forge-derniere');
    try { GuardianSpirit.suggestUniverse(true); } catch (e) { return { err: String(e) }; }
    await new Promise((r) => setTimeout(r, 900));
    const w = JSON.parse(localStorage.getItem('fort-propositions-acceptees') || '[]');
    const t = document.getElementById('gardienToast');
    return { salles: w.length, jeux: w[0] ? (w[0].trials || []).length : 0,
             demande: !!(t && t.querySelector('[data-gp-accept],[data-gp-decline]')),
             essai: !!(t && t.querySelector('[data-forge-essai]'))
               || (GuardianSpirit.journal || []).some((e) => /d.office/.test(e.msg || '')) };
  });
  if (auto.err) ko('autonomie : ' + auto.err);
  else if (auto.salles !== 1 || auto.jeux !== 1 || auto.demande || !auto.essai)
    ko('autonomie du Gardien : ' + JSON.stringify(auto));
  else ok('le Gardien batit seul sa salle (un seul jeu inedit, sans demander)');
  await page.close();
}

(async () => {
  console.log('Vérification de : ' + FICHIER);
  const options = { headless: true, args: ['--no-sandbox', '--disable-gpu'] };
  if (CHROME) options.executablePath = CHROME;
  let navigateur;
  try {
    navigateur = await puppeteer.launch(options);
  } catch (e) {
    console.error('\nImpossible de démarrer le navigateur de test.');
    console.error('Deux causes habituelles :');
    console.error('  · le navigateur n\'a pas été téléchargé  →  npx puppeteer browsers install chrome');
    console.error('  · il est installé ailleurs               →  CHROME_PATH=/chemin/vers/chrome node outils/verifier.js index.html');
    console.error('\nDétail : ' + String(e.message).split('\n')[0]);
    process.exit(2);
  }
  for (const vp of FORMATS) await controlerFormat(navigateur, vp);
  await navigateur.close();

  console.log('\n══════════════════════════════════');
  if (defauts === 0) console.log('RESULTAT : tout est conforme.');
  else console.log(`RESULTAT : ${defauts} defaut(s) a corriger.`);
  process.exit(defauts === 0 ? 0 : 1);
})();
