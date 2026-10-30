"""Décor original « Le Quartier Néon » — dessiné en vectoriel (SVG) puis rendu en HD.
Ruelle en perspective, enseignes néon, graffitis, câbles, sol mouillé, pluie.
Aucun emprunt : formes, textes et couleurs générés ici. Usage : neon.py W H sortie.svg"""
import sys, random, math
W, H, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
R = random.Random(7)
PORTRAIT = H > W
vx, vy = W * 0.5, H * (0.50 if PORTRAIT else 0.56)
f = (0.62 if PORTRAIT else 0.44) * W
EYE = 1.6
XL, XR = (-2.6, 2.6) if PORTRAIT else (-3.4, 3.4)

def P(X, Y, Z):
    return (vx + f * X / Z, vy - f * (Y - EYE) / Z)
def pts(L):
    return ' '.join('%.1f,%.1f' % p for p in L)
def affine(p00, p10, p01, w, h):
    a = ((p10[0] - p00[0]) / w, (p10[1] - p00[1]) / w); c = ((p01[0] - p00[0]) / h, (p01[1] - p00[1]) / h)
    return 'matrix(%.5f %.5f %.5f %.5f %.2f %.2f)' % (a[0], a[1], c[0], c[1], p00[0], p00[1])

NEONS = ['#ff2ec4', '#29e7ff', '#b45cff', '#ff8a3d', '#3dff9e', '#ffe14d']
out = []
A = out.append
A('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H))
A('''<defs>
<linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0618"/><stop offset=".45" stop-color="#2a0f45"/><stop offset=".8" stop-color="#6b1f6e"/><stop offset="1" stop-color="#c23c86"/></linearGradient>
<linearGradient id="sol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b1840"/><stop offset=".25" stop-color="#140c22"/><stop offset="1" stop-color="#07050d"/></linearGradient>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff5fc8" stop-opacity=".55"/><stop offset=".5" stop-color="#7b3bff" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<linearGradient id="brume" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a4fd0" stop-opacity="0"/><stop offset=".5" stop-color="#b86ad8" stop-opacity=".22"/><stop offset="1" stop-color="#3a1a5a" stop-opacity="0"/></linearGradient>
<linearGradient id="reflet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="vignette" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>
<filter id="g1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="%s"/></filter>
<filter id="g2" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="%s"/></filter>
<filter id="g3" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="%s"/></filter>
<filter id="refl" x="-50%" y="-10%" width="200%" height="140%"><feGaussianBlur stdDeviation="%s %s"/></filter>
<filter id="spray"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.25"/><feComposite in="SourceGraphic" operator="in"/></filter>
<filter id="crepi" x="0" y="0" width="100%%" height="100%%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="4" seed="11"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 -.18"/></filter>
</defs>'''.replace('%s', '{}').format(W * .002, W * .006, W * .016, W * .004, W * .03).replace('%%', '%'))

# --- ciel et ville lointaine ---
A('<rect width="%d" height="%d" fill="url(#ciel)"/>' % (W, H))
for i in range(int(W / 6)):
    A('<circle cx="%.1f" cy="%.1f" r="%.2f" fill="#fff" opacity="%.2f"/>' % (R.uniform(0, W), R.uniform(0, vy * .55), R.uniform(.4, 1.3) * W / 1300, R.uniform(.15, .6)))
for couche, (zf, col, op) in enumerate([(90, '#3a1d5c', .9), (70, '#2a1446', 1), (55, '#1d0f33', 1)]):
    x = -W * .05
    while x < W * 1.05:
        bw = R.uniform(.035, .09) * W; bh = R.uniform(.12, .42) * H * (1.15 - couche * .18)
        top = vy + H * .02 - bh
        A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="%.2f"/>' % (x, top, bw, vy + H * .1 - top, col, op))
        if R.random() < .35:
            A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (x + bw * .45, top - bh * .12, bw * .08, bh * .12, col))
        for wy in range(int(bh / (H * .012))):
            for wx in range(int(bw / (W * .012))):
                if R.random() < .16 + couche * .05:
                    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="%.2f"/>' % (
                        x + W * .004 + wx * W * .012, top + H * .006 + wy * H * .012, W * .005, H * .005,
                        R.choice(['#ffd9a0', '#9ff3ff', '#ff9be6', '#ffffff']), R.uniform(.35, .85)))
        x += bw + R.uniform(0, .01) * W
A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#halo)"/>' % (vx, vy - H * .02, W * .55, H * .2))
A('<rect x="0" y="%.1f" width="%d" height="%.1f" fill="url(#brume)"/>' % (vy - H * .2, W, H * .32))

# --- sol ---
A('<polygon points="%s" fill="url(#sol)"/>' % pts([P(XL - 6, 0, 60), P(XR + 6, 0, 60), (W * 1.5, H), (-W * .5, H)]))

# --- murs (du fond vers l'avant) ---
def facade(side, z0, z1, h, teinte):
    X = XL if side < 0 else XR
    poly = [P(X, 0, z0), P(X, h, z0), P(X, h, z1), P(X, 0, z1)]
    A('<polygon points="%s" fill="%s"/>' % (pts(poly), teinte))
    A('<polygon points="%s" fill="#000" opacity=".25" filter="url(#crepi)"/>' % pts(poly))
    # corniche
    A('<polygon points="%s" fill="#000" opacity=".35"/>' % pts([P(X, h - .25, z0), P(X, h, z0), P(X, h, z1), P(X, h - .25, z1)]))
    # fenêtres
    etages = int((h - 3) / 3)
    for e in range(etages):
        y0 = 3.2 + e * 3
        n = max(1, int((z1 - z0) / 2.2))
        for k in range(n):
            za = z0 + (k + .25) * (z1 - z0) / n; zb = za + (z1 - z0) / n * .5
            if za < 2.6: continue
            allume = R.random() < .45
            col = R.choice(['#ffcf8a', '#8ff0ff', '#ff9ad8', '#c7a6ff']) if allume else '#120a1f'
            q = [P(X, y0, za), P(X, y0 + 1.5, za), P(X, y0 + 1.5, zb), P(X, y0, zb)]
            A('<polygon points="%s" fill="%s" opacity="%.2f"/>' % (pts(q), col, .85 if allume else .9))
            if allume:
                A('<polygon points="%s" fill="%s" opacity=".35" filter="url(#g2)"/>' % (pts(q), col))
                zm = (za + zb) / 2; lw = max(1, f / za * .06)
                A('<polyline points="%s" fill="none" stroke="#1a1028" stroke-width="%.1f"/>' % (pts([P(X, y0, zm), P(X, y0 + 1.5, zm)]), lw))
                A('<polyline points="%s" fill="none" stroke="#1a1028" stroke-width="%.1f"/>' % (pts([P(X, y0 + .9, za), P(X, y0 + .9, zb)]), lw))
                A('<polygon points="%s" fill="#000" opacity=".28"/>' % pts([P(X, y0, za), P(X, y0 + .45, za), P(X, y0 + .45, zb), P(X, y0, zb)]))
                # store / silhouette de plante
                if R.random() < .4:
                    A('<polygon points="%s" fill="#000" opacity=".35"/>' % pts([P(X, y0 + .9, za), P(X, y0 + 1.5, za), P(X, y0 + 1.5, zb), P(X, y0 + .9, zb)]))
    # gouttière
    zg = z0 + .15
    A('<polyline points="%s" fill="none" stroke="#120c1c" stroke-width="%.1f"/>' % (pts([P(X, 0, zg), P(X, h, zg)]), max(1.5, f / zg * .07)))
    # climatiseurs
    for _ in range(R.randint(0, 3)):
        za = R.uniform(z0 + .5, max(z0 + .6, z1 - 1.2)); ya = R.choice([4.2, 7.2, 10.2])
        if ya + 1 > h: continue
        q = [P(X, ya, za), P(X, ya + .7, za), P(X, ya + .7, za + .9), P(X, ya, za + .9)]
        A('<polygon points="%s" fill="#4a4258"/>' % pts(q))
        A('<polygon points="%s" fill="#000" opacity=".3"/>' % pts([P(X, ya, za), P(X, ya + .2, za), P(X, ya + .2, za + .9), P(X, ya, za + .9)]))
    # escalier de secours
    if R.random() < .45 and z1 - z0 > 4:
        za, zb = z0 + 1, z0 + 3.4
        for e in range(1, etages + 1):
            yy = 3 + e * 3 - .2
            if yy > h - 1: break
            A('<polyline points="%s" fill="none" stroke="#0a0710" stroke-width="%.1f"/>' % (pts([P(X, yy, za), P(X, yy, zb)]), max(1.2, f / za * .05)))
            A('<polyline points="%s" fill="none" stroke="#0a0710" stroke-width="%.1f"/>' % (pts([P(X, yy + 1, za), P(X, yy + 1, zb)]), max(1, f / za * .025)))
            A('<polyline points="%s" fill="none" stroke="#0a0710" stroke-width="%.1f"/>' % (pts([P(X, yy, zb), P(X, yy + 3, za)]), max(1, f / za * .03)))
    # rez-de-chaussée : vitrine ou rideau métallique
    zA = z0 + (z1 - z0) * .15; zB = z1 - (z1 - z0) * .15
    if R.random() < .55 and zA > 2.2:
        col = R.choice(NEONS)
        q = [P(X, .1, zA), P(X, 2.3, zA), P(X, 2.3, zB), P(X, .1, zB)]
        A('<polygon points="%s" fill="%s" opacity=".22"/>' % (pts(q), col))
        A('<polygon points="%s" fill="none" stroke="%s" stroke-width="%.1f" opacity=".9"/>' % (pts(q), col, min(W * .006, max(1, f / zA * .02))))
        A('<polygon points="%s" fill="none" stroke="%s" stroke-width="%.1f" opacity=".6" filter="url(#g1)"/>' % (pts(q), col, min(W * .015, max(2, f / zA * .05))))
    else:
        for s in range(14):
            yy = .1 + s * .16
            A('<polyline points="%s" fill="none" stroke="#3a3348" stroke-width="%.1f"/>' % (pts([P(X, yy, zA), P(X, yy, zB)]), max(.8, f / z0 * .018)))
        A('<polygon points="%s" fill="#5a5168" opacity=".35"/>' % pts([P(X, .1, zA), P(X, 2.4, zA), P(X, 2.4, zB), P(X, .1, zB)]))
    return poly

def tableau_mur(side, z, y, w, h):
    """renvoie la transformation qui pose un repère local (w×h px virtuels) sur le mur"""
    X = XL if side < 0 else XR
    if side < 0:
        p00, p10, p01 = P(X, y + h, z), P(X, y + h, z + w), P(X, y, z)
    else:
        p00, p10, p01 = P(X, y + h, z + w), P(X, y + h, z), P(X, y, z + w)
    return p00, p10, p01

def enseigne_drapeau(side, z, y, larg, haut, texte, col, vertical):
    X = (XL + .15) if side < 0 else (XR - .15 - larg)
    x0, y0 = P(X, y + haut, z); x1, y1 = P(X + larg, y, z)
    w, h = x1 - x0, y1 - y0
    sw = max(1.2, w * .035)
    # potence
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a1424" stroke-width="%.1f"/>' % (*P(XL if side < 0 else XR, y + haut + .1, z), *(P(X + (larg if side < 0 else 0), y + haut + .1, z)), sw))
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="#0d0816"/>' % (x0, y0, w, h, w * .08))
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="none" stroke="%s" stroke-width="%.1f" filter="url(#g2)" opacity=".9"/>' % (x0, y0, w, h, w * .08, col, sw * 3))
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="none" stroke="%s" stroke-width="%.1f"/>' % (x0, y0, w, h, w * .08, col, sw))
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="none" stroke="#fff" stroke-width="%.1f" opacity=".7"/>' % (x0, y0, w, h, w * .08, sw * .35))
    if vertical:
        n = len(texte); fs = min(w * .62, h / n * .82)
        for i, ch in enumerate(texte):
            cy = y0 + h * (i + .5) / n + fs * .35
            for flt, op, coul in (('url(#g2)', .95, col), ('', 1, '#fff')):
                A('<text x="%.1f" y="%.1f" font-family="Inter Display, DejaVu Sans" font-weight="900" font-size="%.1f" text-anchor="middle" fill="%s" opacity="%.2f" %s>%s</text>' % (
                    x0 + w / 2, cy, fs, coul, op, ('filter="%s"' % flt) if flt else ('stroke="%s" stroke-width="%.1f"' % (col, fs * .06)), ch))
    else:
        fs = min(h * .55, w / max(1, len(texte)) * 1.5)
        for flt, coul in (('url(#g2)', col), ('', '#fff')):
            A('<text x="%.1f" y="%.1f" font-family="Inter Display, DejaVu Sans" font-weight="900" font-size="%.1f" text-anchor="middle" fill="%s" %s>%s</text>' % (
                x0 + w / 2, y0 + h / 2 + fs * .36, fs, coul, ('filter="%s"' % flt) if flt else ('stroke="%s" stroke-width="%.1f"' % (col, fs * .05)), texte))
    # halo sur le mur et reflet au sol
    A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".22" filter="url(#g3)"/>' % (x0 + w / 2, y0 + h / 2, w * 1.4, h * .8, col))
    fx, fy = P(X + larg / 2, 0, z)
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".45" filter="url(#refl)"/>' % (fx - w * .35, fy, w * .7, min(H - fy, h * 1.4), col))
    return (x0, y0, w, h)

def graffiti(side, z, y, larg, haut, mot, c1, c2):
    p00, p10, p01 = tableau_mur(side, z, y, larg, haut)
    VW, VH = 1000, 1000 * haut / larg
    tr = affine(p00, p10, p01, VW, VH)
    fs = min(VH * .9, VW / len(mot) * 1.55)
    g = ['<g transform="%s">' % tr]
    # éclaboussures et coulures
    for _ in range(26):
        g.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f"/>' % (R.uniform(0, VW), R.uniform(0, VH), R.uniform(3, 22), R.choice([c1, c2, '#ffffff']), R.uniform(.3, .8)))
    g.append('<text x="%.1f" y="%.1f" font-family="Inter Display, DejaVu Sans" font-weight="900" font-style="italic" font-size="%.1f" text-anchor="middle" fill="#0a0612" stroke="#0a0612" stroke-width="%.1f" stroke-linejoin="round" transform="rotate(-6 %.1f %.1f)">%s</text>' % (VW / 2 + 8, VH * .78 + 8, fs, fs * .16, VW / 2, VH / 2, mot))
    g.append('<text x="%.1f" y="%.1f" font-family="Inter Display, DejaVu Sans" font-weight="900" font-style="italic" font-size="%.1f" text-anchor="middle" fill="%s" stroke="#ffffff" stroke-width="%.1f" stroke-linejoin="round" paint-order="stroke" transform="rotate(-6 %.1f %.1f)">%s</text>' % (VW / 2, VH * .78, fs, c1, fs * .07, VW / 2, VH / 2, mot))
    g.append('<text x="%.1f" y="%.1f" font-family="Inter Display, DejaVu Sans" font-weight="900" font-style="italic" font-size="%.1f" text-anchor="middle" fill="%s" opacity=".55" transform="rotate(-6 %.1f %.1f)" clip-path="inset(55%% 0 0 0)">%s</text>' % (VW / 2, VH * .78, fs, c2, VW / 2, VH / 2, mot))
    for _ in range(14):
        x = R.uniform(VW * .1, VW * .9); y0 = R.uniform(VH * .6, VH * .85)
        g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" stroke-linecap="round" opacity=".8"/>' % (x, y0, x, y0 + R.uniform(30, 160), R.choice([c1, c2]), R.uniform(3, 7)))
    g.append('</g>')
    out.extend(g)

# bâtiment du fond de la ruelle (face caméra)
zf = 46
x0, y0 = P(XL - .2, 16, zf); x1, y1 = P(XR + .2, 0, zf)
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#1b0f2c"/>' % (x0, y0, x1 - x0, y1 - y0))
for r_ in range(10):
    for c_ in range(6):
        if R.random() < .5:
            A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".8"/>' % (x0 + (x1 - x0) * (c_ + .25) / 6, y0 + (y1 - y0) * (r_ + .3) / 10.5, (x1 - x0) / 6 * .5, (y1 - y0) / 10.5 * .45, R.choice(['#ffcf8a', '#8ff0ff', '#ff9ad8'])))
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ff2ec4" opacity=".55" filter="url(#g3)"/>' % (x0, y1 - (y1 - y0) * .2, x1 - x0, (y1 - y0) * .2))

segs = {-1: [], 1: []}
for side in (-1, 1):
    z = 44
    while z > 1.0:
        lz = R.uniform(4, 9); h = R.uniform(9, 17)
        segs[side].append((max(1.2, z - lz), z, h))
        z -= lz
murs = []
for side in (-1, 1):
    for (z0, z1, h) in segs[side]:
        teinte = R.choice(['#2b1a3d', '#24183a', '#311c3b', '#1f1730', '#2d2140'])
        murs.append((z0, side, z1, h, teinte))
murs.sort(key=lambda m: -m[0])

# câbles (en arrière-plan des enseignes proches)
def cables():
    for _ in range(9):
        z = R.uniform(4, 30); ya = R.uniform(5, 11); yb = ya + R.uniform(-1.5, 1.5)
        a = P(XL, ya, z); b = P(XR, yb, z * R.uniform(.85, 1.15))
        mx, my = (a[0] + b[0]) / 2, max(a[1], b[1]) + f / z * R.uniform(.6, 1.6)
        A('<path d="M%.1f %.1fQ%.1f %.1f %.1f %.1f" fill="none" stroke="#07040c" stroke-width="%.1f" opacity=".9"/>' % (a[0], a[1], mx, my, b[0], b[1], max(1, f / z * .03)))

TEXTES_G = ['ÉNIGMES', 'ARCADE', 'NUIT', 'RAMEN', 'BAR', 'HÔTEL', 'JEUX', 'OUVERT', 'KARAOKÉ', 'CLÉS', 'FORT', 'ÉCHO']
graffs = [('FORT', '#29e7ff', '#ff2ec4'), ('ÉNIGME', '#ffe14d', '#ff8a3d'), ('GARDIEN', '#3dff9e', '#b45cff'), ('CLÉ', '#ff2ec4', '#ffe14d')]
dessine_cables = False
for i, (z0, side, z1, h, teinte) in enumerate(murs):
    if not dessine_cables and z0 < 22:
        cables(); dessine_cables = True
    facade(side, z0, z1, h, teinte)
    if z1 - z0 > 3 and 2.6 < z0 < 16 and graffs and R.random() < .8:
        mot, c1, c2 = graffs.pop(0)
        graffiti(side, z0 + .4, .25, min(z1 - z0 - .8, 1.3 * len(mot)), 1.9, mot, c1, c2)
# enseignes (de loin vers près)
ens = []
for side in (-1, 1):
    z = R.uniform(30, 38)
    while z > (3.4 if PORTRAIT else 5.5):
        ens.append((z, side))
        z -= R.uniform(3.2, 6.5)
ens.sort(key=lambda e: -e[0])
for k, (z, side) in enumerate(ens):
    vert = R.random() < .6
    txt = TEXTES_G[k % len(TEXTES_G)]
    if vert:
        txt = txt[:6]
        enseigne_drapeau(side, z, R.uniform(3.2, 5), .75, .7 * len(txt), txt, NEONS[k % len(NEONS)], True)
    else:
        enseigne_drapeau(side, z, R.uniform(3, 6), 1.9, .75, txt, NEONS[k % len(NEONS)], False)

# trottoirs
for X in (XL + 1.1, XR - 1.1):
    A('<polyline points="%s" fill="none" stroke="#3b2a52" stroke-width="%.1f" opacity=".8"/>' % (pts([P(X, 0, 1.0), P(X, 0, 46)]), W * .004))
    A('<polygon points="%s" fill="#1d1430" opacity=".6"/>' % pts([P(X, 0, 1.0), P(X, 0, 46), P(XL if X < 0 else XR, 0, 46), P(XL if X < 0 else XR, 0, 1.0)]))
# reflet humide de la lueur du fond
A('<polygon points="%s" fill="#ff6fd0" opacity=".16" filter="url(#g3)"/>' % pts([P(-1.2, 0, 44), P(1.2, 0, 44), P(2.2, 0, 1.6), P(-2.2, 0, 1.6)]))
A('<polygon points="%s" fill="#7f9bff" opacity=".10" filter="url(#g3)"/>' % pts([P(-.4, 0, 44), P(.4, 0, 44), P(.9, 0, 1.6), P(-.9, 0, 1.6)]))
# flaques et reflets du sol
for _ in range(26):
    z = R.uniform(1.6, 30); X = R.uniform(XL + .3, XR - .3)
    cx, cy = P(X, 0, z); rx = f / z * R.uniform(.4, 1.3); ry = rx * .12 * (vy / H + .2)
    A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".2" filter="url(#g1)"/>' % (cx, cy, rx, ry * .7, R.choice(['#ff5fc8', '#7fe9ff', '#b07cff'])))
cx, cy = P(0, 0, 8)
A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#ff7ad9" opacity=".18" filter="url(#g3)"/>' % (vx, vy + (H - vy) * .25, W * .25, (H - vy) * .3))
# bouche d'égout et vapeur
mx, my = P(XL * .35, 0, 4.5)
A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#0a0710" stroke="#3a3348" stroke-width="3"/>' % (mx, my, f / 4.5 * .45, f / 4.5 * .45 * .28))
for i in range(7):
    A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#e9d8ff" opacity="%.2f" filter="url(#g3)"/>' % (mx + R.uniform(-1, 1) * W * .03, my - i * H * .045, W * (.05 + i * .012), H * .03, .16 - i * .015))
# silhouettes au loin (passants avec parapluie)
for (X, z, coul) in ((-.9, 17, '#ff2ec4'), (1.1, 23, '#29e7ff')):
    bx, by = P(X, 0, z); s = f / z
    A('<g fill="#07040d"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f"/><circle cx="%.1f" cy="%.1f" r="%.1f"/></g>' % (bx - s * .22, by - s * 1.45, s * .44, s * 1.45, s * .15, bx, by - s * 1.6, s * .14))
    A('<path d="M%.1f %.1fQ%.1f %.1f %.1f %.1fZ" fill="#07040d" stroke="%s" stroke-width="%.1f" opacity=".95"/>' % (bx - s * .6, by - s * 1.75, bx, by - s * 2.35, bx + s * .6, by - s * 1.75, coul, max(1, s * .03)))
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#07040d" stroke-width="%.1f"/>' % (bx, by - s * 1.75, bx, by - s * 1.1, max(1, s * .03)))
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".3" filter="url(#refl)"/>' % (bx - s * .2, by, s * .4, s * 1.2, '#07040d'))

# pluie
for _ in range(int(W * H / 2600)):
    x = R.uniform(-W * .1, W * 1.1); y = R.uniform(-H * .05, H); l = R.uniform(.012, .035) * H
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#d8ccff" stroke-width="%.2f" opacity="%.2f"/>' % (x, y, x - l * .18, y + l, R.uniform(.6, 1.6) * W / 1300, R.uniform(.08, .28)))
A('<rect width="%d" height="%d" fill="url(#vignette)"/>' % (W, H))
A('</svg>')
open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
