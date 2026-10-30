"""Textures originales 512×276 (pierre, bois, parchemin, laiton) générées par bruit fractal."""
import numpy as np
from PIL import Image
W, H = 512, 276
rng = np.random.default_rng(3)
def fbm(oct=5, base=4, sx=1, sy=1):
    out = np.zeros((H, W)); amp = 1; tot = 0
    for o in range(oct):
        n = base * 2 ** o
        g = rng.random((max(2, int(n * sy)), max(2, int(n * sx))))
        out += amp * np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        tot += amp; amp *= .55
    out /= tot
    return (out - out.mean()) / (out.std() + 1e-6)
def ecrit(nom, moy, var, champ):
    im = np.array(moy, np.float32)[None, None, :] + champ[..., None] * np.array(var, np.float32)[None, None, :]
    Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(f'out/tex-{nom}.webp', quality=82, method=6)
ecrit('stone', (127, 124, 113), (6, 6, 5), fbm(6, 3) + .35 * fbm(3, 24))
x = np.linspace(0, 1, W)[None, :]; y = np.linspace(0, 1, H)[:, None]
veine = np.sin((y * 38 + 2.2 * fbm(4, 2, sx=.4, sy=2)) * np.pi) + .5 * fbm(5, 2, sx=6, sy=.3)
ecrit('wood', (72, 48, 32), (5, 4, 3), veine / veine.std())
ecrit('parch', (234, 217, 182), (3, 3, 5), fbm(6, 2) + .5 * fbm(2, 40))
ray = fbm(3, 2, sx=.2, sy=8) + .6 * np.sin(x * 3 + y * 2)
ecrit('brass', (82, 67, 40), (10, 9, 6), ray / ray.std())
import os
for n in ('stone', 'wood', 'parch', 'brass'): print(n, os.path.getsize(f'out/tex-{n}.webp'))
