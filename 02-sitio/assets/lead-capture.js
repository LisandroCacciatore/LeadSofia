/**
 * Ciclo de captación de consultas · Sofía Strafile
 * =================================================
 *
 * Mismo patrón que la landing del Estudio Segovia, adaptado a un sitio estático
 * de una sola página (este sitio no usa React ni Vite):
 *
 *   1. La persona elige un servicio o un programa → el <select> llega preseleccionado.
 *   2. Completa nombre, WhatsApp, mail y qué necesita.
 *   3. Autoriza el uso de sus datos (Ley 25.326) — obligatorio.
 *   4. Al enviar, la consulta SALE POR WHATSAPP con el texto ya armado. Es el canal
 *      real de Sofía: no depende de que un servidor esté arriba.
 *   5. Si algún día hay backend (n8n, Formspree, Resend), se pone la URL en
 *      <meta name="lead-endpoint" content="https://..."> y el formulario hace POST
 *      JSON en vez de abrir WhatsApp. El mensaje de éxito cambia para no mentir.
 *
 * Regla de la casa: el formulario nunca dice "enviado" si no envió nada.
 *
 * Se escribe como UMD a propósito: el navegador lo carga como script clásico
 * (`defer`, sin `type="module"`, así no depende del MIME con que lo sirva el
 * hosting) y Node lo puede requerir para los tests sin bundler ni jsdom.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
    return;
  }
  if (root) root.LeadCapture = api;
  if (typeof document !== 'undefined') {
    var arrancar = function () {
      api.initLeadCapture(document, typeof window !== 'undefined' ? window : undefined);
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arrancar);
    else arrancar();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  /** Número de WhatsApp de Sofía, formato internacional sin + ni espacios. */
  var WA_DESTINO = '5493416153151';

  /**
   * Catálogo único de lo que se puede consultar. Es el mismo que muestran las
   * secciones #servicios y #programas: si se agrega un servicio al sitio, se agrega
   * acá y aparece en el formulario, en los CTAs y en el mensaje de WhatsApp.
   */
  var SERVICIOS = [
    { value: 'colorimetria', label: 'Análisis de colorimetría', grupo: 'servicio', corto: 'colorimetría' },
    { value: 'asesoria', label: 'Asesoría de imagen 1:1', grupo: 'servicio', corto: 'asesoría 1:1' },
    { value: 'guardarropa', label: 'Armado de guardarropa', grupo: 'servicio', corto: 'guardarropa' },
    {
      value: 'programa-arranque',
      label: 'Programa Arranque (1 sesión + 3 looks)',
      grupo: 'programa',
      corto: 'programa Arranque',
    },
    {
      value: 'programa-renovacion',
      label: 'Programa Renovación (10 looks + 14 días de seguimiento)',
      grupo: 'programa',
      corto: 'programa Renovación',
    },
    {
      value: 'programa-transformacion',
      label: 'Programa Transformación (setup + 2 sesiones)',
      grupo: 'programa',
      corto: 'programa Transformación',
    },
    { value: 'orientacion', label: 'Todavía no sé: quiero orientación', grupo: 'consulta', corto: 'orientación' },
  ];

  /** Deja sólo los dígitos de un teléfono escrito de cualquier forma. */
  function soloDigitos(valor) {
    return String(valor == null ? '' : valor).replace(/\D+/g, '');
  }

  /**
   * Valida el WhatsApp de quien consulta (no el destino).
   * Criterio: 8 a 15 dígitos, que es lo que entra en un número real con código de país.
   */
  function telefonoValido(valor) {
    var d = soloDigitos(valor);
    return d.length >= 8 && d.length <= 15;
  }

  /** Busca el label del interés elegido; si no está en el catálogo, devuelve el valor crudo. */
  function etiquetaInteres(value, servicios) {
    var lista = servicios || SERVICIOS;
    for (var i = 0; i < lista.length; i += 1) {
      if (lista[i].value === value) return lista[i].label;
    }
    return String(value || 'Consulta general');
  }

  /** Link de WhatsApp con el texto precargado. */
  function waLink(texto, destino) {
    var base = 'https://wa.me/' + (destino || WA_DESTINO);
    if (!texto) return base;
    return base + '?text=' + encodeURIComponent(texto);
  }

  /**
   * Arma el texto que llega al WhatsApp de Sofía. Corto y ordenado: el mensaje lo
   * lee una persona en el celular, no un parser.
   */
  function buildLeadMessage(datos, servicios) {
    var d = datos || {};
    var lineas = [
      'Consulta desde el sitio web',
      '',
      'Nombre: ' + String(d.nombre || '').trim(),
      'WhatsApp: ' + String(d.whatsapp || '').trim(),
    ];

    var email = String(d.email || '').trim();
    if (email) lineas.push('Email: ' + email);

    lineas.push('Interés: ' + etiquetaInteres(d.interes, servicios));

    var origen = String(d.origen || '').trim();
    if (origen && origen !== d.interes) lineas.push('Vino de: ' + origen);

    var mensaje = String(d.mensaje || '').trim();
    if (mensaje) lineas.push('', 'Mensaje: ' + mensaje);

    var utm = d.utm || {};
    var campana = [utm.source, utm.medium, utm.campaign].filter(Boolean).join(' / ');
    if (campana) lineas.push('', 'Campaña: ' + campana);

    return lineas.join('\n');
  }

  /**
   * Lee la atribución de la URL y del referrer. Sin cookies y sin terceros: se
   * guarda en campos ocultos y viaja con la consulta.
   */
  function leerAtribucion(search, referrer) {
    var params = new URLSearchParams(String(search || '').replace(/^\?/, ''));
    var pick = function (k) {
      return params.get(k) || '';
    };
    return {
      origen: pick('origen') || pick('utm_source') || 'directo',
      utm: {
        source: pick('utm_source'),
        medium: pick('utm_medium'),
        campaign: pick('utm_campaign'),
      },
      referrer: String(referrer || ''),
    };
  }

  var MENSAJES = {
    whatsapp: 'Listo. Te abrí WhatsApp con tu consulta ya escrita: apretá enviar y te respondo por ahí.',
    api: 'Listo. Recibí tu consulta: te escribo por WhatsApp a la brevedad.',
    sinConsentimiento: 'Necesito tu autorización para usar tus datos y poder responderte.',
    faltaNombre: 'Me falta tu nombre para saber con quién hablo.',
    faltaTelefono: 'Revisá el WhatsApp: parece que falta algún número.',
    error: 'No pudimos enviar la consulta. Escribime directo por WhatsApp al +54 9 341 615-3151.',
  };

  /**
   * Engancha el formulario. Devuelve un objeto con el estado para poder
   * inspeccionarlo desde un test o desde la consola; no crea globales extra.
   */
  function initLeadCapture(doc, win) {
    var d = doc || (typeof document !== 'undefined' ? document : null);
    if (!d) return null;

    var form = d.getElementById('lead-form');
    if (!form) return null;

    var w = win || d.defaultView || (typeof window !== 'undefined' ? window : null);
    var status = d.getElementById('lead-status');
    var submit = form.querySelector('[type="submit"]');
    var consent = form.querySelector('[name="consent"]');
    var interes = form.querySelector('[name="interes"]');
    var meta = function (name) {
      var el = d.querySelector('meta[name="' + name + '"]');
      return el ? String(el.getAttribute('content') || '').trim() : '';
    };
    var endpoint = meta('lead-endpoint');
    var destino = soloDigitos(meta('lead-whatsapp')) || WA_DESTINO;

    var estado = {
      via: endpoint ? 'api' : 'whatsapp',
      endpoint: endpoint,
      envios: 0,
      ultimoMensaje: '',
      ultimoPayload: null,
      origenElegido: '',
    };

    // ── atribución: origen, utm y referrer viajan con la consulta ────────────
    // Sin campos ocultos a propósito: cada input del formulario es un campo real
    // con su <label> (criterio C17 del gate del sitio). La atribución vive acá y
    // se suma al payload del endpoint o al texto de WhatsApp.
    var loc = (w && w.location) || { search: '', href: '' };
    var atrib = leerAtribucion(loc.search || '', d.referrer || '');
    atrib.pagina = loc.href || '';

    var mostrar = function (tipo, texto) {
      if (!status) return;
      status.setAttribute('data-state', tipo);
      status.textContent = texto;
    };

    var limpiar = function () {
      form.reset();
      if (interes) interes.value = SERVICIOS[0].value;
      if (consent) consent.checked = false;
      if (submit) {
        submit.disabled = true;
        submit.removeAttribute('data-enviando');
      }
    };

    // ── el botón sólo se habilita con la autorización marcada ────────────────
    var sincronizarBoton = function () {
      if (submit && consent) submit.disabled = !consent.checked;
    };
    if (consent) consent.addEventListener('change', sincronizarBoton);
    sincronizarBoton();

    // ── cada servicio o programa del sitio preselecciona su interés ──────────
    var ctas = d.querySelectorAll('[data-lead-servicio]');
    Array.prototype.forEach.call(ctas, function (cta) {
      cta.addEventListener('click', function () {
        var value = cta.getAttribute('data-lead-servicio');
        var existe = SERVICIOS.some(function (s) {
          return s.value === value;
        });
        if (interes && existe) interes.value = value;
        estado.origenElegido = value;
        var nombre = form.querySelector('[name="nombre"]');
        if (nombre && typeof nombre.focus === 'function') nombre.focus({ preventScroll: true });
      });
    });

    form.addEventListener('submit', function (event) {
      if (event && typeof event.preventDefault === 'function') event.preventDefault();

      var datos = {};
      new FormData(form).forEach(function (v, k) {
        datos[k] = typeof v === 'string' ? v : (v && v.name) || '';
      });

      // Honeypot: si un bot lo completa, no se envía nada y no se le avisa.
      if (String(datos.empresa || '').trim()) {
        limpiar();
        mostrar('ok', MENSAJES[estado.endpoint ? 'api' : 'whatsapp']);
        return estado;
      }

      if (!datos.consent) {
        mostrar('error', MENSAJES.sinConsentimiento);
        if (consent && typeof consent.focus === 'function') consent.focus();
        return estado;
      }

      if (!String(datos.nombre || '').trim()) {
        mostrar('error', MENSAJES.faltaNombre);
        var nom = form.querySelector('[name="nombre"]');
        if (nom && typeof nom.focus === 'function') nom.focus();
        return estado;
      }

      if (!telefonoValido(datos.whatsapp)) {
        mostrar('error', MENSAJES.faltaTelefono);
        var tel = form.querySelector('[name="whatsapp"]');
        if (tel && typeof tel.focus === 'function') tel.focus();
        return estado;
      }

      // La atribución de la URL se suma a lo que escribió la persona. Si llegó
      // desde una tarjeta de servicio, ese es el origen que manda.
      datos.origen = estado.origenElegido || atrib.origen;
      datos.referrer = atrib.referrer.slice(0, 180);
      datos.pagina = atrib.pagina;
      datos.utm = atrib.utm;
      estado.ultimoMensaje = buildLeadMessage(datos);

      // Sin backend: la consulta sale por WhatsApp con el mensaje ya escrito.
      if (!estado.endpoint) {
        if (w && typeof w.open === 'function') {
          w.open(waLink(estado.ultimoMensaje, destino), '_blank', 'noopener,noreferrer');
        }
        estado.envios += 1;
        limpiar();
        mostrar('ok', MENSAJES.whatsapp);
        return estado;
      }

      // Con backend: POST JSON al endpoint declarado en el <meta>.
      estado.ultimoPayload = {
        nombre: datos.nombre,
        whatsapp: datos.whatsapp,
        email: datos.email || '',
        interes: datos.interes,
        interesLabel: etiquetaInteres(datos.interes),
        mensaje: datos.mensaje || '',
        consent: true,
        origen: datos.origen || '',
        utm: datos.utm,
        referrer: datos.referrer || '',
        pagina: datos.pagina || '',
        enviado: new Date().toISOString(),
      };

      var fetchFn =
        w && typeof w.fetch === 'function' ? w.fetch.bind(w) : typeof fetch === 'function' ? fetch : null;
      if (!fetchFn) {
        mostrar('error', MENSAJES.error);
        return estado;
      }

      if (submit) {
        submit.disabled = true;
        submit.setAttribute('data-enviando', 'true');
      }

      return fetchFn(estado.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(estado.ultimoPayload),
      })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          estado.envios += 1;
          limpiar();
          mostrar('ok', MENSAJES.api);
          return estado;
        })
        .catch(function () {
          mostrar('error', MENSAJES.error);
          if (submit) submit.removeAttribute('data-enviando');
          sincronizarBoton();
          return estado;
        });
    });

    return estado;
  }

  return {
    WA_DESTINO: WA_DESTINO,
    SERVICIOS: SERVICIOS,
    MENSAJES: MENSAJES,
    soloDigitos: soloDigitos,
    telefonoValido: telefonoValido,
    etiquetaInteres: etiquetaInteres,
    waLink: waLink,
    buildLeadMessage: buildLeadMessage,
    leerAtribucion: leerAtribucion,
    initLeadCapture: initLeadCapture,
  };
});
