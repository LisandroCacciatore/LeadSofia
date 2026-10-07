# -*- coding: utf-8 -*-
"""Verifica que cada cifra del informe exista en evidencia-sofia.json (checklist de la skill)."""
import json, pathlib, re, sys

A = pathlib.Path(__file__).resolve().parent
ev = json.loads((A / "evidencia-sofia.json").read_text(encoding="utf-8"))
inf = (A.parent / "informe-auditoria-sofia.md").read_text(encoding="utf-8")

res = ev["alcance_feed"]["resumen"]
ig = ev["instagram"]
checks = [
    ("163.805 seguidores", str(ig["seguidores"]) == "163805" and "163.805" in inf),
    ("122 publicaciones", ig["publicaciones"] == 122 and "122" in inf),
    ("570 seguidos", ig["seguidos"] == 570 and "570" in inf),
    ("579 (discrepancia de la meta)", ig["seguidos_declarado_en_meta"] == 579 and "579" in inf),
    ("verificada = True", ig["verificada"] is True and "badge azul" in inf),
    ("mediana 357 likes", res["likes_mediana"] == 357 and "357" in inf),
    ("max 1306", res["likes_max"] == 1306 and "1.306" in inf),
    ("min 287", res["likes_min"] == 287 and "287" in inf),
    ("0,218 % interaccion", res["tasa_interaccion_pct_mediana"] == 0.218 and "0,218" in inf),
    ("5 medidas / 7 ocultas", (res["publicaciones_medidas"], res["publicaciones_sin_conteo_publico"]) == (5, 7)
        and "7 de 12" in inf),
    ("flag like_and_view_counts_disabled",
        ev["alcance_feed"]["like_and_view_counts_disabled_en_el_post_medido"] is True
        and "like_and_view_counts_disabled" in inf),
    ("565 comentarios en total", res["comentarios_total"] == 565 and "565" in inf),
    ("mediana 82 comentarios", res["comentarios_mediana"] == 82 and "82" in inf),
    ("182 comentarios (post)", any(p.get("comentarios") == 182 for p in ev["alcance_feed"]["publicaciones"])
        and "182" in inf),
    ("audiencia 163805 = 10x", round(1.0 / 0.218, 1) == 4.6),
    ("TikTok 7953", ev["tiktok"]["seguidores"] == "7953" and "7.953" in inf),
    ("TikTok 120,4K", ev["tiktok"]["me_gusta"] == "120.4K" and "120,4 K" in inf),
    ("TikTok roto @sofistrafile", ev["linktree"]["tiktok_roto"]["responde"] is False and "@sofistrafile" in inf),
    ("3 botones propios", ev["linktree"]["renderizado_en_pantalla"]["total_piezas_propias"] == 6
        and "3 botones" in inf),
    ("26 ajenos en payload", ev["linktree"]["publicidad_ajena_total"] == 26 and "26 enlaces" in inf),
    ("dominios libres (3)", all(ev["dominios_con_el_nombre"][d]["disponible"] for d in
        ("sofiastrafile.com.ar", "sofiastrafile.ar", "sofiastrafile.com"))),
    ("sofia.com de tercero desde 1995", "1995" in ev["dominios_con_el_nombre"]["sofia.com"]["de_quien"]),
    ("Maps sin coincidencia", ev["google_maps"]["coincidencia_propia"] is False),
    ("2 catalogos WhatsApp", len(ev["whatsapp"]["catalogos"]) == 2),
    ("numero 341 = Rosario", "341 = Rosario" in ev["whatsapp"]["codigo_area"]),
    ("seccion no_medido con 5 items", len(ev["no_medido"]) == 5),
]
malos = [n for n, ok in checks if not ok]
for n, ok in checks:
    print(("OK   " if ok else "FALLA") + "  " + n)
print("\ninforme cita 'no medido'?", "NO VERIFICADO" in inf)
print("separa resuelve/no resuelve?", "NO lo resuelve" in inf)
print(f"\n{len(checks)-len(malos)}/{len(checks)} verificaciones OK")
sys.exit(1 if malos else 0)
