# Auditoría del repo + ciclo de captación de consultas

**Lead:** Sofía Strafile · asesora de imagen y colorimetría · atención online desde Argentina
**Fecha de esta corrida:** 10 de noviembre de 2026
**Qué se miró:** el repo `LeadSofia` (auditoría, propuesta y sitio), el perfil `@sofiastrafile` remedido hoy, y el patrón de captación de `Segovia_landing` como referencia.
**Evidencia cruda:** `00-auditoria/remedicion-2026-11/ig.json`, `ig-perfil.png`, `captura-mensaje-whatsapp.txt`, capturas en `02-sitio/capturas/`.

---

## 1 · Estado del repo, medido

| Qué | Valor | Cómo se midió |
|---|---|---|
| Commits | 1 (`d52e527`) | `git log --oneline` |
| Piezas | `00-auditoria/` · `01-propuesta/` · `02-sitio/` · `brand/` · `scripts/` (24) · `templates/` | `ls` |
| Gates del motor | **6/6 en verde** | `bash scripts/verificar-todo.sh` |
| Criterios del sitio | **17/18** (C15 declarado pendiente) | `python scripts/generar-sitio.py verificar` |
| Publicado | `…github.io/LeadSofia/` y `…/sitio/` → HTTP 200 | `curl -w "%{http_code}"` |

C15 queda pendiente por diseño: la config no tiene dirección ni teléfono *completos* como texto visible, porque Sofía atiende online y no publica dirección. No es un defecto del sitio.

**Línea base antes de tocar nada:** el sitio **no tenía formulario**. El criterio C17 lo decía con todas las letras: *«sin formulario: no hay campos que etiquetar»*.

---

## 2 · Los servicios, según Instagram (remedido hoy)

Perfil `@sofiastrafile`, leído sin sesión con Chrome real:

| Dato | Valor |
|---|---|
| Seguidores | **164 mil** (IG redondea; la auditoría de octubre registró 163.805 exactos) |
| Seguidos | 586 |
| Nombre de perfil | Sofía Strafile \| Asesora de imagen y colorimetría |
| Bio | «Imagen ✨Colorimetría ✨Estilo personal. / Atención Online al 🌏 / 🇦🇷» |
| Destacadas | `Colorimetría` · `Ustedes` · `🇪🇸🎓` |
| Link de bio | `linktr.ee/sofia.strafile` — **un Linktree, no el sitio** |

### Engagement medido (likes / 164 mil)

| Fecha | Formato | Likes | Comentarios | Tasa |
|---|---|---|---|---|
| 2026-11-09 | foto | 173 | 8 | 0,105 % |
| 2026-10-27 | foto | 231 | 2 | 0,141 % |
| 2026-10-13 | reel | 375 | 21 | 0,229 % |
| 2026-08-26 | reel | 332 | 188 | 0,202 % |
| 2026-11-06 | reel | `[NO VERIFICABLE]` | — | — |
| 2026-06-06 | foto | `[NO VERIFICABLE]` | — | — |

**Mediana: 281,5 likes → 0,172 %.** Los dos casos sin contadores son el pitfall conocido: Instagram sirve el `og:description` sin el prefijo de interacción; no se estiman.

El dato que importa para la venta: **188 comentarios en un reel contra 2 en una foto**. La audiencia responde cuando hay conversación, y ese comentario hoy no tiene destino: no hay formulario, no hay captura, no hay lista.

### Servicios que la cuenta comunica hoy

| Servicio | Evidencia en IG | ¿Está en el sitio? |
|---|---|---|
| Colorimetría / análisis de paleta | nombre de perfil, bio, destacada `Colorimetría`, 5 de 8 posts con `#colorimetria` | ✅ |
| Asesoría de imagen 1:1 | nombre de perfil, `#asesoradeimagen`, «Nunca es tarde para cambiar la forma en la que elegís tu ropa» | ✅ |
| Armado de guardarropa | los mismos posts de «cómo elegís tu ropa» | ✅ |

**Los 3 servicios del sitio coinciden con lo que la cuenta comunica.** Los 3 programas (Arranque, Renovación, Transformación) **no aparecen en el perfil**: son oferta del sitio, no comunicación de la cuenta. Eso no es un error, es una decisión pendiente de ella.

---

## 3 · Los cinco hallazgos

### P1 · No existía captación: el sitio era una puerta que se cerraba
Los 12 enlaces del sitio abrían WhatsApp con un **texto fijo** («Hola Sofía! Me interesa…»). Consecuencias concretas:

- Si la persona no aprieta enviar, **no queda nada**: ni nombre, ni el servicio que miraba.
- Sofía recibe «Hola Sofía!» sin saber **por qué programa** entró.
- No hay forma de saber **qué servicio genera consultas**, así que no se puede priorizar contenido ni pauta.
- No hay consentimiento explícito ni aviso de datos.

### P1 · Se pedían datos personales sin política
El sitio decía *«No dejo tus datos en ninguna lista»* — una promesa sin respaldo escrito. Con un formulario eso deja de ser un detalle: hay que decir quién recibe los datos, para qué y cómo se borran.

### P2 · La oferta se contradecía
La tarjeta de reserva decía *«Estos son los **dos** programas que ya tengo publicados»* y arriba había **tres** programas. Un visitante atento lo nota, y una persona que duda del catálogo no compra.

### P2 · Instagram no lleva al sitio
La bio apunta a Linktree. El sitio tiene canonical a `sofiastrafile.com.ar`, que **no está registrado** (verificado por whois a NIC.ar el 2026-10-07; **no re-verificado hoy**). Es decir: el activo de 164 mil seguidores no tiene un camino al sitio nuevo. Esto no se arregla con código, se arregla con una decisión de ella.

### P3 · Sin precios publicados
Los valores «se coordinan por WhatsApp». Es defendible comercialmente, pero significa que **toda consulta arranca pidiendo precio**. El formulario ahora captura el interés concreto (servicio o programa) para poder cotizar sin ida y vuelta.

---

## 4 · Qué se construyó

Un ciclo de captación web, con el mismo patrón que la landing del Estudio Segovia, adaptado a un sitio estático de una sola página:

```
tarjeta de servicio / programa          ← data-lead-servicio="colorimetria" | "programa-renovacion" …
        ↓ (preselecciona el interés y lleva el foco al nombre)
#consulta  ·  formulario                 ← nombre, WhatsApp, mail, interés, mensaje, consentimiento
        ↓  (sin backend, que es el caso de hoy)
WhatsApp de Sofía con el mensaje armado  ← nombre, WhatsApp, interés legible, mensaje, campaña
        ↓  (si algún día hay backend)
POST JSON al endpoint declarado          ← n8n / Formspree / Resend / lo que ella elija
```

### Piezas nuevas

| Archivo | Qué hace |
|---|---|
| `02-sitio/assets/lead-capture.js` | Catálogo de servicios, armado del mensaje, validación, atribución y enganche del formulario. Sin dependencias. |
| `02-sitio/index.html` | Formulario en `#reserva`, CTA en cada servicio y programa, sección `#privacidad`, `meta` del endpoint. |
| `tests/lead-capture.test.mjs` | 20 tests: lógica pura + contrato del HTML (catálogo único, labels por campo, sin dominios de terceros). |
| `tests/e2e-captura.py` | 18 comprobaciones en Chrome real: que el mensaje que llega a WhatsApp sea el correcto. |

### Decisiones y por qué

- **WhatsApp como destino, no un backend:** es el canal real de Sofía y no depende de que un servidor esté arriba. El formulario **no dice «enviado»** si no envió nada: dice «te abrí WhatsApp con tu consulta ya escrita».
- **Consentimiento obligatorio** con cita de la Ley 25.326 y sección de privacidad propia. El botón no se habilita sin tildar.
- **Honeypot** invisible: si un bot lo completa, no se envía y no se le avisa.
- **Atribución sin cookies:** `utm_*`, referrer y el servicio de origen viajan en el mensaje/POST. Cero terceros, coherente con C18 y con el pie del sitio («sin cookies ni rastreadores»).
- **Vanilla JS y estilos propios** (`.lf-*`): el sitio tiene Tailwind **compilado** y C18 prohíbe CDN. Además detecté que `sm:grid-cols-3`, `py-20` y `mt-16` no están en el CSS emitido (los purgó el build) — por eso el formulario no depende de clases utilitarias: se vería igual tras recompilar.
- **Endpoint opcional:** se pega la URL en `<meta name="lead-endpoint">` y el formulario cambia a POST JSON, con mensaje de éxito distinto. No hay que reescribir nada.

---

## 5 · Evidencia de que funciona

```
node --test tests/lead-capture.test.mjs      →  20/20 OK
python tests/e2e-captura.py                  →  18/18 OK  (Chrome real, headless)
python scripts/generar-sitio.py verificar    →  17/18  (C17 ahora verde: 7 <label> para 7 campos)
bash scripts/verificar-todo.sh               →   6/6 OK, exit 0
```

Del e2e, el mensaje que efectivamente se abre en WhatsApp (archivo `02-sitio/capturas/captura-mensaje-whatsapp.txt`):

```
Consulta desde el sitio web

Nombre: Marina Gómez
WhatsApp: +54 9 341 555 1234
Email: marina@ejemplo.com
Interés: Análisis de colorimetría
Vino de: colorimetria

Mensaje: Quiero renovar el guardarropa antes de un viaje.

Campaña: instagram / bio / noviembre
```

También verificado en el e2e: el botón arranca deshabilitado, el CTA preselecciona el servicio, un teléfono inválido **no** abre WhatsApp y muestra el error, el honeypot no dispara nada, el formulario se limpia después de enviar, y a 390 px no hay desborde horizontal (`scrollWidth 390 = clientWidth 390`).

---

## 6 · Lo que falta decidir (lista completa, de una sola vez)

| # | Qué | Quién | Bloquea |
|---|---|---|---|
| 1 | **¿Por dónde quiere recibir las consultas?** WhatsApp (ya funciona) o mail/planilla (necesita endpoint: n8n, Formspree o Resend) | Sofía | nada hoy; define el paso 2 del ciclo |
| 2 | **Precios de los tres programas** y formas de pago | Sofía | publicar precios y cotizar sin ida y vuelta |
| 3 | **Fotos propias** (9 imágenes; hoy hay marcadores declarados) | Sofía | entrega final |
| 4 | **1–2 testimonios con permiso de uso** por escrito | Sofía | sección de prueba social |
| 5 | **Dominio:** `sofiastrafile.com.ar` está libre; el canonical ya apunta ahí | Sofía | publicar en su dominio |
| 6 | **Cambiar el link de la bio** del Linktree al sitio | Sofía | que los 164 mil lleguen al sitio |
| 7 | **Mail profesional** (propuesta: `hola@sofiastrafile.com.ar`) | Sofía | respaldo del canal WhatsApp |

---

## 7 · Límites de esta auditoría

- **No se completó ninguna reserva ni pago.** El flujo se verifica hasta abrir el WhatsApp; apretar «enviar» queda del lado de la persona.
- **El POST al endpoint no se probó contra un servidor real** porque no existe todavía. Está implementado y cubierto por el test de contrato del HTML; el envío real se prueba el día que haya endpoint.
- **Dos publicaciones sin contadores** quedaron `[NO VERIFICABLE]`; no se estimó su engagement.
- **164 mil es un redondeo de Instagram**, no un número exacto. El número exacto de octubre (163.805) está en la auditoría original.
- **La disponibilidad del dominio no se re-verificó hoy**: la última medición (whois a NIC.ar) es del 2026-10-07. Antes de publicar hay que repetirla.
