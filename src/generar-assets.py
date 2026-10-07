# -*- coding: utf-8 -*-
"""Genera los assets locales del sitio: placeholders de foto y la imagen Open Graph.

Por qué placeholders y no fotos: el sitio no tiene todavía las fotos propias de Sofía.
Inventar una foto (o bajar una de internet) sería un dato falso en el entregable y un
problema de derechos. El motor contempla este caso como PENDIENTE declarado: se usan
imágenes locales, con la paleta de la marca y un rótulo que dice que falta la foto real.
Cada placeholder se genera en dos anchos para que el srcset sea real.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("02-sitio/assets/img")
OUT.mkdir(parents=True, exist_ok=True)

AZUL = (31, 58, 95)
CREMA = (231, 223, 214)
FONDO = (247, 245, 242)
ROJO = (188, 32, 75)

FUENTES = ["C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf",
           "C:/Windows/Fonts/arial.ttf"]


def fuente(px):
    for f in FUENTES:
        if Path(f).exists():
            return ImageFont.truetype(f, px)
    return ImageFont.load_default()


def degradado(w, h, c1, c2):
    """Degradado vertical suave entre dos colores."""
    base = Image.new("RGB", (w, h), c1)
    d = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return base


def placeholder(nombre, w, h, etiqueta, sub=""):
    img = degradado(w, h, AZUL, (21, 40, 64))
    d = ImageDraw.Draw(img)
    # marco interior
    borde = max(2, w // 220)
    d.rectangle([borde * 6, borde * 6, w - borde * 6, h - borde * 6], outline=CREMA, width=borde)
    # rótulo centrado
    f1 = fuente(max(16, w // 16))
    f2 = fuente(max(12, w // 26))
    tw = d.textlength(etiqueta, font=f1)
    d.text(((w - tw) / 2, h / 2 - w / 22), etiqueta, font=f1, fill=CREMA)
    if sub:
        tw2 = d.textlength(sub, font=f2)
        d.text(((w - tw2) / 2, h / 2 + w / 40), sub, font=f2, fill=(200, 205, 213))
    # punto de marca
    r = max(5, w // 90)
    d.ellipse([w - borde * 16 - r, borde * 16 - r, w - borde * 16 + r, borde * 16 + r], fill=ROJO)
    img.save(OUT / f"{nombre}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
    return (OUT / f"{nombre}.jpg").stat().st_size


def og():
    w, h = 1200, 630
    img = degradado(w, h, AZUL, (14, 26, 43))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h - 14, w, h], fill=ROJO)
    d.text((80, 150), "Sofía Strafile", font=fuente(76), fill=(255, 255, 255))
    d.text((80, 260), "Asesora de imagen y colorimetría", font=fuente(40), fill=CREMA)
    d.text((80, 340), "Tu ropa habla antes que vos.", font=fuente(34), fill=(190, 196, 206))
    d.text((80, 470), "sofiastrafile.com.ar", font=fuente(30), fill=(188, 32, 75))
    img.save(OUT / "og-sofia.jpg", "JPEG", quality=86, optimize=True)
    return (OUT / "og-sofia.jpg").stat().st_size


piezas = [
    ("hero-retrato",       (800, 1000), "Foto pendiente", "retrato principal"),
    ("sofia-estudio",      (700, 700),  "Foto pendiente", "estudio / colorimetría"),
    ("servicio-colorimetria", (640, 480), "Foto pendiente", "análisis de color"),
    ("servicio-asesoria",  (640, 480),  "Foto pendiente", "asesoría 1:1"),
    ("servicio-guardarropa", (640, 480), "Foto pendiente", "armado de guardarropa"),
    ("caso-1",             (800, 600),  "Foto pendiente", "caso real"),
    ("caso-2",             (800, 600),  "Foto pendiente", "caso real"),
    ("caso-3",             (800, 600),  "Foto pendiente", "caso real"),
    ("caso-4",             (800, 600),  "Foto pendiente", "caso real"),
]

total = 0
for nombre, (w, h), etq, sub in piezas:
    for sufijo, escala in (("", 1.0), ("-640", 0.55)):
        ww, hh = int(w * escala), int(h * escala)
        if ww < 320:
            continue
        b = placeholder(f"{nombre}{sufijo}", ww, hh, etq, sub)
        total += b
        print(f"  {nombre}{sufijo}.jpg  {ww}x{hh}  {b//1024} KB")
b = og()
total += b
print(f"  og-sofia.jpg  1200x630  {b//1024} KB")
print(f"\nTOTAL assets de imagen: {total//1024} KB")
