// Fort Énigma — partie automatique « iPad iOS 15 » (contrôle de jouabilité).
// Usage : node outils/partie-ipad.js [durée_en_secondes=900] ["user-agent"]   (nécessite Playwright + Chromium)
// Le robot lance une partie solo courte avec l'identité d'un iPad sous iOS 15 (mode allégé actif),
// appuie sur le bouton principal de chaque écran, touche les éléments de jeu, et relève :
// le parcours des écrans, tout blocage de plus de 50 s, les animations EN PAUSE hors décor, les erreurs JS.
const { chromium } = require('playwright');
const UA = process.argv[3] || 'Mozilla/5.0 (iPad; CPU OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0 Mobile/15E148 Safari/604.1';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1024, height: 653 }, userAgent: UA, hasTouch: true });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 150)));
  await p.goto('file://' + require('path').resolve(__dirname, '..', 'index.html') + '?meteo=0'); await p.waitForTimeout(5000);
  await p.evaluate(() => document.getElementById('goSolo').click()); await p.waitForTimeout(1200);
  await p.evaluate(() => { const n = document.getElementById('playerName'); if (n) { n.value = 'Testeur'; n.dispatchEvent(new Event('input')); } [...document.querySelectorAll('button')].find(b => /Courte/.test(b.textContent)).click(); });
  const vus = []; const pauses = {}; const ecrans = {}; let dernier = '', fixe = 0;
  const t0 = Date.now(), DUREE = +(process.argv[2] || 900) * 1000;
  while (Date.now() - t0 < DUREE) {
    await p.waitForTimeout(1200);
    const r = await p.evaluate(() => {
      const ecran = document.body.dataset.screen || '?';
      const vis = e => { if (!e.offsetParent && getComputedStyle(e).position !== 'fixed') return false; const r = e.getBoundingClientRect(); return r.width > 4 && r.height > 4 && getComputedStyle(e).visibility !== 'hidden' && !e.disabled && +getComputedStyle(e).opacity > .05; };
      const titre = (document.querySelector('.trial-title, .screen.active h2, h2') || {}).textContent || '';
      // animations en pause dans la zone de jeu (hors décor d'accueil)
      const p = document.getAnimations().filter(a => a.playState === 'paused' && a.effect && a.effect.target && a.effect.target.closest && !a.effect.target.closest('.pp-port,#scene,.ff-couche,#mt-meteo,#fs-deco')).map(a => (a.animationName || 'WAAPI') + '<' + String(a.effect.target.className && a.effect.target.className.baseVal !== undefined ? a.effect.target.className.baseVal : a.effect.target.className).split(' ')[0] + '>');
      // champ de saisie : on tape une réponse
      const inp = [...document.querySelectorAll('input[type=text],input[type=number],input:not([type]),textarea')].filter(vis).filter(i => i.id !== 'playerName');
      inp.forEach(i => { i.value = '1'; i.dispatchEvent(new Event('input', { bubbles: true })); });
      // éléments de jeu à toucher (cartes, cibles, cases…) : tout ce qui est cliquable dans la zone de l'épreuve
      const zone = document.body;
      const app = document.getElementById('app') || document.body;
      const pointeurs = [...app.querySelectorAll('div,span,li,svg,g')].filter(e => getComputedStyle(e).cursor === 'pointer' && !(e.parentElement && getComputedStyle(e.parentElement).cursor === 'pointer')).slice(0, 40);
      const touches = [...new Set([...zone.querySelectorAll('[data-i],[data-idx],[data-index],[data-k],[data-v],[data-choice],.choice-card,.card,.cell,.target,.tile,.seal,.slot,.choice,.option,.rune,.key,.btn,button,canvas')].concat(pointeurs))].filter(vis).filter(e => !/retour|back|home|quitter|abandon|×|✕|☰|menu|mute|🔊|🔇|aide|règle|options|fm-|gardien-spirit|guardian|pp-spr|son|musique|plein|partager|copier|legende|histoire/i.test((e.id || '') + ' ' + e.textContent + ' ' + e.className));
      let action = '';
      const fin = document.getElementById('sansCleAccueil'); if (fin && vis(fin)) { fin.click(); return { ecran: 'FIN-sans-cle', titre: '', p: [], action: 'retour accueil (aucune clé)', n: 1 }; }
      const principal = touches.filter(e => e.tagName === 'BUTTON' && /btn-gold|btn-primary|primary|continuer|valider|suivant|commencer|go|start/i.test(e.className + ' ' + e.id + ' ' + e.textContent));
      const cible = principal.length ? principal[0] : touches[Math.floor(Math.random() * touches.length)];
      if (cible) { try { cible.scrollIntoView({ block: 'center' }); } catch (e) {} cible.click(); action = (cible.id ? '#' + cible.id : cible.tagName) + ' « ' + cible.textContent.trim().slice(0, 28) + ' »'; }
      return { ecran, titre: titre.trim().slice(0, 40), p, action, n: touches.length, tier: document.documentElement.getAttribute('data-fx-tier'), cls: document.documentElement.className.match(/ios-\S+/g) };
    });
    const cle = r.ecran + ' | ' + r.titre;
    ecrans[r.ecran] = (ecrans[r.ecran] || 0) + 1;
    if (fixe === 40) vus.push('!!! BLOQUÉ 70 s sur ' + cle);
    if (cle !== dernier) { vus.push(cle + '  (' + r.n + ' éléments, ' + r.action + ')'); dernier = cle; fixe = 0; } else fixe++;
    r.p.forEach(x => pauses[x + ' @' + r.ecran] = (pauses[x + ' @' + r.ecran] || 0) + 1);
    if (/^(fin|victoire|defaite|bilan|final|game-over|gameover|epilogue|fin-partie|FIN-|salle-tresor)/i.test(r.ecran)) { vus.push('>>> écran de fin atteint : ' + r.ecran); break; }
  }
  console.log('Classes :', await p.evaluate(() => document.documentElement.className.match(/ios-\S+|perf-lite|fp-calme/g)), 'palier', await p.evaluate(() => document.documentElement.getAttribute('data-fx-tier')));
  console.log('Parcours :\n  ' + vus.join('\n  '));
  console.log('Écrans (nb de relevés) :', JSON.stringify(ecrans));
  console.log('Animations de jeu en pause :', Object.keys(pauses).length ? JSON.stringify(pauses) : 'aucune');
  console.log('Erreurs JS :', errs.length ? errs : 'aucune');
  await p.screenshot({ path: 'partie_fin.png' });
  await b.close();
})();
