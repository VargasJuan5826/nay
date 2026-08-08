// Verifica la funcionalidad del port: botón escapista, validaciones, lluvia de gatos,
// PDF y navegación completa.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const NAY = 'http://localhost:8511';
const DL = path.join(__dirname, 'downloads');
fs.mkdirSync(DL, { recursive: true });

let pass = 0;
let fail = 0;
const check = (label, ok, detail = '') => {
  console.log(`${ok ? 'OK  ' : 'FALLA'} ${label}${detail ? ' — ' + detail : ''}`);
  ok ? pass++ : fail++;
};

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 560, height: 1000 }, acceptDownloads: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));

  await page.goto(NAY, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.st-key-nay_start button', { timeout: 30000 });
  await page.waitForTimeout(1500);
  const click = async (s) => { await page.click(s); await page.waitForTimeout(800); };

  // --- paso 0 -> 1
  await click('.st-key-nay_start button');
  check('paso 0 avanza al 1', (await page.locator('.st-key-nay_si button').count()) === 1);

  // --- botón "No": escapa al pasar el mouse
  const noBox = async () => {
    const l = page.locator('.st-key-nay_no button');
    if ((await l.count()) === 0) return null;
    return l.evaluate((el) => { const b = el.getBoundingClientRect(); return { x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height), fs: getComputedStyle(el).fontSize }; });
  };
  const siBox = async () => page.locator('.st-key-nay_si button').evaluate((el) => ({ fs: getComputedStyle(el).fontSize, w: Math.round(el.getBoundingClientRect().width) }));

  const no0 = await noBox();
  const si0 = await siBox();
  const hover = async () => {
    const b = await noBox();
    if (!b) return false;
    await page.mouse.move(2, 2);
    await page.mouse.move(b.x + b.w / 2, b.y + b.h / 2);
    await page.waitForTimeout(1100);
    return true;
  };
  await hover();
  const no1 = await noBox();
  const si1 = await siBox();
  check('el hover mueve el "No"', !!no1 && (no1.x !== no0.x || no1.y !== no0.y), `${no0.x},${no0.y} -> ${no1 && no1.x},${no1 && no1.y}`);
  // El original arranca en 12px y su fórmula da max(14-intentos, 8): 13, 12, 11, 10, 9.
  check('el "No" sigue la secuencia del original', !!no1 && no1.fs === '13px', `${no0.fs} -> ${no1 && no1.fs}`);
  check('el "Sí" crece', parseFloat(si1.fs) > parseFloat(si0.fs), `${si0.fs} -> ${si1.fs}`);
  const msg = await page.locator('.nay-no-msg').first().textContent().catch(() => '');
  check('aparece el mensaje de error', /opción no válida/.test(msg || ''), msg || '(vacío)');

  for (let i = 0; i < 5; i++) await hover();
  const noGone = (await page.locator('.st-key-nay_no button').count()) === 0;
  check('el "No" desaparece tras 5 intentos', noGone);
  const msg5 = await page.locator('.nay-no-msg').first().textContent().catch(() => '');
  check('mensaje final del "No"', /ya no existe en el sistema/.test(msg5 || ''), msg5 || '(vacío)');

  // --- paso 1 -> 2 y validación de fecha
  await click('.st-key-nay_si button');
  check('paso 1 avanza al 2', (await page.locator('.st-key-nay_field_date button').count()) === 1);
  await click('.st-key-nay_confirm_date button');
  const dateErr = await page.locator('.err-msg').first().textContent().catch(() => '');
  check('valida fecha y hora faltantes', /selecciona fecha y hora/.test(dateErr || ''), dateErr || '(vacío)');

  // --- calendario: días pasados deshabilitados
  await click('.st-key-nay_field_date button');
  const dayStates = await page.locator('[class*="st-key-nay_day_"] button').evaluateAll((els) => els.map((e) => ({ t: e.textContent.trim(), d: e.disabled })));
  const today = new Date().getDate();
  const past = dayStates.filter((d) => +d.t < today);
  check('los días pasados están deshabilitados', past.length === 0 || past.every((d) => d.d), `${past.filter((d) => d.d).length}/${past.length}`);
  // navegación de mes
  const monthBefore = await page.locator('.nay-cal-month').textContent();
  await click('.st-key-nay_calnav_next button');
  const monthAfter = await page.locator('.nay-cal-month').textContent();
  check('el calendario cambia de mes', monthBefore !== monthAfter, `${monthBefore} -> ${monthAfter}`);
  await click('.st-key-nay_calnav_prev button');

  // elegir un día futuro
  const pickable = await page.locator('[class*="st-key-nay_day_"] button:not([disabled])').first();
  const dayText = (await pickable.textContent()).trim();
  await pickable.click();
  await page.waitForTimeout(800);
  const fieldDate = await page.locator('.st-key-nay_field_date button').textContent();
  check('el día elegido llega al campo', fieldDate.includes(dayText.padStart(2, '0')), fieldDate);

  // --- reloj
  await click('.st-key-nay_field_time button');
  const face0 = await page.locator('.nay-clock-face').textContent();
  await click('.st-key-nay_clocknav_plus button');
  const face1 = await page.locator('.nay-clock-face').textContent();
  check('el + cambia la hora', face0 !== face1, `${face0} -> ${face1}`);
  await click('.st-key-nay_min_45 button');
  const face2 = await page.locator('.nay-clock-face').textContent();
  check('los minutos se aplican', face2.includes('45'), face2);
  await click('.st-key-nay_preset_noche button');
  const face3 = await page.locator('.nay-clock-face').textContent();
  check('el preset Noche fija 21:00', face3.replace(/\s/g, '') === '21:00', face3);
  await click('.st-key-nay_time_done button');
  const fieldTime = await page.locator('.st-key-nay_field_time button').textContent();
  check('la hora llega al campo', fieldTime.includes('21:00'), fieldTime);

  await click('.st-key-nay_confirm_date button');
  check('paso 2 avanza al 3', (await page.locator('.st-key-nay_opt_3_0 button').count()) === 1);

  // --- preguntas: validación y selección
  await click('.st-key-nay_next_3 button');
  const optErr = await page.locator('.err-msg').first().textContent().catch(() => '');
  check('valida opción sin elegir', /Elige algo porfa/.test(optErr || ''), optErr || '(vacío)');

  const picked = [];
  for (const [step, index] of [[3, 1], [4, 2], [5, 0], [6, 3]]) {
    const label = (await page.locator(`.st-key-nay_opt_${step}_${index} button`).textContent()).trim();
    picked.push(label);
    await click(`.st-key-nay_opt_${step}_${index} button`);
    const selected = await page.locator(`.st-key-nay_opt_${step}_${index} button`).evaluate((el) => getComputedStyle(el).borderColor);
    check(`la opción elegida de la pregunta ${step - 2} se resalta`, selected === 'rgb(124, 58, 237)', selected);
    await click(`.st-key-nay_next_${step} button`);
  }

  // --- resumen
  const values = await page.locator('.s-value').allTextContents();
  check('el resumen tiene 5 filas', values.length === 5, JSON.stringify(values));
  const okSummary = values[0] === picked[0] && values[1] === picked[1] && values[3] === picked[2] && values[4] === picked[3]
    && /a las 21:00/.test(values[2]);
  check('el resumen refleja las respuestas', okSummary, JSON.stringify(values));

  // --- final: lluvia de gatos + PDF
  await click('.st-key-nay_celebrate button');
  check('aparece el mensaje final', /Match confirmado/.test(await page.locator('.finale').textContent()));
  const cats = await page.locator('.float-cat').count();
  check('llueven 16 gatitos', cats === 16, String(cats));
  const catStyles = await page.locator('.float-cat').evaluateAll((els) => els.map((e) => e.style.animationDelay));
  check('los gatitos caen escalonados', new Set(catStyles).size > 5, catStyles.slice(0, 4).join(','));

  const frame = page.frameLocator('iframe').last();
  const pdfBtn = frame.locator('#dl');
  check('el botón de PDF está presente', (await pdfBtn.count()) === 1);
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 30000 }).catch(() => null),
    pdfBtn.click(),
  ]);
  if (download) {
    const file = path.join(DL, download.suggestedFilename());
    await download.saveAs(file);
    const head = fs.readFileSync(file).subarray(0, 5).toString('latin1');
    const size = fs.statSync(file).size;
    check('descarga un PDF válido', head === '%PDF-' && size > 10000, `${download.suggestedFilename()} ${size}B ${head}`);
  } else {
    check('descarga un PDF válido', false, 'no se disparó el evento de descarga');
  }

  const realErrors = errors.filter((e) => !/favicon|Failed to load resource: the server responded with a status of 404/.test(e));
  check('sin errores de consola', realErrors.length === 0, realErrors.slice(0, 3).join(' | '));

  console.log(`\n${pass} OK, ${fail} fallas`);
  await browser.close();
  process.exit(fail ? 1 : 0);
})();
