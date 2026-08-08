// Captura los mismos pasos en ambas apps con animaciones congeladas y hace pixel-diff.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { PNG } = require('pngjs');
const pixelmatch = require('pixelmatch').default || require('pixelmatch');

const OUT = path.join(__dirname, 'shots', 'diff');
fs.mkdirSync(OUT, { recursive: true });
const FREEZE = `*, *::before, *::after { animation: none !important; transition: none !important; }
.float-cat { display: none !important; }`;

const SEL = {
  ref: {
    start: 'text=INICIAR PROTOCOLO',
    si: 'button:has-text("Sí")',
    fieldDate: 'button:has-text("Selecciona una fecha")',
    fieldTime: 'button:has-text("Selecciona una hora")',
    day: 'button:text-is("25")',
    min30: 'button:text-is(":30")',
    noche: 'button:text-is("Noche")',
    timeDone: 'button:has-text("Listo")',
    confirmDate: 'button:has-text("CONFIRMAR FECHA")',
    opt: (q) => `#s${q} .opt >> nth=0`,
    next: (q) => `#s${q} button:has-text("SIGUIENTE")`,
    celebrate: 'button:has-text("ACEPTO LOS")',
  },
  nay: {
    start: '.st-key-nay_start button',
    si: '.st-key-nay_si button',
    fieldDate: '.st-key-nay_field_date button',
    fieldTime: '.st-key-nay_field_time button',
    day: '.st-key-nay_day_25 button',
    min30: '.st-key-nay_min_30 button',
    noche: '.st-key-nay_preset_noche button',
    timeDone: '.st-key-nay_time_done button',
    confirmDate: '.st-key-nay_confirm_date button',
    opt: (q) => `.st-key-nay_opt_${q}_0 button`,
    next: (q) => `.st-key-nay_next_${q} button`,
    celebrate: '.st-key-nay_celebrate button',
  },
};

async function run(page, mode, dir) {
  fs.mkdirSync(dir, { recursive: true });
  const sel = SEL[mode];
  const wait = mode === 'nay' ? 800 : 300;
  const click = async (s) => { await page.click(s); await page.waitForTimeout(wait); };
  const shot = async (name) => {
    await page.mouse.move(2, 2);          // el hover deforma los botones (scale/translate)
    await page.waitForTimeout(250);
    await page.screenshot({ path: path.join(dir, name + '.png'), fullPage: true });
  };

  await shot('00-intro');
  await click(sel.start);
  await shot('01-confirm');
  await click(sel.si);
  await shot('02-agenda');
  await click(sel.fieldDate);
  await shot('02b-datepicker');
  await click(sel.day);
  await click(sel.fieldTime);
  await shot('02c-timepicker');
  await click(sel.min30);
  await click(sel.noche);
  await shot('02d-time-tuned');
  await click(sel.timeDone);
  await shot('02e-ready');
  await click(sel.confirmDate);
  await shot('03-q1');
  await click(sel.opt(3));
  await shot('03b-q1-selected');
  await click(sel.next(3));
  await shot('04-q2');
  await click(sel.opt(4));
  await click(sel.next(4));
  await shot('05-q3');
  await click(sel.opt(5));
  await click(sel.next(5));
  await shot('06-q4');
  await click(sel.opt(6));
  await click(sel.next(6));
  await shot('07-summary');
  await click(sel.celebrate);
  await shot('07b-finale');
}

(async () => {
  const browser = await chromium.launch();
  const opts = { viewport: { width: 560, height: 1400 }, deviceScaleFactor: 1 };

  const ref = await (await browser.newContext(opts)).newPage();
  await ref.goto('http://localhost:3007', { waitUntil: 'networkidle' });
  await ref.addStyleTag({ content: FREEZE });
  await ref.waitForTimeout(700);
  await run(ref, 'ref', path.join(OUT, 'ref'));

  const nay = await (await browser.newContext(opts)).newPage();
  await nay.goto('http://localhost:8511', { waitUntil: 'domcontentloaded' });
  await nay.waitForSelector('.st-key-nay_start button', { timeout: 30000 });
  await nay.waitForTimeout(1500);
  await nay.addStyleTag({ content: FREEZE });
  await run(nay, 'nay', path.join(OUT, 'nay'));
  await browser.close();

  const names = fs.readdirSync(path.join(OUT, 'ref'));
  let worst = [];
  for (const name of names) {
    const a = PNG.sync.read(fs.readFileSync(path.join(OUT, 'ref', name)));
    const b = PNG.sync.read(fs.readFileSync(path.join(OUT, 'nay', name)));
    const w = Math.min(a.width, b.width);
    const h = Math.min(a.height, b.height);
    const crop = (src) => {
      const out = new PNG({ width: w, height: h });
      PNG.bitblt(src, out, 0, 0, w, h, 0, 0);
      return out;
    };
    const ca = crop(a);
    const cb = crop(b);
    const diff = new PNG({ width: w, height: h });
    const n = pixelmatch(ca.data, cb.data, diff.data, w, h, { threshold: 0.12 });
    const pct = ((n / (w * h)) * 100).toFixed(2);
    fs.writeFileSync(path.join(OUT, 'diff-' + name), PNG.sync.write(diff));
    const sizeNote = a.height !== b.height ? ` (alto ref=${a.height} nay=${b.height})` : '';
    console.log(`${name}: ${pct}% (${n}px)${sizeNote}`);
    worst.push([parseFloat(pct), name]);
  }
  worst.sort((x, y) => y[0] - x[0]);
  console.log('\npeores:', worst.slice(0, 5).map(([p, n]) => `${n}=${p}%`).join(', '));
})();
