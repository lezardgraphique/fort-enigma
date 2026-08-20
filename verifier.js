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
    puppeteer = require(process.env.PUPPETEER_PATH
      || '/home/claude/.npm-global/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');
  } catch (__) {
    console.error('Puppeteer est introuvable. Installez-le : npm install puppeteer');
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
const FLOTTANTS = 'footer.credits,#fortV2Menu,#journalFab,.journal-fab,'
  + '#fortDailyContract,#fortV2Hud,.gardien-toast,.clue-journal,.master-chat';

async function controlerFormat(navigateur, vp) {
  const page = await navigateur.newPage();
  const erreurs = [];
  page.on('pageerror', (e) => erreurs.push(e.message.slice(0, 90)));
  await page.setViewport({ width: vp.w, height: vp.h });
  await page.goto('file://' + FICHIER, { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 2800));

  console.log(`\n── ${vp.nom} (${vp.w}×${vp.h}) ────────────────`);

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

  /* 6 — carnet d'observation : un seul journal, compteur coherent */
  const carnet = await page.evaluate(async () => {
    try { go('accueil'); } catch (_) {}
    /* le bouton est (re)cree par un minuteur : on l'attend au lieu de
       supposer un delai fixe */
    let fab = null;
    for (let i = 0; i < 30 && !fab; i++) {
      fab = document.getElementById('journalFab');
      if (!fab) await new Promise((r) => setTimeout(r, 150));
    }
    if (!fab) return { err: 'bouton du carnet absent' };
    fab.click();
    await new Promise((r) => setTimeout(r, 500));
    const ouvert = !!document.querySelector('#carnetMarche.ouvert');
    const ancien = !!document.getElementById('clueJournal');
    const reperes = document.querySelectorAll('#carnetMarche .cm-reperes .hs').length;
    const c = document.getElementById('carnetMarche');
    if (c) c.classList.remove('ouvert');
    return { ouvert, ancien, reperes };
  });
  if (carnet.err) ko(carnet.err);
  else if (!carnet.ouvert) ko('le carnet ne s\'ouvre pas');
  else if (carnet.ancien) ko('l\'ancien journal existe encore');
  else if (carnet.reperes < 12) ko(`carnet : ${carnet.reperes} reperes au lieu de 12`);
  else ok(`carnet d'observation : ouvert, 12 reperes, ancien journal supprime`);

  /* 7 — jeux acceptes : creation immediate + essai jouable */
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
    const q = document.querySelector('#bandeauEssai .be-quitter');
    if (q) q.click();
    await new Promise((r) => setTimeout(r, 700));
    return { enJeu: w.filter((x) => x.compiled).length, panneau, enEssai,
             retour: document.body.dataset.screen };
  });
  if (jeux.err) ko(jeux.err);
  else {
    if (jeux.enJeu < 1) ko('jeu accepte : pas cree immediatement');
    if (!jeux.panneau) ko('jeu accepte : panneau d\'annonce absent');
    if (!jeux.enEssai) ko('jeu accepte : l\'essai ne se lance pas');
    if (jeux.retour !== 'accueil') ko('jeu accepte : sortie d\'essai incorrecte');
    if (jeux.enJeu >= 1 && jeux.panneau && jeux.enEssai && jeux.retour === 'accueil')
      ok('jeu accepte : cree aussitot, essai jouable, retour propre');
  }

  /* 8 — anti-clignotement : fond sombre des la premiere image */
  const flash = await page.evaluate(() => ({
    fond: getComputedStyle(document.documentElement).backgroundColor,
    theme: getComputedStyle(document.documentElement).colorScheme,
  }));
  const sombre = /rgba?\(\s*(\d+)/.exec(flash.fond);
  if (!sombre || +sombre[1] > 60) ko('fond de page clair : risque de flash blanc');
  else if (flash.theme !== 'dark') ko('color-scheme non declare en sombre');
  else ok('anti-clignotement : fond sombre + theme sombre declares');

  /* 9 — les jeux forges doivent etre REELLEMENT differents entre eux */
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
    for (const m of ['sequence', 'tri', 'pression']) {
      localStorage.setItem('fort-propositions-acceptees', JSON.stringify([{
        date: 't', universe: 'Test', emoji: '🧪', compiled: true,
        trials: [{ icon: '⚙️', name: 'E', mech: m }],
      }]));
      state.mode = 'solo'; state.solo = newRun(1, 'T', false);
      const c = makeAtelier(state.solo, 2);
      c.difficulty = getDiffLevel(2);
      launchChallenge(c);
      await new Promise((r) => setTimeout(r, 450));
      jouables[m] = m === 'sequence' ? document.querySelectorAll('.atl-seq-btn').length > 0
        : m === 'tri' ? document.querySelectorAll('.atl-tri-piece').length > 0
        : !!document.getElementById('atlCurseur');
    }
    try { go('accueil'); } catch (_) {}
    return { total: mechs.length, distinctes: new Set(mechs).size, jouables };
  });
  if (meca.distinctes < meca.total)
    ko(`jeux forges : ${meca.distinctes} mecaniques pour ${meca.total} epreuves (doublons)`);
  else ok(`jeux forges : ${meca.total} epreuves, ${meca.distinctes} mecaniques differentes`);
  const muettes = Object.entries(meca.jouables).filter(([, v]) => !v).map(([k]) => k);
  if (muettes.length) ko('mecaniques sans interface : ' + muettes.join(', '));
  else ok('les 3 mecaniques inedites sont jouables');

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

  console.log('\n═════════════════════════════════');
  if (defauts === 0) console.log('RESULTAT : tout est conforme.');
  else console.log(`RESULTAT : ${defauts} defaut(s) a corriger.`);
  process.exit(defauts === 0 ? 0 : 1);
})();
