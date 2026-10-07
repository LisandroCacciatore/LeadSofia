# Auditoría de presencia digital — Sofía Strafile (@sofiastrafile)

**Fecha:** 7 de octubre de 2026 · **Método:** Chrome real headless, sin sesión ni API (IP 181.1.45.41)
**Evidencia:** `00-auditoria/evidencia-sofia.json` · **Crudos y capturas:** `00-auditoria/`

---

## 1 · Quién es, en números propios

| Dato | Valor | Estado |
|---|---|---|
| Nombre | Sofía Strafile \| Asesora de imagen y colorimetría | MEDIDO |
| Seguidores | **163.805** | MEDIDO (JSON embebido de IG) |
| Publicaciones | 122 | MEDIDO |
| Sigue a | 570 (la meta dice 579: **las dos medidas de IG no coinciden**) | MEDIDO |
| Verificada | **Sí**, badge azul | MEDIDO |
| Bio | «Imagen ✨Colorimetría ✨Estilo personal. / Atención Online al 🌏 / 🇦🇷» | MEDIDO |
| Link en bio | `linktr.ee/sofia.strafile` (Linktree) | MEDIDO |
| Sitio propio | **No tiene** | MEDIDO |
| Google Maps | **Sin ficha** (la búsqueda devuelve homónimas ajenas) | MEDIDO |
| TikTok | **@sofiastrafile** · 7.953 seguidores · 120,4 K me gusta | MEDIDO |
| WhatsApp | +54 9 **341** 615-3151 → **Rosario**, no CABA | MEDIDO |
| Oferta real publicada | 2 catálogos de WhatsApp: «PROGRAMA 1:1 ASESORÍA DE IMAGEN» y «COLORIMETRÍA 1:1» | MEDIDO |
| Precios | no los expone fuera de la app | NO VERIFICADO |

## 2 · El hallazgo que reordena la auditoría: 163 K seguidores, 0,22 % de interacción

Se midieron las 12 publicaciones visibles sin sesión. **En 7 de 12 los «me gusta» están ocultos**
(`like_and_view_counts_disabled: true` está en el HTML del post). En las 5 medibles:

```
ventana: 26 ago → 3 oct 2026 (37 días)      publica ~1 vez por semana
likes:   min 287 · mediana 357 · máx 1.306 · promedio 638
comentarios: 565 en total, mediana 82 por post
tasa de interacción: 357 / 163.805 = 0,218 %   (rubro: 1-3 % [INFERIBLE])
```

Dos lecturas, las dos ciertas:

- **Lo bueno:** los comentarios son altísimos para el tamaño (82 de mediana, 182 en un post) porque
  su llamado es «comentá este reel y charlemos». **Su motor real es el comentario → DM, no el
  «link en bio».** Eso es un activo, y el sitio hoy no lo toca.
- **Lo malo:** **el número que muestra no es el que tiene.** 0,22 % está diez veces abajo del rango
  del rubro, y encima **no se puede medir del todo** porque ella misma esconde los likes en la
  mayoría de los posts. Un sitio nuevo no cambia esto. **Decirlo antes de que lo diga ella.**
  Y la muestra no es aleatoria: puede estar sobrerrepresentando las piezas fuertes.

## 3 · Los canales alquilados: dónde vive hoy todo su embudo

| Canal | De quién es | Dónde termina la clienta |
|---|---|---|
| Instagram (163 K) | Meta | en su DM, sin registro de nada |
| Linktree (plan gratis) | Linktree | en 3 botones que llevan **los tres al mismo WhatsApp** |
| WhatsApp + 2 catálogos | Meta | en un chat; **no guarda el contacto en ningún lado suyo** |
| TikTok (7.953 / 120,4 K) | ByteDance | — |
| Google (dominio, Maps) | **nadie: no existe** | no la encuentra quien la busca por nombre |

Su página de enlaces son **3 botones (Asesoría de imagen · WhatsApp · Colorimetría), los tres al
mismo WhatsApp**, más 3 íconos sociales. **Ningún precio, ningún servicio por escrito, ningún dato
que quede.** Y la página trabaja para Linktree: cierra con «**Únete a sofia.strafile en Linktree**»,
o sea que le ofrece Linktree a su propia audiencia de 163 mil personas — publicidad ajena, pero de
la plataforma, no de marcas.

> **Aclaración metodológica:** en el payload de esa página hay 26 enlaces de afiliados de terceros
> (Hulu, HelloFresh, Curology, Babbel…). **No se renderizan** en la vista pública: van en el JSON,
> no en la pantalla. Se declaran acá para que no aparezcan como si fueran suyos.

Y un enlace roto: su ícono de TikTok manda a **`tiktok.com/@sofistrafile`**, que **no existe**
(TikTok responde «No se pudo encontrar esta cuenta»). La cuenta real es **`@sofiastrafile`**.
Es el único desvío propio que tiene y está caído.

## 4 · El nombre: libre. El apellido: colonizado

Verificado por whois TCP (NIC.ar puerto 43 / Verisign puerto 43), no por status HTTP:

| Dominio | Disponible | De quién |
|---|---|---|
| `sofiastrafile.com.ar` | **SÍ** | — |
| `sofiastrafile.ar` | **SÍ** | — |
| `sofiastrafile.com` | **SÍ** | — |
| `sofia-strafile.com` | SÍ | — |
| `strafile.com` | no | tercero, registrado 2024-06-05 (Squarespace Domains) |
| `sofia.com.ar` | no | tercero, López Fuente Luciano, desde 2016, vence 26/07/2027 |
| `sofia.com` | no | tercero, registrado 1995 (GoDaddy/Atom) |

El nombre exacto que ya usa a diario está **libre en los tres TLD que importan**. Ese es un activo
con fecha de vencimiento: se registra hoy o se registra caro después.

## 5 · El mockup que recibió el DSH: veredicto afirmación por afirmación

El HTML dice estar en `Palermo, Buenos Aires`, con mail `hola@sofia.com`, +100 clientas y tres
testimonios con nombre y apellido. Contrastado con su presencia real:

| # | Afirmación del mockup | Veredicto | Qué poner en su lugar |
|---|---|---|---|
| A1 | Marca «Sofia.» / «Sofia Asesoría Urbana» | **INVENTADO** | «Sofía Strafile» — es marca personal, no una razón social |
| A2 | «Asesora de Imagen Profesional» | **OK** | sumale **colorimetría**, que es su palabra |
| A3 | Personal shopping | NO VERIFICADO | su oferta publicada es 1:1 imagen + colorimetría |
| A4 | «Palermo, Buenos Aires» | **INVENTADO** | su bio dice «Atención Online», sin dirección; el teléfono es de Rosario |
| A6 | «+100 ejecutivas transformadas» | **SUBASTIMADO por 1.600×** | 163.805 seguidores; y los comentarios, que es su prueba real |
| A7 | Testimonios Lucas M. / Mariana V. / Carolina R. | **INVENTADOS** | highlights «Ustedes» + 182 comentarios reales en un reel |
| A8 | «Asesora certificada» | **CON RESPALDO, sin decir cuál** | su post del 6/6/26: se graduó en España, `@institutoimagenpersonal` |
| A9 | Colorimetría | **OK — es su core** | es lo que vende *y* lo que la hace viral |
| A12-A14 | Planes Arranque / Renovación / Transformación, con «cápsula de 30 prendas», «3 looks», «14 días de seguimiento» | **INVENTADOS** | sus productos reales: «Programa 1:1 Asesoría de imagen» y «Colorimetría 1:1» |
| A15 | «3 cuotas. Reembolso total o parcial» | **INVENTADO y grave** | es un compromiso comercial con consecuencia legal: no se inventa |
| A17 | WhatsApp +54 9 341 615-3151 | **CORRECTO** | coincide con su Linktree |
| A18 | `hola@sofia.com` | **INVENTADO y peligroso** | `sofia.com` es de un tercero desde 1995: **ese mail no le llega a ella** |
| A19 | «Respuesta en menos de 24 hs» | NO VERIFICADO | — |
| — | Formulario de reserva | **NO ENVÍA NADA** | `type="button"`, sin `action` ni `name`: hoy es un embudo muerto |

**Traducción:** de las 15 piezas verificables, 2 son correctas, 4 son «suena bien pero nadie lo
chequeó» y **9 son datos inventados**, dos de ellos con riesgo concreto (el mail a un dominio ajeno
y una política de reembolso que ella nunca prometió). Un sitio así se cae en la primera
conversación, que es exactamente donde vive su negocio.

## 6 · Lo que el entregable SÍ resuelve y lo que NO

**Resuelve (y es mucho, porque hoy no existe nada):**
1. **Casa propia en el nombre que ya usa** — `sofiastrafile.com.ar` está libre hoy.
2. **El link en bio deja de trabajar para otro** — hoy son 3 botones al mismo WhatsApp dentro del
   chrome de Linktree (que además le ofrece Linktree a su audiencia).
3. **Arreglar el TikTok roto** (`@sofistrafile` → `@sofiastrafile`).
4. **Descubrimiento:** sin fichа de Maps ni dominio, quien la busca por nombre no la encuentra.
5. **Capturar el contacto** que hoy nace en el comentario, pasa al DM y muere sin registro.

**NO lo resuelve — y hay que decirlo en la primera línea:**
1. **La interacción del 0,22 %.** Es audiencia y formato, no diseño. El sitio no lo arregla.
2. **Los likes ocultos en 7 de 12 posts.** No hay prueba social que mostrar ni alcance que medir.
3. **Que su viralidad sea en cuerpos ajenos** (Tini, Luisana Lopilato, Emilia, Celeste Cid): el
   sitio no le construye autoridad propia, eso es contenido y oferta.

## 7 · Qué falta antes de que el DSH toque el HTML

Lo mínimo, en orden, sin lo cual cualquier construcción sobre ese mockup propaga datos falsos:

1. **Confirmar con ella**: localidad real (¿Rosario? ¿atiende presencial?), oferta y precios reales,
   si tiene testimonios con permiso de uso y si da cuotas/reembolsos.
2. **Registrar el dominio** antes de escribir una línea de HTML (mientras esté libre).
3. **Reemplazar los 9 inventados** por lo medido de este informe, o borrarlos.
4. **Definir el formulario**: si va a existir, tiene que enviar a algún lado (mail propio o CRM);
   si no, el camino sigue siendo el catálogo de WhatsApp, que ya funciona.
5. **Decidir qué se muestra como prueba social** mientras los likes estén ocultos.

## 8 · Lo que no se pudo medir (y por qué)

| Qué | Por qué | Estado |
|---|---|---|
| Seguidores reales vs comprados | Instagram solo publica el total | NO VERIFICADO |
| Precios de sus programas | los catálogos de WhatsApp no los exponen fuera de la app | NO VERIFICADO |
| Presencia orgánica en Google por su nombre | Google devolvió captcha «tráfico inusual» desde esta red | NO VERIFICADO |
| Alcance de las 7 publicaciones con likes ocultos | `like_and_view_counts_disabled` | NO VERIFICADO por diseño |
| Localidad real | la bio dice «Atención Online», sin dirección | NO VERIFICADO |
| Visitas, DMs, conversión a venta | internos | no se estiman |
