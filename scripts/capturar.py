#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capturar.py · captura la evidencia visual: el sitio actual y el sitio nuevo.

Deja dos cosas:
  1. Capturas completas (evidencia): escritorio y celular, de los dos sitios.
  2. Recortes de portada para la propuesta: los primeros 1500px, en JPEG y 900px
     de ancho, que es lo que se embebe en 01-propuesta/propuesta.html.

Las dos URLs salen de `config.json`, nunca de este archivo:
  · el sitio actual  <- meta.url (o meta.presenciaUrl si no tiene sitio propio)
  · el sitio nuevo   <- modelo.url; si no hay, cae al 02-sitio/index.html local

Esto importa porque el sitio nuevo puede venir de afuera —armado en otro motor y
publicado en GitHub Pages—, y una URL clavada acá capturaba el sitio equivocado
en cuanto el motor se copiaba a otra carpeta. Si la config no declara una URL,
el script lo dice y sigue con lo que sí pueda capturar: no inventa.

El celular se captura con el truco del iframe (ver scripts/movil.py): Chrome en
Windows no acepta ventanas de menos de ~500px, así que --window-size no sirve.

Uso:
    python scripts/capturar.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from movil import CHROME_CANDIDATES, ENVOLTORIO  # noqa: E402

AUD = ROOT / "00-auditoria" / "capturas"
SIT = ROOT / "02-sitio" / "capturas"
ALTO_DESKTOP = 3400
ALTO_RECORTE = 1500
ANCHO_RECORTE = 900


def leer_config() -> dict:
    p = ROOT / "config.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  ⚠ config.json no parsea ({e}); se captura sólo lo que tenga URL explícita")
        return {}


def url_publica(valor) -> Optional[str]:
    """Una URL http(s), o None. Un texto como «sin sitio propio» no es una URL:
    tratarlo como tal haría que Chrome capture una página de error y la guarde
    como si fuera el sitio del cliente."""
    v = str(valor or "").strip()
    return v if v.startswith(("http://", "https://")) else None


def chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    raise SystemExit("No encontré Chrome ni Edge.")


def comunes(ch: str, perfil: Path):
    return [ch, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
            "--allow-file-access-from-files", f"--user-data-dir={perfil}",
            "--virtual-time-budget=13000"]


def capturar_escritorio(ch: str, src: str, destino: Path, perfil: Path, ancho=1440):
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(comunes(ch, perfil) + [f"--window-size={ancho},{ALTO_DESKTOP}",
                                          f"--screenshot={destino}", src],
                   capture_output=True, text=True, errors="replace")


def capturar_movil(ch: str, src: str, destino: Path, tmp: Path, ancho=390):
    """Emula el ancho con un iframe, porque la ventana de Chrome no baja de ~500px.

    `src` puede ser una URL remota o un file:// local: el iframe acepta las dos.
    """
    envoltorio = tmp / f"envoltorio-{ancho}.html"
    envoltorio.write_text(
        ENVOLTORIO.format(src=src, ancho=ancho, alto=ALTO_DESKTOP),
        encoding="utf-8")
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(comunes(ch, tmp / f"prof-{ancho}") +
                   [f"--window-size={ancho},{ALTO_DESKTOP}", f"--screenshot={destino}",
                    envoltorio.as_uri()],
                   capture_output=True, text=True, errors="replace")


def recorte_portada(origen: Path, destino: Path, alto=ALTO_RECORTE, ancho=ANCHO_RECORTE):
    try:
        from PIL import Image
    except ImportError:
        print("  ⚠ falta Pillow: no recorto la portada. pip install pillow")
        return None
    im = Image.open(origen).convert("RGB")
    im = im.crop((0, 0, im.width, min(alto, im.height)))
    if im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, "JPEG", quality=78, optimize=True, progressive=True)
    return im.size


def main() -> int:
    cfg = leer_config()
    meta = cfg.get("meta") or {}
    modelo = cfg.get("modelo") or {}

    url_actual = url_publica(meta.get("url")) or url_publica(meta.get("presenciaUrl"))
    url_nueva = url_publica(modelo.get("url"))
    nuevo_local = ROOT / "02-sitio" / "index.html"

    if not url_actual:
        print("  ⚠ la config no declara sitio actual (meta.url): me salteo el «antes».")
    print(f"  antes : {url_actual or '—'}")
    src_nuevo = url_nueva or (nuevo_local.as_uri() if nuevo_local.exists() else None)
    print(f"  después: {src_nuevo or '—'}")
    if not src_nuevo:
        print("  ⚠ ni modelo.url ni 02-sitio/index.html: no hay «después» que capturar.")

    ch = chrome()
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        if url_actual:
            print("Capturando el sitio actual…")
            capturar_escritorio(ch, url_actual, AUD / "actual-desktop.png", tmp / "p1")
            capturar_movil(ch, url_actual, AUD / "actual-mobile.png", tmp, 390)
        if src_nuevo:
            print("Capturando el sitio nuevo…")
            capturar_escritorio(ch, src_nuevo, SIT / "nuevo-desktop.png", tmp / "p2")
            capturar_movil(ch, src_nuevo, SIT / "nuevo-mobile.png", tmp, 390)

    print("Recortando portadas para la propuesta…")
    pares = [(AUD / "actual-desktop.png", AUD / "antes-portada.jpg"),
             (SIT / "nuevo-desktop.png", SIT / "despues-portada.jpg")]
    for origen, destino in pares:
        if not origen.exists():
            print(f"  · sin {origen.name}: no hay de dónde recortar")
            continue
        r = recorte_portada(origen, destino)
        if r:
            print(f"  {destino.name:22} {r[0]}x{r[1]}  {destino.stat().st_size // 1024} KB")

    for carpeta, archivos in ((AUD, ("actual-desktop.png", "actual-mobile.png", "antes-portada.jpg")),
                              (SIT, ("nuevo-desktop.png", "nuevo-mobile.png", "despues-portada.jpg"))):
        for f in archivos:
            p = carpeta / f
            if p.exists():
                print(f"  {p.relative_to(ROOT)}  {p.stat().st_size // 1024} KB")

    if not url_actual and src_nuevo:
        print("\n  Nota: sin «antes» el informe queda sin el par comparativo. Declaralo en alcance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
