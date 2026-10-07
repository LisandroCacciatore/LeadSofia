#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar-sitio.py · el bot generador de páginas.

Del `config.json` del lead deriva el CONTRATO del sitio nuevo —los datos reales
del negocio, las promesas de la base y los criterios de aceptación ejecutables—
se lo entrega a DSH (DeepSeek Harness) y **verifica el resultado en disco**: el
auto-reporte del agente no es evidencia.

## Por qué el contrato sale del config y no de un brief aparte

El `config.json` ya es la spec del sitio: las promesas de la base son exactamente
lo que el gate §10 va a cotejar contra el sitio publicado. Si el generador
inventara su propio brief, construiría un sitio lindo que después falla el gate y
nadie sabría si el problema es el sitio o el gate. Acá los criterios de aceptación
se derivan del mismo archivo que después audita, y por eso el generador y el
auditor pueden discutir con datos.

## Los criterios no se inventan: salen de los gates que ya existen

Cada criterio es una señal que `verificar-sitio.py` (la auditoría del sitio) o
`cotejar-promesas.py` (§10) ya miran. Tres estados, igual que el §10:

    CUMPLE     · NO CUMPLE   (bloqueante)
    PENDIENTE  (declarado: falta un insumo que el cliente no dio)

## Subcomandos

    python scripts/generar-sitio.py contrato    # escribe y muestra el contrato
    python scripts/generar-sitio.py generar     # invoca DSH con el contrato
    python scripts/generar-sitio.py verificar   # corre los criterios sobre 02-sitio
    python scripts/generar-sitio.py enchufar --url <URL>   # la pone en modelo.url
    python scripts/generar-sitio.py publicar    # armar-dist + push + espera Pages

`--dry-run` en `generar` muestra el comando sin ejecutarlo.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.json"
SITIO = ROOT / "02-sitio"
CONTRATO = SITIO / "CONTRATO.md"

# ── Los umbrales son los mismos que usa verificar-sitio.py: si los cambiara acá,
#    el generador y el auditor dejarían de medir lo mismo.
DESC_MIN, DESC_MAX = 120, 165
WA_MIN = 8
OG_MIN = 6
H2_MIN = 5
ESPERA_DSH = 1500
MARCADOR = "PENDIENTE-DOMINIO"     # lo escribe el contrato cuando el dominio no está definido


# ─────────────────────────── lectura de la config ───────────────────────────

def leer_config() -> dict:
    if not CONFIG.exists():
        raise SystemExit("no hay config.json en la raíz del lead")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def datos_del_lead(cfg: dict) -> dict:
    """Todo lo que el sitio tiene que decir, en un solo lugar.

    `meta` trae la identidad; el bloque `sitio` (nuevo) trae los datos de contacto
    y el contenido. Lo que no está, no se inventa: queda para `preguntasAbiertas`.
    """
    meta = cfg.get("meta") or {}
    s = cfg.get("sitio") or {}
    branding = cfg.get("branding") or {}
    faltantes = []
    d = {
        "nombre": meta.get("nombre", ""),
        "negocio": meta.get("negocio") or meta.get("profesion") or "",
        "rubro": meta.get("rubro", ""),
        "color": branding.get("colorPrimario", ""),
        "direccion": s.get("direccion", ""),
        "telefono": s.get("telefono", ""),
        "whatsapp": s.get("whatsapp", ""),
        "whatsappMensaje": s.get("whatsappMensaje", "Hola! Quiero hacer un pedido."),
        "horarios": s.get("horarios", ""),
        "mapa": s.get("mapa", ""),
        "redes": s.get("redes") or {},
        "secciones": s.get("secciones") or [],
        "productos": s.get("productos") or [],
        "imagenes": s.get("imagenes", ""),
        "habilitacion": meta.get("habilitacion") or meta.get("matricula") or "",
        "canonical": s.get("canonical", ""),
        "dominioPrevisto": s.get("dominioPrevisto", ""),
    }
    for campo in ("nombre", "negocio", "direccion", "telefono", "whatsapp", "color", "secciones"):
        if not d[campo]:
            faltantes.append(campo)
    d["_faltantes"] = faltantes
    return d


def promesas(cfg: dict) -> list:
    """Las promesas de la base: lo que la propuesta afirma y el §10 coteja."""
    base = cfg.get("base") or {}
    return list(base.get("items") or cfg.get("baseItems") or [])


def secciones_prometidas(promesas_: list) -> int:
    """«7 secciones con tus datos reales» → 7. El §10 las cuenta en la navegación."""
    for p in promesas_:
        m = re.search(r"\b(\d+)\s+secciones", str(p))
        if m:
            return int(m.group(1))
    return 0


# ─────────────────────── los criterios de aceptación ───────────────────────
# Firma única: (piezas, conf) donde piezas = {"html", "robots", "sitemap"}.
# Cada criterio devuelve (estado, evidencia) con estado en {"cumple","no","pendiente"}.

def _imgs(dom):
    return re.findall(r"<img\b[^>]*>", dom, re.I)


def c_lang(p, _):
    dom = p["html"]
    m = re.search(r'<html[^>]*\blang="([^"]*)"', dom, re.I)
    v = m.group(1) if m else "sin atributo"
    return ("cumple" if v.lower().startswith("es-ar") else "no"), f'lang="{v}"'


def c_descripcion(p, _):
    m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', p["html"], re.I)
    if not m:
        return "no", "sin meta description"
    n = len(m.group(1))
    return ("cumple" if DESC_MIN <= n <= DESC_MAX else "no"), f"{n} caracteres (se esperan {DESC_MIN}-{DESC_MAX})"


def c_canonical(p, conf):
    m = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', p["html"], re.I)
    if not m:
        return "no", "sin URL canónica"
    v = m.group(1)
    esperado = (conf.get("canonical") or "").rstrip("/")
    if not esperado:
        # Sin dominio declarado, el agente no tiene de dónde sacarla: si la inventa,
        # puede apuntar al sitio de un tercero. Se declara en vez de darla por buena.
        return "pendiente", f"el dominio no está declarado; el sitio puso {v[:52]} (declarado)"
    return ("cumple" if v.rstrip("/") == esperado else "no"), \
        f"{v[:52]} (declarada: {esperado[:48]})"


HOSTS_PERMITIDOS = {"wa.me", "api.whatsapp.com", "schema.org", "www.w3.org", "w3.org"}


def c_dominios(p, conf):
    """Ningún dominio de terceros.

    Este criterio nace de un caso real: sin dominio declarado en la config, el agente
    inventó el que le pareció más lógico — y el sitio quedó canónico y datos
    estructurados apuntando al dominio de OTRO negocio. Un sitio con el nombre del
    cliente no puede enlazar a un tercero sin que nadie lo note.
    """
    hosts = set(re.findall(r"https?://([a-z0-9.\-]+)", p["html"], re.I))
    permitidos = set(HOSTS_PERMITIDOS)
    for clave in ("canonical",):
        for u in re.findall(r"https?://([a-z0-9.\-]+)", conf.get(clave) or "", re.I):
            permitidos.add(u)
    for u in (conf.get("mapa") or "", *(conf.get("redes") or {}).values()):
        for h in re.findall(r"https?://([a-z0-9.\-]+)", u, re.I):
            permitidos.add(h)
    raros = sorted(h for h in hosts if h not in permitidos and not h.endswith(".w3.org"))
    if raros:
        return "no", f"dominios no declarados en la config: {', '.join(raros)[:90]}"
    return "cumple", f"{len(hosts)} dominio(s), todos declarados en la config"


def c_estructurados(p, _):
    bloques = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', p["html"], re.S | re.I)
    if not bloques:
        return "no", "sin bloques JSON-LD"
    tipos, rotos = [], []
    for b in bloques:
        try:
            data = json.loads(b.strip())
        except Exception as e:  # noqa: BLE001
            rotos.append(str(e)[:60]); continue
        nodos = data.get("@graph", [data]) if isinstance(data, dict) else data
        for n in nodos:
            if isinstance(n, dict) and "@type" in n:
                t = n["@type"]
                tipos += t if isinstance(t, list) else [t]
    if rotos:
        return "no", f"JSON-LD roto: {rotos[0]}"
    return "cumple", f"{len(bloques)} bloque(s): {', '.join(sorted(set(tipos)))[:90]}"


def c_whatsapp(p, _):
    n = len(re.findall(r"wa\.me/", p["html"], re.I))
    return ("cumple" if n >= WA_MIN else "no"), f"{n} enlaces wa.me (mínimo {WA_MIN})"


def c_alt(p, _):
    imgs = _imgs(p["html"])
    con = [i for i in imgs if re.search(r'\balt="[^"]{3,}"', i, re.I)]
    return ("cumple" if imgs and len(con) == len(imgs) else "no"), f"{len(con)} de {len(imgs)} imágenes con alt real"


def c_lazy(p, _):
    imgs = _imgs(p["html"])
    con = [i for i in imgs if re.search(r'loading="lazy"', i, re.I)]
    ok = len(imgs) > 0 and len(con) >= len(imgs) - 1     # la portada va eager a propósito
    return ("cumple" if ok else "no"), f"{len(con)} de {len(imgs)} con carga diferida (la portada se exceptúa)"


def c_srcset(p, conf):
    n = len([i for i in _imgs(p["html"]) if "srcset" in i.lower()])
    if n >= 2:
        return "cumple", f"{n} imágenes con srcset"
    # Sin fotos propias no hay variantes que ofrecer: se declara, no se finge.
    if conf.get("imagenes"):
        return "pendiente", f"{n} con srcset — declarado: {conf['imagenes'][:80]}"
    return "no", f"sólo {n} imágenes con srcset (se esperan 2+)"


def c_h1(p, _):
    n = len(re.findall(r"<h1\b", p["html"], re.I))
    return ("cumple" if n == 1 else "no"), f"{n} h1 (debe haber exactamente 1)"


def c_h2(p, _):
    n = len(re.findall(r"<h2\b", p["html"], re.I))
    return ("cumple" if n >= H2_MIN else "no"), f"{n} h2 (mínimo {H2_MIN})"


def c_og(p, _):
    n = len(re.findall(r'property="og:', p["html"], re.I))
    return ("cumple" if n >= OG_MIN else "no"), f"{n} etiquetas Open Graph (mínimo {OG_MIN})"


def c_nav(p, conf):
    objetivo = conf.get("_secciones_prometidas") or 0
    m = re.search(r"<nav\b.*?</nav>", p["html"], re.S | re.I) or \
        re.search(r"<header\b.*?</header>", p["html"], re.S | re.I)
    n = len(re.findall(r"<a\b", m.group(0), re.I)) if m else 0
    if not objetivo:
        return ("cumple" if n >= 2 else "no"), f"{n} enlaces en la navegación (la base no promete cantidad)"
    return ("cumple" if n >= objetivo else "no"), f"{n} enlaces en la navegación (la base promete {objetivo})"


def c_robots(p, _):
    t = p.get("robots", "")
    if not t:
        return "no", "no hay robots.txt"
    return "cumple", f"robots.txt presente ({len(t)} caracteres)"


def c_sitemap(p, _):
    t = p.get("sitemap", "")
    if not t:
        return "no", "no hay sitemap.xml"
    return ("cumple" if "<urlset" in t else "no"), \
        ("sitemap.xml con <urlset>" if "<urlset" in t else "sitemap.xml sin <urlset>")


def c_contacto(p, conf):
    dom = p["html"]
    if not conf.get("direccion") or not conf.get("telefono"):
        return "pendiente", "la config no tiene dirección y teléfono completos"
    faltan = [c for c in ("direccion", "telefono") if conf[c] not in dom]
    return ("cumple" if not faltan else "no"), ("dirección y teléfono como texto" if not faltan
                                               else f"no aparecen como texto: {faltan}")


def c_tel_link(p, _):
    n = len(re.findall(r'href="tel:', p["html"], re.I))
    return ("cumple" if n >= 1 else "no"), f"{n} enlace(s) telefónico(s)"


def c_labels(p, _):
    dom = p["html"]
    campos = len(re.findall(r"<input\b|<textarea\b|<select\b", dom, re.I))
    labels = len(re.findall(r"<label\b", dom, re.I))
    if campos == 0:
        return "cumple", "sin formulario: no hay campos que etiquetar"
    return ("cumple" if labels >= campos else "no"), f"{labels} <label> para {campos} campos"


CRITERIOS = [
    ("C01", "Idioma declarado es-AR", c_lang),
    ("C02", f"Descripción para Google de {DESC_MIN} a {DESC_MAX} caracteres", c_descripcion),
    ("C03", "URL canónica", c_canonical),
    ("C04", "Datos estructurados JSON-LD válidos", c_estructurados),
    ("C05", f"{WA_MIN}+ llamados a WhatsApp", c_whatsapp),
    ("C06", "Toda imagen con texto alternativo real", c_alt),
    ("C07", "Carga diferida (salvo la portada)", c_lazy),
    ("C08", "Imágenes con srcset", c_srcset),
    ("C09", "Exactamente un h1", c_h1),
    ("C10", f"{H2_MIN}+ h2 (jerarquía)", c_h2),
    ("C11", f"{OG_MIN}+ etiquetas Open Graph", c_og),
    ("C12", "Navegación con las secciones prometidas", c_nav),
    ("C13", "robots.txt", c_robots),
    ("C14", "sitemap.xml", c_sitemap),
    ("C15", "Dirección y teléfono como texto visible", c_contacto),
    ("C16", "Enlace telefónico tel:", c_tel_link),
    ("C17", "Formulario con etiquetas reales", c_labels),
    ("C18", "Ningún dominio de terceros sin declarar", c_dominios),
]


# ─────────────────────────── armar el contrato ───────────────────────────

def armar_contrato(cfg: dict) -> str:
    d = datos_del_lead(cfg)
    proms = promesas(cfg)
    n_sec = secciones_prometidas(proms)
    d["_secciones_prometidas"] = n_sec
    modelo = cfg.get("modelo") or {}

    def lista(items, marca="-", vacio="(la config no declara nada acá)"):
        return "\n".join(f"{marca} {i}" for i in items) if items else vacio

    productos = d["productos"]
    redes = d["redes"]
    pend = [c for c, v in d.items() if c.startswith("_") is False and v in ("", [], {}, None)]

    checklist = "\n".join(
        f"| {cid} | {desc} | {'bloqueante' if cid not in ('C08',) else 'declarable'} |"
        for cid, desc, _ in CRITERIOS)

    return f"""# CONTRATO DEL SITIO NUEVO — {d['nombre']}

Este archivo es la orden de trabajo y, a la vez, el criterio con el que el trabajo
se va a aceptar o rechazar. Está generado desde `config.json`: **no lo edites acá**,
se regenera.

---

## TAREA

Construir el sitio web nuevo de **{d['nombre']}** — {d['negocio']} — como un sitio
estático de una sola página (`index.html`) más sus recursos, listo para publicarse.
Es un reemplazo del sitio que hoy no existe: su presencia actual es Instagram y un
PDF del menú alojado en Google Drive.

## ALCANCE

Escribí **únicamente** dentro del directorio actual (`02-sitio/`). Los archivos que
podés crear o modificar son:

- `index.html`
- `assets/` (imágenes, hojas de estilo, lo que necesites)
- `robots.txt`
- `sitemap.xml`

No toques nada fuera de este directorio. No crees README, ni notas, ni archivos de
prueba. No instales dependencias: es HTML, CSS y, si hace falta, JavaScript del lado
del navegador, sin frameworks ni CDN de terceros.

## DATOS REALES (usá estos, no inventes otros)

| Dato | Valor |
|---|---|
| Nombre | {d['nombre']} |
| Qué es | {d['negocio']} |
| Rubro y ciudad | {d['rubro']} |
| Dirección | {d['direccion'] or '**(falta en la config)**'} |
| Teléfono | {d['telefono'] or '**(falta en la config)**'} |
| WhatsApp | {'+'+d['whatsapp'] if d['whatsapp'] else '**(falta en la config)**'} |
| Mensaje que abre el WhatsApp | «{d['whatsappMensaje']}» |
| Horarios | {d['horarios'] or '**(falta: NO inventar horarios)**'} |
| Cómo llegar | {d['mapa'] or '—'} |
| Color de marca | `{d['color']}` (medido del logo real) |
| Habilitación | {d['habilitacion'] or '—'} |
| URL canónica (C03) | {d['canonical'] or '**(pendiente: el dominio todavía no está definido)**'} |
| Dominio previsto | {d['dominioPrevisto'] or '**(sin decidir)**'} |

Redes (enlazalas tal cual):
{lista([f'{k}: {v}' for k, v in redes.items()])}

Productos y secciones de contenido:
{lista(productos)}

Secciones que la navegación **tiene que tener** (la propuesta promete {n_sec}):
{lista(d['secciones'] or [f'({n_sec} secciones: elegilas vos, coherentes con los productos)'])}

### Reglas de contenido

1. **Todo dato que sale de esta tabla se escribe como texto en el HTML** (no como
   imagen): dirección, teléfono, horarios y productos. Es lo que Google lee.
2. **Lo que dice «falta en la config» no se inventa y no se rellena con un
   supuesto.** Si falta el horario, la sección de horarios muestra «Consultá por
   WhatsApp» y vos lo anotás en tu respuesta final como dato pendiente.
3. **No hay fotos propias del cliente.** No hay que usar fotos de terceros ni
   imágenes bajadas de internet. Construí las piezas gráficas que necesites como
   SVG propios (patrones, siluetas, íconos), todos con `alt` descriptivo en
   español. `C08` (srcset) queda declarado como pendiente por este motivo.
4. Español de Argentina, trato de **vos**, sin signos de admiración apilados y sin
   emojis en el cuerpo del texto.
5. **No inventes el dominio ni la URL canónica.** Si la tabla dice que están
   pendientes, poné exactamente `href="PENDIENTE-DOMINIO"` en el `canonical` y en el
   `og:url`, y anotalo en tu respuesta. Un dominio adivinado a partir del nombre del
   negocio puede ser el sitio de otra empresa: el criterio C18 rechaza cualquier
   dominio que no esté declarado en esa tabla.

## ACEPTACIÓN

El trabajo se acepta sólo si pasa **los {len(CRITERIOS)} criterios** de esta lista. Son
ejecutables: el script que los corre después parsea tu `index.html` y tus archivos.

| # | Criterio | Tipo |
|---|---|---|
{checklist}

Detalle de los que se prestan a confusión:

- **C02:** la meta description debe medir entre {DESC_MIN} y {DESC_MAX} caracteres.
  Contá los caracteres antes de entregar.
- **C05:** {WA_MIN} enlaces `wa.me` como mínimo, todos apuntando a
  `https://wa.me/{d['whatsapp']}`. El número va en formato internacional sin `+`.
- **C06/C07:** **todas** las `<img>` con `alt` de 3 caracteres o más; todas con
  `loading="lazy"` salvo la de portada, que va primero y con `fetchpriority="high"`.
- **C09/C10:** exactamente **un** `<h1>`, y **{H2_MIN} o más** `<h2>`.
- **C12:** la `<nav>` o el `<header>` tiene que tener al menos **{n_sec} enlaces**.
- **C15:** la dirección y el teléfono tienen que poder leerse como texto en el DOM.
- **C17:** si ponés un formulario, cada campo necesita su `<label>`.

## RESTRICCIONES

1. Nada de CDN ni de librerías externas: el sitio tiene que funcionar sin red más
   allá del propio archivo.
2. Nada de datos inventados: ni teléfonos, ni horarios, ni precios, ni reseñas, ni
   direcciones. Si te falta un dato, decilo, no lo completes.
3. Nada de fotos de terceros.
4. No corras `git`. No publiques nada. No salgas del directorio.
5. No uses `target="_blank"` en enlaces internos: no navega en webviews.

## EVIDENCIA QUE TENÉS QUE DEVOLVER

1. La lista de archivos que creaste, con su tamaño.
2. **La cuenta de caracteres de tu meta description** y el valor exacto.
3. Cuántos enlaces `wa.me`, cuántos `<h1>`, cuántos `<h2>` y cuántas `<img>` con
   `alt` quedaron en el archivo final — contados sobre el archivo, no de memoria.
4. Qué datos de la tabla quedaron **pendientes** y por qué.
"""


def cmd_contrato(args) -> int:
    cfg = leer_config()
    texto = armar_contrato(cfg)
    SITIO.mkdir(parents=True, exist_ok=True)
    CONTRATO.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    print(f"\n[escrito en {CONTRATO.relative_to(ROOT)} — {len(texto)} caracteres]")
    return 0


# ─────────────────────────── invocar a DSH ───────────────────────────

def resolver_dsh():
    """El ejecutable real de `dsh`.

    En Windows `subprocess` sin shell NO resuelve un nombre sin extensión: `dsh` es un
    script y el que corre es `dsh.cmd`. Sin esto, la delegación falla con «no encontré
    el comando dsh» aunque esté instalado y en el PATH.
    """
    for cand in ("dsh", "dsh.cmd"):
        exe = shutil.which(cand)
        if exe:
            return exe
    npm = Path(os.environ.get("APPDATA", "")) / "npm" / "dsh.cmd"
    return str(npm) if npm.exists() else None


def comando_dsh(tarea: str):
    """Los .cmd/.bat necesitan cmd.exe: CreateProcess no los ejecuta solo."""
    exe = resolver_dsh()
    if not exe:
        return None
    if exe.lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/c", exe, "headless", tarea]
    return [exe, "headless", tarea]


def cmd_generar(args) -> int:
    cfg = leer_config()
    texto = armar_contrato(cfg)
    SITIO.mkdir(parents=True, exist_ok=True)
    CONTRATO.write_text(texto + "\n", encoding="utf-8")
    print(f"contrato escrito: {CONTRATO.relative_to(ROOT)} ({len(texto)} caracteres)")

    tarea = (
        "Vas a construir un sitio web. El contrato completo —tarea, alcance, datos "
        "reales, criterios de aceptación, restricciones y evidencia que tenés que "
        "devolver— está en el archivo CONTRATO.md del directorio actual. "
        "Leelo entero primero y ejecutalo al pie de la letra. Empezá ahora."
    )
    cmd = comando_dsh(tarea)
    if not cmd:
        print("\n✗ no encontré el comando `dsh`. Verificá: dsh --version")
        return 2
    print(f"\n$ {' '.join(cmd[:2])} headless …   (cwd={SITIO})")
    if args.dry_run:
        print("\n[dry-run: no ejecuto DSH]")
        return 0

    try:
        r = subprocess.run(cmd, cwd=str(SITIO), capture_output=True, text=True,
                           errors="replace", timeout=ESPERA_DSH, shell=False)
    except subprocess.TimeoutExpired:
        print(f"\n✗ DSH no terminó en {ESPERA_DSH}s. Revisá {SITIO} igual: puede haber entregado.")
        return 2
    except OSError as e:
        print(f"\n✗ no pude ejecutar DSH: {e}")
        return 2

    print("\n--- lo que dijo DSH (auto-reporte: NO es evidencia) ---")
    print((r.stdout or "").strip()[:2500] or "(sin salida)")
    if r.stderr.strip():
        print("\n--- stderr ---")
        print(r.stderr.strip()[:800])
    print(f"\nexit={r.returncode}")
    print("\nAhora verificalo:  python scripts/generar-sitio.py verificar")
    return 0 if r.returncode == 0 else 1


# ─────────────────────────── verificar ───────────────────────────

def leer_piezas() -> dict:
    idx = SITIO / "index.html"
    if not idx.exists():
        raise SystemExit(f"no existe {idx.relative_to(ROOT)}: no hay nada que verificar")
    p = {"html": idx.read_text(encoding="utf-8", errors="replace")}
    for nombre in ("robots.txt", "sitemap.xml"):
        f = SITIO / nombre
        p[nombre.split(".")[0]] = f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
    return p


def cmd_verificar(args) -> int:
    cfg = leer_config()
    conf = datos_del_lead(cfg)
    conf["_secciones_prometidas"] = secciones_prometidas(promesas(cfg))
    p = leer_piezas()

    print("=" * 74)
    print(f"  VERIFICANDO EL SITIO NUEVO · {conf['nombre']}")
    print("=" * 74)
    print(f"  index.html: {len(p['html'])} caracteres\n")

    cumple, no, pend = [], [], []
    for cid, desc, fn in CRITERIOS:
        try:
            estado, ev = fn(p, conf)
        except Exception as e:  # noqa: BLE001
            estado, ev = "no", f"el criterio no pudo evaluarse: {e}"
        (cumple if estado == "cumple" else no if estado == "no" else pend).append((cid, desc, ev))

    for titulo, items, marca in (("CUMPLEN", cumple, "✓"),
                                 ("NO CUMPLEN", no, "✗"),
                                 ("PENDIENTES (declarados)", pend, "·")):
        if not items:
            continue
        print(f"  {titulo} ({len(items)}):")
        for cid, desc, ev in items:
            print(f"    {marca} {cid}  {desc[:58]:<58} {ev}")
        print()

    print("-" * 74)
    if no:
        print(f"  ✗ {len(no)} criterio(s) sin cumplir de {len(CRITERIOS)}: el sitio no se publica así.")
        return 1
    print(f"  ✓ {len(cumple)}/{len(CRITERIOS)} criterios cumplidos"
          + (f", {len(pend)} declarado(s) como pendiente" if pend else ""))
    return 0


# ─────────────────────────── enchufar la URL ───────────────────────────

def cmd_enchufar(args) -> int:
    if not args.url:
        print("falta --url"); return 2

    # Guardián: `modelo.url` viaja al entregable publicado —es el botón «Abrir el sitio
    # nuevo» del hub y el `modelo.url` que el §10 coteja—. Si queda una dirección local,
    # el botón no le abre a nadie. Pasó de verdad: se publicó el hub apuntando a
    # http://127.0.0.1:8942 y el entregable salió roto sin que ningún gate lo viera.
    if re.match(r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(:\d+)?(/|$)", args.url, re.I):
        if not args.permitir_local:
            print(f"✗ {args.url} es una dirección LOCAL.")
            print("  Ese valor se publica: es el botón «Abrir el sitio nuevo» del entregable.")
            print("  Para cotejar contra un servidor local usá --permitir-local, y antes de")
            print("  publicar volvé a enchufar la URL pública del sitio.")
            return 2
        print(f"⚠ {args.url} es local: sirve para cotejar, NO para publicar.")

    cfg = leer_config()
    modelo = cfg.setdefault("modelo", {})
    previo = modelo.get("url")
    modelo["url"] = args.url
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"modelo.url: {previo!r} → {args.url!r}")
    print("\nAhora el §10 tiene contra qué cotejar:  python scripts/cotejar-promesas.py")
    return 0


# ─────────────────────────── fijar el dominio ───────────────────────────

def cmd_dominio(args) -> int:
    """Reemplaza el marcador PENDIENTE-DOMINIO por la URL real del sitio.

    Es el paso que cierra C03. Existe como comando y no como edición a mano porque el
    marcador aparece en cinco lugares distintos —canónica, og:url, tres nodos del
    JSON-LD, robots.txt y sitemap.xml— y una edición a mano deja alguno atrás.
    """
    if not args.url:
        print("falta --url"); return 2
    url = args.url if args.url.endswith("/") else args.url + "/"
    cfg = leer_config()
    cfg.setdefault("sitio", {})["canonical"] = url
    if not (cfg.get("sitio") or {}).get("_canonicalNota"):
        cfg["sitio"]["_canonicalNota"] = "fijado por generar-sitio.py dominio"
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tocados = []
    for nombre in ("index.html", "robots.txt", "sitemap.xml"):
        f = SITIO / nombre
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        n = t.count(MARCADOR)
        if not n:
            continue
        t = t.replace(MARCADOR, url)
        # El marcador se usaba pegado a "/sitemap.xml": con la barra final del dominio
        # quedaba una barra doble. Se limpia acá, no en el sitio ya publicado.
        t = t.replace("//sitemap.xml", "/sitemap.xml")
        f.write_text(t, encoding="utf-8")
        tocados.append(f"{nombre} ({n})")

    print(f"dominio: {url}")
    print(f"  config.sitio.canonical actualizado")
    print(f"  marcador reemplazado en: {', '.join(tocados) if tocados else 'ningún archivo'}")
    print(f"\nAhora:  python scripts/generar-sitio.py verificar")
    return 0


# ─────────────────────────── publicar ───────────────────────────

def cmd_publicar(args) -> int:
    """El sitio no se publica aparte: `armar-dist.py` ya lo lleva a dist/sitio/
    y el workflow de Pages del repo del lead lo sube. Acá se orquesta eso."""
    pasos = [
        (["python", str(ROOT / "scripts" / "armar-dist.py")], "armar dist/"),
        (["git", "add", "-A"], "git add"),
        (["git", "-c", "user.name=Lisandro Cacciatore",
          "-c", "user.email=lisandrocacciatore@gmail.com",
          "commit", "-m", "sitio nuevo: construido por el bot generador y verificado"], "commit"),
    ]
    for cmd, desc in pasos:
        print(f"$ {' '.join(cmd[:3])}…  ({desc})")
        if args.dry_run:
            continue
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, errors="replace")
        if r.returncode != 0 and desc != "commit":
            print(f"  ✗ falló: {(r.stderr or r.stdout).strip()[:300]}")
            return 1
    print("\nFalta el push y esperar el deploy. Verificá por SHA del commit, no por «el último run»:")
    print("  git push origin main")
    print("  gh run list --limit 3")
    print("Después:  python scripts/generar-sitio.py enchufar --url <URL de Pages>/sitio/")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Generador del sitio nuevo de un lead")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre, fn, ayuda in (("contrato", cmd_contrato, "deriva y muestra el contrato del sitio"),
                              ("generar", cmd_generar, "invoca a DSH con el contrato"),
                              ("verificar", cmd_verificar, "corre los criterios sobre 02-sitio/"),
                              ("dominio", cmd_dominio, "fija la URL canónica y reemplaza el marcador"),
                              ("enchufar", cmd_enchufar, "escribe la URL en config.modelo.url"),
                              ("publicar", cmd_publicar, "arma dist, commitea y guía el push")):
        s = sub.add_parser(nombre, help=ayuda)
        s.add_argument("--dry-run", action="store_true")
        if nombre in ("enchufar", "dominio"):
            s.add_argument("--url", default="")
        if nombre == "enchufar":
            s.add_argument("--permitir-local", action="store_true",
                           help="acepta una URL local (sólo para cotejar, no para publicar)")
        s.set_defaults(func=fn)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
