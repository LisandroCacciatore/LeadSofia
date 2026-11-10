# Marcar los contactos y vender por WhatsApp, sin API

**Para:** Sofía Strafile · **Armado:** 10 de noviembre de 2026
**Idea:** todo lo de este documento se hace desde la app **WhatsApp Business** del celular (gratis).
No hace falta la API, ni un servidor, ni pagar nada.

---

## 1 · Lo que ya llega marcado solo

Desde hoy, toda persona que escribe desde el sitio entra al chat con **la primera línea ya escrita**.
Y la primera línea es justo lo que se ve en la lista de chats, antes de abrir la conversación:

```
Consulta web · colorimetría        ← esto se ve en la lista, sin abrir nada
Consulta web · programa Renovación
Consulta web · orientación
```

Además, los botones que abren WhatsApp sin pasar por el formulario (la cabecera, el botón flotante,
el pie) dicen **«Hola Sofía! (web)…»**. Así ninguna consulta de la web queda sin marcar, entre por
donde entre.

**Lo que esto te da:** con solo mirar la lista de chats sabés **qué servicio está generando consultas**.
No hay que abrir nada, ni anotar nada, ni acordarse de nada.

---

## 2 · Las etiquetas de WhatsApp Business (2 toques por contacto)

En WhatsApp Business, dentro de un chat: menú **⋮ → Etiquetar**. Creá estas seis y usá sólo estas
(nombre corto, sin acentos ni espacios, para que no se confundan):

| Etiqueta | Cuándo |
|---|---|
| `lead-web` | entró desde el sitio y todavía no compró |
| `colorimetria` | consultó o compró análisis de color |
| `asesoria` | consultó o compró la asesoría 1:1 |
| `guardarropa` | consultó o compró armado de guardarropa |
| `pago` | dejó seña o pagó completo |
| `no-contesto` | le escribiste y no respondió (para el recontacto) |

Un contacto puede tener dos: `lead-web` + `colorimetria`.

**Regla de oro:** la etiqueta se pone **cuando termina la conversación**, no cuando empieza. Al
principio ya sabés de dónde viene (está en el mensaje); lo que la etiqueta agrega es el **resultado**:
compró, no compró, no contestó.

Con seis etiquetas alcanza para saber, en un mes: cuántos leads web entraron, qué servicio pidieron
más, y cuántos terminaron en pago. Eso es todo el tablero que necesitás para decidir qué contenido
hacer y qué programa empujar.

---

## 3 · Para promover la compra: el catálogo

Tu sitio ya tiene dos links a tu catálogo de WhatsApp (`wa.me/p/…`): el programa 1:1 y colorimetría.
Cuando alguien toca uno, **ve el producto con el precio y puede escribirte desde ahí**. Ese es el
camino de compra más corto que existe sin API.

Para que funcione de verdad, cada programa del catálogo necesita:

1. **Nombre claro** (ej. «Programa Renovación · 10 looks + 14 días»)
2. **Precio visible** — si preferís no publicar el número, poné el rango o «desde»
3. **Qué incluye**, en tres líneas
4. **Cómo se paga** en la descripción: transferencia / Mercado Pago / cuotas, y si hay seña

Con el catálogo completo, la persona no te escribe para *preguntar cuánto sale*: te escribe para
*comprar*. Esa es la diferencia entre una consulta y una venta.

Falta el tercer link (Programa Transformación): se crea en el catálogo y se agrega al sitio en
cinco minutos.

### Mensajes rápidos (Respuestas rápidas de WhatsApp Business)

Creá tres y se escriben con `/`:

- `/precios` → lista de los tres programas con valores y qué incluye
- `/pago` → formas de pago, seña y cómo se reserva el horario
- `/recordatorio` → «Hola {nombre}, te reservo el lugar de {programa}. ¿Transferís la seña y te
  confirmo el horario?»

---

## 4 · Una seña antes de la sesión

Es lo que convierte «me interesa» en venta y lo que evita el ausentismo. No requiere API: es un
alias o un link de pago mandado por el mismo chat, y la respuesta rápida `/pago` lo explica en un
mensaje. La etiqueta `pago` se pone cuando entra la seña.

---

## 5 · Lo que sí requiere algo más (para que no te sorprenda)

| Querés saber | ¿Se puede sin API? |
|---|---|
| De qué servicio viene cada persona | **Sí** — ya está en la primera línea del mensaje |
| Cuántos leads web entraron este mes | **Sí** — contás las conversaciones con `lead-web` |
| Quién compró y quién no | **Sí** — etiquetas `pago` / `no-contesto` |
| **Cuánta gente abrió el chat y no escribió** | **No** — WhatsApp no avisa. Requiere un contador de clics aparte (una hoja de cálculo, no la API) |
| Respuesta automática fuera de horario | No sin API. Se reemplaza con el mensaje de ausencia de WhatsApp Business |
| Recordatorios automáticos el día antes | No sin API. Se reemplaza con `/recordatorio` a mano |

Nada de la columna «No» es urgente. La primera tabla es la que decide si el sitio funciona.
