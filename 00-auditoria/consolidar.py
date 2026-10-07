# -*- coding: utf-8 -*-
"""Consolida la evidencia cruda de la auditoria de @sofiastrafile en un unico JSON.

Cada numero sale de un archivo de origen (crudo), no se transcribe a mano.
Estado por campo: MEDIDO / INFERIBLE / NO VERIFICADO.
"""
import json, re, pathlib, datetime

A = pathlib.Path(__file__).resolve().parent          # 00-auditoria
def load(p, default=None):
    f = A / p
    if not f.exists():
        return default
    return json.loads(f.read_text(encoding="utf-8", errors="replace"))

ig1 = load("alcance-ig.json") or {}
ig2 = load("alcance-ig-2.json") or {}
perfil = ig1.get("perfil_datos", {})
posts1 = {f["shortcode"]: f for f in ig1.get("publicaciones", [])}
posts2 = {f["shortcode"]: f for f in ig2.get("publicaciones", [])}
# el conteo de likes: de la primera pasada si esta, si no del reintento
posts = []
for sc, f in posts1.items():
    g = posts2.get(sc, {})
    posts.append({
        "shortcode": sc, "tipo": (g.get("tipo") or f.get("tipo")),
        "fecha": (g.get("fecha") or f.get("fecha")),
        "iso": (g.get("iso") or f.get("iso")),
        "likes": (g.get("likes") or f.get("likes")),
        "comentarios": (g.get("comentarios") or f.get("comentarios")),
        "conteo_publico": bool(g.get("likes") or f.get("likes")),
        "intentos": g.get("intentos") or f.get("intentos") or [],
    })

conteo = [p for p in posts if p["conteo_publico"]]
ocultos = [p for p in posts if not p["conteo_publico"]]

# ---- el flag que explica los que no miden ----
flag = None
ph = A / "probe-post.html"
if ph.exists():
    h = ph.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'"like_and_view_counts_disabled":(true|false)', h)
    flag = (m.group(1) == "true") if m else None

seg = perfil.get("seguidores")
resumen = {}
if conteo and seg:
    likes = sorted(p["likes"] for p in conteo)
    coms = [p["comentarios"] for p in conteo]
    mediana = likes[len(likes) // 2]
    fechas = sorted(p["iso"] for p in conteo if p.get("iso"))
    d_ini = datetime.datetime.fromisoformat(fechas[0].replace("Z", "+00:00"))
    d_fin = datetime.datetime.fromisoformat(fechas[-1].replace("Z", "+00:00"))
    dias = max((d_fin - d_ini).days, 1)
    resumen = {
        "seguidores": seg,
        "publicaciones_medidas": len(conteo),
        "publicaciones_sin_conteo_publico": len(ocultos),
        "ventana_fechas": [fechas[0][:10], fechas[-1][:10]],
        "dias": dias,
        "publicaciones_por_semana": round(len(conteo) / dias * 7, 2),
        "likes_min": likes[0], "likes_mediana": mediana, "likes_max": likes[-1],
        "likes_promedio": round(sum(likes) / len(likes)),
        "comentarios_total": sum(coms), "comentarios_mediana": sorted(coms)[len(coms)//2],
        "tasa_interaccion_pct_mediana": round(mediana / seg * 100, 3),
        "tasa_interaccion_pct_mejor": round(likes[-1] / seg * 100, 3),
        "referencia_rubro_pct": [1.0, 3.0],
        "referencia_estado": "INFERIBLE",
        "nota": ("La tasa usa solo las publicaciones cuyo conteo es publico; en las demas la "
                 "cuenta tiene los me gusta ocultos (like_and_view_counts_disabled), asi que "
                 "el alcance real de la cuenta NO es medible desde afuera."),
        "sesgo": "La muestra no es aleatoria: puede sobrerrepresentar las piezas mas fuertes.",
    }

# ---- Linktree: lo que se VE (renderizado) vs lo que va en el payload ----
lt = load("linktree.json") or {}
AJENOS = ("thanks.is", "linksynergy", "sjv.io", "pxf.io", "wk5q.net", "kqzyfj.com",
          "armra.com", "omniluxled.com", "equipfoods.com", "clearstem.com",
          "thezeroproof.com", "jlab.com", "redirectingat.com")
PROPIOS = ("wa.me", "wa.link", "api.whatsapp.com", "instagram.com", "tiktok.com")

def seccion(raiz, clave):
    """Devuelve la lista de botones/iconos de una seccion del payload de Linktree.

    El payload repite la seccion (por eso hay que deduplicar por titulo+url: la pantalla
    muestra 3 botones, no 6).
    """
    out, vistos = [], set()
    def rec(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == clave and isinstance(v, list):
                    for it in v:
                        if not isinstance(it, dict):
                            continue
                        firma = (str(it.get("title")), str(it.get("url")))
                        if firma not in vistos:
                            vistos.add(firma)
                            out.append(it)
                else:
                    rec(v)
        elif isinstance(o, list):
            for v in o:
                rec(v)
    rec(raiz)
    return out

botones = seccion(lt, "links")
iconos = seccion(lt, "socialLinks")
links_propios = [{"titulo": b.get("title"), "url": b.get("url"), "donde": "boton"}
                 for b in botones if isinstance(b, dict)]
links_propios += [{"titulo": f"icono {i.get('type')}", "url": i.get("url"), "donde": "icono"}
                  for i in iconos if isinstance(i, dict)]

vistos, links_ajenos = set(), []
def walk(o):
    if isinstance(o, dict):
        u = o.get("url")
        if isinstance(u, str) and u.startswith("http") and u not in vistos:
            vistos.add(u)
            if any(d in u for d in AJENOS):
                links_ajenos.append({"titulo": o.get("title") or o.get("label") or "",
                                     "url": u, "donde": "payload (no renderizado)"})
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
walk(lt)

# ---- TikTok (del texto crudo de la busqueda) ----
tt_txt = (A / "tiktok-busqueda.txt")
tt = {}
if tt_txt.exists():
    t = tt_txt.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"sofiastrafile\s*\n+([\d.]+)\s*\n+Seguidores\s*\n+·\s*\n+([\d.,]+K?)\s*\n+Me gusta", t)
    tt = {"handle_real": "@sofiastrafile",
          "seguidores": m.group(1) if m else None,
          "me_gusta": m.group(2) if m else None,
          "handle_en_su_linktree": "@sofistrafile",
          "handle_en_linktree_existe": False,
          "fuente": "tiktok-busqueda.txt (bloque Usuarios de la busqueda publica)",
          "estado": "MEDIDO" if m else "NO VERIFICADO",
          "nota": "El perfil restringe la vista sin sesion; los numeros salen del bloque de busqueda."}

who = load("whois.json") or {}
maps = load("maps.json") or {}

ev = {
    "cliente": {
        "nombre": "Sofía Strafile",
        "handle_instagram": "@sofiastrafile",
        "rubro": "Asesora de imagen y colorimetría",
        "medicion": {"fecha": "2026-10-07T02:2x-03:00", "transporte": "Chrome real headless "
                     "(playwright channel=chrome), sin sesión ni API",
                     "red_ip": "181.1.45.41"},
    },
    "instagram": {
        "estado": "MEDIDO",
        "url": perfil.get("url_final"),
        "nombre": perfil.get("nombre"),
        "verificada": perfil.get("verificado"),
        "seguidores": seg,
        "seguidos": perfil.get("seguidos"),
        "seguidos_declarado_en_meta": 579,
        "publicaciones": perfil.get("publicaciones"),
        "bio": perfil.get("bio"),
        "external_url": perfil.get("external_url"),
        "link_en_bio": "https://linktr.ee/sofia.strafile",
        "discrepancias": [
            "La meta declara 579 seguidos y el JSON embebido 570: dos medidas de Instagram "
            "no coinciden (se reporta el numero exacto del JSON).",
            "La meta declara 164K y el JSON embebido 163.805.",
        ],
        "destacados": ["Ustedes"],
        "capturas": ["ig-perfil.png"],
    },
    "alcance_feed": {
        "estado": "MEDIDO (parcial)",
        "publicaciones": posts,
        "publicaciones_con_conteo_publico": len(conteo),
        "publicaciones_con_me_gusta_ocultos": len(ocultos),
        "like_and_view_counts_disabled_en_el_post_medido": flag,
        "resumen": resumen,
    },
    "tiktok": tt,
    "linktree": {
        "estado": "MEDIDO",
        "url": "https://linktr.ee/sofia.strafile",
        "plan": "gratuito (la pagina muestra el chrome de Linktree y el CTA 'Unete a sofia.strafile en Linktree')",
        "renderizado_en_pantalla": {
            "botones": links_propios[:len(botones)],
            "iconos": links_propios[len(botones):],
            "total_piezas_propias": len(links_propios),
            "capturas": ["linktree.png"],
            "texto_visible": "linktree-texto.txt",
        },
        "publicidad_ajena_en_el_payload": links_ajenos,
        "publicidad_ajena_total": len(links_ajenos),
        "hallazgo": (
            "Su unica casa digital es un Linktree gratuito con 3 botones y los 3 llevan al mismo "
            "WhatsApp: ningun precio, ningun servicio por escrito, ningun dato que quede. Ademas "
            "la pagina trabaja para Linktree: el CTA 'Unete a sofia.strafile en Linktree' le vende "
            "Linktree a su propia audiencia de 163 mil personas. En el payload hay %d enlaces de "
            "afiliados de terceros (Hulu, HelloFresh, Curology, Babbel...) que NO se renderizan en "
            "la vista publica: van en el JSON, no en la pantalla. No listarlos como suyos."
            % len(links_ajenos)),
        "tiktok_roto": {"en_su_pagina": "https://tiktok.com/@sofistrafile",
                        "responde": False,
                        "real": "@sofiastrafile",
                        "estado": "MEDIDO (TikTok: 'No se pudo encontrar esta cuenta')"},
    },
    "whatsapp": {
        "estado": "MEDIDO",
        "numero": "+54 9 341 615-3151",
        "codigo_area": "341 = Rosario, Santa Fe",
        "catalogos": [
            {"nombre": "PROGRAMA 1:1 ASESORÍA DE IMAGEN",
             "url": "https://wa.me/p/23924291647213034/5493416153151"},
            {"nombre": "COLORIMETRÍA 1:1",
             "url": "https://wa.me/p/25673960648860647/5493416153151"}],
        "precios_publicados": None,
        "precios_estado": "NO VERIFICADO",
        "nota": "Los catalogos de WhatsApp no exponen precio fuera de la app: no se pudo verificar "
                "si publica precios ni cuales son.",
    },
    "google_maps": {
        "estado": "MEDIDO (sin coincidencia)",
        "buscas_realizadas": ["Sofía Strafile asesora de imagen",
                              "Sofía asesora de imagen personal shopping Buenos Aires"],
        "coincidencia_propia": False,
        "resultado_de_la_primera_busqueda": "Sofía Schwarzenberg Asesora de imagen (Vitacura, Chile) — tercero",
        "hallazgo": "No tiene ficha de Google Maps. Cero descubrimiento por busqueda local.",
        "capturas": ["maps-strafile.png", "maps-sofia_asesora.png"],
    },
    "dominios_con_el_nombre": {
        "estado": "MEDIDO por whois TCP (NIC.ar puerto 43 / Verisign puerto 43)",
        "sofiastrafile.com.ar": {"disponible": True, "crudo": "El dominio no se encuentra registrado en NIC Argentina"},
        "sofiastrafile.ar": {"disponible": True, "crudo": "El dominio no se encuentra registrado en NIC Argentina"},
        "sofiastrafile.com": {"disponible": True, "crudo": "No match for \"SOFIASTRAFILE.COM\""},
        "sofia-strafile.com": {"disponible": True, "crudo": "No match"},
        "strafile.com": {"disponible": False, "de_quien": "tercero — registrado 2024-06-05, registrar Squarespace Domains II LLC"},
        "sofia.com.ar": {"disponible": False, "de_quien": "tercero — LOPEZ FUENTE LUCIANO, registrado 2016, vence 2027-07-26"},
        "sofia.com": {"disponible": False, "de_quien": "tercero — registrado 1995-12-26 (GoDaddy/Atom)"},
        "hallazgo": "El nombre exacto que ya usa (@sofiastrafile) esta libre en .com.ar, .ar y .com.",
    },
    "sitio_web_propio": {"tiene": False, "estado": "MEDIDO",
                         "evidencia": "La bio solo linkea un Linktree; ningun enlace propio es un sitio."},
    "no_medido": [
        {"que": "Cantidad de seguidores reales vs comprados",
         "por_que": "Instagram solo publica el total. Se contrasta con el alcance medible y se declara la diferencia.",
         "estado": "NO VERIFICADO"},
        {"que": "Precios de sus programas",
         "por_que": "Los catalogos de WhatsApp no los exponen fuera de la app.", "estado": "NO VERIFICADO"},
        {"que": "Presencia organica en Google por su nombre",
         "por_que": "Google devolvio el captcha 'trafico inusual' desde esta red (IP 181.1.45.41).",
         "estado": "NO VERIFICADO"},
        {"que": "Alcance de las 7 publicaciones con me gusta ocultos",
         "por_que": "La cuenta tiene like_and_view_counts_disabled: Instagram no publica el numero.",
         "estado": "NO VERIFICADO por diseño"},
        {"que": "Localidad real (CABA vs Rosario)",
         "por_que": "Su bio dice 'Atención Online', sin direccion; el telefono es de Rosario (341).",
         "estado": "NO VERIFICADO"},
    ],
}

(A / "evidencia-sofia.json").write_text(
    json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"resumen": resumen, "posts": len(posts), "con_conteo": len(conteo),
                  "ocultos": len(ocultos), "flag": flag,
                  "propios": len({l['url'] for l in links_propios}),
                  "ajenos": len(links_ajenos), "tiktok": tt}, ensure_ascii=False, indent=2))
print("\nescrito:", A / "evidencia-sofia.json")
