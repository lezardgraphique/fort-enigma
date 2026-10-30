"""Atelier commun des décors de Fort Énigma.
Une seule facture pour tous les mondes : aplats dégradés, lumière d'ambiance nocturne
ou crépusculaire, liserés de lumière sur les arêtes, halos doux, brume en couches,
texture de pierre/grain par bruit, vignette. Tout est dessiné ici (aucune image extérieure)."""
import math, random

class Scene:
    def __init__(s, W, H, graine=1):
        s.W, s.H = W, H
        s.U = min(W, H)
        s.P = H > W
        s.R = random.Random(graine)
        s.o = []
        s.defs = []
        s._id = 0
        U = s.U
        s.defs.append(
            '<filter id="b1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{:.1f}"/></filter>'
            '<filter id="b2" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{:.1f}"/></filter>'
            '<filter id="b3" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="{:.1f}"/></filter>'
            '<filter id="b4" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="{:.1f}"/></filter>'
            '<filter id="texture" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="{:.4f}" numOctaves="5" seed="7"/>'
            '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .9 -.32"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
            '<filter id="fin" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="3"/>'
            '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 -.15"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
            '<filter id="nuage" x="-20%" y="-60%" width="140%" height="220%"><feTurbulence type="fractalNoise" baseFrequency="{:.5f}" numOctaves="4" seed="2"/>'
            '<feDisplacementMap in="SourceGraphic" scale="{:.1f}"/><feGaussianBlur stdDeviation="{:.1f}"/></filter>'
            '<radialGradient id="vignette" cx=".5" cy=".42" r=".8"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".62"/></radialGradient>'
            .format(U * .002, U * .007, U * .02, U * .05, 6.0 / U, 3.0 / U, U * .06, U * .007))

    # ---------- outils ----------
    def id(s, p='g'):
        s._id += 1
        return '%s%d' % (p, s._id)
    def a(s, x):
        s.o.append(x)
    def lin(s, stops, x1=0, y1=0, x2=0, y2=1):
        i = s.id('l')
        s.defs.append('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (
            i, x1, y1, x2, y2, ''.join('<stop offset="%s" stop-color="%s"%s/>' % (o, c, (' stop-opacity="%s"' % op) if op is not None else '') for o, c, op in [(t + (None,))[:3] for t in stops])))
        return 'url(#%s)' % i
    def rad(s, stops, cx=.5, cy=.5, r=.5):
        i = s.id('r')
        s.defs.append('<radialGradient id="%s" cx="%s" cy="%s" r="%s">%s</radialGradient>' % (
            i, cx, cy, r, ''.join('<stop offset="%s" stop-color="%s"%s/>' % (o, c, (' stop-opacity="%s"' % op) if op is not None else '') for o, c, op in [(t + (None,))[:3] for t in stops])))
        return 'url(#%s)' % i
    def poly(s, pts, fill, extra=''):
        s.a('<polygon points="%s" fill="%s" %s/>' % (' '.join('%.1f,%.1f' % p for p in pts), fill, extra))
    def path(s, d, fill='none', extra=''):
        s.a('<path d="%s" fill="%s" %s/>' % (d, fill, extra))
    def rect(s, x, y, w, h, fill, extra=''):
        s.a('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" %s/>' % (x, y, w, h, fill, extra))
    def ell(s, cx, cy, rx, ry, fill, extra=''):
        s.a('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" %s/>' % (cx, cy, rx, ry, fill, extra))
    def circ(s, cx, cy, r, fill, extra=''):
        s.a('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" %s/>' % (cx, cy, r, fill, extra))
    def texture(s, d_ou_rect, op=.35):
        """grain de matière (pierre, bois…) posé sur une forme"""
        if isinstance(d_ou_rect, tuple):
            x, y, w, h = d_ou_rect
            s.a('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#000" opacity="%.2f" filter="url(#texture)"/>' % (x, y, w, h, op))
        else:
            s.a('<path d="%s" fill="#000" opacity="%.2f" filter="url(#texture)"/>' % (d_ou_rect, op))

    # ---------- lumière ----------
    def halo(s, x, y, r, col, op=.6, flou='b3'):
        s.circ(x, y, r, col, 'opacity="%.2f" filter="url(#%s)"' % (op, flou))
    def lueur(s, x, y, r, col, force=1.0):
        g = s.rad([(0, col, .75 * force), (.35, col, .25 * force), (1, col, 0)])
        s.circ(x, y, r, g)
    def flamme(s, x, y, t, col1='#ffd36b', col2='#ff7a1a'):
        """flamme de torche/bougie, base en (x, y), hauteur t"""
        s.lueur(x, y - t * .4, t * 3.2, col2, .9)
        d = 'M%.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fZ' % (
            x - t * .32, y, x - t * .4, y - t * .55, x - t * .05, y - t * .7, x + t * .02, y - t,
            x + t * .2, y - t * .62, x + t * .45, y - t * .45, x + t * .32, y)
        s.path(d, col2)
        d2 = 'M%.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fZ' % (
            x - t * .16, y, x - t * .2, y - t * .35, x, y - t * .45, x + t * .02, y - t * .68,
            x + t * .12, y - t * .42, x + t * .22, y - t * .3, x + t * .16, y)
        s.path(d2, col1)
    def torche(s, x, y, t):
        s.poly([(x - t * .08, y), (x + t * .08, y), (x + t * .05, y + t * .9), (x - t * .05, y + t * .9)], '#3a2614')
        s.rect(x - t * .14, y - t * .05, t * .28, t * .12, '#5a3c1e')
        s.flamme(x, y - t * .02, t * .7)

    # ---------- ciel ----------
    def ciel(s, stops, horizon=None):
        if horizon:
            t = horizon / s.H
            stops = [(round(x[0] * t, 4),) + tuple(x[1:]) for x in stops] + [(1, stops[-1][1])]
        s.rect(0, 0, s.W, s.H, s.lin(stops))
    def etoiles(s, n, ymax, op=1.0):
        R = s.R
        for _ in range(n):
            x, y = R.uniform(0, s.W), R.uniform(0, ymax)
            s.circ(x, y, R.choice([.5, .6, .8, 1, 1.3, 1.7]) * s.U / 1100, R.choice(['#fff', '#dfe6ff', '#fff3d6']),
                   'opacity="%.2f"' % (R.uniform(.4, 1) * op * (1 - y / ymax * .55)))
        for _ in range(max(3, n // 120)):
            x, y = R.uniform(0, s.W), R.uniform(0, ymax * .8); t = R.uniform(.006, .013) * s.U
            s.circ(x, y, t * .45, '#dfe6ff', 'opacity="%.2f" filter="url(#b1)"' % (.5 * op))
            s.path('M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZM%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (
                x - t, y, x, y - t * .08, x + t, y, x, y + t * .08, x, y - t, x + t * .08, y, x, y + t, x - t * .08, y), '#fff', 'opacity="%.2f"' % (.9 * op))
    def lune(s, x, y, r):
        s.circ(x, y, r * 6, s.rad([(0, '#e8ecff', .5), (.25, '#b9c6ff', .2), (1, '#8090ff', 0)]))
        s.circ(x, y, r, s.rad([(0, '#fffdf2'), (.7, '#e9e8de'), (1, '#c4c8d4')], .42, .38, .62))
        s.a('<g filter="url(#b1)" fill="#8a8fa3">')
        for (dx, dy, rx, ry, rot, op) in [(-.32, -.18, .30, .17, 25, .22), (-.05, -.02, .22, .12, -10, .18), (.22, .12, .16, .24, 40, .2), (-.18, .32, .2, .09, 5, .15)]:
            s.a('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" opacity="%.2f" transform="rotate(%d %.1f %.1f)"/>' % (x + dx * r, y + dy * r, rx * r, ry * r, op, rot, x + dx * r, y + dy * r))
        s.a('</g>')
    def soleil(s, x, y, r, c1='#fff2c4', c2='#ffb347'):
        s.circ(x, y, r * 7, s.rad([(0, c2, .6), (.3, c2, .2), (1, c2, 0)]))
        s.circ(x, y, r, s.rad([(0, '#fffbe8'), (.6, c1), (1, c2)]))
    def nuages(s, liste, ombre, lumiere):
        """liste de (cx, cy, rx, ry, opacité) en fractions de l'écran"""
        for (cx, cy, rx, ry, op) in liste:
            s.ell(cx * s.W, cy * s.H, rx * s.W, ry * s.H * 2.2, ombre, 'opacity="%.2f" filter="url(#nuage)"' % op)
            s.ell(cx * s.W, (cy - ry * .9) * s.H, rx * s.W * .8, ry * s.H * .8, lumiere, 'opacity="%.2f" filter="url(#nuage)"' % (op * .6))

    # ---------- relief ----------
    def crete(s, y_base, amp, graine, sommets=4, rug=.5, n=5):
        rr = random.Random(graine); W = s.W
        pics = [(rr.uniform(-.05, 1.05) * W, rr.uniform(.45, 1) * amp * 2.2, rr.uniform(.08, .22) * W) for _ in range(sommets)]
        haut = lambda x: max([0] + [h * max(0, 1 - abs(x - px) / lw) for px, h, lw in pics])
        pts = [(x, y_base - haut(x)) for x in [i * W / 16 for i in range(17)]]
        a = amp * .35
        for _ in range(n):
            nv = []
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                nv += [(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + rr.uniform(-a, a))]
            nv.append(pts[-1]); pts = nv; a *= rug
        return pts
    def relief(s, pts, couleur_haut, couleur_bas, liseré=None, op_lis=.5, bas=None):
        bas = s.H if bas is None else bas
        d = 'M0 %.1f ' % bas + ' '.join('L%.1f %.1f' % p for p in pts) + ' L%d %.1fZ' % (s.W, bas)
        top = min(p[1] for p in pts)
        g = s.lin([(0, couleur_haut), (1, couleur_bas)], 0, 0, 0, 1)
        s.path(d, g)
        s.texture(d, .22)
        if liseré:
            seg = ['M%.1f %.1fL%.1f %.1f' % (x0, y0, x1, y1) for (x0, y0), (x1, y1) in zip(pts, pts[1:]) if y1 < y0]
            s.path(' '.join(seg), 'none', 'stroke="%s" stroke-width="%.1f" opacity="%.2f" stroke-linecap="round"' % (liseré, s.U * .0025, op_lis))
        return d
    def brume(s, y, h, col, op=.35):
        s.rect(0, y, s.W, h, s.lin([(0, col, 0), (.55, col, op), (1, col, 0)]))

    # ---------- maçonnerie ----------
    def appareil(s, x, y, w, h, bloc, joint='#0e0d16', op=.55, variations=('#8b90b0', '#2a2d44', '#5d6284', '#3b3f5c')):
        """lignes de joints et pierres légèrement variées dans un rectangle"""
        R = s.R
        s.a('<g>')
        k = 0; yy = y
        while yy < y + h:
            s.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" opacity="%.2f"/>' % (x, yy, x + w, yy, joint, max(1, s.U * .0016), op))
            xx = x + (k % 2) * bloc * .5 - bloc * .25
            while xx < x + w:
                lw = bloc * R.uniform(.8, 1.3)
                x0 = max(x, xx); x1 = min(x + w, xx + lw)
                if x1 > x0:
                    s.a('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".14"/>' % (x0, yy, x1 - x0, min(bloc * .45, y + h - yy), R.choice(variations)))
                if xx > x:
                    s.a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" opacity="%.2f"/>' % (xx, yy, xx, min(y + h, yy + bloc * .45), joint, max(1, s.U * .0016), op * .9))
                xx += lw
            yy += bloc * .45; k += 1
        s.a('</g>')
    def runes(s, x, y, larg, n, taille, col, op=.9):
        """frise de runes lumineuses (même motif que la porte des mondes)"""
        R = s.R
        for i in range(n):
            cx = x + larg * (i + .5) / n
            d = 'M%.1f %.1fV%.1f' % (cx, y - taille, y + taille)
            for _ in range(R.randint(1, 3)):
                y0 = y - taille + R.random() * taille * 1.4; dx = R.choice([-1, 1]) * taille * R.uniform(.5, .9)
                d += 'M%.1f %.1fL%.1f %.1f' % (cx, y0, cx + dx, y0 + taille * (R.random() - .3) * .9)
            s.path(d, 'none', 'stroke="%s" stroke-width="%.1f" stroke-linecap="round" opacity="%.2f" filter="url(#b1)"' % (col, taille * .35, op * .6))
            s.path(d, 'none', 'stroke="%s" stroke-width="%.1f" stroke-linecap="round" opacity="%.2f"' % (col, taille * .16, op))

    def lucioles(s, n, x0, x1, y0, y1, col='#cfe4ff'):
        R = s.R
        for _ in range(n):
            x, y, r = R.uniform(x0, x1), R.uniform(y0, y1), s.U * R.uniform(.003, .007)
            s.circ(x, y, r * 4, col, 'opacity=".5" filter="url(#b2)"')
            s.circ(x, y, r * .5, '#fff')

    def fin(s):
        s.rect(0, 0, s.W, s.H, 'url(#vignette)')
    def ecrire(s, chemin):
        out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><defs>%s</defs>' % (s.W, s.H, s.W, s.H, ''.join(s.defs))]
        out += s.o
        out.append('</svg>')
        open(chemin, 'w', encoding='utf-8').write('\n'.join(out))
