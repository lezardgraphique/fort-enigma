"""Les mondes de Fort Énigma, tous dessinés avec l'atelier commun.
Usage : mondes.py <monde> W H sortie.svg"""
import sys, math, random
from atelier import Scene

def merlons(S, x0, x1, y, h, w, couleur, lum='#ffffff', op_lum=.15):
    x = x0
    while x < x1:
        S.rect(x, y - h, min(w, x1 - x), h + 1, couleur)
        S.rect(x, y - h, min(w, x1 - x), S.U * .004, lum, 'opacity="%.2f"' % op_lum)
        x += w * 1.8

def tour(S, cx, base, top, r, teinte, lum, flag=None):
    g = S.lin([(0, '#000', .55), (.35, '#000', .1), (.7, lum, .18), (1, '#000', .5)], 0, 0, 1, 0)
    S.rect(cx - r, top, 2 * r, base - top, teinte)
    S.appareil(cx - r, top, 2 * r, base - top, r * .55)
    S.texture((cx - r, top, 2 * r, base - top), .3)
    S.rect(cx - r, top, 2 * r, base - top, g)
    # couronne crénelée
    S.rect(cx - r * 1.12, top - S.U * .012, r * 2.24, S.U * .02, teinte)
    merlons(S, cx - r * 1.12, cx + r * 1.12, top - S.U * .012, S.U * .03, r * .3, teinte, lum, .25)
    # toit conique et fanion
    S.poly([(cx - r * 1.05, top - S.U * .04), (cx, top - r * 2.1), (cx + r * 1.05, top - S.U * .04)], S.lin([(0, '#3a2a40'), (1, '#1c1424')], 0, 0, 1, 0))
    S.poly([(cx, top - r * 2.1), (cx + r * 1.05, top - S.U * .04), (cx + r * .35, top - S.U * .04)], lum, 'opacity=".18"')
    if flag:
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1c1424" stroke-width="%.1f"/>' % (cx, top - r * 2.1, cx, top - r * 2.6, S.U * .004))
        S.path('M%.1f %.1fq%.1f %.1f %.1f %.1fq%.1f %.1f %.1f %.1fz' % (cx, top - r * 2.6, r * .4, -r * .05, r * .8, r * .1, -r * .4, r * .1, -r * .8, r * .2), flag)
    # meurtrières éclairées
    for k in range(2):
        yy = top + (base - top) * (.25 + k * .3)
        S.rect(cx - r * .07, yy, r * .14, r * .45, '#ffb347')
        S.halo(cx, yy + r * .2, r * .3, '#ff9a3c', .35, 'b2')

def pave(S, y0, y1, col1, col2, lumiere=None):
    """sol de pavés en perspective entre y0 (loin) et y1 (près)"""
    S.rect(0, y0, S.W, y1 - y0, S.lin([(0, col1), (1, col2)]))
    R = S.R; y = y0; k = 0
    while y < y1:
        t = (y - y0) / max(1, (y1 - y0))
        h = S.U * (.008 + .05 * t * t)
        w = h * 2.2
        x = -(k % 2) * w * .5
        while x < S.W:
            S.ell(x + w / 2, y + h / 2, w * .46, h * .42, R.choice(['#ffffff', '#c8b8a0', '#000000']), 'opacity="%.2f"' % R.uniform(.04, .12))
            x += w
        S.a('<line x1="0" y1="%.1f" x2="%d" y2="%.1f" stroke="#000" stroke-width="%.1f" opacity=".35"/>' % (y, S.W, y, max(1, h * .08)))
        y += h; k += 1
    S.texture((0, y0, S.W, y1 - y0), .3)
    if lumiere:
        x, r, col = lumiere
        S.ell(x, y0 + (y1 - y0) * .25, r, (y1 - y0) * .35, col, 'opacity=".28" filter="url(#b4)"')

# ============================================================== FORT
def fort(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.56 if P else .7)
    S.ciel([(0, '#1a1236'), (.35, '#3b2154'), (.62, '#8a3f63'), (.85, '#e0774f'), (1, '#f7b267')], sol - U * .05)
    S.etoiles(int(W * H / 9000), H * .3, .6)
    S.soleil(W * .72, sol - U * (.5 if P else .38), U * .05, '#ffd8a0', '#ff8a4c')
    S.nuages([(.25, .12, .3, .018, .7), (.75, .16, .28, .015, .6), (.5, .26, .45, .02, .55), (.15, .32, .25, .012, .5)], '#4a2650', '#ffb08a')
    # mer et horizon
    S.rect(0, sol - U * .07, W, U * .07, S.lin([(0, '#6a4a7a'), (1, '#2a2040')]))
    for i in range(30):
        y = sol - U * .07 + S.R.uniform(0, U * .07); x = S.R.uniform(0, W)
        S.rect(x, y, S.R.uniform(.02, .08) * W, U * .0025, '#ffcf9a', 'opacity="%.2f"' % S.R.uniform(.2, .6))
    # courtine
    mx0, mx1 = W * (.12 if P else .2), W * (.88 if P else .8)
    mtop = sol - U * (.34 if P else .3)
    S.rect(mx0, mtop, mx1 - mx0, sol - mtop, '#4a4058')
    S.appareil(mx0, mtop, mx1 - mx0, sol - mtop, U * .07)
    S.texture((mx0, mtop, mx1 - mx0, sol - mtop), .35)
    S.rect(mx0, mtop, mx1 - mx0, sol - mtop, S.lin([(0, '#ffb08a', .18), (.4, '#000', 0), (1, '#000', .45)]))
    merlons(S, mx0, mx1, mtop, U * .035, U * .045, '#4a4058', '#ffb08a', .3)
    # grande porte : arche, lumière dorée, herse levée, frise de runes
    gx, gw = W / 2, U * (.2 if P else .17); gt = sol - U * (.22 if P else .19)
    arche = 'M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (gx - gw / 2, sol, gt + gw / 2, gw / 2, gw / 2, gx + gw / 2, gt + gw / 2, sol)
    S.path(arche, S.lin([(0, '#fff3c4'), (.5, '#ffc56b'), (1, '#e07a2a')]))
    S.halo(gx, sol - gw * .4, gw * .9, '#ffb347', .5, 'b4')
    for k in range(7):
        x = gx - gw / 2 + gw * (k + .5) / 7
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a1a10" stroke-width="%.1f" opacity=".85"/>' % (x, gt, x, gt + gw * .35, U * .005))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a1a10" stroke-width="%.1f"/>' % (gx - gw / 2, gt + gw * .3, gx + gw / 2, gt + gw * .3, U * .006))
    S.path(arche, 'none', 'stroke="#2a2232" stroke-width="%.1f"' % (U * .018))
    S.runes(gx - gw * .6, gt - U * .03, gw * 1.2, 7, U * .009, '#ffd36b')
    # tours
    tr = U * (.085 if P else .075)
    for cx in (mx0, mx1):
        tour(S, cx, sol, sol - U * (.48 if P else .42), tr, '#4f4560', '#ffb08a', '#f4d03f')
    # torches de part et d'autre de la porte
    for dx in (-1, 1):
        S.torche(gx + dx * gw * .78, sol - U * .13, U * .05)
    # cour pavée
    pave(S, sol, H, '#3a3046', '#15121c', (gx, U * .25, '#ffb347'))
    # mouettes
    for (x, y, t) in ((.3, .18, .018), (.36, .15, .012), (.68, .1, .014)):
        S.path('M%.1f %.1fq%.1f %.1f %.1f %.1fq%.1f %.1f %.1f %.1f' % (x * W - U * t, y * H, U * t * .5, -U * t * .6, U * t, 0, U * t * .5, -U * t * .6, U * t, 0), 'none', 'stroke="#1a1020" stroke-width="%.1f" stroke-linecap="round"' % (U * .003))

# ============================================================== FÊTE FORAINE
def foraine(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.6 if P else .72)
    S.ciel([(0, '#0b0820'), (.5, '#231a4a'), (.85, '#4a2a5e'), (1, '#6a3a62')], sol)
    S.etoiles(int(W * H / 2600), sol, .9)
    S.lune(W * .82, H * (.1 if P else .14), U * .045)
    S.nuages([(.3, .2, .3, .015, .5), (.7, .3, .3, .015, .4)], '#1a1438', '#8a86c8')
    # grande roue
    cx, cy, r = W * (.36 if P else .32), sol - U * (.36 if P else .3), U * (.3 if P else .26)
    S.lueur(cx, cy, r * 1.4, '#ff6f9f', .35)
    S.a('<g stroke="#2a2036" fill="none">')
    S.a('<circle cx="%.1f" cy="%.1f" r="%.1f" stroke-width="%.1f"/><circle cx="%.1f" cy="%.1f" r="%.1f" stroke-width="%.1f"/>' % (cx, cy, r, U * .008, cx, cy, r * .92, U * .004))
    for k in range(16):
        a = k * math.pi / 8
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke-width="%.1f"/>' % (cx, cy, cx + r * math.cos(a), cy + r * math.sin(a), U * .003))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke-width="%.1f"/><line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke-width="%.1f"/></g>' % (
        cx, cy, cx - r * .55, sol, U * .012, cx, cy, cx + r * .55, sol, U * .012))
    for k in range(48):
        a = k * math.pi / 24; x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        col = '#ffd36b' if k % 3 else '#ff6f9f'
        if k % 7 == 3: col = '#5a4a40'          # ampoules grillées : manège rouillé
        S.circ(x, y, U * .005, col)
        if col != '#5a4a40': S.circ(x, y, U * .012, col, 'opacity=".45" filter="url(#b1)"')
    for k in range(8):
        a = k * math.pi / 4 + .2; x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a2036" stroke-width="%.1f"/>' % (x, y, x, y + U * .02, U * .003))
        S.rect(x - U * .02, y + U * .02, U * .04, U * .03, ['#a33a4a', '#3a6a8a', '#c9a227', '#5a8a4a'][k % 4], 'rx="%.1f"' % (U * .006))
    S.circ(cx, cy, U * .015, '#c9a227')
    # chapiteau rayé
    tx, tw = W * (.72 if P else .7), U * (.36 if P else .34); tt = sol - U * .3
    S.lueur(tx, sol - U * .1, tw, '#ffb347', .45)
    n = 9
    for k in range(n):
        x0 = tx - tw / 2 + tw * k / n; x1 = x0 + tw / n
        S.poly([(tx, tt), (x0, sol - U * .13), (x1, sol - U * .13)], '#e9dcc8' if k % 2 else '#b23a52')
        S.rect(x0, sol - U * .13, tw / n + 1, U * .13, '#d8c9b2' if k % 2 else '#9a2f46')
    S.poly([(tx, tt), (tx - tw / 2, sol - U * .13), (tx, sol - U * .13)], '#000', 'opacity=".3"')
    S.texture((tx - tw / 2, tt, tw, sol - tt), .3)
    S.path('M%.1f %.1fv%.1fa%.1f %.1f 0 0 1 %.1f 0v%.1fZ' % (tx - U * .04, sol, -U * .07, U * .04, U * .04, U * .08, U * .07), S.lin([(0, '#fff0c0'), (1, '#ffa040')]))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a2036" stroke-width="%.1f"/>' % (tx, tt, tx, tt - U * .05, U * .004))
    S.path('M%.1f %.1fl%.1f %.1fl0 %.1fZ' % (tx, tt - U * .05, U * .04, U * .01, U * .02), '#e0457b')
    # guirlande
    gx0, gx1, gy = W * .02, W * .98, sol - U * .2
    d = 'M%.1f %.1fQ%.1f %.1f %.1f %.1f' % (gx0, gy, W / 2, gy + U * .1, gx1, gy - U * .02)
    S.path(d, 'none', 'stroke="#1a1420" stroke-width="%.1f"' % (U * .002))
    for k in range(26):
        t = k / 25; x = (1 - t) ** 2 * gx0 + 2 * (1 - t) * t * W / 2 + t * t * gx1; y = (1 - t) ** 2 * gy + 2 * (1 - t) * t * (gy + U * .1) + t * t * (gy - U * .02)
        col = ['#ffd36b', '#ff6f9f', '#7fd6ea'][k % 3]
        S.circ(x, y + U * .008, U * .006, col); S.circ(x, y + U * .008, U * .016, col, 'opacity=".35" filter="url(#b1)"')
    # stands
    for (x, c) in ((.08, '#3a6a8a'), (.9, '#5a8a4a')):
        sx, sw = x * W, U * .14
        S.rect(sx - sw / 2, sol - U * .1, sw, U * .1, '#2a2036')
        for k in range(6):
            S.path('M%.1f %.1fh%.1fv%.1fa%.1f %.1f 0 0 1 %.1f 0Z' % (sx - sw / 2 + sw * k / 6, sol - U * .14, sw / 6, U * .03, sw / 12, sw / 12, -sw / 6), c if k % 2 else '#e9dcc8')
        S.rect(sx - sw * .4, sol - U * .09, sw * .8, U * .04, '#ffcf7a', 'opacity=".7"')
    # sol de terre battue + tickets éparpillés
    S.rect(0, sol, W, H - sol, S.lin([(0, '#3a2a3a'), (1, '#120c16')]))
    S.texture((0, sol, W, H - sol), .35)
    S.ell(W * .5, sol + U * .05, W * .5, U * .06, '#ffb347', 'opacity=".18" filter="url(#b4)"')
    for _ in range(40):
        x, y = S.R.uniform(0, W), S.R.uniform(sol + U * .01, H)
        t = U * (.006 + .02 * (y - sol) / (H - sol))
        S.a('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".75" transform="rotate(%d %.1f %.1f)"/>' % (x, y, t * 1.8, t, S.R.choice(['#e9dcc8', '#e0457b', '#f4d03f']), S.R.randint(-40, 40), x, y))

# ============================================================== ATELIER À VAPEUR
def engrenage(S, cx, cy, r, dents, col, rot=0):
    pts = []
    for k in range(dents * 4):
        a = rot + k * math.pi * 2 / (dents * 4)
        rr = r * (1.0 if (k % 4) in (1, 2) else .86)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    S.poly(pts, col)
    S.circ(cx, cy, r * .72, '#000', 'opacity=".25"')
    for k in range(6):
        a = rot + k * math.pi / 3
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"/>' % (cx, cy, cx + r * .7 * math.cos(a), cy + r * .7 * math.sin(a), col, r * .12))
    S.circ(cx, cy, r * .74, 'none', 'stroke="%s" stroke-width="%.1f"' % (col, r * .1))
    S.circ(cx, cy, r * .16, col)
    S.circ(cx, cy, r * .06, '#1a1008')
    S.circ(cx, cy, r, S.rad([(0, '#fff', 0), (.75, '#fff', 0), (1, '#fff3c4', .25)], .35, .3, .7))

def steampunk(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.62 if P else .74)
    # mur de briques sombre
    S.rect(0, 0, W, H, S.lin([(0, '#1c120c'), (.6, '#2e1d12'), (1, '#140c08')]))
    S.appareil(0, 0, W, sol, U * .09, '#0a0604', .7, ('#8a4a2a', '#3a1e10', '#6a3a20', '#4a2614'))
    S.texture((0, 0, W, sol), .4)
    # grands engrenages
    for (x, y, r, d, c) in ((.22, .2, .17, 14, '#b88a3c'), (.5, .12, .09, 10, '#8a6a30'), (.78, .26, .14, 12, '#c99a4c'), (.42, .34, .07, 8, '#9a7438')):
        engrenage(S, x * W, y * H * (1 if P else 1.25), r * U * (1.25 if P else 1), d, c, S.R.uniform(0, 1))
    # tuyaux de cuivre
    for (y, ep) in ((.42, .03), (.47, .02)):
        yy = y * H * (1 if P else 1.15)
        S.rect(0, yy, W, U * ep, S.lin([(0, '#f2c27a'), (.4, '#b8703a'), (1, '#4a2410')]))
        for k in range(6):
            S.rect(W * (k + .5) / 6 - U * .01, yy - U * .006, U * .02, U * ep + U * .012, '#7a4a20')
    S.rect(W * .88, 0, U * .035, sol, S.lin([(0, '#4a2410'), (.4, '#f2c27a'), (1, '#4a2410')], 0, 0, 1, 0))
    # four à charbon au centre
    fx, fw = W / 2, U * (.3 if P else .26); ft = sol - U * .3
    S.rect(fx - fw / 2, ft, fw, sol - ft, S.lin([(0, '#3a2a20'), (1, '#1a120c')]))
    S.texture((fx - fw / 2, ft, fw, sol - ft), .4)
    S.path('M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (fx - fw * .3, sol - U * .04, ft + fw * .38, fw * .3, fw * .3, fx + fw * .3, ft + fw * .38, sol - U * .04), S.lin([(0, '#ffe08a'), (.5, '#ff8a2a'), (1, '#c0400a')]))
    S.lueur(fx, sol - U * .1, U * .45, '#ff8a2a', 1.0)
    for k in range(5):
        S.flamme(fx - fw * .2 + fw * .1 * k, sol - U * .045, U * S.R.uniform(.05, .08))
    S.rect(fx - fw * .55, ft - U * .03, fw * 1.1, U * .035, '#5a3a20')
    S.rect(fx - U * .03, 0, U * .06, ft - U * .03, S.lin([(0, '#2a1a10'), (.5, '#5a3a20'), (1, '#2a1a10')], 0, 0, 1, 0))
    # manomètres
    for (x, y) in ((.12, .5), (.86, .48)):
        gx, gy, gr = x * W, y * H * (1 if P else 1.1), U * .045
        S.circ(gx, gy, gr, '#b88a3c'); S.circ(gx, gy, gr * .82, '#f4ead2')
        for k in range(9):
            a = math.pi * (.75 + k * .1875)
            S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a1a10" stroke-width="%.1f"/>' % (gx + gr * .62 * math.cos(a), gy + gr * .62 * math.sin(a), gx + gr * .75 * math.cos(a), gy + gr * .75 * math.sin(a), U * .002))
        a = math.pi * S.R.uniform(.9, 1.9)
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#a02a1a" stroke-width="%.1f" stroke-linecap="round"/>' % (gx, gy, gx + gr * .6 * math.cos(a), gy + gr * .6 * math.sin(a), U * .004))
        S.circ(gx - gr * .3, gy - gr * .35, gr * .3, '#fff', 'opacity=".35" filter="url(#b1)"')
    # vapeur
    for k in range(9):
        x = W * S.R.uniform(.05, .95); y = H * S.R.uniform(.05, .45)
        S.ell(x, y, U * S.R.uniform(.08, .18), U * S.R.uniform(.03, .06), '#f4e6d0', 'opacity="%.2f" filter="url(#b3)"' % S.R.uniform(.08, .2))
    # établi et sol
    S.rect(0, sol, W, H - sol, S.lin([(0, '#3a2414'), (1, '#120a06')]))
    S.texture((0, sol, W, H - sol), .4)
    for k in range(int(W / (U * .12)) + 1):
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#0a0604" stroke-width="%.1f" opacity=".6"/>' % (k * U * .12, sol, k * U * .12 + (k * U * .12 - W / 2) * .6, H, U * .002))
    # étincelles
    for _ in range(26):
        x, y = fx + S.R.gauss(0, U * .12), sol - U * S.R.uniform(.05, .35)
        S.circ(x, y, U * .0025, '#ffd36b'); S.circ(x, y, U * .008, '#ff9a3c', 'opacity=".4" filter="url(#b1)"')

# ============================================================== SALLE NORDIQUE GELÉE
def nordique(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.6 if P else .74)
    S.rect(0, 0, W, H, S.lin([(0, '#04121e'), (.5, '#0b2a40'), (1, '#06182a')]))
    # fond de la grotte : passage lumineux
    S.lueur(W / 2, sol - U * .2, U * .55, '#9fe8ff', 1.0)
    S.ell(W / 2, sol - U * .18, U * .14, U * .3, S.lin([(0, '#e8fbff'), (1, '#6fc3d6')]), 'opacity=".85" filter="url(#b2)"')
    # cascade gelée
    for k in range(9):
        x = W / 2 + (k - 4) * U * .02
        S.rect(x - U * .006, sol - U * .5, U * .012, U * .48, '#e8fbff', 'opacity="%.2f" filter="url(#b1)"' % S.R.uniform(.25, .6))
    # voûte de glace : trois parois percées d'une arche, de la plus lointaine à la plus proche
    for (k, c1, c2, ow, oh) in ((0, '#3a8ab0', '#123a56', .2, .42), (1, '#2a6a90', '#0c2a40', .3, .5), (2, '#1a4a6a', '#061a2a', .42, .6)):
        ow, oh = U * ow * (1 if P else 1.4), U * oh
        d = 'M0 0H%d V%d H0Z ' % (W, H)
        d += 'M%.1f %.1f' % (W / 2 - ow, sol + U * .02)
        pts = []
        for j in range(25):
            a = math.pi * j / 24
            jit = 1 + S.R.uniform(-.06, .06)
            pts.append((W / 2 - ow * math.cos(a) * jit, sol - U * .02 - oh * math.sin(a) * jit))
        d += ''.join('L%.1f %.1f' % q for q in pts) + 'L%.1f %.1fZ' % (W / 2 + ow, sol + U * .02)
        S.path(d, S.lin([(0, c1), (1, c2)], 0, 0, 0, 1), 'fill-rule="evenodd"')
        S.a('<path d="%s" fill="#000" opacity=".2" filter="url(#texture)" fill-rule="evenodd"/>' % d)
        S.a('<polyline points="%s" fill="none" stroke="#dff8ff" stroke-width="%.1f" opacity=".5"/>' % (' '.join('%.1f,%.1f' % q for q in pts), U * .004))
        for _ in range(10):
            j = S.R.randint(2, 22); x, y = pts[j]
            S.poly([(x - U * .012, y), (x + U * .012, y), (x, y + U * S.R.uniform(.04, .1))], '#cff4ff', 'opacity=".7"')
    # stalactites de glace
    for _ in range(46):
        x = S.R.uniform(0, W); l = U * S.R.uniform(.04, .22); w = U * S.R.uniform(.01, .03)
        y0 = U * S.R.uniform(-.01, .06) + (abs(x - W / 2) / (W / 2)) ** 2 * U * .05
        S.poly([(x - w, y0), (x + w, y0), (x + w * .1, y0 + l)], S.lin([(0, '#dff8ff', .9), (1, '#6fc3d6', .5)]))
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#fff" stroke-width="%.1f" opacity=".6"/>' % (x - w * .5, y0, x - w * .05, y0 + l * .8, U * .0015))
    # pierres runiques et braseros bleus
    for dx in (-1, 1):
        px = W / 2 + dx * U * (.28 if P else .36); pt = sol - U * .22
        S.path('M%.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fZ' % (px - U * .05, sol, px - U * .045, pt + U * .03, px, pt - U * .02, px + U * .045, pt + U * .03, px + U * .05, sol), S.lin([(0, '#4a5a6a'), (1, '#1a2430')]))
        S.texture('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (px - U * .05, sol, px - U * .045, pt, px + U * .045, pt, px + U * .05, sol), .35)
        for k in range(4):
            S.runes(px - U * .02, pt + U * (.05 + k * .04), U * .04, 1, U * .012, '#7fd6ea')
        bx = px + dx * U * .1
        S.poly([(bx - U * .03, sol - U * .07), (bx + U * .03, sol - U * .07), (bx + U * .015, sol - U * .04), (bx - U * .015, sol - U * .04)], '#2a3440')
        S.rect(bx - U * .006, sol - U * .04, U * .012, U * .04, '#2a3440')
        S.flamme(bx, sol - U * .07, U * .07, '#e8fbff', '#3fb8e0')
    # sol gelé, reflets
    S.rect(0, sol, W, H - sol, S.lin([(0, '#3a7a9a'), (.2, '#123a56'), (1, '#04121e')]))
    S.ell(W / 2, sol + U * .04, U * .25, U * .05, '#bfefff', 'opacity=".35" filter="url(#b3)"')
    S.texture((0, sol, W, H - sol), .25)
    for _ in range(30):
        x, y = S.R.uniform(0, W), S.R.uniform(sol, H)
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#bfefff" stroke-width="%.1f" opacity=".2"/>' % (x, y, x + S.R.uniform(-1, 1) * U * .08, y + S.R.uniform(0, 1) * U * .02, U * .0015))
    # cristaux scintillants et brume
    S.brume(sol - U * .12, U * .2, '#bfefff', .3)
    S.lucioles(22, 0, W, U * .1, sol, '#bfefff')

# ============================================================== CRIQUE DES PIRATES
def galion(S, x, y, t, col='#120e18'):
    S.path('M%.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fZ' % (x - t, y - t * .25, x + t * .9, y - t * .3, x + t * .7, y + t * .15, x, y + t * .12, x - t * .8, y + t * .05), col)
    for (dx, h) in ((-.45, 1.1), (.05, 1.35), (.5, .95)):
        mx = x + dx * t
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"/>' % (mx, y - t * .25, mx, y - t * .25 - h * t, col, t * .025))
        for k in range(3):
            sy = y - t * .25 - h * t * (.25 + k * .28); sw = t * (.32 - k * .06)
            S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (mx - sw, sy, mx, sy + t * .05, mx + sw, sy, mx + sw * .9, sy + h * t * .2, mx, sy + h * t * .25, mx - sw * .9, sy + h * t * .2), '#c8c0a8', 'opacity=".55"')
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"/>' % (x + t * .9, y - t * .3, x + t * 1.4, y - t * .55, col, t * .02))
    for k in range(4):
        S.circ(x - t * .5 + k * t * .3, y - t * .12, t * .025, '#ffcf7a')

def pirate(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    hz = H * (.4 if P else .5); sol = H * (.6 if P else .74)
    S.ciel([(0, '#050a18'), (.5, '#0e2238'), (.9, '#1e4258'), (1, '#2a5468')], hz)
    S.etoiles(int(W * H / 3000), hz, .9)
    mx, my = W * .7, H * (.12 if P else .16)
    S.lune(mx, my, U * .05)
    S.nuages([(.35, .14, .35, .016, .55), (.8, .24, .3, .014, .45), (.2, .3, .3, .014, .4)], '#0e1a2c', '#9ab8d0')
    # mer
    S.rect(0, hz, W, sol - hz, S.lin([(0, '#1e4a5e'), (1, '#0a1e2a')]))
    S.a('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="#e8f4ff" opacity=".22" filter="url(#b2)"/>' % (mx - U * .02, hz, mx + U * .02, hz, mx + U * .2, sol, mx - U * .2, sol))
    for _ in range(140):
        y = S.R.uniform(hz, sol); t = (y - hz) / (sol - hz)
        x = S.R.gauss(mx, U * (.04 + .25 * t)) if S.R.random() < .6 else S.R.uniform(0, W)
        S.rect(x, y, U * S.R.uniform(.01, .05) * (.3 + t), U * .002 * (1 + t * 2), '#d8ecff', 'opacity="%.2f"' % S.R.uniform(.25, .8))
    # île lointaine et galion
    S.relief(S.crete(hz, U * .03, 41, 3), '#14283a', '#0a1824', None, 0, hz + U * .01)
    galion(S, W * (.42 if P else .38), hz + U * .02, U * (.16 if P else .14))
    # falaise à gauche
    d = 'M0 %.1fL0 %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fZ' % (sol + U * .05, H * .08, W * .12, H * .1, W * .16, hz - U * .1, W * .2, hz + U * .05, W * .3, sol, W * .3, sol + U * .05)
    S.path(d, S.lin([(0, '#2a3440'), (1, '#0a1018')], 0, 0, 1, 0)); S.texture(d, .45)
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1f' % (W * .12, H * .1, W * .16, hz - U * .1, W * .2, hz + U * .05), 'none', 'stroke="#9ab8d0" stroke-width="%.1f" opacity=".35"' % (U * .003))
    # palmiers à droite
    for (x, h, a) in ((.86, .3, -8), (.94, .24, 6)):
        bx, by = x * W, sol
        S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1f' % (bx, by, bx - U * .04, by - h * U * .5, bx - U * .02 + a * U * .002, by - h * U), 'none', 'stroke="#0a1018" stroke-width="%.1f" stroke-linecap="round"' % (U * .014))
        tx, ty = bx - U * .02 + a * U * .002, by - h * U
        for k in range(7):
            ang = math.pi * (1.05 + k * .16)
            ex, ey = tx + math.cos(ang) * U * .12, ty - math.sin(ang) * U * .06 + U * .05
            S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (tx, ty, (tx + ex) / 2, ty - U * .04, ex, ey, (tx + ex) / 2, ty - U * .01, tx, ty), '#0a1018')
    # vagues sur la plage
    for k in range(3):
        y = sol - U * (.02 - k * .012)
        S.path('M0 %.1f' % y + ''.join('Q%.1f %.1f %.1f %.1f' % (x + U * .05, y - U * .012, x + U * .1, y) for x in [i * U * .1 for i in range(int(W / (U * .1)) + 2)]), 'none', 'stroke="#e8f4ff" stroke-width="%.1f" opacity="%.2f"' % (U * .004, .5 - k * .12))
    # plage
    S.rect(0, sol, W, H - sol, S.lin([(0, '#6a6a6a'), (.1, '#3a3a40'), (1, '#121218')]))
    S.texture((0, sol, W, H - sol), .35)
    # coffre au trésor, tonneaux, canon
    cx, cy, cw = W * (.3 if P else .24), sol + U * .1, U * .14
    S.lueur(cx, cy - cw * .3, cw * 2, '#ffb347', .9)
    S.rect(cx - cw / 2, cy - cw * .45, cw, cw * .45, S.lin([(0, '#7a4a20'), (1, '#3a2010')]))
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fZ' % (cx - cw / 2, cy - cw * .45, cx, cy - cw * .95, cx + cw / 2, cy - cw * .45, cx - cw / 2, cy - cw * .45), '#2a1608')
    S.ell(cx, cy - cw * .48, cw * .46, cw * .12, '#ffd36b')
    for _ in range(18):
        S.circ(cx + S.R.uniform(-.42, .42) * cw, cy - cw * .5 + S.R.uniform(-.05, .05) * cw, cw * .035, S.R.choice(['#ffe08a', '#f4c430', '#fff3c4']))
    for dx in (-.45, 0, .45):
        S.rect(cx + dx * cw - cw * .03, cy - cw * .45, cw * .06, cw * .45, '#c9a227')
    for _ in range(9):
        S.circ(cx + S.R.uniform(-1, 1) * cw, cy + S.R.uniform(0, .2) * cw, cw * .035, '#f4c430')
    for (x, y, t) in ((.62, .03, .08), (.7, .06, .1)):
        bx, by, bt = W * (x + (.08 if P else 0)), sol + U * y, U * t
        S.ell(bx, by, bt * .45, bt * .55, S.lin([(0, '#2a1608'), (.5, '#6a4020'), (1, '#2a1608')], 0, 0, 1, 0))
        for k in (-.3, .3):
            S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a1008" stroke-width="%.1f"/>' % (bx - bt * .44, by + k * bt, bx + bt * .44, by + k * bt, bt * .06))

# ============================================================== MANOIR HANTÉ
def manoir(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.62 if P else .76)
    # papier peint damassé
    S.rect(0, 0, W, sol, S.lin([(0, '#1a1024'), (1, '#2a1a32')]))
    st = U * .09
    for i in range(int(W / st) + 2):
        for j in range(int(sol / st) + 2):
            x, y = i * st + (j % 2) * st / 2, j * st
            S.path('M%.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fZ' % (x, y - st * .3, x + st * .25, y - st * .1, x + st * .2, y + st * .2, x, y + st * .3, x - st * .2, y + st * .2, x - st * .25, y - st * .1, x, y - st * .3), '#3a2848', 'opacity=".55"')
    S.texture((0, 0, W, sol), .4)
    # fenêtre et rayon de lune
    wx, ww = W * (.78 if P else .8), U * .2; wt, wb = H * .08, sol - U * .05
    S.path('M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (wx - ww / 2, wb, wt + ww / 2, ww / 2, ww / 2, wx + ww / 2, wt + ww / 2, wb), S.lin([(0, '#7a8ac8'), (1, '#2a3260')]))
    S.lune(wx + ww * .15, wt + ww * .55, U * .03)
    for k in (1, 2):
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#120a18" stroke-width="%.1f"/>' % (wx - ww / 2 + ww * k / 3, wt, wx - ww / 2 + ww * k / 3, wb, U * .005))
    for k in range(1, 5):
        y = wt + ww / 2 + (wb - wt - ww / 2) * k / 5
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#120a18" stroke-width="%.1f"/>' % (wx - ww / 2, y, wx + ww / 2, y, U * .005))
    S.poly([(wx - ww / 2, wt + ww * .3), (wx + ww / 2, wt + ww * .3), (W * .3, H), (W * -.2, H)], '#c8d4ff', 'opacity=".1" filter="url(#b3)"')
    for side in (-1, 1):
        cx = wx + side * ww * .62
        S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (cx - U * .05, wt - U * .03, cx + side * U * .04, (wt + sol) / 2, cx - U * .03, sol, cx + U * .05, sol, cx + U * .07, (wt + sol) / 2, cx + U * .05, wt - U * .03), S.lin([(0, '#4a1a2a'), (.5, '#6a2a3a'), (1, '#2a0a18')], 0, 0, 1, 0))
    # fantôme près de la fenêtre
    gx, gy = wx - ww * .55, sol - U * .32
    S.path('M%.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fZ' % (
        gx, gy, gx + U * .06, gy, gx + U * .07, gy + U * .1, gx + U * .08, gy + U * .3, gx + U * .05, gy + U * .27, gx + U * .03, gy + U * .31,
        gx, gy + U * .27, gx - U * .03, gy + U * .31, gx - U * .05, gy + U * .27, gx - U * .08, gy + U * .3, gx - U * .07, gy + U * .1, gx - U * .06, gy, gx, gy),
        '#d8e4ff', 'opacity=".35" filter="url(#b1)"')
    S.circ(gx - U * .015, gy + U * .05, U * .006, '#1a1030', 'opacity=".6"'); S.circ(gx + U * .015, gy + U * .05, U * .006, '#1a1030', 'opacity=".6"')
    # portrait aux yeux luisants
    px, py, pw, ph = W * (.3 if P else .3), H * (.1 if P else .1), U * .2, U * .26
    S.rect(px - pw / 2 - U * .02, py - U * .02, pw + U * .04, ph + U * .04, S.lin([(0, '#e0b860'), (.5, '#8a6020'), (1, '#e0b860')], 0, 0, 1, 1))
    S.rect(px - pw / 2, py, pw, ph, S.lin([(0, '#3a2a30'), (1, '#1a1018')]))
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (px - pw * .35, py + ph, px - pw * .3, py + ph * .55, px, py + ph * .55, px, py + ph * .55, px + pw * .3, py + ph * .55, px + pw * .35, py + ph), '#2a1a24')
    S.ell(px, py + ph * .38, pw * .17, ph * .2, '#5a4048')
    for dx in (-1, 1):
        S.circ(px + dx * pw * .06, py + ph * .36, U * .004, '#b9a0f0'); S.circ(px + dx * pw * .06, py + ph * .36, U * .012, '#b9a0f0', 'opacity=".6" filter="url(#b1)"')
    # cheminée et chandelier
    fx, fw = W * (.3 if P else .3), U * .3
    ft = sol - U * .22
    S.rect(fx - fw / 2, ft, fw, sol - ft, S.lin([(0, '#4a3a40'), (1, '#2a2028')])); S.texture((fx - fw / 2, ft, fw, sol - ft), .4)
    S.rect(fx - fw * .58, ft - U * .02, fw * 1.16, U * .025, '#5a4850')
    S.path('M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (fx - fw * .3, sol, ft + U * .1, fw * .3, U * .06, fx + fw * .3, ft + U * .1, sol), '#0a0608')
    for k in range(4): S.flamme(fx - fw * .15 + k * fw * .1, sol - U * .01, U * S.R.uniform(.03, .05))
    cx, cy = fx + fw * .25, ft - U * .02
    S.rect(cx - U * .006, cy - U * .09, U * .012, U * .09, '#c9a227')
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1f' % (cx - U * .05, cy - U * .1, cx, cy - U * .05, cx + U * .05, cy - U * .1, cx, cy - U * .07, cx - U * .05, cy - U * .1), 'none', 'stroke="#c9a227" stroke-width="%.1f"' % (U * .006))
    for dx in (-.05, -.025, 0, .025, .05):
        bx, by = cx + dx * U, cy - U * (.1 if dx else .12)
        S.rect(bx - U * .005, by - U * .04, U * .01, U * .04, '#f4ead2')
        S.flamme(bx, by - U * .04, U * .025)
    # fauteuil
    ax = W * (.62 if P else .58)
    S.path('M%.1f %.1fV%.1fQ%.1f %.1f %.1f %.1fV%.1fZ' % (ax - U * .07, sol, sol - U * .2, ax, sol - U * .26, ax + U * .07, sol - U * .2, sol), S.lin([(0, '#4a2a3a'), (1, '#1a0a14')]))
    S.rect(ax - U * .09, sol - U * .09, U * .18, U * .05, '#3a1a2a', 'rx="%.1f"' % (U * .015))
    # parquet
    S.rect(0, sol, W, H - sol, S.lin([(0, '#3a2418'), (1, '#0c0806')]))
    for k in range(-20, 21):
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#0a0604" stroke-width="%.1f" opacity=".6"/>' % (W / 2 + k * U * .05, sol, W / 2 + k * U * .22, H, U * .002))
    S.texture((0, sol, W, H - sol), .35)
    S.lucioles(14, 0, W, H * .05, sol, '#d8e4ff')

# ============================================================== JUNGLE DE JADE
def feuille(S, x, y, l, ang, col, larg=.35):
    ca, sa = math.cos(ang), math.sin(ang)
    ex, ey = x + ca * l, y + sa * l
    nx, ny = -sa * l * larg, ca * l * larg
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (x, y, x + ca * l * .5 + nx, y + sa * l * .5 + ny, ex, ey, x + ca * l * .5 - nx, y + sa * l * .5 - ny, x, y), col)
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#000" stroke-width="%.1f" opacity=".2"/>' % (x, y, ex, ey, l * .02))

def jungle(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.6 if P else .74)
    S.rect(0, 0, W, H, S.lin([(0, '#0a2018'), (.45, '#174a30'), (.75, '#0e3020'), (1, '#04120a')]))
    S.lueur(W * .55, H * .1, U * .7, '#c8ffb0', .7)
    # temple en ruine au fond
    tx, tw = W / 2, U * (.5 if P else .44); tt = sol - U * .38
    for k in range(4):
        w = tw * (1 - k * .18); h = U * .08
        y = sol - h * (k + 1)
        S.rect(tx - w / 2, y, w, h, S.lin([(0, '#5a7a60'), (1, '#2a4030')])); S.appareil(tx - w / 2, y, w, h, U * .06, '#0a1a10', .6, ('#7a9a70', '#2a4030', '#4a6a50'))
    S.texture((tx - tw / 2, sol - U * .32, tw, U * .32), .4)
    # tête de statue ancienne (visage stylisé)
    hx, hy, hs = tx, sol - U * .42, U * .12
    S.path('M%.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (hx - hs * .7, hy + hs, hx - hs * .75, hy - hs * .4, hx, hy - hs * 1.05, hx + hs * .75, hy - hs * .4, hx + hs * .7, hy + hs, hx, hy + hs * 1.15, hx - hs * .7, hy + hs), S.lin([(0, '#7a9a78'), (1, '#33503a')]))
    S.texture('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (hx - hs * .7, hy + hs, hx - hs * .75, hy - hs * .4, hx + hs * .75, hy - hs * .4, hx + hs * .7, hy + hs), .45)
    for dx in (-1, 1):
        S.path('M%.1f %.1fq%.1f %.1f %.1f 0' % (hx + dx * hs * .38 - hs * .16, hy, hs * .16, -hs * .1, hs * .32), 'none', 'stroke="#1a2a1e" stroke-width="%.1f" stroke-linecap="round"' % (hs * .07))
        S.circ(hx + dx * hs * .38, hy + hs * .04, hs * .05, '#46d17f'); S.circ(hx + dx * hs * .38, hy + hs * .04, hs * .15, '#46d17f', 'opacity=".5" filter="url(#b1)"')
    S.path('M%.1f %.1fv%.1fh%.1f' % (hx, hy + hs * .1, hs * .35, hs * .1), 'none', 'stroke="#1a2a1e" stroke-width="%.1f"' % (hs * .05))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a2a1e" stroke-width="%.1f" stroke-linecap="round"/>' % (hx - hs * .25, hy + hs * .7, hx + hs * .25, hy + hs * .7, hs * .06))
    S.runes(tx - tw * .35, sol - U * .05, tw * .7, 8, U * .01, '#46d17f', .8)
    # rais de lumière
    for k in range(5):
        x = W * (.25 + k * .14)
        S.poly([(x, 0), (x + U * .05, 0), (x + U * .2, sol), (x + U * .08, sol)], '#d8ffc0', 'opacity=".07" filter="url(#b2)"')
    # lianes
    for _ in range(14):
        x = S.R.uniform(0, W); l = H * S.R.uniform(.15, .5)
        S.path('M%.1f 0Q%.1f %.1f %.1f %.1f' % (x, x + S.R.uniform(-1, 1) * U * .08, l / 2, x + S.R.uniform(-1, 1) * U * .03, l), 'none', 'stroke="#0c2a18" stroke-width="%.1f"' % (U * S.R.uniform(.003, .007)))
        for k in range(6):
            feuille(S, x + S.R.uniform(-1, 1) * U * .02, l * (k + 1) / 7, U * .03, S.R.uniform(0, 6.3), '#1f6a3a')
    # feuillage en couches, du fond vers l'avant
    for (cols, n, taille, y0, y1) in ((('#123a24', '#16442a'), 60, .09, 0, .35), (('#1a5a32', '#1f6a3a'), 40, .13, .0, .3), (('#0a2a16', '#0e3a1e', '#0c301a'), 46, .2, .5, 1.0)):
        for _ in range(n):
            bord = S.R.random() < .5
            x = S.R.uniform(-.05, .25) * W if bord else S.R.uniform(.75, 1.05) * W
            if y0 >= .5: x = S.R.uniform(-.05, 1.05) * W
            y = (S.R.uniform(y0, y1) * (sol if y0 < .5 else H)) if y0 < .5 else S.R.uniform(sol - U * .05, H)
            feuille(S, x, y, U * taille * S.R.uniform(.6, 1.2), S.R.uniform(0, 6.3), S.R.choice(cols))
    S.brume(sol - U * .15, U * .25, '#b0ffd0', .22)
    S.lucioles(12, 0, W, H * .1, sol, '#d8ff9a')

# ============================================================== TEMPLE DES SABLES
def desert(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.6 if P else .72)
    S.ciel([(0, '#2a1438'), (.35, '#7a2a40'), (.62, '#d8582a'), (.82, '#f4a03c'), (1, '#ffd27a')], sol)
    S.etoiles(int(W * H / 12000), H * .2, .5)
    S.soleil(W * .5, sol - U * .08, U * .09, '#fff0c0', '#ff9a3c')
    S.nuages([(.2, .18, .3, .012, .6), (.8, .12, .25, .01, .5), (.55, .3, .4, .014, .45)], '#5a2030', '#ffc890')
    # dunes lointaines
    S.relief(S.crete(sol - U * .02, U * .05, 71, 3, .5), '#c06a3a', '#7a3a20', '#ffd27a', .4, sol + U * .02)
    # colonnade en ruine
    n = 7; x0, x1 = W * (.05 if P else .12), W * (.95 if P else .88)
    cw = (x1 - x0) / n * .45; ct = sol - U * (.36 if P else .32)
    S.rect(x0 - cw * .3, ct - U * .04, (x1 - x0) * .55, U * .045, S.lin([(0, '#8a5a3a'), (1, '#4a2a18')]))
    for k in range(n):
        cx = x0 + (x1 - x0) * (k + .5) / n
        haut = ct + (U * .12 if k in (4, 6) else 0)
        S.rect(cx - cw / 2, haut, cw, sol - haut, S.lin([(0, '#3a1e10'), (.4, '#a06a40'), (.7, '#c08050'), (1, '#4a2614')], 0, 0, 1, 0))
        S.texture((cx - cw / 2, haut, cw, sol - haut), .4)
        for j in range(4):
            S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a140a" stroke-width="%.1f" opacity=".5"/>' % (cx - cw / 2, haut + (sol - haut) * (j + 1) / 5, cx + cw / 2, haut + (sol - haut) * (j + 1) / 5, U * .002))
        S.rect(cx - cw * .65, haut - U * .02, cw * 1.3, U * .025, '#8a5a3a')
        if k % 2 == 0:
            S.runes(cx - cw * .3, haut + (sol - haut) * .4, cw * .6, 1, U * .013, '#ffd36b', .9)
    # statue de chat gardien (silhouette)
    sx, sy, ss = W * (.86 if P else .82), sol, U * (.24 if P else .22)
    S.path('M%.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fZ' % (
        sx - ss * .3, sy, sx - ss * .25, sy - ss * .55, sx - ss * .2, sy - ss * .85, sx - ss * .1, sy - ss * .9, sx - ss * .12, sy - ss * 1.08, sx, sy - ss * .95,
        sx + ss * .1, sy - ss * 1.08, sx + ss * .1, sy - ss * .85, sx + ss * .22, sy - ss * .5, sx + ss * .32, sy), S.lin([(0, '#3a1e10'), (.7, '#7a4a28'), (1, '#c08050')], 0, 0, 1, 0))
    S.texture('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (sx - ss * .3, sy, sx - ss * .2, sy - ss, sx + ss * .1, sy - ss, sx + ss * .32, sy), .4)
    S.circ(sx + ss * .03, sy - ss * .88, ss * .015, '#ffd36b')
    # sable et grains soufflés
    S.rect(0, sol, W, H - sol, S.lin([(0, '#d8904a'), (.3, '#8a4a24'), (1, '#2a140a')]))
    S.texture((0, sol, W, H - sol), .3)
    for k in range(6):
        y = sol + (H - sol) * (k + .5) / 6
        S.path('M0 %.1fQ%.1f %.1f %.1f %.1fT%.1f %.1f' % (y, W * .25, y - U * .02, W * .5, y, W, y), 'none', 'stroke="#ffd27a" stroke-width="%.1f" opacity=".18"' % (U * .003))
    for _ in range(9):
        y = S.R.uniform(sol - U * .25, sol + U * .1)
        S.ell(S.R.uniform(0, W), y, U * S.R.uniform(.2, .45), U * .015, '#ffd8a0', 'opacity="%.2f" filter="url(#b3)"' % S.R.uniform(.12, .25))
    # oriflammes déchirées
    for x in (x0 + cw, x0 + (x1 - x0) * .43):
        S.path('M%.1f %.1fl%.1f %.1fl%.1f %.1fl%.1f %.1fl%.1f %.1fZ' % (x, ct - U * .04, U * .05, U * .01, -U * .01, U * .06, U * .02, U * .05, -U * .06, -U * .015), '#a02a2a', 'opacity=".85"')


# ============================================================== ACCUEIL : le Fort et sa grande porte des mondes
PHASES = {
    'jour': dict(ciel=[(0, '#3a78c8'), (.6, '#7ab4e8'), (1, '#d8eefa')], mer=('#3a8ac0', '#1a4a78'), astre='soleil', lum='#fff4d8', ombre='#5a6a90', fen=0, nuage=('#9ab0d0', '#ffffff'), mur='#9a94a8', roc=('#7a7488', '#3a3648')),
    'soir': dict(ciel=[(0, '#2a1a4a'), (.45, '#7a3a6a'), (.8, '#e0704a'), (1, '#ffc070')], mer=('#7a4a6a', '#2a1a3a'), astre='couchant', lum='#ffb08a', ombre='#4a2a50', fen=.6, nuage=('#5a2a50', '#ffb08a'), mur='#6a5a78', roc=('#5a4a68', '#241a30')),
    'nuit': dict(ciel=[(0, '#050a1c'), (.6, '#142450'), (1, '#2a4078')], mer=('#1a3058', '#081028'), astre='lune', lum='#c8d4ff', ombre='#1a2040', fen=1, nuage=('#1a2448', '#9aa8d8'), mur='#4a4c68', roc=('#363a58', '#12142a')),
}
def accueil(S, phase):
    W, H, U, P = S.W, S.H, S.U, S.P
    c = PHASES[phase]
    U = S.U * (.66 if P else 1)          # en vertical, le Fort doit tenir au-dessus de la carte d'accueil
    hz = H * (.25 if P else .55)         # horizon marin
    S.ciel(c['ciel'], hz)
    if phase != 'jour': S.etoiles(int(W * H / (2400 if phase == 'nuit' else 9000)), hz, 1 if phase == 'nuit' else .5)
    if c['astre'] == 'soleil': S.soleil(W * .8, H * (.06 if P else .14), U * .05)
    elif c['astre'] == 'couchant': S.soleil(W * .82, hz - U * .03, U * .06, '#ffd8a0', '#ff7a3c')
    else: S.lune(W * .82, H * (.05 if P else .12), U * .04)
    S.nuages([(.2, .04 if P else .1, .3, .01, .6), (.7, .09 if P else .2, .35, .012, .5), (.45, .14 if P else .3, .4, .01, .45)], c['nuage'][0], c['nuage'][1])
    # mer
    S.rect(0, hz, W, H - hz, S.lin([(0, c['mer'][0]), (1, c['mer'][1])]))
    for _ in range(160):
        y = S.R.uniform(hz, H); t = (y - hz) / (H - hz)
        S.rect(S.R.uniform(0, W), y, U * S.R.uniform(.01, .05) * (.3 + t), U * .002 * (1 + 2 * t), c['lum'], 'opacity="%.2f"' % S.R.uniform(.1, .45))
    # promontoire rocheux
    fx = W * (.5 if P else .36); fb = hz + U * (.05 if P else .06)
    rw = U * (.62 if P else .6)
    d = 'M%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (
        fx - rw, fb + U * .05, fx - rw * .7, fb - U * .02, fx - rw * .45, fb - U * .1, fx + rw * .45, fb - U * .1, fx + rw * .7, fb - U * .02, fx + rw, fb + U * .05,
        fx + rw * 1.1, fb + U * .08, fx, fb + U * .1, fx - rw * 1.1, fb + U * .08)
    S.path(d, S.lin([(0, c['roc'][0]), (1, c['roc'][1])])); S.texture(d, .45)
    S.ell(fx, fb + U * .09, rw * 1.1, U * .02, c['lum'], 'opacity=".25" filter="url(#b2)"')
    base = fb - U * .1
    # tours et courtines
    mur = c['mur']
    tops = []
    for (dx, h, r) in ((-.42, .2, .045), (-.2, .26, .05), (.2, .26, .05), (.42, .2, .045)):
        tops.append((fx + dx * rw, base, base - h * U, r * U))
    S.rect(fx - rw * .42, base - U * .14, rw * .84, U * .14, mur); S.appareil(fx - rw * .42, base - U * .14, rw * .84, U * .14, U * .045)
    S.texture((fx - rw * .42, base - U * .14, rw * .84, U * .14), .35)
    merlons(S, fx - rw * .42, fx + rw * .42, base - U * .14, U * .018, U * .022, mur, c['lum'], .3)
    # donjon central
    S.rect(fx - U * .07, base - U * .32, U * .14, U * .32, mur); S.appareil(fx - U * .07, base - U * .32, U * .14, U * .32, U * .04)
    S.texture((fx - U * .07, base - U * .32, U * .14, U * .32), .35)
    S.rect(fx - U * .07, base - U * .32, U * .14, U * .32, S.lin([(0, '#000', .35), (.6, c['lum'], .12), (1, '#000', .4)], 0, 0, 1, 0))
    S.poly([(fx - U * .085, base - U * .32), (fx, base - U * .45), (fx + U * .085, base - U * .32)], S.lin([(0, '#3a2a48'), (1, '#1a1428')], 0, 0, 1, 0))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a1428" stroke-width="%.1f"/>' % (fx, base - U * .45, fx, base - U * .5, U * .003))
    S.path('M%.1f %.1fl%.1f %.1fl0 %.1fZ' % (fx, base - U * .5, U * .035, U * .01, U * .02), '#f4d03f')
    for (x, b, t, r) in tops:
        tour(S, x, b, t, r, mur, c['lum'], '#f4d03f')
    # la grande porte des mondes : arche runique lumineuse
    gw = U * .085; gt = base - U * .1
    S.halo(fx, base - gw * .5, gw * 1.6, '#ffd36b', .55 if phase != 'jour' else .35, 'b4')
    arche = 'M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (fx - gw / 2, base, gt + gw / 2, gw / 2, gw / 2, fx + gw / 2, gt + gw / 2, base)
    S.path(arche, S.lin([(0, '#fffbe0'), (.4, '#ffe08a'), (.75, '#b9a0f0'), (1, '#7fd6ea')]))
    for k in range(9):
        a = math.pi * (k + .5) / 9; rr = gw * .62
        S.circ(fx - rr * math.cos(a), gt + gw / 2 - rr * math.sin(a), U * .004, '#ffd36b')
    S.path(arche, 'none', 'stroke="#2a2232" stroke-width="%.1f"' % (U * .008))
    S.runes(fx - gw * .7, gt - U * .02, gw * 1.4, 5, U * .006, '#ffd36b')
    # étincelles qui s'échappent de la porte
    for _ in range(18):
        x, y = fx + S.R.gauss(0, gw * .8), base - S.R.uniform(0, U * .2)
        S.circ(x, y, U * .0025, S.R.choice(['#ffd36b', '#b9a0f0', '#7fd6ea', '#ff6f9f'])); S.circ(x, y, U * .008, '#ffe08a', 'opacity=".3" filter="url(#b1)"')
    # fenêtres allumées le soir et la nuit
    if c['fen']:
        for (x, b, t, r) in tops:
            for k in range(2):
                S.rect(x - r * .12, t + (b - t) * (.3 + k * .3), r * .24, r * .4, '#ffc46b', 'opacity="%.2f"' % c['fen'])
    # chemin qui monte vers la porte
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fT%.1f %.1f' % (fx - gw * .3, base, fx - rw * .3, fb, fx + rw * .2, fb + U * .04, fx + rw * .6, fb + U * .1), 'none', 'stroke="#d8c8a8" stroke-width="%.1f" opacity=".35"' % (U * .012))
    # port : maisons et bateaux
    for side in (-1, 1):
        for k in range(7):
            hx = fx + side * (rw * 1.05 + k * U * .06); hw = U * S.R.uniform(.045, .06); hh = U * S.R.uniform(.05, .09)
            if hx < -hw or hx > W + hw: continue
            hy = fb + U * .07
            S.rect(hx - hw / 2, hy - hh, hw, hh, S.R.choice(['#c8a888', '#a87858', '#d8c0a0', '#8a6a5a']) if phase == 'jour' else S.R.choice(['#5a4a5a', '#4a3a4a', '#6a5a68']))
            S.poly([(hx - hw * .6, hy - hh), (hx, hy - hh - hw * .5), (hx + hw * .6, hy - hh)], S.R.choice(['#a03a2a', '#7a3a2a', '#5a3a4a']))
            for j in range(2):
                S.rect(hx - hw * .3 + j * hw * .35, hy - hh * .7, hw * .22, hh * .22, '#ffc46b' if c['fen'] and S.R.random() < .7 else '#2a3040', 'opacity=".95"')
    for (x, t) in ((.12, .05), (.88, .06), (.72, .04)):
        bx, by = x * W, fb + U * .14
        S.path('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (bx - U * t, by, bx + U * t, by, bx + U * t * .7, by + U * t * .35, bx - U * t * .7, by + U * t * .35), '#3a2418')
        S.poly([(bx, by - U * t * 1.6), (bx, by - U * t * .1), (bx + U * t * .9, by - U * t * .3)], '#e8dcc8' if phase == 'jour' else '#b8a8a0')
    if phase == 'nuit': S.lucioles(10, 0, W, H * .02, hz, '#ffe8a0')

# ============================================================== INTRO : le hall des portes
PORTES = [('#f4d03f', 'tour'), ('#ff6f9f', 'roue'), ('#e0a050', 'engrenage'), ('#7fd6ea', 'flocon'), ('#4fc49a', 'ancre'),
          ('#b9a0f0', 'masque'), ('#46d17f', 'feuille'), ('#f39c3c', 'soleil'), ('#ff2ec4', 'eclair'), ('#9aa6ff', 'lune')]
def embleme(S, x, y, t, kind, col):
    st = 'stroke="%s" stroke-width="%.1f" fill="none" stroke-linecap="round" stroke-linejoin="round"' % (col, t * .12)
    if kind == 'tour': S.path('M%.1f %.1fv%.1fh%.1fv%.1fh%.1fv%.1fh%.1fv%.1fh%.1fv%.1f' % (x - t * .4, y + t * .5, -t * .8, t * .2, t * .2, t * .2, -t * .2, t * .2, t * .2, t * .2, -t * .2) + 'v%.1fZ' % (t * .8), 'none', st)
    elif kind == 'roue':
        S.circ(x, y, t * .45, 'none', st)
        for k in range(4): a = k * math.pi / 4; S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" %s/>' % (x - t * .45 * math.cos(a), y - t * .45 * math.sin(a), x + t * .45 * math.cos(a), y + t * .45 * math.sin(a), st))
    elif kind == 'engrenage':
        S.circ(x, y, t * .3, 'none', st)
        for k in range(8): a = k * math.pi / 4; S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" %s/>' % (x + t * .3 * math.cos(a), y + t * .3 * math.sin(a), x + t * .48 * math.cos(a), y + t * .48 * math.sin(a), st))
    elif kind == 'flocon':
        for k in range(3): a = k * math.pi / 3; S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" %s/>' % (x - t * .5 * math.cos(a), y - t * .5 * math.sin(a), x + t * .5 * math.cos(a), y + t * .5 * math.sin(a), st))
    elif kind == 'ancre': S.path('M%.1f %.1fv%.1fM%.1f %.1fh%.1fM%.1f %.1fq0 %.1f %.1f %.1fq%.1f 0 %.1f %.1f' % (x, y - t * .5, t * .95, x - t * .22, y - t * .25, t * .44, x - t * .4, y + t * .15, t * .3, t * .4, t * .3, t * .4, t * .4, -t * .3), "none", st)
    elif kind == 'masque': S.path('M%.1f %.1fq%.1f %.1f %.1f 0q0 %.1f %.1f %.1fq%.1f 0 %.1f %.1fZ' % (x - t * .45, y - t * .2, t * .45, -t * .15, t * .9, t * .5, -t * .45, t * .6, -t * .45, -t * .45, -t * .6), 'none', st)
    elif kind == 'feuille': S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fM%.1f %.1fL%.1f %.1f' % (x - t * .4, y + t * .4, x - t * .4, y - t * .4, x + t * .4, y - t * .4, x + t * .4, y + t * .4, x - t * .4, y + t * .4, x - t * .4, y + t * .4, x + t * .2, y - t * .2), 'none', st)
    elif kind == 'soleil':
        S.circ(x, y, t * .22, 'none', st)
        for k in range(8): a = k * math.pi / 4; S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" %s/>' % (x + t * .32 * math.cos(a), y + t * .32 * math.sin(a), x + t * .5 * math.cos(a), y + t * .5 * math.sin(a), st))
    elif kind == 'eclair': S.path('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1f' % (x + t * .15, y - t * .5, x - t * .2, y + t * .05, x + t * .15, y + t * .05, x - t * .15, y + t * .5), 'none', st)
    elif kind == 'lune': S.path('M%.1f %.1fA%.1f %.1f 0 1 0 %.1f %.1fA%.1f %.1f 0 1 1 %.1f %.1fZ' % (x + t * .1, y - t * .45, t * .45, t * .45, x + t * .1, y + t * .45, t * .32, t * .32, x + t * .1, y - t * .45), 'none', st)

def intro(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    vx, vy = W / 2, H * (.3 if P else .46)
    f = W * (.55 if P else .42)
    XL, XR, EYE, HV = -2.2, 2.2, 1.6, 4.2           # largeur du hall, hauteur des yeux et de la voûte
    def Pj(X, Y, Z): return (vx + f * X / Z, vy - f * (Y - EYE) / Z)
    pts = lambda L: ' '.join('%.1f,%.1f' % q for q in L)
    S.rect(0, 0, W, H, '#0a0a14')
    ZF = 11
    # fond : la grande porte entrouverte sur le ciel des mondes
    a0, a1 = Pj(-1.5, 0, ZF), Pj(1.5, 3.5, ZF)
    dw, dh = a1[0] - a0[0], a0[1] - a1[1]
    d_ouv = 'M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (a0[0], a0[1], a1[1] + dw / 2, dw / 2, dw / 2, a1[0], a1[1] + dw / 2, a0[1])
    S.path(d_ouv, S.lin([(0, '#1a1050'), (.5, '#3a2a80'), (1, '#6a3a8a')]))
    S.a('<clipPath id="clipPorte"><path d="%s"/></clipPath><g clip-path="url(#clipPorte)">' % d_ouv)
    for _ in range(160):
        S.circ(S.R.uniform(a0[0], a1[0]), S.R.uniform(a1[1], a0[1]), S.R.uniform(.4, 1.4) * U / 1100, '#fff', 'opacity="%.2f"' % S.R.uniform(.4, 1))
    S.ell(vx - dw * .1, a1[1] + dh * .5, dw * .5, dh * .25, '#ff6fd0', 'opacity=".35" filter="url(#b3)" transform="rotate(-35 %.1f %.1f)"' % (vx, a1[1] + dh * .5))
    S.ell(vx + dw * .1, a1[1] + dh * .4, dw * .35, dh * .15, '#7fd6ea', 'opacity=".3" filter="url(#b3)"')
    mx, my, mr = vx + dw * .15, a1[1] + dh * .45, dw * .16
    S.circ(mx, my, mr * 2.4, S.rad([(0, '#e8ecff', .5), (1, '#e8ecff', 0)]))
    S.path('M%.1f %.1fA%.1f %.1f 0 1 0 %.1f %.1fA%.1f %.1f 0 1 1 %.1f %.1fZ' % (mx, my - mr, mr, mr, mx, my + mr, mr * .78, mr * .78, mx, my - mr), '#f4f1e3')
    S.a('</g>')
    # battants de la porte entrouverts
    for side in (-1, 1):
        bx = a0[0] if side < 0 else a1[0]
        S.poly([(bx, a0[1]), (bx, a1[1] + dw * .3), (bx - side * dw * .22, a1[1] + dw * .2), (bx - side * dw * .22, a0[1] + dh * .03)], S.lin([(0, '#5a3a20'), (1, '#2a1a10')], 0, 0, 1, 0))
    S.path(d_ouv, 'none', 'stroke="#c8d4ff" stroke-width="%.1f" opacity=".7" filter="url(#b1)"' % (U * .004))
    S.halo(vx, a0[1] - dh * .4, dw * .9, '#9aa6ff', .35, 'b4')
    # mur du fond autour de la porte
    fb = [Pj(XL, 0, ZF), Pj(XL, HV, ZF), Pj(XR, HV, ZF), Pj(XR, 0, ZF)]
    S.a('<path d="M%s Z %s" fill="#2a2838" fill-rule="evenodd"/>' % ('M' + ' L'.join('%.1f %.1f' % q for q in fb), d_ouv))
    S.runes(a0[0] - dw * .1, a1[1] - U * .015, dw * 1.2, 7, U * .006, '#ffd36b')
    # murs latéraux, voûte et sol (perspective)
    for side, X in ((-1, XL), (1, XR)):
        S.poly([Pj(X, 0, 1.0), Pj(X, HV, 1.0), Pj(X, HV, ZF), Pj(X, 0, ZF)], S.lin([(0, '#1a1824'), (1, '#2e2c3e')], 0 if side < 0 else 1, 0, 1 if side < 0 else 0, 0))
    S.poly([Pj(XL, 0, 1.0), Pj(XR, 0, 1.0), Pj(XR, 0, ZF), Pj(XL, 0, ZF)], S.lin([(0, '#3a3448'), (1, '#121018')]))
    # voûte en berceau : courbes successives + ciel de constellations peint
    vault = []
    for k in range(0, 41):
        a = math.pi * k / 40
        vault.append((2.2 * math.cos(a), HV + 1.6 * math.sin(a)))
    for z in (1.0, ZF):
        pass
    contour = [Pj(x, y, 1.0) for x, y in vault] + [Pj(x, y, ZF) for x, y in reversed(vault)]
    S.poly(contour, '#151a34')
    for _ in range(200):
        x, y = S.R.uniform(0, W), S.R.uniform(0, min(Pj(0, HV, ZF)[1], H))
        S.circ(x, y, S.R.uniform(.5, 1.5) * U / 1100, '#dfe6ff', 'opacity="%.2f"' % S.R.uniform(.3, .9))
    for _ in range(7):   # constellations
        cx, cy = S.R.uniform(.1, .9) * W, S.R.uniform(.02, .9) * Pj(0, HV, 3)[1]
        q = [(cx + S.R.uniform(-1, 1) * U * .08, cy + S.R.uniform(-1, 1) * U * .05) for _ in range(5)]
        S.a('<polyline points="%s" fill="none" stroke="#c8d4ff" stroke-width="%.1f" opacity=".35"/>' % (pts(q), U * .0015))
        for (x, y) in q: S.circ(x, y, U * .003, '#fff')
    for z in (1.6, 2.4, 3.6, 5.4, 8, 12):
        arc = [Pj(x, y, z) for x, y in vault]
        S.a('<polyline points="%s" fill="none" stroke="#3a3850" stroke-width="%.1f"/>' % (pts(arc), max(2, f / z * .12)))
        S.a('<polyline points="%s" fill="none" stroke="#8a86b0" stroke-width="%.1f" opacity=".35"/>' % (pts(arc), max(1, f / z * .02)))
    # assises de pierre sur les murs
    for side, X in ((-1, XL), (1, XR)):
        for y in [k * .35 for k in range(1, 13)]:
            S.a('<polyline points="%s" fill="none" stroke="#0a0810" stroke-width="%.1f" opacity=".45"/>' % (pts([Pj(X, y, 1.0), Pj(X, y, ZF)]), U * .0018))
        for z in [1.2 + k * .5 for k in range(20)]:
            for y0 in [k * .7 for k in range(6)]:
                yy = y0 + (.35 if int(z * 2) % 2 else 0)
                S.a('<polyline points="%s" fill="none" stroke="#0a0810" stroke-width="%.1f" opacity=".35"/>' % (pts([Pj(X, yy, z), Pj(X, yy + .35, z)]), max(1, f / z * .006)))
        S.a('<polygon points="%s" fill="#000" opacity=".3" filter="url(#texture)"/>' % pts([Pj(X, 0, 1.0), Pj(X, HV, 1.0), Pj(X, HV, ZF), Pj(X, 0, ZF)]))
    # dalles du sol
    for z in (1.3, 1.7, 2.2, 2.9, 3.8, 5, 6.6, 8.8, 11.6):
        S.a('<polyline points="%s" fill="none" stroke="#0a0810" stroke-width="%.1f" opacity=".7"/>' % (pts([Pj(XL, 0, z), Pj(XR, 0, z)]), max(1, f / z * .015)))
    for x in (-1.5, -.75, 0, .75, 1.5):
        S.a('<polyline points="%s" fill="none" stroke="#0a0810" stroke-width="%.1f" opacity=".6"/>' % (pts([Pj(x, 0, 1.0), Pj(x, 0, ZF)]), U * .002))
    S.poly([Pj(-.9, 0, ZF), Pj(.9, 0, ZF), Pj(1.6, 0, 1.2), Pj(-1.6, 0, 1.2)], '#9aa6ff', 'opacity=".1" filter="url(#b3)"')
    # les portes des mondes, 5 de chaque côté, avec torches entre elles
    for i, z in enumerate((3.0, 4.4, 6.0, 7.8, 9.8)):
        for side, X in ((-1, XL), (1, XR)):
            col, kind = PORTES[i * 2 + (0 if side < 0 else 1)]
            za, zb = z - .55, z + .55
            q = [Pj(X, 0, za), Pj(X, 2.4, za), Pj(X, 2.4, zb), Pj(X, 0, zb)]
            top = Pj(X, 3.0, z)
            d = 'M%.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fZ' % (q[0][0], q[0][1], q[1][0], q[1][1], top[0], top[1] - (q[1][1] - top[1]) * .2, q[2][0], q[2][1], q[3][0], q[3][1])
            S.path(d, '#0e0c14')
            S.path(d, col, 'opacity=".2"')
            S.path(d, 'none', 'stroke="%s" stroke-width="%.1f" opacity=".5" filter="url(#b1)"' % (col, max(2, f / z * .06)))
            S.path(d, 'none', 'stroke="%s" stroke-width="%.1f"' % (col, max(1, f / z * .015)))
            c = Pj(X, 1.5, z)
            S.halo(c[0], c[1], f / z * .5, col, .35, 'b3')
            embleme(S, c[0], c[1], f / z * .55, kind, col)
            if i < 4:
                t = Pj(X, 2.1, z + .9)
                S.torche(t[0], t[1], f / (z + .9) * .35)
    # le Gardien à la lanterne, de dos, au milieu du hall
    gz = 5.2; gx, gy = Pj(.35, 0, gz); s = f / gz
    S.ell(gx, gy, s * .4, s * .06, '#000', 'opacity=".55" filter="url(#b1)"')
    cape = 'M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (
        gx - s * .32, gy, gx - s * .3, gy - s * .9, gx - s * .14, gy - s * 1.45, gx, gy - s * 1.78, gx + s * .14, gy - s * 1.45, gx + s * .3, gy - s * .9, gx + s * .32, gy, gx, gy + s * .03, gx - s * .32, gy)
    S.path(cape, S.lin([(0, '#14121c'), (.5, '#26222e'), (1, '#0a0910')], 0, 0, 1, 0))
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1f' % (gx + s * .14, gy - s * 1.45, gx + s * .3, gy - s * .9, gx + s * .32, gy), 'none', 'stroke="#9aa6ff" stroke-width="%.1f" opacity=".45"' % (s * .012))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3a2614" stroke-width="%.1f" stroke-linecap="round"/>' % (gx - s * .38, gy, gx - s * .42, gy - s * 1.6, s * .03))
    lx, ly = gx + s * .36, gy - s * .7
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#14121c" stroke-width="%.1f"/>' % (gx + s * .22, gy - s * 1.0, lx, ly - s * .1, s * .04))
    S.lueur(lx, ly + s * .05, s * 1.3, '#ffb347', 1.0)
    S.rect(lx - s * .06, ly - s * .05, s * .12, s * .17, '#ffd27a', 'stroke="#2a1d10" stroke-width="%.1f" rx="%.1f"' % (s * .015, s * .015))
    S.ell(lx, ly + s * .03, s * .025, s * .05, '#fff6d0', 'filter="url(#b1)"')
    S.lucioles(16, W * .2, W * .8, vy - U * .2, vy + U * .25, '#ffe8a0')

# ============================================================== ACCUEIL v2 : le château, la ville et le marché du port
def maison(S, x, base, w, h, mur, toit, nuit, lum):
    S.rect(x - w / 2, base - h, w, h, mur)
    S.texture((x - w / 2, base - h, w, h), .25)
    for k in range(1, 3):   # colombages
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3a2418" stroke-width="%.1f"/>' % (x - w / 2, base - h * k / 3, x + w / 2, base - h * k / 3, w * .035))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3a2418" stroke-width="%.1f"/>' % (x - w / 2 + w * .08, base - h, x + w / 2 - w * .08, base - h / 3, w * .03))
    S.poly([(x - w * .62, base - h), (x, base - h - w * .62), (x + w * .62, base - h)], toit)
    S.poly([(x, base - h - w * .62), (x + w * .62, base - h), (x + w * .15, base - h)], lum, 'opacity=".15"')
    for j in range(2):
        for k in range(2):
            fx, fy = x - w * .28 + k * w * .38, base - h + h * (.12 + j * .36)
            allume = nuit and S.R.random() < .75
            S.rect(fx, fy, w * .18, h * .16, '#ffc46b' if allume else '#2a3040')
            if allume: S.rect(fx - w * .05, fy - h * .04, w * .28, h * .24, '#ffb347', 'opacity=".3" filter="url(#b1)"')

def etal(S, x, base, w, c1, c2, nuit):
    S.rect(x - w / 2, base - w * .35, w, w * .35, '#4a3020')
    S.rect(x - w * .45, base - w * .33, w * .9, w * .1, '#7a5030')
    for k in range(5):   # marchandises
        S.circ(x - w * .35 + k * w * .17, base - w * .36, w * .05, S.R.choice(['#e04a3a', '#f4c430', '#7ab04a', '#e08a3a', '#c8a0e0']))
    for side in (-1, 1):
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a1a10" stroke-width="%.1f"/>' % (x + side * w * .47, base, x + side * w * .47, base - w * .7, w * .03))
    n = 6
    for k in range(n):
        x0 = x - w * .55 + w * 1.1 * k / n
        S.path('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fA%.1f %.1f 0 0 1 %.1f %.1fZ' % (
            x0 + w * .55 / n * 0, base - w * .62, x - w * .3 + w * .6 * k / n, base - w * .82, x - w * .3 + w * .6 * (k + 1) / n, base - w * .82,
            x0 + w * 1.1 / n, base - w * .62, w * .55 / n, w * .35 / n, x0, base - w * .62), c1 if k % 2 else c2)
    if nuit:
        S.circ(x, base - w * .55, w * .05, '#ffd27a'); S.lueur(x, base - w * .45, w * .9, '#ffb347', .8)

def foule(S, x0, x1, base, t, n, col):
    for _ in range(n):
        x = S.R.uniform(x0, x1); h = t * S.R.uniform(.85, 1.15)
        S.path('M%.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fZ' % (x - h * .2, base, x - h * .14, base - h * .75, x, base - h * .85, x + h * .14, base - h * .75, x + h * .2, base), col)
        S.circ(x, base - h * .93, h * .11, col)

def accueil2(S, phase):
    W, H, P = S.W, S.H, S.P
    c = PHASES[phase]; nuit = phase != 'jour'
    U = S.U * (.46 if P else .66)
    hz = H * (.205 if P else .5)
    S.ciel(c['ciel'], hz)
    if nuit: S.etoiles(int(W * H / (2400 if phase == 'nuit' else 9000)), hz, 1 if phase == 'nuit' else .5)
    if c['astre'] == 'soleil': S.soleil(W * .14, H * (.04 if P else .12), U * .06)
    elif c['astre'] == 'couchant': S.soleil(W * .1, hz - U * .02, U * .07, '#ffd8a0', '#ff7a3c')
    else: S.lune(W * .16, H * (.035 if P else .1), U * .05)
    S.nuages([(.25, .03 if P else .08, .3, .006 if P else .012, .6), (.7, .06 if P else .16, .35, .006 if P else .012, .5)], c['nuage'][0], c['nuage'][1])
    # mer et port
    S.rect(0, hz, W, H - hz, S.lin([(0, c['mer'][0]), (1, c['mer'][1])]))
    for _ in range(120):
        y = S.R.uniform(hz, H); t = (y - hz) / (H - hz)
        S.rect(S.R.uniform(0, W * .5), y, U * S.R.uniform(.01, .05) * (.3 + t), U * .002 * (1 + 2 * t), c['lum'], 'opacity="%.2f"' % S.R.uniform(.1, .45))
    for (x, y, t) in ((.06, .02, .11), (.2, .05, .08), (.3, .015, .06)):
        galion(S, W * x, hz + U * y, U * t, '#2a1a20' if nuit else '#4a3020')
    # colline, château et sa grande porte des mondes
    cx = W * (.58 if P else .4)
    colline = 'M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (
        cx - U * .55, hz + U * .05, cx - U * .3, hz - U * .1, cx, hz - U * .12, cx + U * .35, hz - U * .1, W + U * .1, hz + U * .02, W, H, cx - U * .55, H)
    S.path(colline, S.lin([(0, c['roc'][0]), (1, c['roc'][1])])); S.texture(colline, .4)
    base = hz - U * .11; mur = c['mur']
    S.rect(cx - U * .26, base - U * .12, U * .52, U * .12, mur); S.appareil(cx - U * .26, base - U * .12, U * .52, U * .12, U * .04)
    merlons(S, cx - U * .26, cx + U * .26, base - U * .12, U * .016, U * .02, mur, c['lum'], .3)
    S.rect(cx - U * .07, base - U * .3, U * .14, U * .3, mur); S.appareil(cx - U * .07, base - U * .3, U * .14, U * .3, U * .035)
    S.rect(cx - U * .07, base - U * .3, U * .14, U * .3, S.lin([(0, '#000', .35), (.6, c['lum'], .12), (1, '#000', .4)], 0, 0, 1, 0))
    S.poly([(cx - U * .085, base - U * .3), (cx, base - U * .43), (cx + U * .085, base - U * .3)], S.lin([(0, '#3a2a48'), (1, '#1a1428')], 0, 0, 1, 0))
    for (dx, h, r) in ((-.26, .2, .04), (-.13, .25, .045), (.13, .25, .045), (.26, .2, .04)):
        tour(S, cx + dx * U, base, base - h * U, r * U, mur, c['lum'], '#f4d03f')
    gw = U * .07; gt = base - U * .09
    S.halo(cx, base - gw * .5, gw * 1.6, '#ffd36b', .5 if nuit else .3, 'b4')
    arche = 'M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (cx - gw / 2, base, gt + gw / 2, gw / 2, gw / 2, cx + gw / 2, gt + gw / 2, base)
    S.path(arche, S.lin([(0, '#fffbe0'), (.4, '#ffe08a'), (.75, '#b9a0f0'), (1, '#7fd6ea')]))
    S.path(arche, 'none', 'stroke="#2a2232" stroke-width="%.1f"' % (U * .007))
    S.runes(cx - gw * .7, gt - U * .018, gw * 1.4, 5, U * .005, '#ffd36b')
    for _ in range(14):
        x, y = cx + S.R.gauss(0, gw * .8), base - S.R.uniform(0, U * .18)
        S.circ(x, y, U * .0025, S.R.choice(['#ffd36b', '#b9a0f0', '#7fd6ea', '#ff6f9f']))
    # la ville qui descend vers le quai
    quai = hz + U * (.2 if P else .26)
    rangs = [(hz - U * .03, .055, .35), (hz + U * .07, .07, .15), (hz + U * .17, .085, 0)]
    for (yb, t, voile) in rangs:
        x = cx - U * .45 + S.R.uniform(0, U * .05)
        while x < W + U * .1:
            w = U * t * S.R.uniform(.8, 1.2); h = U * t * S.R.uniform(.9, 1.7)
            if abs(x - cx) < U * .12 and yb < hz: x += w * 1.6; continue   # la porte du château reste visible
            maison(S, x, yb - S.R.uniform(0, U * .02), w, h, S.R.choice(['#d8c0a0', '#c8a888', '#e0d0b0', '#b89878']) if not nuit else S.R.choice(['#6a5a68', '#5a4a5a', '#7a6a70']),
                   S.R.choice(['#8a3a2a', '#6a3a2a', '#4a3a4a', '#7a4a3a']), nuit, c['lum'])
            x += w * S.R.uniform(1.25, 1.9)
        if voile: S.ell(cx + U * .3, yb - U * .06, W * .7, U * .09, c['nuage'][0], 'opacity="%.2f" filter="url(#b4)"' % (voile * .7))
    # le quai et le marché
    S.path('M%.1f %.1fL%d %.1fL%d %dL%.1f %dZ' % (cx - U * .62, quai - U * .03, W, quai - U * .05, W, H, cx - U * .75, H), S.lin([(0, '#8a7a6a' if not nuit else '#4a4050'), (1, '#2a2230')]))
    S.texture('M%.1f %.1fL%d %.1fL%d %dL%.1f %dZ' % (cx - U * .62, quai - U * .03, W, quai - U * .05, W, H, cx - U * .75, H), .35)
    for k in range(14):
        y = quai + (H - quai) * (k / 14) ** 1.4
        S.a('<line x1="%.1f" y1="%.1f" x2="%d" y2="%.1f" stroke="#000" stroke-width="%.1f" opacity=".25"/>' % (cx - U * .7, y, W, y, max(1, U * .002 * (1 + k * .3))))
    # guirlande de lanternes
    gx0, gx1, gy = cx - U * .55, W, quai - U * .1
    for k in range(22):
        t = k / 21; x = gx0 + (gx1 - gx0) * t; y = gy + math.sin(t * math.pi * 3) * U * .015 + U * .02 * t
        S.circ(x, y, U * .004, ['#ffd36b', '#ff6f9f', '#7fd6ea'][k % 3])
        if nuit: S.circ(x, y, U * .012, '#ffd36b', 'opacity=".35" filter="url(#b1)"')
    rayures = [('#e9dcc8', '#b23a52'), ('#e9dcc8', '#3a6a8a'), ('#e9dcc8', '#5a8a4a'), ('#f4d03f', '#a0522d'), ('#e9dcc8', '#7a4a9a')]
    x = cx - U * .5; k = 0
    while x < W + U * .05:
        w = U * S.R.uniform(.09, .12)
        etal(S, x, quai + U * .05, w, *rayures[k % len(rayures)], nuit)
        x += w * 1.35; k += 1
    foule(S, cx - U * .55, W, quai + U * .09, U * .045, 26, '#1a1420' if nuit else '#3a2a30')
    # second rang d'étals au premier plan
    q2 = quai + U * .32; x = cx - U * .62; k = 2
    while x < W + U * .1:
        w = U * S.R.uniform(.16, .2)
        etal(S, x, q2, w, *rayures[k % len(rayures)], nuit)
        x += w * 1.5; k += 1
    foule(S, cx - U * .7, W, q2 + U * .06, U * .08, 14, '#120e18' if nuit else '#2a2028')
    # le Gardien, lanterne en main, au bord du quai
    gx, gy, s = cx - U * .58, quai + U * .12, U * .12
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (gx - s * .3, gy, gx - s * .2, gy - s * 1.2, gx, gy - s * 1.5, gx + s * .2, gy - s * 1.2, gx + s * .3, gy), '#14121c')
    S.lueur(gx + s * .35, gy - s * .6, s * 1.2, '#ffb347', 1.0 if nuit else .6)
    S.rect(gx + s * .3, gy - s * .68, s * .1, s * .14, '#ffd27a')
    if phase == 'nuit': S.lucioles(10, 0, W, H * .02, hz, '#ffe8a0')

MONDES = dict(intro=intro, accueil_jour=lambda S: accueil2(S, 'jour'), accueil_soir=lambda S: accueil2(S, 'soir'), accueil_nuit=lambda S: accueil2(S, 'nuit'), fort=fort, foraine=foraine, steampunk=steampunk, nordique=nordique, pirate=pirate, manoir=manoir, jungle=jungle, desert=desert)
if __name__ == '__main__':
    nom, W, H, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    S = Scene(W, H, graine=sum(map(ord, nom)))
    MONDES[nom](S)
    S.fin()
    S.ecrire(out)
