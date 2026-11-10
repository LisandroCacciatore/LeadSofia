/**
 * Tests del ciclo de captación de consultas · Sofía Strafile
 * ===========================================================
 *
 * Dos capas, las dos ejecutables sin dependencias (sólo Node):
 *
 *   1. Lógica pura de `02-sitio/assets/lead-capture.js`: catálogo, armado del
 *      mensaje de WhatsApp, validación del teléfono y atribución.
 *   2. Contrato del HTML servido: que el formulario exista, que cada campo tenga
 *      su <label> (criterio C17 del gate), que el catálogo del <select> y el del
 *      JS sean el mismo, y que no se hayan colado dominios de terceros (C18).
 *
 * El comportamiento real en el navegador (abrir WhatsApp, mostrar estados,
 * preseleccionar el servicio) se verifica con el e2e de `tests/e2e-captura.mjs`,
 * porque ese sí necesita un motor de verdad.
 *
 * Uso:  node --test tests/lead-capture.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const require = createRequire(import.meta.url);
const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(AQUI, '..');
const SITIO = join(RAIZ, '02-sitio');
const HTML_PATH = join(SITIO, 'index.html');

const LC = require(join(SITIO, 'assets', 'lead-capture.js'));
const html = readFileSync(HTML_PATH, 'utf8');

// ─────────────────────────── 1 · lógica pura ────────────────────────────────

test('el catálogo cubre los 3 servicios y los 3 programas del sitio', () => {
  const servicios = LC.SERVICIOS.filter((s) => s.grupo === 'servicio');
  const programas = LC.SERVICIOS.filter((s) => s.grupo === 'programa');
  assert.equal(servicios.length, 3, 'esperaba 3 servicios');
  assert.equal(programas.length, 3, 'esperaba 3 programas');
  assert.ok(LC.SERVICIOS.some((s) => s.value === 'orientacion'), 'falta la salida "no sé"');
});

test('no hay valores repetidos en el catálogo', () => {
  const values = LC.SERVICIOS.map((s) => s.value);
  assert.equal(new Set(values).size, values.length);
});

test('el mensaje de WhatsApp lleva los datos ordenados', () => {
  const texto = LC.buildLeadMessage({
    nombre: 'Marina Gómez',
    whatsapp: '+54 9 341 555 1234',
    email: 'marina@ejemplo.com',
    interes: 'programa-renovacion',
    mensaje: 'Quiero renovar el guardarropa antes de un viaje.',
  });
  assert.match(texto, /^Consulta desde el sitio web/);
  assert.match(texto, /Nombre: Marina Gómez/);
  assert.match(texto, /WhatsApp: \+54 9 341 555 1234/);
  assert.match(texto, /Email: marina@ejemplo\.com/);
  assert.match(texto, /Interés: Programa Renovación/);
  assert.match(texto, /Mensaje: Quiero renovar el guardarropa/);
});

test('el mensaje omite el email vacío y el mensaje vacío', () => {
  const texto = LC.buildLeadMessage({ nombre: 'Ana', whatsapp: '3415551234', interes: 'colorimetria' });
  assert.doesNotMatch(texto, /Email:/);
  assert.doesNotMatch(texto, /Mensaje:/);
  assert.match(texto, /Interés: Análisis de colorimetría/);
});

test('el origen se informa sólo si aporta algo distinto del interés', () => {
  const sinOrigen = LC.buildLeadMessage({ nombre: 'Ana', whatsapp: '3415551234', interes: 'asesoria', origen: 'asesoria' });
  assert.doesNotMatch(sinOrigen, /Vino de:/);

  const conOrigen = LC.buildLeadMessage({ nombre: 'Ana', whatsapp: '3415551234', interes: 'asesoria', origen: 'guardarropa' });
  assert.match(conOrigen, /Vino de: guardarropa/);
});

test('la campaña viaja en el mensaje cuando hay UTM', () => {
  const texto = LC.buildLeadMessage({
    nombre: 'Ana',
    whatsapp: '3415551234',
    interes: 'colorimetria',
    utm: { source: 'instagram', medium: 'bio', campaign: 'noviembre' },
  });
  assert.match(texto, /Campaña: instagram \/ bio \/ noviembre/);
});

test('waLink apunta al WhatsApp de Sofía y escapa el texto', () => {
  const url = LC.waLink('Hola & chau, ¿todo bien?');
  assert.ok(url.startsWith('https://wa.me/5493416153151?text='));
  assert.equal(url, 'https://wa.me/5493416153151?text=' + encodeURIComponent('Hola & chau, ¿todo bien?'));
  assert.ok(!url.includes('Hola & chau'), 'el texto tiene que ir escapado');
  assert.equal(LC.waLink(), 'https://wa.me/5493416153151');
});

test('el teléfono de quien consulta se acepta con formato humano y se rechaza si es basura', () => {
  assert.ok(LC.telefonoValido('341 555 1234'));
  assert.ok(LC.telefonoValido('+54 9 341 615-3151'));
  assert.ok(LC.telefonoValido('(0341) 555-1234'));
  assert.ok(!LC.telefonoValido('123'));
  assert.ok(!LC.telefonoValido(''));
  assert.ok(!LC.telefonoValido(null));
  assert.equal(LC.soloDigitos('+54 9 341 615-3151'), '5493416153151');
});

test('la atribución se lee de la URL, con "directo" como default', () => {
  const conUtm = LC.leerAtribucion('?utm_source=instagram&utm_medium=bio&utm_campaign=nov', 'https://instagram.com/');
  assert.deepEqual(conUtm.utm, { source: 'instagram', medium: 'bio', campaign: 'nov' });
  assert.equal(conUtm.origen, 'instagram');
  assert.equal(conUtm.referrer, 'https://instagram.com/');

  const directo = LC.leerAtribucion('', '');
  assert.equal(directo.origen, 'directo');
});

// ───────────────────────── 2 · contrato del HTML ────────────────────────────

test('el formulario existe con sus piezas mínimas', () => {
  assert.match(html, /<form id="lead-form"/);
  assert.match(html, /id="lead-status"[^>]*aria-live="polite"/);
  assert.match(html, /id="consulta"/, 'los CTA apuntan a #consulta');
  assert.match(html, /<button class="lf-submit" type="submit" disabled>/, 'el botón arranca deshabilitado');
});

test('el endpoint queda declarado y vacío: hoy la consulta sale por WhatsApp', () => {
  const m = html.match(/<meta name="lead-endpoint" content="([^"]*)"/);
  assert.ok(m, 'falta la meta lead-endpoint');
  assert.equal(m[1], '', 'el endpoint tiene que venir vacío hasta que exista backend');
  assert.match(html, /<meta name="lead-whatsapp" content="5493416153151"/);
});

test('cada campo del formulario tiene su <label> (criterio C17)', () => {
  const form = html.slice(html.indexOf('<form id="lead-form"'), html.indexOf('</form>', html.indexOf('<form id="lead-form"')));
  const campos = (form.match(/<input\b|<select\b|<textarea\b/gi) || []).length;
  const labels = (form.match(/<label\b/gi) || []).length;
  assert.ok(campos > 0, 'el formulario no tiene campos');
  assert.ok(labels >= campos, `${labels} <label> para ${campos} campos`);
});

test('el catálogo del <select> y el del JS son exactamente el mismo', () => {
  const form = html.slice(html.indexOf('<form id="lead-form"'));
  const delHtml = Array.from(form.slice(0, form.indexOf('</select>')).matchAll(/value="([a-z-]+)"/g)).map((m) => m[1]);
  const delJs = LC.SERVICIOS.map((s) => s.value);
  assert.deepEqual(delHtml.sort(), delJs.sort());
});

test('cada CTA de servicio o programa apunta a un interés que existe', () => {
  const ctas = Array.from(html.matchAll(/data-lead-servicio="([^"]+)"/g)).map((m) => m[1]);
  assert.ok(ctas.length >= 6, `esperaba al menos 6 CTA, encontré ${ctas.length}`);
  const validos = new Set(LC.SERVICIOS.map((s) => s.value));
  for (const cta of ctas) assert.ok(validos.has(cta), `data-lead-servicio="${cta}" no existe en el catálogo`);
});

test('el script del ciclo se carga y el archivo está al lado del HTML', () => {
  assert.match(html, /<script src="assets\/lead-capture\.js" defer><\/script>/);
  assert.ok(existsSync(join(SITIO, 'assets', 'lead-capture.js')));
});

test('el consentimiento es obligatorio y cita la Ley 25.326', () => {
  assert.match(html, /name="consent" type="checkbox" required/);
  assert.match(html, /Ley 25\.326/);
  assert.match(html, /href="#privacidad"/);
  assert.match(html, /<section id="privacidad"/);
});

test('no hay teléfonos enmascarados ni tel: inválidos', () => {
  const tels = Array.from(html.matchAll(/href="tel:([^"]*)"/g)).map((m) => m[1]);
  assert.ok(tels.length >= 1, 'falta el enlace tel:');
  for (const t of tels) {
    assert.match(t, /^\+?\d{8,15}$/, `tel: inválido: "${t}"`);
  }
});

test('se mantienen los llamados a WhatsApp que pide el gate (mínimo 8)', () => {
  const n = (html.match(/wa\.me/g) || []).length;
  assert.ok(n >= 8, `sólo ${n} enlaces wa.me`);
});

test('no se colaron dominios de terceros (criterio C18)', () => {
  const permitidos = new Set([
    'wa.me',
    'www.instagram.com',
    'instagram.com',
    'www.tiktok.com',
    'tiktok.com',
    'sofiastrafile.com.ar',
    'www.w3.org',
    'schema.org',
  ]);
  const hosts = new Set(
    Array.from(html.matchAll(/https?:\/\/([a-z0-9.-]+)/gi)).map((m) => m[1].toLowerCase())
  );
  const raros = [...hosts].filter((h) => !permitidos.has(h));
  assert.deepEqual(raros, [], `dominios no declarados: ${raros.join(', ')}`);
});

test('el módulo no deja direcciones locales en el entregable', () => {
  const js = readFileSync(join(SITIO, 'assets', 'lead-capture.js'), 'utf8');
  assert.doesNotMatch(js, /127\.0\.0\.1|localhost/);
  assert.doesNotMatch(html, /127\.0\.0\.1|localhost/);
});
