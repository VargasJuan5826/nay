const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const { PNG } = require('pngjs');
const H2C = fs.readFileSync(path.join(__dirname, '..', 'vendor', 'html2canvas.min.js'), 'utf8');
const FREEZE = '*,*::before,*::after{animation:none!important;transition:none!important}.float-cat{display:none!important}';
const OUT = path.join(__dirname, 'shots', 'canvas'); fs.mkdirSync(OUT, { recursive: true });

const RENDER = `(async () => {
  const el = document.getElementById('pdf-confirmation');
  const rect = el.getBoundingClientRect();
  const w = Math.ceil(rect.width), h = Math.ceil(rect.height);
  let info = 'sin clon';
  const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: '#ffffff',
    width: w, height: h, windowWidth: w, windowHeight: h, scrollX: 0, scrollY: 0,
    onclone: (doc) => {
      const card = doc.getElementById('pdf-confirmation');
      const rows = card ? card.querySelectorAll('div[style*="padding:10px 14px"], div[style*="padding: 10px 14px"]') : [];
      const row = rows[0];
      const cs = (n) => n ? getComputedStyle(n) : null;
      const r = cs(row), b = cs(doc.body), h2 = cs(doc.documentElement), c = cs(card);
      const probe = doc.createElement('div');
      probe.style.cssText = 'position:absolute;top:0;left:0;font-size:16px;line-height:normal;font-family:Nunito, sans-serif';
      probe.textContent = 'Hg';
      (doc.body || card).appendChild(probe);
      const dataRow = rows[1];
      const dr = dataRow ? getComputedStyle(dataRow) : null;
      const spans = dataRow ? [...dataRow.children].map((sp) => {
        const cs2 = getComputedStyle(sp);
        return cs2.fontSize + '/' + cs2.lineHeight + '/' + cs2.display + '/' + Math.round(sp.getBoundingClientRect().height * 100) / 100 + '/' + cs2.fontFamily.slice(0, 22);
      }) : [];
      info = JSON.stringify({
        filas: rows.length,
        rowH: dataRow ? Math.round(dataRow.getBoundingClientRect().height * 100) / 100 : null,
        rowFs: dataRow ? getComputedStyle(dataRow).fontSize : null,
        cardH: card ? Math.round(card.getBoundingClientRect().height * 100) / 100 : null,
        strut16: Math.round(probe.getBoundingClientRect().height * 100) / 100,
        card: c && (c.fontSize + '/' + c.lineHeight + '/' + c.width),
        estilos: doc.querySelectorAll('style').length,
        links: doc.querySelectorAll('link[rel=stylesheet]').length,
        rowDisplay: dr && dr.display, rowLh: dr && dr.lineHeight, rowPad: dr && dr.padding,
        rowFont: dr && dr.fontFamily.slice(0, 22),
        spans,
        rowHtml: dataRow ? dataRow.innerHTML.slice(0, 90) : null,
      });
      probe.remove();
    } });
  return { img: canvas.toDataURL('image/png'), info };
})()`;

(async () => {
  const b = await chromium.launch();
  const c = async (p, s, w) => { await p.click(s); await p.waitForTimeout(w); };
  const save = (dataUrl, file) => {
    fs.writeFileSync(path.join(OUT, file), Buffer.from(dataUrl.split(',')[1], 'base64'));
    return path.join(OUT, file);
  };

  const ref = await (await b.newContext({ viewport: { width: 700, height: 1400 } })).newPage();
  await ref.goto('http://localhost:3007', { waitUntil: 'networkidle' });
  await ref.addStyleTag({ content: FREEZE }); await ref.waitForTimeout(500);
  await c(ref, 'text=INICIAR PROTOCOLO', 300); await c(ref, 'button:has-text("Sí")', 300);
  await c(ref, 'button:has-text("Selecciona una fecha")', 300); await c(ref, 'button:text-is("25")', 300);
  await c(ref, 'button:has-text("Selecciona una hora")', 300); await c(ref, 'button:has-text("Listo")', 300);
  await c(ref, 'button:has-text("CONFIRMAR FECHA")', 400);
  for (const q of [3, 4, 5, 6]) { await c(ref, `#s${q} .opt >> nth=0`, 200); await c(ref, `#s${q} button:has-text("SIGUIENTE")`, 300); }
  await c(ref, 'button:has-text("ACEPTO LOS")', 700);
  await ref.addScriptTag({ content: H2C });
  const rr = await ref.evaluate(RENDER); console.log('REF clon:', rr.info); save(rr.img, 'ref.png');

  const nay = await (await b.newContext({ viewport: { width: 700, height: 1400 } })).newPage();
  await nay.goto('http://localhost:8511', { waitUntil: 'domcontentloaded' });
  await nay.waitForSelector('.st-key-nay_start button'); await nay.waitForTimeout(1400);
  await nay.addStyleTag({ content: FREEZE });
  await c(nay, '.st-key-nay_start button', 800); await c(nay, '.st-key-nay_si button', 800);
  await c(nay, '.st-key-nay_field_date button', 800); await c(nay, '.st-key-nay_day_25 button', 800);
  await c(nay, '.st-key-nay_field_time button', 800); await c(nay, '.st-key-nay_time_done button', 800);
  await c(nay, '.st-key-nay_confirm_date button', 900);
  for (const q of [3, 4, 5, 6]) { await c(nay, `.st-key-nay_opt_${q}_0 button`, 700); await c(nay, `.st-key-nay_next_${q} button`, 800); }
  await c(nay, '.st-key-nay_celebrate button', 1500);
  await nay.addScriptTag({ content: H2C });
  const nn = await nay.evaluate(RENDER); console.log('NAY clon:', nn.info); save(nn.img, 'nay.png');
  await b.close();

  const A = PNG.sync.read(fs.readFileSync(path.join(OUT, 'ref.png')));
  const B = PNG.sync.read(fs.readFileSync(path.join(OUT, 'nay.png')));
  console.log(`canvas ref ${A.width}x${A.height} | nay ${B.width}x${B.height}`);
  const w = Math.min(A.width, B.width), h = Math.min(A.height, B.height);
  let n = 0, max = 0;
  const rows = new Map();
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const ia = (A.width * y + x) * 4, ib = (B.width * y + x) * 4;
    const d = Math.max(Math.abs(A.data[ia] - B.data[ib]), Math.abs(A.data[ia + 1] - B.data[ib + 1]), Math.abs(A.data[ia + 2] - B.data[ib + 2]));
    if (d > 24) { n++; rows.set(y, (rows.get(y) || 0) + 1); }
    if (d > max) max = d;
  }
  console.log(`canvas del PDF: distintos=${n} (${((n / (w * h)) * 100).toFixed(3)}%) delta_max=${max}`);
  const top = [...rows.entries()].sort((p, q) => q[1] - p[1]).slice(0, 6);
  console.log('filas con más diferencias:', JSON.stringify(top));
})();
