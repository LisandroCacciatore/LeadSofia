# -*- coding: utf-8 -*-
"""Captura la portada del sitio nuevo servida por HTTP local (no file://, que rompe las fuentes)."""
import functools
import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path("02-sitio").resolve()
DEST = RAIZ / "capturas"
DEST.mkdir(parents=True, exist_ok=True)

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(RAIZ))
httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
puerto = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{puerto}/index.html"
print("sirviendo:", url)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for nombre, w, h, dsr, completo in (("despues-portada", 1440, 1000, 1, False),
                                        ("despues-completa", 1440, 1000, 1, True),
                                        ("despues-mobile", 390, 844, 2, True)):
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dsr,
                            locale="es-AR")
        pg = ctx.new_page()
        errores = []
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pg.on("requestfailed", lambda r: errores.append(f"FALLO {r.url}"))
        pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(1200)
        pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible'))")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(DEST / f"{nombre}.jpg"), full_page=completo, type="jpeg",
                      quality=80)
        # medir el ancho real: scrollWidth == clientWidth significa que no desborda
        med = pg.evaluate("""() => ({
            sw: document.documentElement.scrollWidth,
            cw: document.documentElement.clientWidth,
            peso: performance.getEntriesByType('resource').reduce((a,r)=>a+(r.transferSize||0),0)
        })""")
        print(f"  {nombre}: viewport {w}x{h}  scrollWidth={med['sw']} clientWidth={med['cw']} "
              f"desborde={'NO' if med['sw'] <= med['cw'] + 1 else 'SI'}  "
              f"recursos={round(med['peso']/1024)} KB")
        if errores:
            print("   errores de consola/red:", errores[:6])
        ctx.close()
    b.close()
httpd.shutdown()
print("capturas en", DEST)
