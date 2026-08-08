"""Acceso a los memes: URL estática para el DOM y data-uri para los iframes."""

from __future__ import annotations

import base64
import functools
from pathlib import Path

STATIC_DIR = Path(__file__).resolve().parent.parent / "static" / "memes"
VENDOR_DIR = Path(__file__).resolve().parent.parent / "vendor"


def url(name: str) -> str:
    """URL relativa servida por Streamlit (`enableStaticServing`)."""
    return f"app/static/memes/{name}"


@functools.lru_cache(maxsize=None)
def data_uri(name: str) -> str:
    """Data-uri: necesaria dentro de iframes (srcdoc no resuelve rutas relativas)."""
    raw = (STATIC_DIR / name).read_bytes()
    mime = "image/jpeg" if name.lower().endswith((".jpg", ".jpeg")) else "image/png"
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


@functools.lru_cache(maxsize=None)
def vendor_js(name: str) -> str:
    """Librería JS embebida en el repo (sin CDN, funciona offline)."""
    return (VENDOR_DIR / name).read_text(encoding="utf-8")
