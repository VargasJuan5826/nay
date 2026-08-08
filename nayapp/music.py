"""Música de fondo con un embed (oculto) de YouTube y una barra de reproductor propia.

Dos restricciones que definen el diseño:

* **Autoplay con sonido:** los navegadores lo bloquean hasta que hay un gesto del usuario.
  Por eso la música arranca en el primer click (el botón "INICIAR"): ese gesto habilita el
  audio, y como es lo primero que se toca, se siente automático.
* **Persistencia entre reruns:** Streamlit recrea los iframes de `components.html` en cada
  rerun, así que un player montado ahí se reiniciaría al cambiar de paso. Para evitarlo, el
  iframe del componente sólo hace de *bootstrap*: inyecta —una única vez, con guarda— un
  `<script>` en el documento padre. Ese script corre en el contexto del padre (fuera del
  árbol de React de Streamlit, colgado de `document.body`), así el player, su barra de
  reproductor y el estado sobreviven a los reruns y a los cambios de paso.

El video de YouTube va oculto; lo que se ve es una barra propia (play/pausa, tiempo, una
barra para scrubbear/adelantar y mute) construida sobre la IFrame API de YouTube.
"""

from __future__ import annotations

import json

import streamlit.components.v1 as components

# Corre en el documento PADRE (lo inyecta el bootstrap). `window` es la ventana principal.
_PARENT_SCRIPT = r"""
(function () {
  var VIDEO_ID = "__VIDEO_ID__";
  var state = { ready: false, started: false, muted: false, want: false, seeking: false, player: null };
  window.__nayMusic = state;

  // Estilos de la barra (el thumb del range necesita hoja de estilos, no inline). También
  // deja aire abajo del contenido para que la barra no tape el último botón.
  var css = document.createElement('style');
  css.textContent =
    // Barra full-width pegada arriba (tipo header de la web), no un pill flotante.
    '#nay-music-bar{position:fixed;top:0;left:0;right:0;width:100%;z-index:9998;' +
    'background:#ffffff;border-bottom:1px solid #ece9fb;box-shadow:0 2px 10px rgba(124,58,237,0.10);' +
    "font-family:'Nunito',sans-serif;box-sizing:border-box;}" +
    // Los controles se alinean en la misma columna de 560px que el resto de la app.
    '#nay-music-inner{max-width:560px;margin:0 auto;display:flex;align-items:center;gap:10px;' +
    'padding:8px 14px;box-sizing:border-box;}' +
    '#nay-music-bar button{border:none;background:none;cursor:pointer;padding:0;color:#5b21b6;' +
    'display:flex;align-items:center;justify-content:center;line-height:1;}' +
    '#nay-music-play{width:30px;height:30px;border-radius:50%;flex:0 0 auto;' +
    'background:linear-gradient(135deg,#7c3aed,#ec4899)!important;color:#fff!important;font-size:14px;}' +
    '#nay-music-mute{font-size:16px;flex:0 0 auto;}' +
    '#nay-music-bar .nay-t{font-size:10px;color:#6b7280;font-variant-numeric:tabular-nums;flex:0 0 auto;min-width:28px;text-align:center;}' +
    '#nay-music-seek{-webkit-appearance:none;appearance:none;flex:1 1 auto;height:4px;border-radius:2px;' +
    'background:#e9e5f7;outline:none;cursor:pointer;}' +
    '#nay-music-seek::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:13px;height:13px;' +
    'border-radius:50%;background:#7c3aed;cursor:pointer;box-shadow:0 1px 3px rgba(124,58,237,0.5);}' +
    '#nay-music-seek::-moz-range-thumb{width:13px;height:13px;border-radius:50%;background:#7c3aed;border:none;cursor:pointer;}' +
    '[data-testid="stAppViewContainer"] [data-testid="stMainBlockContainer"]{padding-top:60px!important;}';
  document.head.appendChild(css);

  // Host oculto para el player de YouTube. Colgado de <body> (fuera del root de Streamlit),
  // así los reruns no lo tocan.
  var host = document.createElement('div');
  host.id = 'nay-yt-host';
  host.style.cssText = 'position:fixed;left:-9999px;top:0;width:1px;height:1px;overflow:hidden;';
  var slot = document.createElement('div');
  slot.id = 'nay-yt-player';
  host.appendChild(slot);
  document.body.appendChild(host);

  // Barra de reproductor.
  var bar = document.createElement('div');
  bar.id = 'nay-music-bar';
  bar.innerHTML =
    '<div id="nay-music-inner">' +
    '<button id="nay-music-play" type="button" aria-label="Play/Pausa">▶</button>' +
    '<span class="nay-t" id="nay-music-cur">0:00</span>' +
    '<input id="nay-music-seek" type="range" min="0" max="100" value="0" step="0.1" aria-label="Adelantar">' +
    '<span class="nay-t" id="nay-music-dur">0:00</span>' +
    '<button id="nay-music-mute" type="button" aria-label="Silenciar">🔊</button>' +
    '</div>';
  document.body.appendChild(bar);

  var playBtn = document.getElementById('nay-music-play');
  var muteBtn = document.getElementById('nay-music-mute');
  var seek = document.getElementById('nay-music-seek');
  var curEl = document.getElementById('nay-music-cur');
  var durEl = document.getElementById('nay-music-dur');

  function fmt(s) {
    s = Math.max(0, Math.floor(s || 0));
    var m = Math.floor(s / 60);
    var r = s % 60;
    return m + ':' + (r < 10 ? '0' : '') + r;
  }
  function isPlaying() {
    try { return state.player && state.player.getPlayerState() === 1; } catch (e) { return false; }
  }

  function start() {
    if (!state.player || !state.ready) { state.want = true; return; }
    if (state.started) return;
    state.started = true;
    try { state.player.unMute(); state.player.setVolume(45); state.player.playVideo(); } catch (e) {}
  }
  function toggleMute() {
    if (!state.player) return;
    if (state.muted) { try { state.player.unMute(); } catch (e) {} state.muted = false; }
    else { try { state.player.mute(); } catch (e) {} state.muted = true; }
    muteBtn.textContent = state.muted ? '🔇' : '🔊';
  }

  playBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    if (!state.player) return;
    if (!state.started) { start(); return; }
    try { if (isPlaying()) state.player.pauseVideo(); else state.player.playVideo(); } catch (e2) {}
  });
  muteBtn.addEventListener('click', function (e) { e.stopPropagation(); toggleMute(); });

  // Scrubbear / adelantar.
  seek.addEventListener('input', function () { state.seeking = true; curEl.textContent = fmt(seek.value); });
  var commitSeek = function () {
    var v = parseFloat(seek.value);
    try { state.player.seekTo(v, true); } catch (e) {}
    curEl.textContent = fmt(v);
    // Mantené "seeking" un toque más: seekTo() es async y getCurrentTime() todavía
    // devuelve la posición vieja por un instante; sin esto el loop volvería el slider
    // hacia atrás apenas lo soltás (parece que "se mueve solo").
    setTimeout(function () { state.seeking = false; }, 800);
  };
  seek.addEventListener('change', commitSeek);
  seek.addEventListener('pointerup', commitSeek);
  seek.addEventListener('click', function (e) { e.stopPropagation(); });

  // Refresco de la barra (a menos que se esté arrastrando). Sólo actualiza con valores
  // sanos, así un valor transitorio raro del player no hace saltar el slider.
  setInterval(function () {
    if (!state.player || !state.ready) return;
    try {
      var d = state.player.getDuration() || 0;
      var t = state.player.getCurrentTime();
      if (d && parseFloat(seek.max) !== d) { seek.max = d; durEl.textContent = fmt(d); }
      if (!state.seeking && typeof t === 'number' && isFinite(t) && t >= 0 && (!d || t <= d + 1)) {
        seek.value = t; curEl.textContent = fmt(t);
      }
      playBtn.textContent = isPlaying() ? '⏸' : '▶';
    } catch (e) {}
  }, 400);

  // El primer gesto del usuario en cualquier lado (el click de "INICIAR") arranca la
  // música con sonido. No frena la propagación, así el botón sigue funcionando normal.
  var onFirstGesture = function () {
    start();
    if (state.started || state.want) {
      document.removeEventListener('click', onFirstGesture, true);
      document.removeEventListener('touchend', onFirstGesture, true);
    }
  };
  document.addEventListener('click', onFirstGesture, true);
  document.addEventListener('touchend', onFirstGesture, true);

  // API de YouTube (en el documento padre).
  function makePlayer() {
    state.player = new window.YT.Player('nay-yt-player', {
      videoId: VIDEO_ID,
      playerVars: {
        autoplay: 0, controls: 0, playsinline: 1, modestbranding: 1, rel: 0, fs: 0, disablekb: 1
      },
      events: {
        onReady: function () { state.ready = true; if (state.want) start(); },
        onStateChange: function (ev) {
          // Loop propio (sin playlist): al terminar, vuelve a empezar.
          if (ev.data === window.YT.PlayerState.ENDED) {
            try { ev.target.seekTo(0, true); ev.target.playVideo(); } catch (e) {}
          }
        }
      }
    });
  }
  if (window.YT && window.YT.Player) {
    makePlayer();
  } else {
    var prev = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = function () {
      if (typeof prev === 'function') { try { prev(); } catch (e) {} }
      makePlayer();
    };
    if (!document.getElementById('nay-yt-api')) {
      var tag = document.createElement('script');
      tag.id = 'nay-yt-api';
      tag.src = 'https://www.youtube.com/iframe_api';
      document.head.appendChild(tag);
    }
  }
})();
"""

_BOOTSTRAP = r"""
<script>
(function () {
  var pdoc, pwin;
  try { pdoc = window.parent.document; pwin = window.parent; } catch (e) { return; }
  if (!pdoc || !pdoc.body || pwin.__nayMusicInjected) return;
  pwin.__nayMusicInjected = true;  // marca antes de inyectar: evita doble montaje
  var s = pdoc.createElement('script');
  s.textContent = __PARENT_SCRIPT__;
  pdoc.body.appendChild(s);
})();
</script>
"""


def background(video_id: str) -> None:
    """Monta (una sola vez) la música de fondo en loop con una barra de reproductor propia."""
    parent = _PARENT_SCRIPT.replace("__VIDEO_ID__", video_id)
    # `parent` viaja como literal de string JS; escapamos "</" para que ningún fragmento
    # pueda cerrar el <script> del bootstrap al parsear el HTML.
    literal = json.dumps(parent).replace("</", "<\\/")
    components.html(_BOOTSTRAP.replace("__PARENT_SCRIPT__", literal), height=0)
