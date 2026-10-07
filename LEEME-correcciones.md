# Lead Sofía Strafile — qué se hizo, qué se corrigió y qué falta

Medición: **7 de octubre de 2026**, Chrome real sin sesión ni API.
Evidencia cruda: `00-auditoria/evidencia-sofia.json` + capturas en `00-auditoria/`.
Entregable: `00-auditoria/` (informe) · `01-propuesta/` (propuesta) · `02-sitio/` (sitio nuevo).

---

## 1 · La línea que se trazó con el HTML que me pasaste

Me dijiste que ese HTML es la fuente de verdad de **copy y datos**. Se respetó el **copy**:
los titulares, la voz, el orden de las secciones, el lema, las preguntas frecuentes y los nombres de
los tres programas son los del HTML, casi sin tocar. De los **datos** se respetó sólo lo verificable:
un dato inventado en un sitio que se va a publicar con el nombre de una persona real no es una
licencia creativa, es un problema para ella. Entonces:

- **Copy, estructura y diseño** → del HTML, verbatim.
- **Datos duros** (dirección, mail, credenciales, cantidades, testimonios, políticas) → sólo lo medido.
- Lo que falta → **declarado** (`preguntasAbiertas`, `alcance`, marcadores de foto), nunca rellenado.

## 2 · Correcciones aplicadas

| En el HTML que me pasaste | Qué se hizo | Por qué |
|---|---|---|
| `hola@sofia.com` | **eliminado** | `sofia.com` es de un tercero desde 1995: ese mail no llega a nadie suyo |
| «Palermo, Buenos Aires» | **eliminado**; el sitio dice «Atención online» | su bio dice «Atención Online», sin dirección, y el teléfono es de **Rosario** (341) |
| «+100 profesionales transformadas» | **163.805 seguidores** (el número real) | el número chico subestimaba su activo en 1.600× |
| Testimonios «Lucas M. / Mariana V. / Carolina R.» con 5 estrellas | **sección reemplazada** por sus números reales (163.805 · 120,4 mil · 122) y el destacado «Ustedes» | los testimonios eran inventados: nombre y apellido de personas que no existen |
| Banner «Formación académica: Elle / Ejemplo 2 / Ejemplo 3» | **reemplazado** por «Instituto de Imagen Personal (España), 2026» | «Elle» es una revista, no una formación; y «Ejemplo 2/3» eran marcadores sin resolver |
| «Disponible en hasta 3 cuotas. Política de reembolso total o parcial.» | **eliminado** | compromiso comercial con consecuencia legal que ella nunca prometió |
| «Más elegido» (badge) | **«El más completo»** | «más elegido» afirma popularidad medida, y no hay dato |
| Formulario que posteaba a `tuservidor-n8n.com` | **reemplazado por WhatsApp primero** (3 botones, con sus 2 catálogos reales) | el formulario era un embudo muerto hacia un dominio ajeno; su embudo real es WhatsApp |
| Imágenes de `lh3.googleusercontent.com` | **assets locales** con marcadores declarados | eran imágenes de IA alojadas en un tercero |
| Tailwind y Google Fonts por CDN | **compilado y auto-hospedado** | el sitio no puede depender de un tercero en runtime |
| TikTok en el pie | **`@sofiastrafile`** (el real) | su Linktree apuntaba a `@sofistrafile`, que no existe |
| `«Casos Reales»` | **«En la práctica»** | no hay casos verificados: se describen las cuatro situaciones, sin afirmar clientas reales |
| «30 minutos recuperados cada mañana» | reformulado a «decisiones que ya no te cuestan cada mañana» | era una promesa de resultado con una unidad de tiempo inventada |

## 3 · Lo que necesita ella (está en `preguntasAbiertas`)

1. Valores de los tres programas y formas de pago (**no hay precio publicado**: no se inventa, y por eso la propuesta no calcula el costo de no hacer nada en dinero).
2. Fotos propias (9 imágenes; hoy van marcadores locales declarados).
3. Uno o dos testimonios con permiso de uso.
4. Si atiende presencial en alguna ciudad (para el Perfil de Empresa en Google).
5. El mail profesional (propuesta: `hola@sofiastrafile.com.ar`).

## 4 · El dominio, antes de publicar

`sofiastrafile.com.ar`, `sofiastrafile.ar` y `sofiastrafile.com` están **libres** (whois directo a
NIC.ar y Verisign). El canonical del sitio ya apunta a `https://sofiastrafile.com.ar/`: **hay que
registrarlo antes de publicar en su dominio**. Mientras el preview viva en GitHub Pages va con
`noindex`, como todos los leads.

## 5 · Cómo se corre el estándar

```bash
bash scripts/verificar-todo.sh     # los 6 gates · con uno en rojo no hay PDF
bash scripts/generar.sh            # sólo construir, para iterar contenido
python scripts/generar-sitio.py verificar   # los 18 criterios del sitio (02-sitio/)
python src/capturar-sitio.py       # recapturar la portada del sitio nuevo
```
