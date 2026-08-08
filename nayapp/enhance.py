"""Realce del botón "No".

Dos cosas:

1. Traduce el hover del "No" (Streamlit sólo entrega clicks) en un click sobre el mismo
   botón, así corre el callback de Python. Si el iframe no pudiera hablar con el documento
   padre, el botón sigue funcionando a click: la degradación es silenciosa.

2. Guarda anti "ghost click" de mobile. Al tocar un botón, el navegador móvil dispara un
   click de mouse "fantasma" ~300ms después; entrando a este paso, ese click caía sobre el
   "No" recién montado (o sobre el "No" que acababa de saltar) y lo hacía escapar solo —a
   veces en cascada— como si lo hubieras tocado. Acá, en cada render del paso, se traga en
   capture phase (antes que Streamlit) el primer click/touch que caiga sobre el Sí/No
   durante ~450ms. Se re-arma en cada render, así cubre tanto la primera vez como cada
   escape posterior y las re-entradas.
"""

from __future__ import annotations

import streamlit.components.v1 as components


def hover_to_click(token: str) -> None:
    markup = f"""
    <script>
    (function () {{
      var TOKEN = "{token}";
      var doc;
      try {{ doc = window.parent.document; }} catch (error) {{ return; }}
      if (!doc) return;

      function hitYesNo(target, sel) {{
        return target && target.closest ? target.closest(sel) : null;
      }}

      // --- Guarda anti "ghost click" (se re-arma en cada render de este paso) ----------
      var armedUntil = Date.now() + 450;
      var onClick = function (e) {{
        if (Date.now() > armedUntil) return;
        if (hitYesNo(e.target, '.st-key-nay_no, .st-key-nay_si')) {{
          e.stopImmediatePropagation();
          e.preventDefault();
        }}
      }};
      var onTouch = function (e) {{
        if (Date.now() > armedUntil) return;
        if (hitYesNo(e.target, '.st-key-nay_no, .st-key-nay_si') && e.cancelable) {{
          e.preventDefault();
        }}
      }};
      // Un solo par de listeners a la vez: el render anterior se limpia acá.
      if (doc.__nayGuard) {{
        doc.removeEventListener('click', doc.__nayGuard.c, true);
        doc.removeEventListener('touchstart', doc.__nayGuard.t, true);
      }}
      doc.__nayGuard = {{ c: onClick, t: onTouch }};
      doc.addEventListener('click', onClick, true);
      doc.addEventListener('touchstart', onTouch, true);

      // --- Pasado el margen, engancha el escape por hover/touch -----------------------
      var start = Date.now();
      var timer = setInterval(function () {{
        var no = doc.querySelector('.st-key-nay_no button');
        if (!no) return;
        if (Date.now() - start < 450) return;
        if (no.dataset.nayToken === TOKEN) {{ clearInterval(timer); return; }}
        no.dataset.nayToken = TOKEN;
        var escape = function (event) {{
          if (event.cancelable) event.preventDefault();
          no.click();
        }};
        no.addEventListener('mouseenter', escape, {{ once: true }});
        no.addEventListener('touchstart', escape, {{ once: true, passive: false }});
        clearInterval(timer);
      }}, 60);
    }})();
    </script>
    """
    components.html(markup, height=0)
