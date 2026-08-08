"""Descarga del PDF de confirmación.

Mismo mecanismo que el original (html2canvas + jsPDF sobre una tarjeta oculta), con dos
diferencias de implementación:

* las librerías viajan dentro del repo (`vendor/`) en vez de venir de un bundle npm, así
  el deploy en Streamlit Cloud no depende de ningún CDN;
* la tarjeta se dibuja en el documento principal y no dentro del iframe del botón. Es
  necesario: html2canvas rearma el documento en un iframe propio y, si el origen es el
  iframe chico del componente, las líneas que combinan `line-height: normal` con emojis
  resuelven más bajas y el PDF sale comprimido.
"""

from __future__ import annotations

import html as html_lib

import streamlit.components.v1 as components

from . import assets, content

_ROW_TEMPLATE = (
    '<div style="padding:10px 14px;border-bottom:1px solid #e5e7eb;{extra}">'
    '<span style="font-size:9px;color:#6b7280">{icon} {label} </span>'
    '<span style="font-size:10px;font-weight:700">{value}</span>'
    "</div>"
)


def _rows(answers: dict) -> str:
    rows = []
    last = len(content.SUMMARY_ROWS) - 1
    for position, (icon, label, key) in enumerate(content.SUMMARY_ROWS):
        value = html_lib.escape(str(answers.get(key) or "—"))
        extra = "background:#f9fafb;" if position % 2 == 1 else ""
        if position == last:
            extra += "border-bottom:none;"
        rows.append(_ROW_TEMPLATE.format(icon=icon, label=label, value=value, extra=extra))
    return "".join(rows)


def card(answers: dict) -> str:
    """La tarjeta que html2canvas convierte en PDF. Oculta fuera de pantalla, igual que
    el `#pdf-confirmation` del original."""
    markup = f"""
    <div class="nay">
      <div id="pdf-confirmation">
        <div style="padding:20px;text-align:center">
          <img src="{assets.url('gatito1.png')}" alt="gatito"
               style="width:80px;height:auto;margin:0 auto 16px">
          <div style="font-size:20px;font-weight:bold;color:#7c3aed;margin:0 0 4px">
            💜 ¡Salida Confirmada! 💜</div>
          <div style="font-size:10px;color:#6b7280;margin:0 0 20px">
            // salida.exe iniciada correctamente</div>
        </div>
        <div style="padding:0 20px 20px">
          <div style="border:2px solid #ede9fe;border-radius:12px;overflow:hidden;margin-bottom:16px">
            <div style="background:#f3e8ff;padding:10px 14px;font-weight:800;font-size:11px;color:#7c3aed">
              📋 Resumen de tu salida</div>
            {_rows(answers)}
          </div>
          <div style="font-size:9px;color:#6b7280;text-align:center;line-height:1.6;margin:0">
            ¡Nos vemos pronto! 💜<br>
            <span style="font-size:8px">// generado por peticion_random_v2.0.cat</span>
          </div>
        </div>
      </div>
    </div>
    """
    return "".join(line.strip() for line in markup.strip().splitlines())


# El posicionamiento fuera de pantalla de la tarjeta está en nayapp/theme.py.

# 12px de margen superior + 41px de botón: el mismo alto que la fila del original.
HEIGHT = 53


def download_button() -> None:
    """Botón "📄 Descargar PDF" idéntico al original, dentro de un iframe propio."""
    markup = f"""
    <style>
      html, body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
      * {{ box-sizing: border-box; }}
      .pdf-row {{ display: flex; gap: 8px; margin-top: 12px; font-family: 'Nunito', sans-serif; }}
      #dl {{
        flex: 1; background: #7c3aed; color: #fff; border: none; border-radius: 12px;
        padding: 12px 16px; font-weight: 800; font-size: 12px; cursor: pointer;
        display: flex; align-items: center; justify-content: center; gap: 6px;
        box-shadow: 0 4px 12px rgba(124,58,237,0.3);
        font-family: 'Nunito', sans-serif; transition: all .2s ease;
      }}
      #dl:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(124,58,237,0.4); }}
      #dl:disabled {{ opacity: .7; cursor: progress; transform: none; }}
    </style>
    <div class="pdf-row">
      <button id="dl" type="button">📄 Descargar PDF</button>
    </div>
    <script>{assets.vendor_js('html2canvas.min.js')}</script>
    <script>{assets.vendor_js('jspdf.umd.min.js')}</script>
    <script>
    (function () {{
      var button = document.getElementById('dl');

      // La tarjeta vive en el documento principal (ver docstring del módulo).
      function findCard() {{
        try {{
          return window.parent.document.getElementById('pdf-confirmation');
        }} catch (error) {{
          return null;
        }}
      }}

      button.addEventListener('click', async function () {{
        var element = findCard();
        if (!element) {{
          console.error('No se encontró la tarjeta del PDF');
          return;
        }}
        var label = button.textContent;
        button.disabled = true;
        button.textContent = '📄 Generando...';
        try {{
          var canvas = await html2canvas(element, {{
            scale: 2, useCORS: true, backgroundColor: '#ffffff'
          }});
          var imgData = canvas.toDataURL('image/png');
          var pdf = new window.jspdf.jsPDF({{
            orientation: 'portrait', unit: 'mm', format: 'a5'
          }});
          var imgWidth = 148;
          var imgHeight = (canvas.height * imgWidth) / canvas.width;
          pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
          save(pdf, 'salida_confirmada.pdf');
        }} catch (error) {{
          console.error('Error generating PDF:', error);
        }} finally {{
          button.disabled = false;
          button.textContent = label;
        }}
      }});

      // El iframe de Streamlit puede tener el sandbox sin `allow-downloads`: en ese caso
      // se dispara el anchor desde el documento padre, que no está restringido.
      function save(pdf, name) {{
        try {{
          var doc = window.parent.document;
          if (!doc || !doc.body) throw new Error('no parent');
          var url = URL.createObjectURL(pdf.output('blob'));
          var anchor = doc.createElement('a');
          anchor.href = url;
          anchor.download = name;
          anchor.style.display = 'none';
          doc.body.appendChild(anchor);
          anchor.click();
          setTimeout(function () {{
            anchor.remove();
            URL.revokeObjectURL(url);
          }}, 5000);
        }} catch (error) {{
          pdf.save(name);
        }}
      }}
    }})();
    </script>
    """
    components.html(markup, height=HEIGHT)
