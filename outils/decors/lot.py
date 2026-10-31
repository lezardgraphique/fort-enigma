"""Génère et rend plusieurs mondes d'un coup : lot.py fort,foraine,... [P|L|PL]"""
import sys, asyncio, io, os, re, subprocess
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright
noms = sys.argv[1].split(','); fmts = sys.argv[2] if len(sys.argv) > 2 else 'PL'
SALLES2 = ['tresor','bibliotheque','atlantide','farwest','cirque','station','maya','carnaval','cite','crypte','labyrinthe','jardin','ruche','laboratoire','palais']
TAILLES = {'P': (1290, 2048), 'L': (2048, 1152)}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nom in noms:
            for f in fmts:
                W, H = TAILLES[f]; svg = f'out/{nom}_{f}.svg'
                subprocess.run([sys.executable, 'mondes2.py' if nom in SALLES2 else 'mondes.py', nom, str(W), str(H), svg], check=True)
                pg = await b.new_page(viewport={'width': W, 'height': H})
                await pg.set_content('<html><body style="margin:0;background:#000">' + open(svg, encoding='utf-8').read() + '</body></html>')
                await pg.wait_for_timeout(200)
                png = await pg.screenshot(clip={'x': 0, 'y': 0, 'width': W, 'height': H}); await pg.close()
                im = np.asarray(Image.open(io.BytesIO(png)).convert('RGB')).astype(np.float32)
                im += np.random.default_rng(5).normal(0, 2.5, im.shape[:2])[..., None]
                out = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8))
                out.save(f'out/{nom}_{f}.webp', quality=84, method=6)
                out.resize((W // 3, H // 3), Image.LANCZOS).save(f'out/{nom}_{f}_apercu.png')
                print(nom, f, os.path.getsize(f'out/{nom}_{f}.webp') // 1024, 'Ko', flush=True)
        await b.close()
asyncio.run(main())
