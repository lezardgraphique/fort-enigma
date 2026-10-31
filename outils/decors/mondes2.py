"""Décors des salles proposées par le Gardien (même atelier, même facture que les mondes).
Usage : mondes2.py <salle> W H sortie.svg"""
import sys, math, random
from atelier import Scene
from mondes import merlons, tour, galion, maison, feuille, engrenage, etal3, foule

def couloir(S, vy_f, f_f, XL=-2.4, XR=2.4, EYE=1.6):
    """projection d'un couloir vu de face (comme le hall des portes)"""
    W, H = S.W, S.H
    vx, vy = W / 2, H * vy_f
    f = W * f_f
    return (lambda X, Y, Z: (vx + f * X / Z, vy - f * (Y - EYE) / Z)), f, vx, vy

def pts(L): return ' '.join('%.1f,%.1f' % q for q in L)

# ================================================================= BIBLIOTHÈQUE INTERDITE (et Archives)
def bibliotheque(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    Pj, f, vx, vy = couloir(S, .34 if P else .44, .5 if P else .4)
    S.rect(0, 0, W, H, '#140e18')
    ZF = 12
    # mur du fond : grande fenêtre ogivale et lune
    a0, a1 = Pj(-1.1, .8, ZF), Pj(1.1, 4.2, ZF)
    S.poly([Pj(-2.4, 0, ZF), Pj(-2.4, 6, ZF), Pj(2.4, 6, ZF), Pj(2.4, 0, ZF)], '#2a1e24')
    fen = 'M%.1f %.1fV%.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fV%.1fZ' % (a0[0], a0[1], a1[1] + (a1[0] - a0[0]) * .5, a0[0], a1[1], vx, a1[1] - (a1[0] - a0[0]) * .2, a1[0], a1[1], a1[0], a1[1] + (a1[0] - a0[0]) * .5, a0[1])
    S.path(fen, S.lin([(0, '#3a4a8a'), (1, '#1a2048')]))
    S.lune(vx + (a1[0] - a0[0]) * .2, a1[1] + (a0[1] - a1[1]) * .3, U * .025)
    S.path(fen, 'none', 'stroke="#5a4048" stroke-width="%.1f"' % (U * .006))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#5a4048" stroke-width="%.1f"/>' % (vx, a1[1], vx, a0[1], U * .004))
    # rayon de lune poussiéreux
    S.poly([(a0[0], a1[1] + U * .05), (a1[0], a1[1] + U * .05), (vx + U * .5, H), (vx - U * .3, H)], '#c8d4ff', 'opacity=".08" filter="url(#b3)"')
    # étagères des deux côtés
    cols = ['#7a2a2a', '#2a4a6a', '#5a4a2a', '#3a5a3a', '#6a3a5a', '#8a6a3a', '#2a2a4a']
    for side, X in ((-1, -2.4), (1, 2.4)):
        S.poly([Pj(X, 0, 1.0), Pj(X, 6, 1.0), Pj(X, 6, ZF), Pj(X, 0, ZF)], S.lin([(0, '#1e1418'), (1, '#3a2a24')], 0 if side < 0 else 1, 0, 1 if side < 0 else 0, 0))
        for etage in range(7):
            y0 = .2 + etage * .8
            for z0 in [1.2 + k * .55 for k in range(19)]:
                z1 = z0 + .5
                if z1 > ZF: break
                # rangée de livres : petits quadrilatères
                n = 4
                for b in range(n):
                    za = z0 + (z1 - z0) * b / n; zb = za + (z1 - z0) / n * .85
                    h = .55 + S.R.uniform(-.12, .1)
                    if S.R.random() < .08: continue
                    S.poly([Pj(X, y0, za), Pj(X, y0 + h, za), Pj(X, y0 + h, zb), Pj(X, y0, zb)], S.R.choice(cols))
            S.poly([Pj(X, y0 - .06, 1.0), Pj(X, y0, 1.0), Pj(X, y0, ZF), Pj(X, y0 - .06, ZF)], '#4a3020')
        S.poly([Pj(X, 0, 1.0), Pj(X, 6, 1.0), Pj(X, 6, ZF), Pj(X, 0, ZF)], '#0e0b18', 'opacity=".25"')
    # échelle
    for (x, z) in ((-2.3, 3.4),):
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6a4a2a" stroke-width="%.1f"/>' % (*Pj(x + .3, 0, z), *Pj(x, 5, z), f / z * .03))
        S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6a4a2a" stroke-width="%.1f"/>' % (*Pj(x + .3, 0, z + .4), *Pj(x, 5, z + .4), f / z * .03))
    # sol et tapis
    S.poly([Pj(-2.4, 0, 1.0), Pj(2.4, 0, 1.0), Pj(2.4, 0, ZF), Pj(-2.4, 0, ZF)], S.lin([(0, '#3a2418'), (1, '#0c0806')]))
    S.poly([Pj(-.9, 0, 1.0), Pj(.9, 0, 1.0), Pj(.9, 0, ZF), Pj(-.9, 0, ZF)], '#5a1a2a', 'opacity=".75"')
    # livres qui volent et pages
    for _ in range(9):
        x, y = S.R.uniform(.2, .8) * W, S.R.uniform(.3, .9) * vy
        t = U * S.R.uniform(.025, .045); a = S.R.uniform(-30, 30)
        S.a('<g transform="rotate(%d %.1f %.1f)"><path d="M%.1f %.1fq%.1f %.1f %.1f 0v%.1fq%.1f %.1f %.1f 0z" fill="%s"/><path d="M%.1f %.1fq%.1f %.1f %.1f 0v%.1fq%.1f %.1f %.1f 0z" fill="#e8dcc0"/></g>' % (
            a, x, y, x - t, y, -t * .5, -t * .3, -t, t * .6, t * .5, t * .3, t, S.R.choice(cols), x, y, t * .5, -t * .3, t, t * .6, -t * .5, t * .3, -t))
        S.halo(x, y, t * 1.3, '#ffe8a0', .25, 'b2')
    # chandelier et bougies
    c = Pj(0, 4.6, 3.2)
    S.a('<line x1="%.1f" y1="0" x2="%.1f" y2="%.1f" stroke="#2a1a10" stroke-width="%.1f"/>' % (c[0], c[0], c[1], U * .003))
    S.ell(c[0], c[1], U * .09, U * .012, '#8a6a2a')
    for k in range(5):
        x = c[0] - U * .08 + k * U * .04
        S.rect(x - U * .004, c[1] - U * .03, U * .008, U * .03, '#f4ead2'); S.flamme(x, c[1] - U * .03, U * .022)
    # le bibliothécaire fantôme
    g = Pj(.8, 0, 5.5); s = f / 5.5
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (g[0] - s * .3, g[1], g[0] - s * .2, g[1] - s * 1.4, g[0], g[1] - s * 1.7, g[0] + s * .2, g[1] - s * 1.4, g[0] + s * .3, g[1]), '#d8e4ff', 'opacity=".28" filter="url(#b1)"')
    S.lumiere = (c[0], c[1], '#ffb347')

# ================================================================= ATLANTIDE ENGLOUTIE
def atlantide(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.52 if P else .74)
    S.rect(0, 0, W, H, S.lin([(0, '#0a5a6a'), (.4, '#063a52'), (1, '#021a2a')]))
    for k in range(7):     # rais de lumière depuis la surface
        x = W * (.15 + k * .12)
        S.poly([(x, 0), (x + U * .04, 0), (x + U * .18, sol), (x + U * .06, sol)], '#bff4ff', 'opacity=".09" filter="url(#b2)"')
    S.rect(0, 0, W, U * .03, '#bff4ff', 'opacity=".25" filter="url(#b2)"')
    # temple englouti
    tx, tw = W * (.5 if P else .36), U * .6
    tt = sol - U * .3
    S.poly([(tx - tw / 2, tt), (tx, tt - U * .13), (tx + tw / 2, tt)], S.lin([(0, '#7ab0b0'), (1, '#3a6a72')]))
    S.rect(tx - tw / 2, tt, tw, U * .03, '#5a8a8a')
    for k in range(7):
        cx = tx - tw / 2 + tw * (k + .5) / 7
        haut = tt + U * .03 + (U * .14 if k in (2, 5) else 0)
        S.rect(cx - U * .022, haut, U * .044, sol - haut, S.lin([(0, '#2a5058'), (.5, '#8ac0c0'), (1, '#2a5058')], 0, 0, 1, 0))
        if k in (2, 5): S.path('M%.1f %.1fl%.1f %.1fl%.1f %.1fl%.1f %.1fZ' % (cx - U * .022, haut, U * .015, -U * .02, U * .015, U * .015, U * .014, -U * .01), '#8ac0c0')
    S.ell(tx, tt - U * .16, U * .07, U * .05, '#5a8a8a'); S.runes(tx - U * .08, tt + U * .015, U * .16, 5, U * .007, '#7fffe0')
    S.brume(sol - U * .2, U * .3, '#0a5a6a', .35)
    # algues, coraux et poissons
    for _ in range(18):
        x = S.R.uniform(0, W); h = U * S.R.uniform(.08, .25)
        S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fQ%.1f %.1f %.1f %.1f' % (x, sol + U * .02, x + U * .04, sol - h * .5, x - U * .01, sol - h * .7, x - U * .03, sol - h, x + U * .01, sol - h), 'none', 'stroke="%s" stroke-width="%.1f" stroke-linecap="round"' % (S.R.choice(['#1a6a4a', '#2a8a5a', '#a04a6a']), U * .008))
    for _ in range(9):
        x, y, t = S.R.uniform(.1, .9) * W, S.R.uniform(.1, .45) * H, U * S.R.uniform(.015, .03)
        S.path('M%.1f %.1fq%.1f %.1f %.1f 0q%.1f %.1f %.1f 0l%.1f %.1fv%.1fz' % (x, y, t, -t * .6, t * 2, -t, t * .6, -t * 2, -t * .5, -t * .4, t * .8), '#0e2a3a', 'opacity=".8"')
    S.sol(sol, '#3a6a6a', '#021018', 'sable', lum=(tx, '#7fffe0'), brume='#0a5a6a')
    for _ in range(30):     # bulles
        x, y, r = S.R.uniform(0, W), S.R.uniform(0, sol), U * S.R.uniform(.003, .009)
        S.circ(x, y, r, 'none', 'stroke="#d8fbff" stroke-width="%.1f" opacity=".6"' % (U * .0015))
    S.lumiere = (W * .5, 0, '#bff4ff')

# ================================================================= FAR WEST (et Canyon)
def farwest(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.52 if P else .74)
    S.ciel([(0, '#3a1a3a'), (.4, '#a04a3a'), (.75, '#f08a3a'), (1, '#ffd08a')], sol)
    S.soleil(W * (.62 if P else .42), sol - U * .1, U * .07, '#ffe0a0', '#ff8a3c')
    # mesas
    for (x, w, h, c) in ((.1, .3, .22, '#7a3a2a'), (.55, .25, .3, '#8a4a2a'), (.85, .3, .18, '#6a2a22')):
        S.poly([(W * x - U * w * .7, sol), (W * x - U * w * .5, sol - U * h), (W * x + U * w * .5, sol - U * h), (W * x + U * w * .7, sol)], S.lin([(0, c), (1, '#3a1a14')]))
        S.texture('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (W * x - U * w * .7, sol, W * x - U * w * .5, sol - U * h, W * x + U * w * .5, sol - U * h, W * x + U * w * .7, sol), .3)
    S.voile(sol, '#f08a3a', .15)
    # saloon
    sx, sw = W * (.3 if P else .2), U * .34
    S.rect(sx - sw / 2, sol - U * .26, sw, U * .26, S.lin([(0, '#6a4224'), (1, '#3a2414')]))
    S.rect(sx - sw * .55, sol - U * .33, sw * 1.1, U * .08, '#5a3a20')
    S.a('<text x="%.1f" y="%.1f" font-family="Georgia,serif" font-weight="700" font-size="%.1f" text-anchor="middle" fill="#f4d58a">SALOON</text>' % (sx, sol - U * .275, U * .04))
    for k in range(9): S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a1a0c" stroke-width="%.1f" opacity=".5"/>' % (sx - sw / 2 + sw * k / 8, sol - U * .26, sx - sw / 2 + sw * k / 8, sol, U * .002))
    for dx in (-.3, .3): S.rect(sx + sw * dx - U * .03, sol - U * .2, U * .06, U * .07, '#ffc46b')
    S.path('M%.1f %.1fh%.1fv%.1fh%.1fz' % (sx - U * .035, sol, U * .07, -U * .1, -U * .07), '#2a1a0c')
    # château d'eau et cactus
    wx = W * (.82 if P else .58)
    for dx in (-1, 1): S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a1a0c" stroke-width="%.1f"/>' % (wx + dx * U * .05, sol, wx + dx * U * .03, sol - U * .18, U * .008))
    S.rect(wx - U * .06, sol - U * .3, U * .12, U * .12, '#4a2a18'); S.poly([(wx - U * .07, sol - U * .3), (wx, sol - U * .35), (wx + U * .07, sol - U * .3)], '#3a2014')
    for (x, h) in ((.6 if P else .38, .14), (.95, .1)):
        cx = W * x
        S.path('M%.1f %.1fv%.1fq0 %.1f %.1f 0v%.1fM%.1f %.1fh%.1fv%.1fM%.1f %.1fh%.1fv%.1f' % (cx, sol, -U * h, -U * .02, U * .04, U * h, cx + U * .04, sol - U * h * .5, U * .03, -U * .05, cx, sol - U * h * .6, -U * .03, -U * .04), 'none', 'stroke="#1a3a1a" stroke-width="%.1f" stroke-linecap="round"' % (U * .03))
    S.sol(sol, '#c07a40', '#2a140a', 'sable', lum=(W * .5, '#ffc070'), brume='#f0a060')
    S.ombre(sx, sol + U * .01, sw)
    S.lumiere = (W * .5, sol - U * .1, '#ffc070')

# ================================================================= CIRQUE MYSTIQUE
def cirque(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.55 if P else .72)
    S.rect(0, 0, W, H, '#140a1e')
    # toile rayée qui converge vers le mât
    cx, cy = W / 2, -H * .1
    n = 16
    for k in range(n):
        a0 = math.pi * (.05 + .9 * k / n); a1 = math.pi * (.05 + .9 * (k + 1) / n)
        S.poly([(cx, cy), (cx + math.cos(a0) * W * 1.4, cy + math.sin(a0) * H * 1.2), (cx + math.cos(a1) * W * 1.4, cy + math.sin(a1) * H * 1.2)], '#6a1a3a' if k % 2 else '#2a1a4a')
    S.rect(0, 0, W, sol, S.lin([(0, '#000', .1), (1, '#000', .55)]))
    # guirlandes d'ampoules
    for r in (.25, .4):
        for k in range(30):
            a = math.pi * (.08 + .84 * k / 29); x, y = cx + math.cos(a) * W * r * 1.6, cy + math.sin(a) * H * r * 1.3
            S.circ(x, y, U * .004, '#ffd36b'); S.circ(x, y, U * .01, '#ffd36b', 'opacity=".35" filter="url(#b1)"')
    # trapèze
    tx = W * (.62 if P else .42)
    for dx in (-1, 1): S.a('<line x1="%.1f" y1="0" x2="%.1f" y2="%.1f" stroke="#c8b8a0" stroke-width="%.1f"/>' % (tx + dx * U * .06, tx + dx * U * .06, sol - U * .45, U * .002))
    S.rect(tx - U * .07, sol - U * .45, U * .14, U * .008, '#c9a227')
    # projecteurs
    for (x, a) in ((.1, 1), (.9, -1)):
        S.poly([(W * x, 0), (W * x + U * .03, 0), (W * (.45 if not P else .5) + a * U * .2, sol + U * .05), (W * (.45 if not P else .5) - a * U * .1, sol + U * .05)], '#fff3c4', 'opacity=".09" filter="url(#b2)"')
    # piste de sciure
    pcx = W * (.5 if P else .36)
    S.sol(sol, '#4a2a3a', '#0e0b18', 'terre', vp=pcx, lum=(pcx, '#ffd36b'))
    S.ell(pcx, sol + U * .14, U * .5, U * .1, '#c88a4a'); S.ell(pcx, sol + U * .14, U * .5, U * .1, 'none', 'stroke="#b23a52" stroke-width="%.1f"' % (U * .02))
    S.texture((pcx - U * .5, sol + U * .04, U * 1.0, U * .2), .25)
    # piédestaux et ballons
    for (dx, c) in ((-.3, '#b23a52'), (0, '#3a6a8a'), (.3, '#c9a227')):
        px = pcx + dx * U
        S.rect(px - U * .04, sol + U * .04, U * .08, U * .06, c); S.ell(px, sol + U * .04, U * .04, U * .012, '#f4ead2')
        S.circ(px, sol + U * .01, U * .03, S.rad([(0, '#fff'), (.4, c), (1, '#1a0a14')], .35, .3, .7))
    # dompteur d'ombres : silhouette au chapeau haut-de-forme
    gx, gb, s = pcx + U * .42, sol + U * .12, U * .2
    S.path('M%.1f %.1fl%.1f %.1fh%.1fl%.1f %.1fz' % (gx - s * .2, gb, s * .08, -s * .9, s * .24, s * .08, s * .9), '#0a0610')
    S.circ(gx, gb - s * .98, s * .1, '#0a0610'); S.rect(gx - s * .1, gb - s * 1.25, s * .2, s * .18, '#0a0610'); S.rect(gx - s * .15, gb - s * 1.08, s * .3, s * .03, '#0a0610')
    S.lumiere = (pcx, sol - U * .2, '#ffd36b')

# ================================================================= STATION ORBITALE
def station(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.55 if P else .74)
    S.rect(0, 0, W, H, '#0a0e18')
    # grande baie vitrée : planète et étoiles
    bx0, by0, bx1, by1 = W * .08, H * (.06 if P else .08), W * .92, sol - U * .12
    S.rect(bx0, by0, bx1 - bx0, by1 - by0, '#02040c', 'rx="%.1f"' % (U * .05))
    S.a('<clipPath id="baie"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f"/></clipPath><g clip-path="url(#baie)">' % (bx0, by0, bx1 - bx0, by1 - by0, U * .05))
    for _ in range(int(W * H / 2500)): S.circ(S.R.uniform(bx0, bx1), S.R.uniform(by0, by1), S.R.uniform(.4, 1.3) * U / 1100, '#fff', 'opacity="%.2f"' % S.R.uniform(.3, 1))
    pr = U * .45; px, py = W * (.5 if P else .38), by1 + pr * .35
    S.circ(px, py, pr * 1.15, S.rad([(0, '#5ec8e5', .4), (1, '#5ec8e5', 0)]))
    S.circ(px, py, pr, S.rad([(0, '#7ad8ff'), (.55, '#2a6ab0'), (1, '#0a1a3a')], .35, .3, .75))
    for k in range(4): S.ell(px - pr * .1, py - pr * (.5 - k * .2), pr * (.7 - k * .05), pr * .04, '#e8f8ff', 'opacity=".35" filter="url(#b1)"')
    S.circ(px + pr * 1.4, py - pr * 1.1, pr * .12, S.rad([(0, '#e8e2d8'), (1, '#6a6a7a')], .35, .3, .7))
    S.a('</g>')
    S.rect(bx0, by0, bx1 - bx0, by1 - by0, 'none', 'rx="%.1f" stroke="#3a4a5a" stroke-width="%.1f"' % (U * .05, U * .02))
    for k in range(1, 4): S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3a4a5a" stroke-width="%.1f"/>' % (bx0 + (bx1 - bx0) * k / 4, by0, bx0 + (bx1 - bx0) * k / 4, by1, U * .008))
    # consoles
    for k in range(int(W / (U * .22)) + 1):
        x = k * U * .22
        S.rect(x, sol - U * .1, U * .2, U * .1, S.lin([(0, '#3a4a5a'), (1, '#1a222c')]))
        for j in range(5): S.rect(x + U * (.02 + j * .035), sol - U * .07, U * .02, U * .012, S.R.choice(['#5ec8e5', '#46d17f', '#ffd36b', '#ff5c5c']))
        S.rect(x + U * .02, sol - U * .045, U * .16, U * .03, '#0a1a2a'); S.rect(x + U * .03, sol - U * .035, U * S.R.uniform(.03, .12), U * .01, '#5ec8e5', 'opacity=".8"')
    S.sol(sol, '#3a4a5a', '#05080e', 'dalles', lum=(W * .5, '#5ec8e5'))
    S.lumiere = (px, py - pr * .5, '#7ad8ff')

# ================================================================= TEMPLE MAYA (et Temple)
def maya(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.52 if P else .74)
    S.ciel([(0, '#1a1a3a'), (.5, '#6a3a5a'), (.85, '#e07a4a'), (1, '#ffc070')], sol)
    S.soleil(W * (.75 if P else .48), sol - U * .32, U * .06, '#ffe0a0', '#ff8a3c')
    tx = W * (.5 if P else .34); base_w = U * .7
    for k in range(6):
        w = base_w * (1 - k * .14); h = U * .06; y = sol - h * (k + 1)
        S.rect(tx - w / 2, y, w, h, S.lin([(0, '#8a8a5a'), (1, '#4a4a2a')]))
        S.rect(tx - w / 2, y, w, U * .006, '#c8c080', 'opacity=".5"')
        S.modele(tx - w / 2, y, w, h)
    S.poly([(tx - U * .06, sol), (tx + U * .06, sol), (tx + U * .035, sol - U * .36), (tx - U * .035, sol - U * .36)], '#6a6a3a')
    for k in range(18): S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3a3a1a" stroke-width="%.1f"/>' % (tx - U * (.06 - k * .0014), sol - k * U * .02, tx + U * (.06 - k * .0014), sol - k * U * .02, U * .002))
    S.rect(tx - U * .08, sol - U * .46, U * .16, U * .1, '#6a6a3a'); S.rect(tx - U * .025, sol - U * .43, U * .05, U * .07, '#1a1408')
    S.circ(tx, sol - U * .52, U * .045, 'none', 'stroke="#46d17f" stroke-width="%.1f"' % (U * .006)); S.halo(tx, sol - U * .52, U * .07, '#46d17f', .4, 'b2')
    S.runes(tx - U * .2, sol - U * .2, U * .4, 6, U * .009, '#46d17f')
    for _ in range(40): feuille(S, S.R.choice([S.R.uniform(-.05, .2), S.R.uniform(.8, 1.05)]) * W, S.R.uniform(.3, 1) * sol, U * S.R.uniform(.08, .18), S.R.uniform(0, 6.3), S.R.choice(['#0a2a16', '#123a20', '#06180c']))
    S.sol(sol, '#5a5a3a', '#0e0b10', 'dalles', vp=tx, lum=(tx, '#ffc070'))
    S.lumiere = (W * .5, sol - U * .3, '#ffc070')

# ================================================================= CARNAVAL VÉNITIEN
def carnaval(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    hz = H * (.42 if P else .55)
    S.ciel([(0, '#0a0e2a'), (.6, '#2a1a4a'), (1, '#6a3a6a')], hz)
    S.etoiles(int(W * H / 3000), hz * .6, .8)
    S.lune(W * .75, H * .07, U * .035)
    # palais vénitiens de part et d'autre du canal
    for side in (-1, 1):
        x = W / 2 + side * U * .14; k = 0
        while (side < 0 and x > -U * .2) or (side > 0 and x < W + U * .2):
            w = U * S.R.uniform(.16, .24); h = U * S.R.uniform(.35, .55)
            x0 = x - (w if side < 0 else 0)
            S.rect(x0, hz - h, w, h, S.R.choice(['#8a4a3a', '#b07a5a', '#6a3a4a', '#a0605a']))
            S.rect(x0, hz - h, w, h, '#0e0b18', 'opacity=".35"')
            for r in range(3):
                for c in range(3):
                    fx = x0 + w * (.15 + c * .28); fy = hz - h + h * (.12 + r * .28)
                    S.path('M%.1f %.1fv%.1fh%.1fv%.1fa%.1f %.1f 0 0 0 %.1f 0z' % (fx, fy + h * .16, -h * .1, w * .16, h * .1, w * .08, w * .08, -w * .16), '#ffc46b' if S.R.random() < .55 else '#2a2030')
            S.rect(x0, hz - h * .4, w, U * .008, '#e8d8c0', 'opacity=".5"')
            x += side * w * 1.02; k += 1
    # canal, reflets, gondole
    S.rect(0, hz, W, H - hz, S.lin([(0, '#1a2a4a'), (1, '#050814')]))
    for _ in range(160):
        y = S.R.uniform(hz, H); t = (y - hz) / (H - hz)
        S.rect(S.R.uniform(0, W), y, U * S.R.uniform(.01, .05) * (.3 + t), U * .002 * (1 + 2 * t), S.R.choice(['#ffc46b', '#c8d4ff', '#ff8aa0']), 'opacity="%.2f"' % S.R.uniform(.15, .5))
    gx, gy, gs = W * (.45 if P else .32), hz + U * .12, U * .35
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fL%.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (gx - gs * .5, gy - gs * .12, gx, gy + gs * .08, gx + gs * .5, gy - gs * .16, gx + gs * .45, gy - gs * .1, gx, gy + gs * .02, gx - gs * .45, gy - gs * .06), '#0a0610')
    S.path('M%.1f %.1fq%.1f %.1f %.1f %.1f' % (gx + gs * .5, gy - gs * .16, gs * .03, -gs * .1, -gs * .02, -gs * .14), 'none', 'stroke="#c9a227" stroke-width="%.1f"' % (gs * .02))
    S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#0a0610" stroke-width="%.1f"/>' % (gx + gs * .25, gy - gs * .1, gx + gs * .1, gy - gs * .55, gs * .01))
    # masque sur un poteau à lanterne
    mx, my = W * (.18 if P else .1), hz - U * .05
    S.rect(mx - U * .006, my - U * .3, U * .012, U * .3 + U * .1, '#1a1020')
    S.path('M%.1f %.1fq%.1f %.1f %.1f 0q0 %.1f %.1f %.1fq%.1f 0 %.1f %.1fz' % (mx - U * .06, my - U * .34, U * .06, -U * .03, U * .12, U * .05, -U * .06, U * .07, -U * .06, 0, -U * .07), '#f4ead2')
    for dx in (-.025, .025): S.ell(mx + dx * U, my - U * .32, U * .014, U * .008, '#1a1020')
    S.path('M%.1f %.1fl%.1f %.1fM%.1f %.1fl%.1f %.1f' % (mx - U * .06, my - U * .36, -U * .03, -U * .05, mx + U * .06, my - U * .36, U * .03, -U * .05), 'none', 'stroke="#c9a227" stroke-width="%.1f"' % (U * .005))
    S.lumiere = (W * .75, H * .07, '#ffc46b')

# ================================================================= CITÉ (ville fantastique)
def cite(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    hz = H * (.45 if P else .6)
    S.ciel([(0, '#0a0a24'), (.6, '#2a2a5a'), (1, '#6a4a7a')], hz)
    S.etoiles(int(W * H / 2600), hz * .8, .9)
    S.lune(W * .2, H * .08, U * .045)
    for (base, t, col, of) in ((hz - U * .05, .07, '#3a3a6a', .15), (hz + U * .05, .09, '#2a2a4a', .25), (hz + U * .16, .11, '#1a1a30', .35)):
        x = -U * .05
        while x < W:
            w = U * t * S.R.uniform(.8, 1.4); h = U * t * S.R.uniform(1.2, 3.2)
            S.rect(x, base - h, w, h + U, col)
            r = S.R.random()
            if r < .3: S.ell(x + w / 2, base - h, w * .5, w * .45, col)            # coupole
            elif r < .55: S.poly([(x - w * .05, base - h), (x + w / 2, base - h - w * 1.1), (x + w * 1.05, base - h)], col)   # flèche
            for j in range(int(h / (U * .03))):
                if S.R.random() < of: S.rect(x + w * .3, base - h + U * .02 + j * U * .03, w * .15, U * .012, '#ffc46b')
            x += w * S.R.uniform(1.0, 1.2)
        S.brume(base - U * .04, U * .08, '#6a4a7a', .2)
    S.rect(0, hz + U * .25, W, H, '#0a0a18')
    S.sol(hz + U * .25, '#2a2238', '#05040a', 'pave', lum=(W * .5, '#ffc46b'))
    S.lumiere = (W * .2, H * .08, '#c8d4ff')

# ================================================================= CRYPTE (Tombeau, Prison)
def crypte(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    Pj, f, vx, vy = couloir(S, .36 if P else .46, .5 if P else .42)
    S.rect(0, 0, W, H, '#0a0c0c')
    ZF = 10
    S.poly([Pj(-2.4, 0, ZF), Pj(-2.4, 4, ZF), Pj(2.4, 4, ZF), Pj(2.4, 0, ZF)], '#3a4038')
    S.halo(vx, vy, U * .3, '#7fffa0', .25, 'b4')
    for z in (8.6, 6.4, 4.6, 3.2, 2.2, 1.4):        # arcades successives, du fond vers l'avant
        g, dd = Pj(-2.0, 0, z), Pj(2.0, 2.6, z)
        w = dd[0] - g[0]
        d = 'M%.1f %.1fH%.1fV%.1fH%.1fZ M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (-W * .1, -H * .1, W * 1.1, H * 1.1, -W * .1, g[0], g[1], dd[1], w / 2, w * .45, dd[0], dd[1], g[1])
        c = int(18 + 46 * (z / ZF))
        S.path(d, '#%02x%02x%02x' % (c, c + 4, c), 'fill-rule="evenodd"')
        S.a('<path d="%s" fill="#000" opacity=".25" filter="url(#texture)" fill-rule="evenodd"/>' % d)
        S.path('M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1f' % (g[0], g[1], dd[1], w / 2, w * .45, dd[0], dd[1], g[1]), 'none', 'stroke="#9a9a80" stroke-width="%.1f" opacity=".35"' % max(1, f / z * .02))
    S.poly([Pj(-2.4, 0, 1.4), Pj(2.4, 0, 1.4), Pj(2.4, 0, ZF), Pj(-2.4, 0, ZF)], S.lin([(0, '#3a3a34'), (1, '#0a0c0c')]))
    # sarcophage au centre
    a, b = Pj(-.8, 0, 4.2), Pj(.8, 1.0, 4.2)
    S.rect(a[0], b[1], b[0] - a[0], a[1] - b[1], S.lin([(0, '#6a6a5a'), (1, '#2a2a24')])); S.texture((a[0], b[1], b[0] - a[0], a[1] - b[1]), .3)
    S.rect(a[0] - U * .01, b[1] - U * .02, b[0] - a[0] + U * .02, U * .03, '#7a7a6a')
    S.runes(a[0] + U * .02, (a[1] + b[1]) / 2, b[0] - a[0] - U * .04, 6, U * .009, '#7fffa0')
    S.ombre((a[0] + b[0]) / 2, a[1], b[0] - a[0])
    # niches à crânes et bougies
    for side in (-1, 1):
        for z in (2.2, 3.2, 4.6):
            c = Pj(side * 2.05, 1.6, z); s = f / z
            S.ell(c[0], c[1], s * .2, s * .14, '#050606')
            S.circ(c[0], c[1] + s * .02, s * .07, '#d8d0b8'); S.ell(c[0] - s * .025, c[1], s * .018, s * .022, '#050606'); S.ell(c[0] + s * .025, c[1], s * .018, s * .022, '#050606')
            S.rect(c[0] + side * -s * .14, c[1] + s * .05, s * .025, s * .07, '#f4ead2'); S.flamme(c[0] + side * -s * .14 + s * .012, c[1] + s * .05, s * .06)
    S.brume(vy, H * .3, '#4aff8a', .12)
    S.lucioles(8, W * .2, W * .8, vy - U * .1, vy + U * .2, '#9affc0')
    S.lumiere = (vx, vy, '#ffb347')

# ================================================================= LABYRINTHE
def labyrinthe(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    Pj, f, vx, vy = couloir(S, .38 if P else .5, .5 if P else .42)
    S.ciel([(0, '#0a1024'), (.7, '#2a3a5a'), (1, '#4a5a7a')], vy)
    S.etoiles(int(W * H / 3000), vy * .9, .8); S.lune(W * .7, H * .08, U * .04)
    # haies de pierre et de lierre, avec des virages
    for side, X in ((-1, -2.2), (1, 2.2)):
        for (z0, z1) in ((1.0, 3.0), (3.6, 6.0), (6.6, 9.0)):
            S.poly([Pj(X, 0, z0), Pj(X, 3.2, z0), Pj(X, 3.2, z1), Pj(X, 0, z1)], S.lin([(0, '#1a3a24'), (1, '#2a5a34')], 0 if side < 0 else 1, 0, 1 if side < 0 else 0, 0))
            S.texture('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (*Pj(X, 0, z0), *Pj(X, 3.2, z0), *Pj(X, 3.2, z1), *Pj(X, 0, z1)), .4)
            S.poly([Pj(X, 3.1, z0), Pj(X, 3.2, z0), Pj(X, 3.2, z1), Pj(X, 3.1, z1)], '#c8d4ff', 'opacity=".25"')
        for z in (3.0, 6.0):     # ouvertures latérales (virages) : faces de retour
            S.poly([Pj(X, 0, z), Pj(X, 3.2, z), Pj(X * 1.8, 3.2, z), Pj(X * 1.8, 0, z)], '#163020')
    a, b = Pj(-2.2, 0, 9.0), Pj(2.2, 3.2, 9.0)
    S.rect(a[0], b[1], b[0] - a[0], a[1] - b[1], '#1e4428')
    # statue au bout
    s = Pj(0, 0, 8.4); t = f / 8.4
    S.rect(s[0] - t * .3, s[1] - t * .4, t * .6, t * .4, '#7a7a8a'); S.path('M%.1f %.1fq%.1f %.1f %.1f %.1fq%.1f %.1f %.1f %.1fz' % (s[0] - t * .2, s[1] - t * .4, 0, -t * 1.2, t * .2, -t * 1.5, t * .2, t * .3, t * .2, t * 1.5), '#9a9aaa')
    S.halo(s[0], s[1] - t, t, '#c8d4ff', .35, 'b3')
    S.rect(0, vy, W, H - vy, '#0a0a0e')
    S.poly([Pj(-2.2, 0, 1.0), Pj(2.2, 0, 1.0), Pj(2.2, 0, 9), Pj(-2.2, 0, 9)], S.lin([(0, '#3a3a3a'), (1, '#0a0a0e')]))
    for z in (1.4, 2, 2.8, 3.8, 5, 6.6, 8.4):
        S.a('<polyline points="%s" fill="none" stroke="#000" stroke-width="%.1f" opacity=".4"/>' % (pts([Pj(-2.2, 0, z), Pj(2.2, 0, z)]), max(1, f / z * .01)))
    S.brume(vy, U * .2, '#c8d4ff', .2)
    S.lumiere = (W * .7, H * .08, '#c8d4ff')

# ================================================================= JARDIN ENCHANTÉ
def jardin(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.52 if P else .74)
    S.ciel([(0, '#0e1430'), (.6, '#2a3a5a'), (1, '#5a6a7a')], sol)
    S.etoiles(int(W * H / 3500), sol * .7, .7); S.lune(W * .8, H * .08, U * .04)
    # arches de roses
    for k, z in enumerate((1.0, .75, .55)):
        cx = W / 2; r = U * .55 * z; y = sol - U * .02
        S.path('M%.1f %.1fA%.1f %.1f 0 0 1 %.1f %.1f' % (cx - r, y, r, r * 1.2, cx + r, y), 'none', 'stroke="#1a3a1a" stroke-width="%.1f"' % (U * .03 * z))
        for j in range(22):
            a = math.pi * j / 21; x, yy = cx - r * math.cos(a), y - r * 1.2 * math.sin(a)
            S.circ(x, yy, U * .012 * z, S.R.choice(['#e04a6a', '#ff8aa0', '#f4ead2']))
    # fontaine
    fx = W * (.5 if P else .36)
    S.ell(fx, sol + U * .04, U * .2, U * .05, '#5a6a7a'); S.ell(fx, sol + U * .035, U * .17, U * .035, '#3a8ab0')
    S.rect(fx - U * .02, sol - U * .12, U * .04, U * .15, '#7a8a9a'); S.ell(fx, sol - U * .12, U * .07, U * .018, '#7a8a9a')
    for dx in (-1, 1): S.path('M%.1f %.1fq%.1f %.1f %.1f %.1f' % (fx, sol - U * .13, dx * U * .06, -U * .06, dx * U * .12, U * .14), 'none', 'stroke="#bff4ff" stroke-width="%.1f" opacity=".7"' % (U * .004))
    S.halo(fx, sol - U * .05, U * .15, '#bff4ff', .3, 'b3')
    # fleurs lumineuses et buissons
    for _ in range(26):
        x, y = S.R.uniform(0, W), sol + S.R.uniform(-U * .02, U * .2)
        S.ell(x, y, U * .05, U * .03, '#0e2a14')
        c = S.R.choice(['#ffd36b', '#b9a0f0', '#7fd6ea', '#ff8aa0']); S.circ(x, y - U * .02, U * .006, c); S.circ(x, y - U * .02, U * .018, c, 'opacity=".35" filter="url(#b1)"')
    S.sol(sol, '#2a4a2a', '#050a06', 'dalles', lum=(fx, '#bff4ff'))
    S.lucioles(10, 0, W, H * .1, sol, '#ffe8a0')
    S.lumiere = (fx, sol - U * .1, '#bff4ff')

# ================================================================= RUCHE
def ruche(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.55 if P else .75)
    S.rect(0, 0, W, H, '#2a1604')
    r = U * .06; hh = r * math.sqrt(3)
    for j in range(int(H / hh) + 2):
        for i in range(int(W / (r * 1.5)) + 2):
            cx = i * r * 1.5; cy = j * hh + (hh / 2 if i % 2 else 0)
            d = (cx - W * .5) ** 2 + (cy - H * .35) ** 2
            plein = S.R.random() < .55
            hx = ' '.join('%.1f,%.1f' % (cx + r * .94 * math.cos(math.pi / 3 * k), cy + r * .94 * math.sin(math.pi / 3 * k)) for k in range(6))
            lum = max(0, 1 - d ** .5 / (U * .9))
            S.a('<polygon points="%s" fill="%s" stroke="#5a3008" stroke-width="%.1f"/>' % (hx, ('#e8a020' if plein else '#3a2008') if lum > .15 else ('#a0620a' if plein else '#24120a'), r * .12))
            if plein and S.R.random() < .2: S.circ(cx - r * .3, cy - r * .3, r * .15, '#fff3c4', 'opacity=".5"')
    S.lueur(W * .5, H * .35, U * .7, '#ffc04a', .7)
    for _ in range(14):     # coulures de miel
        x, y = S.R.uniform(0, W), S.R.uniform(0, sol * .8)
        S.path('M%.1f %.1fv%.1fa%.1f %.1f 0 0 0 %.1f 0v%.1fz' % (x, y, U * S.R.uniform(.03, .1), U * .008, U * .008, U * .016, -U * .05), '#ffb020', 'opacity=".85"')
    for _ in range(10):     # abeilles
        x, y, t = S.R.uniform(.1, .9) * W, S.R.uniform(.1, .5) * H, U * S.R.uniform(.012, .02)
        S.ell(x, y, t, t * .7, '#f4c430'); S.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a1006" stroke-width="%.1f"/>' % (x, y - t * .7, x, y + t * .7, t * .3))
        S.ell(x - t * .3, y - t, t * .6, t * .4, '#fff', 'opacity=".55"'); S.ell(x + t * .3, y - t, t * .6, t * .4, '#fff', 'opacity=".55"')
    S.sol(sol, '#7a4a10', '#140a02', 'dalles', lum=(W * .5, '#ffc04a'))
    S.lumiere = (W * .5, H * .35, '#ffc04a')

# ================================================================= LABORATOIRE (alchimie)
def laboratoire(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    sol = H * (.55 if P else .74)
    S.rect(0, 0, W, sol, S.lin([(0, '#141820'), (1, '#242a34')]))
    S.appareil(0, 0, W, sol, U * .09, '#0a0c10', .6, ('#4a5a6a', '#1a222c', '#3a4a5a'))
    S.texture((0, 0, W, sol), .25)
    # étagères de bocaux
    for k in range(3):
        y = H * (.12 + k * .11) * (1 if P else 1.2)
        S.rect(0, y, W, U * .012, '#4a3020')
        x = U * .03
        while x < W:
            w = U * S.R.uniform(.03, .05); h = U * S.R.uniform(.04, .08); c = S.R.choice(['#46d17f', '#b9a0f0', '#ff6f9f', '#5ec8e5', '#ffd36b'])
            S.rect(x, y - h, w, h, '#c8d8e0', 'opacity=".25" rx="%.1f"' % (w * .2)); S.rect(x + w * .1, y - h * .6, w * .8, h * .55, c, 'opacity=".75"')
            x += w * S.R.uniform(1.3, 2.2)
    # établi, alambic et cercle de transmutation
    S.rect(0, sol - U * .02, W, U * .04, '#4a3020')
    ax = W * (.5 if P else .36)
    S.circ(ax, sol - U * .12, U * .08, S.rad([(0, '#e8fff0', .9), (.5, '#46d17f', .7), (1, '#1a4a2a', .8)], .35, .3, .7))
    S.halo(ax, sol - U * .12, U * .18, '#46d17f', .45, 'b3')
    S.path('M%.1f %.1fq%.1f %.1f %.1f %.1f' % (ax + U * .05, sol - U * .18, U * .15, -U * .12, U * .25, U * .02), 'none', 'stroke="#c8d8e0" stroke-width="%.1f" opacity=".6"' % (U * .008))
    S.flamme(ax, sol - U * .02, U * .05, '#bff4ff', '#3fb8e0')
    for (x, c) in ((.2, '#ff6f9f'), (.8, '#b9a0f0')):
        bx = W * x
        S.path('M%.1f %.1fh%.1fl%.1f %.1fh%.1fz' % (bx - U * .015, sol - U * .14, U * .03, U * .04, U * .12, -U * .11), '#c8d8e0', 'opacity=".3"')
        S.path('M%.1f %.1fh%.1fl%.1f %.1fh%.1fz' % (bx - U * .035, sol - U * .07, U * .07, U * .02, U * .05, -U * .11), c, 'opacity=".8"')
        for _ in range(4): S.circ(bx + S.R.uniform(-1, 1) * U * .02, sol - U * S.R.uniform(.15, .25), U * .006, c, 'opacity=".7"')
    S.sol(sol, '#3a3a44', '#05060a', 'dalles', lum=(ax, '#46d17f'))
    S.ell(ax, sol + U * .12, U * .3, U * .06, 'none', 'stroke="#46d17f" stroke-width="%.1f" opacity=".6"' % (U * .004))
    S.runes(ax - U * .22, sol + U * .12, U * .44, 8, U * .008, '#46d17f', .7)
    S.lumiere = (ax, sol - U * .12, '#46d17f')

# ================================================================= PALAIS (salle du trône)
def palais(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    Pj, f, vx, vy = couloir(S, .36 if P else .46, .5 if P else .42)
    S.rect(0, 0, W, H, '#1a0e14')
    ZF = 11
    S.poly([Pj(-2.6, 0, ZF), Pj(-2.6, 6, ZF), Pj(2.6, 6, ZF), Pj(2.6, 0, ZF)], '#3a1e24')
    # trône
    t = Pj(0, 0, ZF - .5); s = f / (ZF - .5)
    S.rect(t[0] - s * .5, t[1] - s * 2.4, s, s * 2.4, S.lin([(0, '#c9a227'), (1, '#6a4a10')]))
    S.rect(t[0] - s * .4, t[1] - s * 1.0, s * .8, s * .6, '#8a1a2a'); S.halo(t[0], t[1] - s * 1.4, s * 2, '#ffd36b', .35, 'b3')
    S.path('M%.1f %.1fl%.1f %.1fl%.1f %.1fl%.1f %.1fl%.1f %.1fz' % (t[0] - s * .2, t[1] - s * 2.5, s * .1, -s * .2, s * .1, s * .15, s * .1, -s * .15, s * .1, s * .2), '#ffd36b')
    # colonnes
    for z in (1.6, 2.6, 3.8, 5.2, 7, 9):
        for X in (-2.0, 2.0):
            a, b = Pj(X - .2, 0, z), Pj(X + .2, 5.4, z)
            S.rect(a[0], b[1], b[0] - a[0], a[1] - b[1], S.lin([(0, '#4a3038'), (.5, '#c8b0a0'), (1, '#4a3038')], 0, 0, 1, 0))
            S.rect(a[0] - (b[0] - a[0]) * .2, b[1], (b[0] - a[0]) * 1.4, (b[0] - a[0]) * .3, '#c9a227')
    # tapis rouge et sol de marbre
    S.poly([Pj(-2.6, 0, 1.0), Pj(2.6, 0, 1.0), Pj(2.6, 0, ZF), Pj(-2.6, 0, ZF)], S.lin([(0, '#6a5a5a'), (1, '#1a1014')]))
    for z in (1.4, 2, 2.8, 3.8, 5, 6.6, 8.6):
        S.a('<polyline points="%s" fill="none" stroke="#000" stroke-width="%.1f" opacity=".35"/>' % (pts([Pj(-2.6, 0, z), Pj(2.6, 0, z)]), max(1, f / z * .01)))
    S.poly([Pj(-.6, 0, 1.0), Pj(.6, 0, 1.0), Pj(.6, 0, ZF - .5), Pj(-.6, 0, ZF - .5)], '#8a1a2a')
    S.poly([Pj(-.6, 0, 1.0), Pj(-.5, 0, 1.0), Pj(-.5, 0, ZF - .5), Pj(-.6, 0, ZF - .5)], '#c9a227')
    S.poly([Pj(.5, 0, 1.0), Pj(.6, 0, 1.0), Pj(.6, 0, ZF - .5), Pj(.5, 0, ZF - .5)], '#c9a227')
    # lustres
    for z in (2.4, 4.6):
        c = Pj(0, 5.6, z); s2 = f / z
        S.ell(c[0], c[1], s2 * .5, s2 * .07, '#c9a227')
        for k in range(7):
            x = c[0] - s2 * .45 + k * s2 * .15
            S.flamme(x, c[1] - s2 * .02, s2 * .1)
    S.lumiere = (t[0], t[1] - s * 1.4, '#ffd36b')

# ================================================================= SALLE DU COFFRE AU TRÉSOR
def tresor(S):
    W, H, U, P = S.W, S.H, S.U, S.P
    Pj, f, vx, vy = couloir(S, .36 if P else .5, .5 if P else .42)
    S.rect(0, 0, W, H, '#120c08')
    ZF = 9
    # voûte ronde et murs de pierre dorés par la lumière du coffre
    for z in (8.6, 6.4, 4.6, 3.2, 2.2, 1.4):
        g, dd = Pj(-2.6, 0, z), Pj(2.6, 3.0, z)
        w = dd[0] - g[0]
        d = 'M%.1f %.1fH%.1fV%.1fH%.1fZ M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1fZ' % (-W * .1, -H * .1, W * 1.1, H * 1.1, -W * .1, g[0], g[1], dd[1], w / 2, w * .42, dd[0], dd[1], g[1])
        c = z / ZF
        S.path(d, S.lin([(0, '#2a1e14'), (1, '#4a3420' if c > .4 else '#24180e')]), 'fill-rule="evenodd"')
        S.a('<path d="%s" fill="#000" opacity=".25" filter="url(#texture)" fill-rule="evenodd"/>' % d)
        S.path('M%.1f %.1fV%.1fA%.1f %.1f 0 0 1 %.1f %.1fV%.1f' % (g[0], g[1], dd[1], w / 2, w * .42, dd[0], dd[1], g[1]), 'none', 'stroke="#ffd36b" stroke-width="%.1f" opacity="%.2f"' % (max(1, f / z * .015), .5 * (1 - c * .5)))
        S.runes(g[0] + w * .2, dd[1] - w * .26, w * .6, 9, max(2, f / z * .02), '#ffd36b', .55)
    S.poly([Pj(-2.6, 0, .45), Pj(2.6, 0, .45), Pj(2.6, 0, ZF), Pj(-2.6, 0, ZF)], S.lin([(0, '#5a4024'), (1, '#120c08')]))
    # estrade et grand coffre
    e0, e1 = Pj(-1.6, 0, 4.4), Pj(1.6, .45, 4.4)
    S.rect(e0[0], e1[1], e1[0] - e0[0], e0[1] - e1[1], '#3a2a1c'); S.rect(e0[0], e1[1], e1[0] - e0[0], (e0[1] - e1[1]) * .2, '#6a4a2a')
    c0, c1 = Pj(-1.0, .45, 4.2), Pj(1.0, 1.75, 4.2)
    cw, ch = c1[0] - c0[0], c0[1] - c1[1]
    S.lueur(vx, c1[1], cw * 2.4, '#ffc04a', 1.0)
    S.rect(c0[0], c1[1], cw, ch, S.lin([(0, '#8a5a24'), (1, '#4a2a10')]))
    S.path('M%.1f %.1fQ%.1f %.1f %.1f %.1fZ' % (c0[0], c1[1], vx, c1[1] - ch * .9, c1[0], c1[1]), S.lin([(0, '#9a6a2a'), (1, '#5a3414')]))
    for dx in (.1, .5, .9):
        S.rect(c0[0] + cw * dx - cw * .03, c1[1] - ch * .25, cw * .06, ch * 1.25, '#c9a227')
    S.circ(vx, c1[1] + ch * .35, cw * .07, '#ffd36b'); S.rect(vx - cw * .012, c1[1] + ch * .33, cw * .024, ch * .2, '#2a1808')
    S.runes(c0[0] + cw * .15, c1[1] + ch * .78, cw * .7, 5, cw * .03, '#fff3c4')
    # piles de pièces et gemmes
    for _ in range(140):
        side = S.R.choice([-1, 1]); x = vx + side * S.R.uniform(.55, 1.6) * cw; y = e0[1] + S.R.uniform(-.1, .25) * ch * 2
        S.ell(x, y, cw * .03, cw * .012, S.R.choice(['#ffd36b', '#f4c430', '#c9a227', '#fff3c4']))
    for _ in range(14):
        x = vx + S.R.uniform(-1.6, 1.6) * cw; y = e0[1] + S.R.uniform(0, .3) * ch * 2
        S.poly([(x, y - cw * .03), (x + cw * .025, y), (x, y + cw * .02), (x - cw * .025, y)], S.R.choice(['#ff5c8a', '#5ec8e5', '#46d17f', '#b45cff']))
    # serrures à clés sur le mur du fond (une par clé du Fort)
    b0, b1 = Pj(-1.6, 3.9, 8.6), Pj(1.6, 3.9, 8.6)
    for k in range(10):
        x = b0[0] + (b1[0] - b0[0]) * (k + .5) / 10
        S.circ(x, b0[1], U * .012, '#2a1a0c', 'stroke="#ffd36b" stroke-width="%.1f"' % (U * .002)); S.rect(x - U * .002, b0[1], U * .004, U * .012, '#ffd36b')
    # braseros
    for X in (-1.9, 1.9):
        b = Pj(X, 0, 3.6); s = f / 3.6
        S.poly([(b[0] - s * .2, b[1] - s * .9), (b[0] + s * .2, b[1] - s * .9), (b[0] + s * .08, b[1] - s * .7), (b[0] - s * .08, b[1] - s * .7)], '#3a2a1c')
        S.rect(b[0] - s * .03, b[1] - s * .7, s * .06, s * .7, '#3a2a1c'); S.flamme(b[0], b[1] - s * .9, s * .35)
        S.ombre(b[0], b[1], s * .4)
    S.lucioles(10, W * .2, W * .8, vy - U * .2, vy + U * .2, '#ffe8a0')
    S.lumiere = (vx, c1[1], '#ffc04a')

SALLES = dict(tresor=tresor, bibliotheque=bibliotheque, atlantide=atlantide, farwest=farwest, cirque=cirque, station=station, maya=maya,
              carnaval=carnaval, cite=cite, crypte=crypte, labyrinthe=labyrinthe, jardin=jardin, ruche=ruche, laboratoire=laboratoire, palais=palais)
if __name__ == '__main__':
    nom, W, H, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    S = Scene(W, H, graine=sum(map(ord, nom)))
    SALLES[nom](S)
    S.fin()
    S.ecrire(out)
