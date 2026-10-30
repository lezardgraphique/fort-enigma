"""Décor original « La Veillée Nocturne » — terrasse du Fort sous la pleine lune.
Ciel étoilé et Voie lactée, lune, nuages, chaînes de montagnes enneigées, brume,
remparts en pierre, tourelle, lanterne, lunette astronomique, lueurs.
Entièrement dessiné ici (vectoriel), rendu en HD. Usage : nocturne.py W H sortie.svg"""
import sys, random, math
W, H, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
R = random.Random(21)
PORTRAIT = H > W
U = min(W, H)
HZ = H * (0.50 if PORTRAIT else 0.60)       # ligne des montagnes
PAR = H * (0.66 if PORTRAIT else 0.74)      # haut du parapet
o = []; A = o.append
A('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H))
A('''<defs>
<linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05071a"/><stop offset=".45" stop-color="#121a44"/><stop offset=".8" stop-color="#2d3c78"/><stop offset="1" stop-color="#4a5d9c"/></linearGradient>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#e8ecff" stop-opacity=".55"/><stop offset=".25" stop-color="#b9c6ff" stop-opacity=".22"/><stop offset="1" stop-color="#8090ff" stop-opacity="0"/></radialGradient>
<radialGradient id="lune" cx=".42" cy=".38" r=".62"><stop offset="0" stop-color="#fffdf2"/><stop offset=".7" stop-color="#e9e8de"/><stop offset="1" stop-color="#c4c8d4"/></radialGradient>
<linearGradient id="m1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9c6ec"/><stop offset=".18" stop-color="#7183b8"/><stop offset="1" stop-color="#3a4778"/></linearGradient>
<linearGradient id="m2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fb0e0"/><stop offset=".14" stop-color="#4b5c92"/><stop offset="1" stop-color="#232d58"/></linearGradient>
<linearGradient id="m3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4c5d92"/><stop offset=".2" stop-color="#1f2850"/><stop offset="1" stop-color="#121835"/></linearGradient>
<linearGradient id="brume" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9aa9e0" stop-opacity="0"/><stop offset=".55" stop-color="#9aa9e0" stop-opacity=".35"/><stop offset="1" stop-color="#9aa9e0" stop-opacity="0"/></linearGradient>
<linearGradient id="pierre" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6d7392"/><stop offset=".08" stop-color="#4a4f6c"/><stop offset="1" stop-color="#22253a"/></linearGradient>
<linearGradient id="dalle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2d45"/><stop offset="1" stop-color="#11121f"/></linearGradient>
<linearGradient id="laiton" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2d58a"/><stop offset=".45" stop-color="#b88a3c"/><stop offset="1" stop-color="#5a3f18"/></linearGradient>
<radialGradient id="feu" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd27a" stop-opacity=".9"/><stop offset=".3" stop-color="#ff9a3c" stop-opacity=".35"/><stop offset="1" stop-color="#ff7a1a" stop-opacity="0"/></radialGradient>
<radialGradient id="vignette" cx=".5" cy=".45" r=".78"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>
<filter id="b1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{b1}"/></filter>
<filter id="b2" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{b2}"/></filter>
<filter id="b3" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="{b3}"/></filter>
<filter id="voie" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="{vf}" numOctaves="5" seed="4"/><feColorMatrix values="0 0 0 0 .78  0 0 0 0 .80  0 0 0 0 1  0 0 0 1.1 -.42"/><feGaussianBlur stdDeviation="{b1}"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".6" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .5 -.12"/><feComposite in2="SourceGraphic" operator="in"/></filter>
<filter id="nuage" x="-20%" y="-50%" width="140%" height="200%"><feTurbulence type="fractalNoise" baseFrequency="{nf}" numOctaves="4" seed="2"/><feDisplacementMap in="SourceGraphic" scale="{nd}"/><feGaussianBlur stdDeviation="{b2}"/></filter>
<mask id="bande"><rect width="100%" height="100%" fill="#000"/><ellipse cx="0" cy="0" rx="{brx}" ry="{bry}" fill="#fff" filter="url(#b3)" transform="translate({bx} {by}) rotate(-28)"/></mask>
</defs>'''.format(b1=U * .002, b2=U * .007, b3=U * .02, vf=4.0 / U, nf=3.0 / U, nd=U * .06,
                   brx=max(W, H) * .75, bry=U * .13, bx=W * .45, by=H * (.22 if PORTRAIT else .3)))

A('<rect width="%d" height="%d" fill="url(#ciel)"/>' % (W, H))
# Voie lactée : texture nuageuse dans une bande + amas d'étoiles
A('<g mask="url(#bande)"><rect width="%d" height="%d" filter="url(#voie)" opacity=".75"/></g>' % (W, H))
ang = math.radians(-28); cx0, cy0 = W * .45, H * (.22 if PORTRAIT else .3)
for _ in range(int(W * H / 900)):
    t = R.uniform(-1, 1) * max(W, H) * .8; d = R.gauss(0, U * .06)
    x = cx0 + t * math.cos(ang) - d * math.sin(ang); y = cy0 + t * math.sin(ang) + d * math.cos(ang)
    if 0 <= x <= W and 0 <= y <= HZ:
        A('<circle cx="%.1f" cy="%.1f" r="%.2f" fill="#e8eeff" opacity="%.2f"/>' % (x, y, R.uniform(.3, .9) * U / 1100, R.uniform(.25, .8)))
# étoiles
for _ in range(int(W * H / 2200)):
    x, y = R.uniform(0, W), R.uniform(0, HZ * 1.02) ** 1 if True else 0
    r = R.choice([.5, .6, .8, 1, 1.3, 1.8]) * U / 1100
    A('<circle cx="%.1f" cy="%.1f" r="%.2f" fill="%s" opacity="%.2f"/>' % (x, y, r, R.choice(['#ffffff', '#dfe6ff', '#fff3d6', '#cfe0ff']), R.uniform(.45, 1) * (1 - y / HZ * .5)))
for _ in range(14):
    x, y = R.uniform(0, W), R.uniform(0, HZ * .8); s = R.uniform(.006, .014) * U
    A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#dfe6ff" opacity=".5" filter="url(#b1)"/>' % (x, y, s * .4))
    A('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZM%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="#fff" opacity=".9"/>' % (
        x - s, y, x, y - s * .08, x + s, y, x, y + s * .08, x, y - s, x + s * .08, y, x, y + s, x - s * .08, y))
# étoile filante
sx, sy = W * .18, H * (.08 if PORTRAIT else .12); L = U * .28
A('<linearGradient id="filante" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".95"/></linearGradient>')
A('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="url(#filante)"/>' % (sx + L, sy - L * .35, sx, sy - U * .002, sx + U * .002, sy + U * .002))
A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" filter="url(#b1)"/>' % (sx, sy, U * .004))
# nuages éclairés par la lune
for (cx, cy, rx, ry, op) in [(.62, .26, .32, .022, .55), (.86, .3, .22, .016, .45), (.3, .34, .3, .02, .4), (.55, .4, .4, .025, .35), (.12, .22, .2, .014, .3)]:
    cy = cy * (HZ / .6 / H) * H
    A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#2b3566" opacity="%.2f" filter="url(#nuage)"/>' % (cx * W, cy, rx * W, ry * H * 2.2, op * .7))
    A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#c9d3ff" opacity="%.2f" filter="url(#nuage)"/>' % (cx * W, cy - ry * H * .9, rx * W * .8, ry * H * .8, op * .55))

# lune
mx, my, mr = W * (.70 if PORTRAIT else .74), H * (.17 if PORTRAIT else .2), U * (.085 if PORTRAIT else .075)
A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#halo)"/>' % (mx, my, mr * 6))
A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#lune)"/>' % (mx, my, mr))
A('<clipPath id="disque"><circle cx="%.1f" cy="%.1f" r="%.1f"/></clipPath><g clip-path="url(#disque)">' % (mx, my, mr))
A('<g filter="url(#b1)" fill="#8a8fa3">')
for (dx, dy, rx, ry, rot, op) in [(-.32, -.18, .30, .17, 25, .22), (-.05, -.02, .22, .12, -10, .18), (.22, .12, .16, .24, 40, .2), (-.18, .32, .2, .09, 5, .15), (.38, -.32, .1, .07, 0, .14), (.05, .5, .12, .06, 15, .12)]:
    A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" opacity="%.2f" transform="rotate(%d %.1f %.1f)"/>' % (mx + dx * mr, my + dy * mr, rx * mr, ry * mr, op, rot, mx + dx * mr, my + dy * mr))
A('</g>')
for _ in range(7):
    a, d = R.uniform(0, 6.3), R.uniform(.2, .8) * mr; rr = R.uniform(.03, .06) * mr
    cx_, cy_ = mx + d * math.cos(a), my + d * math.sin(a)
    A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#9a9fb2" opacity=".25"/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" opacity=".35"/>' % (cx_, cy_, rr, cx_ + rr * .3, cy_ + rr * .3, rr * .5))
A('</g>')
# montagnes : déplacement du point milieu
def crete(y_base, amp, rugosite, graine, n=9, sommets=4):
    rr = random.Random(graine)
    pics = [(rr.uniform(-.05, 1.05) * W, rr.uniform(.45, 1) * amp * 2.2, rr.uniform(.08, .2) * W) for _ in range(sommets)]
    def haut(x): return max([0] + [h * max(0, 1 - abs(x - px) / lw) for px, h, lw in pics])
    pts_ = [(x, y_base - haut(x)) for x in [i * W / 16 for i in range(17)]]
    a = amp * .35
    for _ in range(n - 4):
        nouv = []
        for (x0, y0), (x1, y1) in zip(pts_, pts_[1:]):
            nouv += [(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + rr.uniform(-a, a))]
        nouv.append(pts_[-1]); pts_ = nouv; a *= rugosite
    return pts_
def chaine(pts_, fond_y, grad, liseré, op_lis):
    d = 'M0 %.1f ' % fond_y + ' '.join('L%.1f %.1f' % p for p in pts_) + ' L%d %.1fZ' % (W, fond_y)
    A('<path d="%s" fill="url(#%s)"/>' % (d, grad))
    A('<path d="%s" fill="#000" opacity=".25" filter="url(#grain)"/>' % d)
    # liseré de lune côté droit des crêtes
    seg = []
    for (x0, y0), (x1, y1) in zip(pts_, pts_[1:]):
        if y1 < y0: seg.append('M%.1f %.1fL%.1f %.1f' % (x0, y0, x1, y1))
    A('<path d="%s" stroke="%s" stroke-width="%.1f" opacity="%.2f" fill="none" stroke-linecap="round"/>' % (' '.join(seg), liseré, U * .0025, op_lis))
c1 = crete(HZ - U * .05, U * .14, .55, 5, sommets=5)
chaine(c1, H, 'm1', '#f4f7ff', .7)
A('<rect x="0" y="%.1f" width="%d" height="%.1f" fill="url(#brume)"/>' % (HZ - U * .06, W, U * .14))
c2 = crete(HZ + U * .02, U * .09, .52, 8, sommets=4)
chaine(c2, H, 'm2', '#e3e9ff', .55)
A('<rect x="0" y="%.1f" width="%d" height="%.1f" fill="url(#brume)" opacity=".8"/>' % (HZ + U * .01, W, U * .12))
c3 = crete(HZ + U * .09, U * .05, .5, 13, sommets=5)
chaine(c3, H, 'm3', '#aab6e8', .35)
# lumières d'un village dans la vallée
for _ in range(18):
    x = R.uniform(.15, .85) * W; y = HZ + U * R.uniform(.11, .15)
    A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffcf7a" opacity="%.2f"/>' % (x, y, U * .0018, R.uniform(.5, .9)))
    A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffb347" opacity=".25" filter="url(#b1)"/>' % (x, y, U * .006))

# tourelle du Fort (bord gauche)
tx, tw = W * (.02 if PORTRAIT else .04), U * .17
tt = PAR - U * .42
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#pierre)"/>' % (tx, tt, tw, H - tt))
for k in range(int((H - tt) / (U * .03))):
    yy = tt + k * U * .03
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#15172a" stroke-width="%.1f" opacity=".6"/>' % (tx, yy, tx + tw, yy, U * .0015))
    off = (k % 2) * U * .035
    for j in range(5):
        xx = tx + off + j * U * .07
        if xx < tx + tw: A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#15172a" stroke-width="%.1f" opacity=".5"/>' % (xx, yy, xx, yy + U * .03, U * .0015))
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" opacity=".12"/>' % (tx + tw * .82, tt, tw * .18, H - tt))
A('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="#1c2140"/>' % (tx - tw * .12, tt, tx + tw / 2, tt - U * .2, tx + tw * 1.12, tt))
A('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="#8fa0d8" opacity=".35"/>' % (tx + tw / 2, tt - U * .2, tx + tw * 1.12, tt, tx + tw * .62, tt))
A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1c2140" stroke-width="%.1f"/>' % (tx + tw / 2, tt - U * .2, tx + tw / 2, tt - U * .25, U * .004))
A('<path d="M%.1f %.1fl%.1f %.1fl0 %.1fZ" fill="#a33a4a"/>' % (tx + tw / 2, tt - U * .25, U * .045, U * .012, U * .024))
wx, wy = tx + tw * .38, tt + U * .08
A('<path d="M%.1f %.1fv%.1fh%.1fv%.1fa%.1f %.1f 0 0 0 %.1f 0Z" fill="#ffc46b"/>' % (wx, wy + U * .06, -U * .04, tw * .24, U * .04, tw * .12, tw * .12, -tw * .24))
A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#feu)" opacity=".7"/>' % (wx + tw * .12, wy + U * .03, U * .08, U * .08))

# parapet crénelé
mh = U * .07; mw = U * .085; ep = U * .02
A('<rect x="0" y="%.1f" width="%d" height="%.1f" fill="url(#pierre)"/>' % (PAR, W, H - PAR))
x = tx + tw
while x < W:
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#pierre)"/>' % (x, PAR - mh, mw, mh + 2))
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c9d3ff" opacity=".28"/>' % (x, PAR - mh, mw, U * .006))
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#000" opacity=".25"/>' % (x + mw * .82, PAR - mh, mw * .18, mh))
    x += mw * 1.9
A('<rect x="0" y="%.1f" width="%d" height="%.1f" fill="#c9d3ff" opacity=".22"/>' % (PAR, W, U * .005))
# appareil de pierres du parapet
bh = U * .035
for k in range(int((H - PAR) / bh) + 1):
    yy = PAR + k * bh
    A('<line x1="0" y1="%.1f" x2="%d" y2="%.1f" stroke="#141625" stroke-width="%.1f" opacity=".55"/>' % (yy, W, yy, U * .0018))
    xx = (k % 2) * U * .05 - U * .02
    while xx < W:
        lw = U * R.uniform(.08, .13)
        A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".18"/>' % (xx, yy, lw, bh, R.choice(['#8b90b0', '#2a2d44', '#5d6284', '#3b3f5c'])))
        A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#141625" stroke-width="%.1f" opacity=".5"/>' % (xx, yy, xx, yy + bh, U * .0018))
        xx += lw
A('<rect x="0" y="%.1f" width="%d" height="%.1f" fill="#000" opacity=".3" filter="url(#grain)"/>' % (PAR - mh, W, H - PAR + mh))

# lanterne posée sur un merlon
lx = W * (.84 if PORTRAIT else .62); ly = PAR - mh
A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#feu)"/>' % (lx, ly - U * .04, U * .16, U * .14))
lw_, lh_ = U * .032, U * .05
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="#ffd27a" stroke="#2a1d10" stroke-width="%.1f"/>' % (lx - lw_ / 2, ly - lh_, lw_, lh_, U * .004, U * .004))
A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a1d10" stroke-width="%.1f"/>' % (lx, ly - lh_, lx, ly, U * .003))
A('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="#2a1d10"/>' % (lx - lw_ * .7, ly - lh_, lx, ly - lh_ - U * .02, lx + lw_ * .7, ly - lh_))
A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#2a1d10" stroke-width="%.1f"/>' % (lx, ly - lh_ - U * .026, U * .006, U * .0025))
A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#fff6d0" filter="url(#b1)"/>' % (lx, ly - lh_ * .45, lw_ * .18, lh_ * .22))

# lunette astronomique sur trépied
bx, by = W * (.30 if PORTRAIT else .26), PAR + U * .02
leg = U * .2
for dx in (-.55, 0, .5):
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3a2a14" stroke-width="%.1f" stroke-linecap="round"/>' % (bx, by - leg * .9, bx + dx * leg, by + leg * .35, U * .007))
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#c99a4c" stroke-width="%.1f" stroke-linecap="round" opacity=".45"/>' % (bx, by - leg * .9, bx + dx * leg, by + leg * .35, U * .0022))
A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#laiton)"/>' % (bx, by - leg * .9, U * .012))
A('<g transform="translate(%.1f %.1f) rotate(-32)">' % (bx, by - leg * .95))
tl = U * .3
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#laiton)"/>' % (-tl * .35, -U * .016, tl, U * .032, U * .006))
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#laiton)"/>' % (tl * .6, -U * .021, tl * .14, U * .042, U * .006))
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#3a2a14" opacity=".6"/>' % (tl * .2, -U * .016, U * .005, U * .032))
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#laiton)"/>' % (-tl * .48, -U * .009, tl * .14, U * .018, U * .004))
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" opacity=".35"/>' % (-tl * .35, -U * .013, tl * 1.0, U * .004))
A('</g>')

# lueurs de la présence nocturne
for _ in range(9):
    x = R.uniform(.1, .9) * W; y = R.uniform(HZ - U * .05, PAR - U * .02); r = U * R.uniform(.003, .007)
    A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#cfe4ff" opacity=".55" filter="url(#b2)"/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff"/>' % (x, y, r * 4, x, y, r * .5))
A('<rect width="%d" height="%d" fill="url(#vignette)"/>' % (W, H))
A('</svg>')
open(OUT, 'w', encoding='utf-8').write('\n'.join(o))
