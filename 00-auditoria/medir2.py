# -*- coding: utf-8 -*-
"""Segunda pasada: reintenta los posts sin conteos y amplia la muestra. Tambien TikTok."""
from playwright.sync_api import sync_playwright
import re, json, pathlib, sys
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
META_RE=re.compile(r"([\d.,]+)\s+likes?,\s*([\d.,]+)\s+comments?\s*-\s*\S+\s+el\s+(\w+\s+\d+,\s+\d+)")
out=pathlib.Path("00-auditoria")
def num(t): return int(t.replace(".","").replace(",",""))

with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", viewport={"width":1440,"height":1000}, user_agent=UA)
    pg=ctx.new_page()

    # ---- juntar shortcodes (scroll largo) ----
    pg.goto("https://www.instagram.com/sofiastrafile/", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    for _ in range(10):
        pg.mouse.wheel(0,3000); pg.wait_for_timeout(1500)
    hrefs=pg.eval_on_selector_all("a[href*='/p/'], a[href*='/reel/']","els=>els.map(e=>e.href)")
    sc=[]; seen=set()
    for h in hrefs:
        c=h.split("?")[0].rstrip("/")
        if c and c not in seen: seen.add(c); sc.append(c)
    print(f"shortcodes visibles: {len(sc)}")

    filas=[]
    for url in sc[:30]:
        fila={"url":url,"shortcode":url.split("/")[-1],
              "tipo":"reel" if "/reel/" in url else "post","intentos":[]}
        for intento in range(3):
            pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(4500 + intento*2500)
            meta=pg.query_selector('meta[name="description"]') or pg.query_selector('meta[property="og:description"]')
            txt=(meta.get_attribute("content") or "") if meta else ""
            mm=META_RE.match(txt)
            fila["intentos"].append(txt[:120])
            if mm:
                fila["likes"]=num(mm.group(1)); fila["comentarios"]=num(mm.group(2))
                fila["fecha"]=mm.group(3); fila["ok_en_intento"]=intento+1; break
        t=pg.query_selector("time[datetime]")
        fila["iso"]=t.get_attribute("datetime") if t else None
        filas.append(fila)
        print(f"  {fila['shortcode']:16} {fila.get('fecha','SIN CONTEO'):20} "
              f"likes={fila.get('likes','?'):>6} com={fila.get('comentarios','?'):>5} intento={fila.get('ok_en_intento','-')}")

    (out/"alcance-ig-2.json").write_text(json.dumps({"publicaciones":filas},ensure_ascii=False,indent=2),encoding="utf-8")

    # ---- TikTok ----
    tt={}
    try:
        pg.goto("https://www.tiktok.com/@sofistrafile", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(8000)
        for sel in ['meta[name="description"]','meta[property="og:description"]']:
            el=pg.query_selector(sel)
            tt[sel]=el.get_attribute("content") if el else None
        tt["title"]=pg.title(); tt["url"]=pg.url
        tt["body"]=pg.inner_text("body")[:800]
        pg.screenshot(path=str(out/"tiktok.png"))
    except Exception as e:
        tt["error"]=str(e)[:200]
    print("\n== TIKTOK ==")
    print(tt.get("title")); print(tt.get("meta[name=\"description\"]") or tt.get("error"))
    (out/"tiktok.json").write_text(json.dumps(tt,ensure_ascii=False,indent=2),encoding="utf-8")
    b.close()
