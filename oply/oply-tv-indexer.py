#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oply TV Indexer (Country-aware)
Crea un "index" por locales (idiomas/países) soportados por Oply y genera archivos de canales por locale.

Objetivo:
- Cuando elegís es_AR, es_ES, es_MX, etc. NO copia la lista global de noticias:
  descarga (o intenta descargar) la playlist por país y genera tv_channels_<locale>.json con canales de ese país.
- NO escribe nada en /root: si se ejecuta como root con SUDO_USER, usa el HOME del usuario real.
- Archivos generados por usuario (en ~/.config/oply):
    - tv_index.json
    - tv_channels_<locale>.json  (por cada locale seleccionado)

Fuente recomendada para playlists por país:
- IPTV-org (playlists por país): https://iptv-org.github.io/iptv/ (countries/<cc>.m3u)

Autor: josejp2424
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import pwd
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


OPLY_DIR = Path("/usr/local/Oply")
OPLY_VIDEO = OPLY_DIR / "Oply-Video.py"

TV_COUNTRY_PLAYLIST_BASE = "https://iptv-org.github.io/iptv/countries/{cc}.m3u"

# Locales disponibles para crear índice TV
LOCALE_CHOICES: List[Dict[str, str]] = [
    # Árabe (Arabia Saudita)
    {"code": "ar_SA", "label": "العربية (السعودية)", "flag": "flags/ar_SA.png"},

    # Catalán
    {"code": "ca_ES", "label": "Català (ES)", "flag": "flags/ca_ES.png"},

    # Inglés
    {"code": "en_US", "label": "English (United States)", "flag": "flags/en_US.png"},
    {"code": "en_GB", "label": "English (United Kingdom)", "flag": "flags/en_GB.png"},

    # Español (variantes)
    {"code": "es_ES", "label": "Español (España)", "flag": "flags/es_ES.png"},
    {"code": "es_AR", "label": "Español (Argentina)", "flag": "flags/es_AR.png"},
    {"code": "es_MX", "label": "Español (México)", "flag": "flags/es_MX.png"},
    {"code": "es_CL", "label": "Español (Chile)", "flag": "flags/es_CL.png"},
    {"code": "es_VE", "label": "Español (Venezuela)", "flag": "flags/es_VE.png"},
    {"code": "es_CO", "label": "Español (Colombia)", "flag": "flags/es_CO.png"},
    {"code": "es_BO", "label": "Español (Bolivia)", "flag": "flags/es_BO.png"},
    {"code": "es_PY", "label": "Español (Paraguay)", "flag": "flags/es_PY.png"},
    {"code": "es_UY", "label": "Español (Uruguay)", "flag": "flags/es_UY.png"},
    {"code": "es_SV", "label": "Español (El Salvador)", "flag": "flags/es_SV.png"},

    # Otros idiomas
    {"code": "fr_FR", "label": "Français (France)", "flag": "flags/fr_FR.png"},
    {"code": "it_IT", "label": "Italiano (Italia)", "flag": "flags/it_IT.png"},
    {"code": "pt_PT", "label": "Português (Portugal)", "flag": "flags/pt_PT.png"},
    {"code": "pt_BR", "label": "Português (Brasil)", "flag": "flags/pt_BR.png"},
    {"code": "hu_HU", "label": "Magyar (Magyarország)", "flag": "flags/hu_HU.png"},
    {"code": "ru_RU", "label": "Русский (Россия)", "flag": "flags/ru_RU.png"},
    {"code": "ja_JP", "label": "日本語 (日本)", "flag": "flags/ja_JP.png"},
    {"code": "zh_CN", "label": "中文 (简体)", "flag": "flags/zh_CN.png"},
    {"code": "zh_TW", "label": "中文 (繁體)", "flag": "flags/zh_TW.png"},
]

LABELS = {it["code"]: it["label"] for it in LOCALE_CHOICES}
DEFAULT_LOCALES = [it["code"] for it in LOCALE_CHOICES]

# Mapeo locale -> país (ISO 3166-1 alpha-2 en minúscula) para la playlist countries/<cc>.m3u
LOCALE_TO_COUNTRY = {
    "ar_SA": "sa",
    "ca_ES": "es",
    "en_US": "us",
    "en_GB": "gb",
    "es_ES": "es",
    "es_AR": "ar",
    "es_MX": "mx",
    "es_CL": "cl",
    "es_VE": "ve",
    "es_CO": "co",
    "es_BO": "bo",
    "es_PY": "py",
    "es_UY": "uy",
    "es_SV": "sv",
    "fr_FR": "fr",
    "it_IT": "it",
    "pt_PT": "pt",
    "pt_BR": "br",
    "hu_HU": "hu",
    "ru_RU": "ru",
    "ja_JP": "jp",
    "zh_CN": "cn",
    "zh_TW": "tw",
}

# Nombres de la lista "global news" (la que trae Oply por defecto)
GLOBAL_NEWS_NAMES = {
    "CGTN News",
    "FOX News",
    "CBSN News",
    "CNA (Singapore)",
    "Sky News (UK)",
    "Al Jazeera English",
    "France 24 (English)",
    "ABC News Live (AU)",
    "DW News",
    "Euronews",
}


def get_real_home() -> Path:
    """Evita escribir en /root cuando se ejecuta vía sudo/pkexec."""
    try:
        if os.geteuid() == 0:
            sudo_user = os.environ.get("SUDO_USER")
            if sudo_user:
                return Path(pwd.getpwnam(sudo_user).pw_dir)
            pkuid = os.environ.get("PKEXEC_UID")
            if pkuid and pkuid.isdigit():
                return Path(pwd.getpwuid(int(pkuid)).pw_dir)
    except Exception:
        pass
    return Path.home()


def config_dir() -> Path:
    return get_real_home() / ".config" / "oply"


def list_oply_locales() -> List[str]:
    return DEFAULT_LOCALES[:]


def get_label(locale_code: str) -> str:
    return LABELS.get(locale_code, locale_code.upper())


def _extract_list_literal(py_path: Path, var_name: str) -> Optional[List[Dict[str, Any]]]:
    """Extrae una lista literal asignada a var_name (ej TV_CHANNELS) sin ejecutar."""
    try:
        src = py_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    try:
        tree = ast.parse(src, filename=str(py_path))
    except Exception:
        return None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == var_name and isinstance(node.value, ast.List):
                    try:
                        return ast.literal_eval(node.value)
                    except Exception:
                        return None
    return None


def load_global_news_from_oply_video() -> List[Dict[str, Any]]:
    embedded = _extract_list_literal(OPLY_VIDEO, "TV_CHANNELS")
    if isinstance(embedded, list):
        out = []
        for ch in embedded:
            if isinstance(ch, dict) and ch.get("name") and ch.get("url"):
                out.append(ch)
        return out
    return []


def load_base_channels(cfg: Path) -> List[Dict[str, Any]]:
    """
    Base:
      1) ~/.config/oply/tv_channels.json  (si el usuario lo define)
      2) TV_CHANNELS embebido en /usr/local/Oply/Oply-Video.py (global news)
      3) lista vacía
    """
    tv = cfg / "tv_channels.json"
    if tv.exists():
        try:
            data = json.loads(tv.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass

    embedded = load_global_news_from_oply_video()
    return embedded if embedded else []


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def looks_like_global_news_list(chs: Any) -> bool:
    """Detecta si tv_channels_<locale>.json contiene la lista global de noticias (viejo comportamiento)."""
    if not isinstance(chs, list) or not chs:
        return False
    names = {str(c.get("name", "")).strip() for c in chs if isinstance(c, dict)}
    hits = len(names.intersection(GLOBAL_NEWS_NAMES))
    return hits >= 6  


def fetch_text(url: str, timeout: int = 10) -> Optional[str]:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Oply-TV-Indexer/1.0 (+https://sourceforge.net/projects/essora/)"
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return raw.decode("latin-1", errors="replace")
    except Exception:
        return None


def parse_m3u(m3u_text: str, icon_fallback: str, max_items: int = 250) -> List[Dict[str, Any]]:
    """
    Parse simple de M3U:
      - #EXTINF... ,Nombre
      - siguiente línea no vacía y no comentada => URL
    """
    out: List[Dict[str, Any]] = []
    pending_name: Optional[str] = None

    for raw in m3u_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            if "," in line:
                pending_name = line.split(",", 1)[1].strip()
            else:
                pending_name = "TV"
            continue
        if line.startswith("#"):
            continue

        # URL
        url = line
        name = pending_name or "TV"
        pending_name = None

        if not (url.startswith("http://") or url.startswith("https://")):
            continue

        out.append({
            "name": name,
            "url": url,
            "icon": icon_fallback,
        })
        if len(out) >= max_items:
            break

    # dedup por url
    dedup = []
    seen = set()
    for ch in out:
        u = ch.get("url")
        if u and u not in seen:
            seen.add(u)
            dedup.append(ch)
    return dedup


def country_channels_for_locale(locale_code: str, max_items: int = 250, allow_fetch: bool = True) -> List[Dict[str, Any]]:
    cc = LOCALE_TO_COUNTRY.get(locale_code)
    if not cc:
        return []

    if not allow_fetch:
        return []

    url = TV_COUNTRY_PLAYLIST_BASE.format(cc=cc)
    text = fetch_text(url)
    if not text:
        return []

    icon_fallback = f"flags/{locale_code}.png"
    return parse_m3u(text, icon_fallback=icon_fallback, max_items=max_items)


def build_index(
    selected_locales: List[str],
    force: bool = False,
    max_items: int = 250,
    no_fetch: bool = False,
) -> Tuple[Path, List[Path], List[str]]:
    cfg = config_dir()
    cfg.mkdir(parents=True, exist_ok=True)

    locales_all = list_oply_locales()
    map_lower = {c.lower(): c for c in locales_all}
    selected: List[str] = []
    for x in selected_locales:
        raw = x.strip()
        if not raw:
            continue
        norm = map_lower.get(raw.lower())
        if norm and norm not in selected:
            selected.append(norm)

    if not (1 <= len(selected) <= 3):
        raise SystemExit("Seleccioná 1, 2 o 3 locales (ej: --locales es_AR,es_ES,ar_SA).")

    base_channels = load_base_channels(cfg)
    created_files: List[Path] = []
    notes: List[str] = []

    items = []
    for loc in selected:
        fn = f"tv_channels_{loc}.json"
        p = cfg / fn
        items.append({"locale": loc, "label": get_label(loc), "channels_file": fn, "flag": f"flags/{loc}.png"})


        must_write = force or (not p.exists())
        if (not must_write) and p.exists():

            try:
                existing = json.loads(p.read_text(encoding="utf-8"))
                if looks_like_global_news_list(existing):
                    must_write = True
                    notes.append(f"{loc}: detecté lista global vieja → actualizo por país")
            except Exception:
                pass

        if must_write:
            chs = country_channels_for_locale(loc, max_items=max_items, allow_fetch=(not no_fetch))
            if not chs:
                chs = base_channels
                notes.append(f"{loc}: no pude obtener playlist por país → uso lista base")
            write_json(p, chs)
            created_files.append(p)

    idx = {
        "meta": {
            "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generator": "oply-tv-indexer",
            "country_mode": True,
            "source": "iptv-org countries/<cc>.m3u (cuando hay internet) + fallback local",
        },
        "selected_locales": selected,
        "active_locale": selected[0],
        "items": items,
    }

    index_path = cfg / "tv_index.json"
    write_json(index_path, idx)
    return index_path, created_files, notes


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Crea un index TV por locales/países para Oply (por país).")
    ap.add_argument("--list-locales", action="store_true", help="Imprime locales soportados (JSON) y sale.")
    ap.add_argument("--locales", type=str, default="", help="Locales a incluir (coma separada). Ej: es_AR,es_ES,ar_SA")
    ap.add_argument("--force", action="store_true", help="Sobrescribe tv_channels_<locale>.json aunque existan.")
    ap.add_argument("--no-fetch", action="store_true", help="No descarga playlists por país (usa la lista base).")
    ap.add_argument("--max", type=int, default=250, help="Máximo de canales por país (default: 250).")
    args = ap.parse_args(argv)

    if args.list_locales:
        locs = list_oply_locales()
        payload = [{"code": c, "label": get_label(c), "flag": f"flags/{c}.png"} for c in locs]
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    selected = [x for x in args.locales.split(",") if x.strip()]
    index_path, created_files, notes = build_index(
        selected,
        force=args.force,
        max_items=max(10, min(int(args.max), 2000)),
        no_fetch=args.no_fetch,
    )

    print(f"OK: {index_path}")
    if notes:
        print("Notas:")
        for n in notes:
            print(f" - {n}")
    if created_files:
        print("Actualizado(s):")
        for p in created_files:
            print(f" - {p}")
    else:
        print("Nota: los archivos tv_channels_<locale>.json ya existían (no se tocaron).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
