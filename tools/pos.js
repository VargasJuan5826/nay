// Compara la posición (y relativa al gatito del header, y x absoluta) de cada elemento.
const { chromium } = require('playwright');

const FREEZE = '*,*::before,*::after{animation:none!important;transition:none!important}.float-cat{display:none!important}';
const TOL = 0.4;

const SEL = {
  ref: {
    start: 'text=INICIAR PROTOCOLO', si: 'button:has-text("Sí")',
    fieldDate: 'button:has-text("Selecciona una fecha")', fieldTime: 'button:has-text("Selecciona una hora")',
    day: 'button:text-is("25")', timeDone: 'button:has-text("Listo")',
    confirmDate: 'button:has-text("CONFIRMAR FECHA")',
    opt: (q) => `#s${q} .opt >> nth=0`, next: (q) => `#s${q} button:has-text("SIGUIENTE")`,
    celebrate: 'button:has-text("ACEPTO LOS")', head: '.header img',
  },
  nay: {
    start: '.st-key-nay_start button', si: '.st-key-nay_si button',
    fieldDate: '.st-key-nay_field_date button', fieldTime: '.st-key-nay_field_time button',
    day: '.st-key-nay_day_25 button', timeDone: '.st-key-nay_time_done button',
    confirmDate: '.st-key-nay_confirm_date button',
    opt: (q) => `.st-key-nay_opt_${q}_0 button`, next: (q) => `.st-key-nay_next_${q} button`,
    celebrate: '.st-key-nay_celebrate button', head: '.nay-header img',
  },
};

// [nombre, selector ref, selector nay]
const POS = {
  '00': [
    ['title', '.header h1', '.nay-title'],
    ['sub', '.header p', '.nay-sub'],
    ['plea', '.plea-card', '.plea-card'],
    ['plea-img', '.plea-card img', '.plea-card img'],
    ['plea-text', '.plea-text', '.plea-text'],
    ['start', '.btn-next', '.st-key-nay_start button'],
  ],
  '01': [
    ['card', '#s1 .q-card', '.st-key-nay_card1'],
    ['img', '#s1 .q-card img', '.step1-imgs img'],
    ['q', '#s1 .q-text', '.step1-q'],
    ['si', 'button:has-text("Sí")', '.st-key-nay_si button'],
    ['no', 'button:has-text("No")', '.st-key-nay_no button'],
  ],
  '02': [
    ['card', '#s2 .q-card', '.st-key-nay_card2'],
    ['img0', '#s2 .q-card img', '.step2-imgs img'],
    ['tag', '#s2 .q-tag', '.q-tag'],
    ['q', '#s2 .q-text', '.step2-q'],
    ['label', '#s2 label', '.picker-label'],
    ['fieldDate', 'button:has-text("Selecciona una fecha")', '.st-key-nay_field_date button'],
    ['fieldTime', 'button:has-text("Selecciona una hora")', '.st-key-nay_field_time button'],
    ['confirm', 'button:has-text("CONFIRMAR FECHA")', '.st-key-nay_confirm_date button'],
  ],
  '02cal': [
    ['prev', 'button:text-is("←")', '.st-key-nay_calnav_prev button'],
    ['next', 'button:text-is("→")', '.st-key-nay_calnav_next button'],
    ['week', '#s2 .q-card div[style*="repeat(7"]', '.nay-cal-week'],
    ['day1', 'button:text-is("1")', '.st-key-nay_day_1 button'],
    ['day25', 'button:text-is("25")', '.st-key-nay_day_25 button'],
    ['calDone', 'button:has-text("Listo")', '.st-key-nay_cal_done button'],
  ],
  '02clock': [
    ['minus', 'button:text-is("-")', '.st-key-nay_clocknav_minus button'],
    ['plus', 'button:text-is("+")', '.st-key-nay_clocknav_plus button'],
    ['min00', 'button:text-is(":00")', '.st-key-nay_min_0 button'],
    ['min45', 'button:text-is(":45")', '.st-key-nay_min_45 button'],
    ['tarde', 'button:text-is("Tarde")', '.st-key-nay_preset_tarde button'],
    ['noche', 'button:text-is("Noche")', '.st-key-nay_preset_noche button'],
    ['timeDone', 'button:has-text("Listo")', '.st-key-nay_time_done button'],
  ],
  '03': [
    ['plabel', '.progress-label', '.nay-progress-label'],
    ['pwrap', '.progress-wrap', '.nay-progress-wrap'],
    ['qheadimg', '#s3 .q-card', '.q-card'],
    ['tag', '#s3 .q-tag', '.q-tag'],
    ['qtext', '#s3 .q-text', '.q-text'],
    ['opt0', '#s3 .opt >> nth=0', '.st-key-nay_opt_3_0 button'],
    ['opt3', '#s3 .opt >> nth=3', '.st-key-nay_opt_3_3 button'],
    ['next', '#s3 button:has-text("SIGUIENTE")', '.st-key-nay_next_3 button'],
  ],
  '07': [
    ['bigcat', '#s7 .big-cat img', '.summary-header img'],
    ['h2', '#s7 h2', '.summary-title'],
    ['table', '.summary-table', '.summary-table'],
    ['row4', '.summary-row >> nth=4', '.summary-row.alt >> nth=2'],
    ['note', '#s7 .summary-header p', '.summary-note'],
    ['row0', '.summary-row', '.summary-row'],
    ['finalq', '#s7 .q-card', '.final-card'],
    ['finalimg', '#s7 .q-card img', '.final-card img'],
    ['finaltext', '#s7 .q-card .q-text', '.final-card .q-text'],
    ['celebrate', 'button:has-text("ACEPTO LOS")', '.st-key-nay_celebrate button'],
  ],
  '07b': [
    ['finale', '.finale', '.finale'],
    ['finaleH', '.finale h3', '.finale-title'],
  ],
};

async function measure(page, probes, mode, headSel) {
  await page.mouse.move(2, 2);            // el hover deforma los botones (scale/translate)
  await page.waitForTimeout(120);
  const head = await page.locator(headSel).first().evaluate((el) => el.getBoundingClientRect().top);
  const out = {};
  for (const [name, refSel, naySel] of probes) {
    const sel = mode === 'ref' ? refSel : naySel;
    const loc = page.locator(sel).first();
    if ((await loc.count()) === 0) { out[name] = null; continue; }
    try {
      const r = await loc.evaluate((el) => {
        const b = el.getBoundingClientRect();
        return { top: b.top, left: b.left, w: b.width, h: b.height };
      });
      out[name] = {
        dy: Math.round((r.top - head) * 10) / 10,
        x: Math.round(r.left * 10) / 10,
        w: Math.round(r.w * 10) / 10,
        h: Math.round(r.h * 10) / 10,
      };
    } catch (e) { out[name] = null; }
  }
  return out;
}

async function drive(page, mode) {
  const sel = SEL[mode];
  const wait = mode === 'nay' ? 800 : 300;
  const click = async (s) => { await page.click(s); await page.waitForTimeout(wait); };
  const res = {};
  res['00'] = await measure(page, POS['00'], mode, sel.head);
  await click(sel.start);
  res['01'] = await measure(page, POS['01'], mode, sel.head);
  await click(sel.si);
  res['02'] = await measure(page, POS['02'], mode, sel.head);
  await click(sel.fieldDate);
  res['02cal'] = await measure(page, POS['02cal'], mode, sel.head);
  await click(sel.day);
  await click(sel.fieldTime);
  res['02clock'] = await measure(page, POS['02clock'], mode, sel.head);
  await click(sel.timeDone);
  await click(sel.confirmDate);
  res['03'] = await measure(page, POS['03'], mode, sel.head);
  for (const q of [3, 4, 5, 6]) { await click(sel.opt(q)); await click(sel.next(q)); }
  res['07'] = await measure(page, POS['07'], mode, sel.head);
  await click(sel.celebrate);
  res['07b'] = await measure(page, POS['07b'], mode, sel.head);
  return res;
}

(async () => {
  const browser = await chromium.launch();
  const opts = { viewport: { width: 560, height: 1400 }, deviceScaleFactor: 1 };
  const ref = await (await browser.newContext(opts)).newPage();
  await ref.goto('http://localhost:3007', { waitUntil: 'networkidle' });
  await ref.addStyleTag({ content: FREEZE });
  await ref.waitForTimeout(700);
  const a = await drive(ref, 'ref');

  const nay = await (await browser.newContext(opts)).newPage();
  await nay.goto('http://localhost:8511', { waitUntil: 'domcontentloaded' });
  await nay.waitForSelector('.st-key-nay_start button', { timeout: 30000 });
  await nay.waitForTimeout(1500);
  await nay.addStyleTag({ content: FREEZE });
  const b = await drive(nay, 'nay');
  await browser.close();

  let issues = 0;
  for (const step of Object.keys(POS)) {
    const lines = [];
    for (const [name] of POS[step]) {
      const x = a[step][name];
      const y = b[step][name];
      if (!x) { lines.push(`  ${name}: ref no encontrado`); continue; }
      if (!y) { lines.push(`  ${name}: NAY no encontrado`); issues++; continue; }
      const bad = [];
      for (const k of ['dy', 'x', 'w', 'h']) {
        if (Math.abs(x[k] - y[k]) > TOL) bad.push(`${k} ref=${x[k]} nay=${y[k]}`);
      }
      if (bad.length) { lines.push(`  ${name}: ${bad.join(' | ')}`); issues++; }
    }
    if (lines.length) console.log(`[${step}]\n${lines.join('\n')}`);
  }
  console.log(issues === 0 ? '\n✅ POSICIONES IDÉNTICAS' : `\n${issues} elementos desalineados`);
})();
