#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
e2e-captura.py · verifica el ciclo de captación de consultas en Chrome real.

No es un test de humo: es la prueba de que el formulario HACE lo que promete.

  python tests/e2e-captura.py                 # levanta un server propio en :8931
  python tests/e2e-captura.py --base http://127.0.0.1:8000

Qué comprueba:

  1. Un CTA de servicio preselecciona ese interés en el <select>.
  2. El botón está deshabilitado hasta marcar el consentimiento.
  3. Al enviar SIN backend, se abre WhatsApp con el mensaje ya armado, y el texto
     que llega contiene nombre, WhatsApp, interés (con su etiqueta legible) y mensaje.
  4. El estado dice la verdad ("te abrí WhatsApp"), no "enviado".
  5. El formulario se limpia y el botón vuelve a bloquearse.
  6. Un teléfono inválido NO abre WhatsApp: muestra el error y no miente.
  7. El honeypot no envía nada.
  8. En 390 px de ancho no hay desborde horizontal (scrollWidth == clientWidth).

Salida: exit 0 si todo pasa. Las capturas quedan en 02-sitio/capturas/.
"""

import argparse
import functools
import http.server
import json
import re
import socketserver
import sys
import threading
import urllib.parse
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
SITIO = RAIZ / "02-sitio"
CAPTURAS = SITIO / "capturas"
PUERTO = 8931
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

ok, fallos = [], []


def check(nombre, cond, detalle=""):
    if cond:
        ok.append(nombre)
        print(f"  OK    {nombre}" + (f" — {detalle}" if detalle else ""))
    else:
        fallos.append(f"{nombre} — {detalle}")
        print(f"  FALLA {nombre}" + (f" — {detalle}" if detalle else ""))


def servir():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(SITIO), **k)

        def log_message(self, *a, **k):  # silencio: el log no es evidencia acá
            pass

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PUERTO), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=f"http://127.0.0.1:{PUERTO}")
    args = ap.parse_args()

    httpd = None
    if args.base.startswith(f"http://127.0.0.1:{PUERTO}"):
        httpd = servir()
        print(f"Servidor local en {args.base} (raíz: {SITIO})")

    CAPTURAS.mkdir(parents=True, exist_ok=True)
    url = args.base.rstrip("/") + "/?utm_source=instagram&utm_medium=bio&utm_campaign=noviembre"

    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome", headless=True)
        ctx = navegador.new_context(viewport={"width": 1440, "height": 900}, locale="es-AR", user_agent=UA)
        pagina = ctx.new_page()
        errores_js = []
        pagina.on("pageerror", lambda e: errores_js.append(str(e)))
        pagina.goto(url, wait_until="load", timeout=60000)
        pagina.wait_for_timeout(600)

        # 1 · el ciclo arranca en la tarjeta del servicio -----------------------
        pagina.click('a[data-lead-servicio="colorimetria"]')
        pagina.wait_for_timeout(400)
        valor = pagina.eval_on_selector('[name="interes"]', "el => el.value")
        check("un CTA de servicio preselecciona el interés", valor == "colorimetria", f"select = {valor}")

        # 2 · el botón espera el consentimiento --------------------------------
        deshabilitado = pagina.eval_on_selector('button[type="submit"]', "el => el.disabled")
        check("el botón arranca deshabilitado", deshabilitado is True)

        # 3 · envío sin backend → WhatsApp con el mensaje armado ---------------
        pagina.fill('[name="nombre"]', "Marina Gómez")
        pagina.fill('[name="whatsapp"]', "+54 9 341 555 1234")
        pagina.fill('[name="email"]', "marina@ejemplo.com")
        pagina.fill('[name="mensaje"]', "Quiero renovar el guardarropa antes de un viaje.")
        pagina.check('[name="consent"]')
        habilitado = pagina.eval_on_selector('button[type="submit"]', "el => !el.disabled")
        check("marcar el consentimiento habilita el envío", habilitado is True)

        with ctx.expect_page(timeout=8000) as info_popup:
            pagina.click('button[type="submit"]')
        popup = info_popup.value
        popup_url = popup.url
        popup.close()

        # wa.me redirige a api.whatsapp.com/send: las dos formas son el mismo destino.
        host = urllib.parse.urlparse(popup_url).netloc.lower()
        check(
            "abre el WhatsApp de Sofía",
            host in ("wa.me", "api.whatsapp.com") and "5493416153151" in popup_url,
            f"{host} · {popup_url[:60]}",
        )

        qs = urllib.parse.parse_qs(urllib.parse.urlparse(popup_url).query)
        texto = (qs.get("text") or [""])[0]
        (CAPTURAS / "captura-mensaje-whatsapp.txt").write_text(texto, encoding="utf-8")
        check("el mensaje lleva el nombre", "Nombre: Marina Gómez" in texto)
        check("el mensaje lleva el WhatsApp de contacto", "WhatsApp: +54 9 341 555 1234" in texto)
        check("el mensaje lleva el interés como etiqueta legible", "Interés: Análisis de colorimetría" in texto)
        check("el mensaje lleva el texto libre", "Mensaje: Quiero renovar el guardarropa" in texto)
        check(
            "el mensaje lleva la campaña de la URL",
            "Campaña: instagram / bio / noviembre" in texto,
            texto.splitlines()[-1] if texto else "(vacío)",
        )
        check("el mensaje no viaja sin escapar", "%20" not in texto and "\\n" not in texto)

        # 4 · el estado dice la verdad ----------------------------------------
        estado = pagina.eval_on_selector("#lead-status", "el => ({t: el.textContent.trim(), s: el.dataset.state})")
        check("el estado es 'ok' y menciona WhatsApp", estado["s"] == "ok" and "WhatsApp" in estado["t"], estado["t"][:70])
        check("no dice 'enviado' (no se envió ningún mail)", "recibí tu consulta" not in estado["t"].lower())

        # 5 · el formulario se limpia -----------------------------------------
        limpio = pagina.evaluate(
            "() => ({n: document.querySelector('[name=nombre]').value,"
            " c: document.querySelector('[name=consent]').checked,"
            " d: document.querySelector('button[type=submit]').disabled})"
        )
        check("el formulario se limpia y el botón se vuelve a bloquear", limpio == {"n": "", "c": False, "d": True}, str(limpio))
        pagina.screenshot(path=str(CAPTURAS / "captura-form-ok.jpg"), full_page=False)

        # 6 · teléfono inválido: no abre nada y avisa --------------------------
        pagina.fill('[name="nombre"]', "Prueba Sin Telefono")
        pagina.fill('[name="whatsapp"]', "12")
        pagina.check('[name="consent"]')
        abrio = []
        pagina.on("popup", lambda pop: abrio.append(pop.url))
        pagina.click('button[type="submit"]')
        pagina.wait_for_timeout(700)
        estado_err = pagina.eval_on_selector("#lead-status", "el => ({t: el.textContent.trim(), s: el.dataset.state})")
        check("un teléfono inválido no abre WhatsApp", not abrio, str(abrio))
        check("y muestra el error correspondiente", estado_err["s"] == "error" and "Revisá el WhatsApp" in estado_err["t"], estado_err["t"][:60])

        # 7 · honeypot: no envía ----------------------------------------------
        pagina.fill('[name="whatsapp"]', "3415551234")
        pagina.fill('[name="empresa"]', "bot")
        abrio.clear()
        pagina.click('button[type="submit"]')
        pagina.wait_for_timeout(700)
        check("el honeypot completa no dispara ningún envío", not abrio, str(abrio))

        # 8 · mobile: sin desborde --------------------------------------------
        movil = ctx.new_page()
        movil.set_viewport_size({"width": 390, "height": 844})
        movil.goto(args.base.rstrip("/") + "/#consulta", wait_until="load", timeout=60000)
        movil.wait_for_timeout(700)
        ancho = movil.evaluate(
            "() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})"
        )
        check(
            "en 390 px no hay desborde horizontal",
            ancho["sw"] <= ancho["cw"] + 1,
            f"scrollWidth {ancho['sw']} vs clientWidth {ancho['cw']}",
        )
        movil.evaluate("document.getElementById('consulta').scrollIntoView({block:'start'})")
        movil.wait_for_timeout(500)
        movil.screenshot(path=str(CAPTURAS / "captura-form-mobile.jpg"), full_page=False)

        check("no hubo errores de JavaScript", not errores_js, "; ".join(errores_js)[:150])

        # captura de la sección completa en escritorio
        pagina.goto(args.base.rstrip("/") + "/#consulta", wait_until="load", timeout=60000)
        pagina.wait_for_timeout(600)
        pagina.evaluate("document.getElementById('consulta').scrollIntoView({block:'start'})")
        pagina.wait_for_timeout(600)
        pagina.screenshot(path=str(CAPTURAS / "captura-form-escritorio.jpg"), full_page=False)

        navegador.close()

    if httpd:
        httpd.shutdown()

    resumen = {"ok": len(ok), "fallos": len(fallos), "detalle_fallos": fallos}
    print("\n" + json.dumps(resumen, ensure_ascii=False))
    if fallos:
        print(f"\n{len(fallos)} comprobación(es) fallida(s).")
        return 1
    print(f"\n{len(ok)} comprobaciones OK — el ciclo de captación funciona en Chrome real.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
