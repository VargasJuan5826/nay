// Mide los mismos elementos en el original (Next) y en el port (Streamlit) y reporta
// diferencias de tamaño / tipografía mayores a la tolerancia.
const { chromium } = require('playwright');

const REF = 'http://localhost:3007';
const NAY = 'http://localhost:8511';
const TOL = 1.5;

const SEL = {
  ref: {
    start: '.btn-next',
    si: 'button:has-text("Sí")',
    no: 'button:has-text("No")',
    fieldDate: 'button:has-text("Selecciona una fecha")',
    fieldTime: 'button:has-text("Selecciona una hora")',
    day25: 'button:text-is("25")',
    min30: 'button:text-is(":30")',
    noche: 'button:text-is("Noche")',
    timeDone: 'button:has-text("Listo")',
    confirmDate: 'button:has-text("CONFIRMAR FECHA")',
    opt: (q, i) => `#s${q} .opt >> nth=${i}`,
    next: (q) => `#s${q} button:has-text("SIGUIENTE")`,
    celebrate: 'button:has-text("ACEPTO LOS")',
  },
  nay: {
    start: '.st-key-nay_start button',
    si: '.st-key-nay_si button',
    no: '.st-key-nay_no button',
    fieldDate: '.st-key-nay_field_date button',
    fieldTime: '.st-key-nay_field_time button',
    day25: '.st-key-nay_day_25 button',
    min30: '.st-key-nay_min_30 button',
    noche: '.st-key-nay_preset_noche button',
    timeDone: '.st-key-nay_time_done button',
    confirmDate: '.st-key-nay_confirm_date button',
    opt: (q, i) => `.st-key-nay_opt_${q}_${i} button`,
    next: (q) => `.st-key-nay_next_${q} button`,
    celebrate: '.st-key-nay_celebrate button',
  },
};

// Cada métrica: nombre -> [selector ref, selector nay, props]
const BOX = ['width', 'height'];
const TYPE = ['fontSize', 'fontWeight', 'fontFamily', 'color'];

const PROBES = {
  '00': [
    ['header-img', '.header img', '.nay-header img', BOX],
    ['title', '.header h1', '.nay-title', [...BOX, ...TYPE]],
    ['sub', '.header p', '.nay-sub', [...BOX, ...TYPE]],
    ['plea-card', '.plea-card', '.plea-card', [...BOX, 'padding', 'borderRadius', 'backgroundColor']],
    ['plea-text', '.plea-text', '.plea-text', ['fontSize', 'fontWeight', 'color']],
    ['plea-note', '.plea-text small', '.plea-note', ['fontSize', 'fontFamily', 'color']],
    ['start-btn', '.btn-next', '.st-key-nay_start button', [...BOX, ...TYPE, 'borderRadius', 'padding']],
  ],
  '01': [
    ['card', '#s1 .q-card', '.st-key-nay_card1', [...BOX, 'padding', 'borderRadius']],
    ['img1', '#s1 .q-card img', '.step1-imgs img', BOX],
    ['q', '#s1 .q-text', '.step1-q', [...BOX, ...TYPE]],
    ['si', 'button:has-text("Sí")', '.st-key-nay_si button', [...BOX, ...TYPE, 'borderRadius']],
    ['no', 'button:has-text("No")', '.st-key-nay_no button', [...BOX, ...TYPE, 'borderRadius']],
  ],
  '02': [
    ['card', '#s2 .q-card', '.st-key-nay_card2', [...BOX, 'padding']],
    ['tag', '#s2 .q-tag', '.q-tag', [...BOX, 'fontSize', 'fontFamily', 'padding']],
    ['q', '#s2 .q-text', '.step2-q', [...BOX, ...TYPE]],
    ['label', '#s2 label', '.picker-label', ['fontSize', 'fontFamily', 'color']],
    ['field', 'button:has-text("Selecciona una fecha")', '.st-key-nay_field_date button', [...BOX, ...TYPE, 'padding', 'borderRadius']],
    ['confirm', 'button:has-text("CONFIRMAR FECHA")', '.st-key-nay_confirm_date button', [...BOX, ...TYPE]],
  ],
  '02cal': [
    ['day', 'button:text-is("25")', '.st-key-nay_day_25 button', [...BOX, 'fontSize', 'borderRadius']],
    ['month', '#s2 span:has-text("de 2026")', '.nay-cal-month', ['fontSize', 'fontWeight', 'color']],
    ['done', 'button:has-text("Listo")', '.st-key-nay_cal_done button', [...BOX, 'fontSize']],
  ],
  '02clock': [
    ['minus', 'button:text-is("-")', '.st-key-nay_clocknav_minus button', [...BOX, 'fontSize', 'borderRadius']],
    ['min', 'button:text-is(":30")', '.st-key-nay_min_30 button', [...BOX, 'fontSize']],
    ['preset', 'button:text-is("Noche")', '.st-key-nay_preset_noche button', [...BOX, 'fontSize']],
  ],
  '03': [
    ['plabel', '.progress-label', '.nay-progress-label', ['fontSize', 'fontFamily', 'color']],
    ['pwrap', '.progress-wrap', '.nay-progress-wrap', BOX],
    ['pfill', '.progress-fill', '.nay-progress-fill', BOX],
    ['qhead-img', '#s3 img', '.nay-qhead img', BOX],
    ['qcard', '#s3 .q-card', '.q-card', [...BOX, 'padding']],
    ['qtext', '#s3 .q-text', '.q-text', [...BOX, ...TYPE]],
    ['opt0', '#s3 .opt >> nth=0', '.st-key-nay_opt_3_0 button', [...BOX, ...TYPE, 'padding', 'borderRadius']],
    ['opt3', '#s3 .opt >> nth=3', '.st-key-nay_opt_3_3 button', BOX],
    ['next', '#s3 button:has-text("SIGUIENTE")', '.st-key-nay_next_3 button', [...BOX, ...TYPE]],
  ],
  '07': [
    ['bigcat', '#s7 .big-cat img', '.summary-header img', BOX],
    ['h2', '#s7 h2', '.summary-title', [...BOX, 'fontSize', 'fontWeight']],
    ['table', '.summary-table', '.summary-table', BOX],
    ['row0', '.summary-row', '.summary-row', [...BOX, 'padding', 'backgroundColor']],
    ['value0', '.s-value', '.s-value', ['fontSize', 'fontWeight']],
    ['finalcard', '#s7 .btn-confirm', '.st-key-nay_celebrate button', [...BOX, ...TYPE]],
  ],
  '07b': [
    ['finale', '.finale', '.finale', [...BOX, 'padding', 'backgroundColor']],
  ],
};

async function measure(page, probes, mode) {
  await page.mouse.move(2, 2);            // el hover deforma los botones (scale/translate)
  await page.waitForTimeout(120);
  const out = {};
  for (const [name, refSel, naySel, props] of probes) {
    const sel = mode === 'ref' ? refSel : naySel;
    const locator = page.locator(sel).first();
    if ((await locator.count()) === 0) { out[name] = null; continue; }
    try {
      out[name] = await locator.evaluate((el, props) => {
        const rect = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        const res = {};
        for (const p of props) {
          if (p === 'width') res.width = Math.round(rect.width * 10) / 10;
          else if (p === 'height') res.height = Math.round(rect.height * 10) / 10;
          else res[p] = cs[p];
        }
        return res;
      }, props);
    } catch (e) { out[name] = null; }
  }
  return out;
}

async function drive(page, mode, sel) {
  const results = {};
  const click = async (s) => { await page.click(s); await page.waitForTimeout(mode === 'nay' ? 800 : 250); };

  results['00'] = await measure(page, PROBES['00'], mode);
  await click(sel.start);
  results['01'] = await measure(page, PROBES['01'], mode);
  await click(sel.si);
  results['02'] = await measure(page, PROBES['02'], mode);
  await click(sel.fieldDate);
  results['02cal'] = await measure(page, PROBES['02cal'], mode);
  await click(sel.day25);
  await click(sel.fieldTime);
  results['02clock'] = await measure(page, PROBES['02clock'], mode);
  await click(sel.min30);
  await click(sel.noche);
  await click(sel.timeDone);
  await click(sel.confirmDate);
  results['03'] = await measure(page, PROBES['03'], mode);
  for (const q of [3, 4, 5, 6]) {
    await click(sel.opt(q, 0));
    await click(sel.next(q));
  }
  results['07'] = await measure(page, PROBES['07'], mode);
  await click(sel.celebrate);
  results['07b'] = await measure(page, PROBES['07b'], mode);
  return results;
}

(async () => {
  const browser = await chromium.launch();
  const ctxOpts = { viewport: { width: 560, height: 1000 }, deviceScaleFactor: 1 };

  const FREEZE = '*, *::before, *::after { animation: none !important; transition: none !important; }';
  const p1 = await (await browser.newContext(ctxOpts)).newPage();
  await p1.goto(REF, { waitUntil: 'networkidle' });
  await p1.addStyleTag({ content: FREEZE });
  await p1.waitForTimeout(1000);
  const refData = await drive(p1, 'ref', SEL.ref);

  const p2 = await (await browser.newContext(ctxOpts)).newPage();
  await p2.goto(NAY, { waitUntil: 'domcontentloaded' });
  await p2.waitForSelector('.st-key-nay_start button', { timeout: 30000 });
  await p2.waitForTimeout(1500);
  await p2.addStyleTag({ content: FREEZE });
  const nayData = await drive(p2, 'nay', SEL.nay);

  let issues = 0;
  for (const step of Object.keys(PROBES)) {
    const lines = [];
    for (const [name] of PROBES[step]) {
      const a = refData[step] && refData[step][name];
      const b = nayData[step] && nayData[step][name];
      if (!a && !b) { lines.push(`  ${name}: AMBOS null`); issues++; continue; }
      if (!a) { lines.push(`  ${name}: ref null (revisar selector)`); continue; }
      if (!b) { lines.push(`  ${name}: NAY NO ENCONTRADO`); issues++; continue; }
      for (const key of Object.keys(a)) {
        const va = a[key];
        const vb = b[key];
        if (typeof va === 'number') {
          if (Math.abs(va - vb) > TOL) { lines.push(`  ${name}.${key}: ref=${va} nay=${vb}`); issues++; }
        } else if (String(va) !== String(vb)) {
          lines.push(`  ${name}.${key}: ref="${va}" nay="${vb}"`);
          issues++;
        }
      }
    }
    if (lines.length) console.log(`[${step}]\n${lines.join('\n')}`);
  }
  console.log(issues === 0 ? '\n✅ PARIDAD TOTAL' : `\n${issues} diferencias`);
  await browser.close();
})();
