#!/usr/bin/env python3
# GreekOS.py — single-file Greece map server for Termux/Linux/Desktop.
# No pip packages are required. Run: python3 GreekOS.py

from __future__ import annotations

import json
import math
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import hashlib
import mimetypes
import zipfile
import io
import uuid
import unicodedata
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APP_NAME = "GreekOS"
VERSION = "2.3.0-project"
DEFAULT_PORT = 17137
USER_AGENT = f"GreekOS/{VERSION} (local Greece map; contact via local user)"
ATHENS_CKAN = "https://opendata.cityofathens.gr"
ATHENS_DATASET = "wifi-highest-visitors-all-stations"
NOMINATIM = (os.environ.get("GREEKOS_NOMINATIM_URL") or "https://nominatim.openstreetmap.org").rstrip("/")
TRAFFIC_KEY = os.environ.get("GREEKOS_TOMTOM_API_KEY") or os.environ.get("TOMTOM_TRAFFIC_API_KEY") or ""
OSRM = (os.environ.get("GREEKOS_OSRM_URL") or "https://router.project-osrm.org").rstrip("/")
OVERPASS = "https://overpass-api.de/api/interpreter"
MAPLIBRE_JS_URL = "https://unpkg.com/maplibre-gl@6.9.1/dist/maplibre-gl.js"
MAPLIBRE_CSS_URL = "https://unpkg.com/maplibre-gl@6.9.1/dist/maplibre-gl.css"
GEONAMES_GR_URL = "https://download.geonames.org/export/dump/GR.zip"
FULL_MAP_RELEASE_TAG = "greek-map-packs"
FULL_MAP_FILENAME = "greece.mbtiles"
PACKAGE_RELEASE_TAG = "greek-map-packs"
PACKAGE_CATALOG_FILENAME = "map_packages.json"
FEATURED_PLACES = [
    ("athens", "Αθήνα", "Athens", 37.9838, 23.7275, 1),
    ("piraeus", "Πειραιάς", "Piraeus", 37.9420, 23.6469, 1),
    ("thessaloniki", "Θεσσαλονίκη", "Thessaloniki", 40.6401, 22.9444, 1),
    ("patras", "Πάτρα", "Patras", 38.2466, 21.7346, 1),
    ("heraklion", "Ηράκλειο", "Heraklion", 35.3387, 25.1442, 1),
    ("larissa", "Λάρισα", "Larissa", 39.6390, 22.4191, 1),
    ("volos", "Βόλος", "Volos", 39.3610, 22.9426, 1),
    ("ioannina", "Ιωάννινα", "Ioannina", 39.6650, 20.8537, 1),
    ("chania", "Χανιά", "Chania", 35.5138, 24.0180, 1),
    ("rhodes", "Ρόδος", "Rhodes", 36.4349, 28.2176, 1),
    ("corfu", "Κέρκυρα", "Corfu", 39.6243, 19.9217, 1),
    ("kavala", "Καβάλα", "Kavala", 40.9396, 24.4069, 2),
    ("alexandroupoli", "Αλεξανδρούπολη", "Alexandroupoli", 40.8457, 25.8744, 2),
    ("serres", "Σέρρες", "Serres", 41.0856, 23.5475, 2),
    ("drama", "Δράμα", "Drama", 41.1499, 24.1473, 2),
    ("kozani", "Κοζάνη", "Kozani", 40.3007, 21.7889, 2),
    ("katerini", "Κατερίνη", "Katerini", 40.2719, 22.5025, 2),
    ("trikala", "Τρίκαλα", "Trikala", 39.5553, 21.7679, 2),
    ("lamia", "Λαμία", "Lamia", 38.8993, 22.4341, 2),
    ("chalkida", "Χαλκίδα", "Chalkida", 38.4635, 23.6028, 2),
    ("agrinio", "Αγρίνιο", "Agrinio", 38.6214, 21.4078, 2),
    ("kalamata", "Καλαμάτα", "Kalamata", 37.0389, 22.1142, 2),
    ("tripoli", "Τρίπολη", "Tripoli", 37.5089, 22.3794, 2),
    ("nafplio", "Ναύπλιο", "Nafplio", 37.5673, 22.8016, 2),
    ("sparta", "Σπάρτη", "Sparta", 37.0745, 22.4303, 2),
    ("rethymno", "Ρέθυμνο", "Rethymno", 35.3656, 24.4822, 2),
    ("agios_nikolaos", "Άγιος Νικόλαος", "Agios Nikolaos", 35.1911, 25.7152, 2),
    ("mytilene", "Μυτιλήνη", "Mytilene", 39.1079, 26.5553, 2),
    ("chios", "Χίος", "Chios", 38.3687, 26.1350, 2),
    ("ermoupoli", "Ερμούπολη", "Ermoupoli", 37.4447, 24.9429, 2),
    ("fira", "Φηρά", "Fira", 36.4167, 25.4315, 2),
    ("mykonos", "Μύκονος", "Mykonos", 37.4467, 25.3289, 2),
    ("naxos", "Νάξος", "Naxos", 37.1036, 25.3764, 2),
    ("parikia", "Παροικιά", "Parikia", 37.0853, 25.1484, 2),
    ("zakynthos", "Ζάκυνθος", "Zakynthos", 37.7870, 20.8999, 2),
    ("argostoli", "Αργοστόλι", "Argostoli", 38.1754, 20.4890, 2),
    ("nea_makri", "Νέα Μάκρη", "Nea Makri", 38.0850, 23.9770, 3),
    ("kalambaka", "Καλαμπάκα", "Kalambaka", 39.7044, 21.6269, 3),
    ("metsovo", "Μέτσοβο", "Metsovo", 39.7694, 21.1828, 3),
    ("parga", "Πάργα", "Parga", 39.2859, 20.4009, 3),
    ("nafpaktos", "Ναύπακτος", "Nafpaktos", 38.3917, 21.8275, 3),
    ("monemvasia", "Μονεμβασιά", "Monemvasia", 36.6876, 23.0553, 3),
    ("arachova", "Αράχωβα", "Arachova", 38.4796, 22.5835, 3),
    ("meteora", "Μετέωρα", "Meteora", 39.7217, 21.6306, 3),
    ("olympia", "Ολυμπία", "Olympia", 37.6380, 21.6300, 3),
    ("delphi", "Δελφοί", "Delphi", 38.4824, 22.5010, 3),
]

WIFI_DATA_PLACES = {
    "athens": {"kind": "feed", "note": "City of Athens public aggregate Wi-Fi visitor feed"},
    "patras": {"kind": "dashboard", "note": "Public smart-city crowd/Wi-Fi dashboard"},
    "drama": {"kind": "dashboard", "note": "Public smart-city crowd/Wi-Fi dashboard"},
    "alexandroupoli": {"kind": "dashboard", "note": "Public smart-city crowd/Wi-Fi dashboard"},
    "lamia": {"kind": "system", "note": "Documented visitor analytics system"},
}

SCRIPT_DIR = Path(__file__).resolve().parent
FULL_MAP_SOURCE_FILE = SCRIPT_DIR / "full_map_source.json"
PACKAGE_CATALOG_FILE = SCRIPT_DIR / PACKAGE_CATALOG_FILENAME
PROJECT_RUNTIME = SCRIPT_DIR / "runtime"
PACKAGE_INSTALL_FILE = PROJECT_RUNTIME / "installed_package.json"
GREEKOS_HOME = Path(os.environ.get("GREEKOS_HOME") or PROJECT_RUNTIME).expanduser()
PACKAGE_INSTALL_FILE = GREEKOS_HOME / "installed_package.json"
PACKAGE_DOWNLOAD_DIR = GREEKOS_HOME / "package-downloads"
VENDOR_DIR = GREEKOS_HOME / "vendor"
HTTP_CACHE_DIR = GREEKOS_HOME / "http-cache"
DB_PATH = GREEKOS_HOME / "greekos.sqlite3"
for _dir in (GREEKOS_HOME, VENDOR_DIR, HTTP_CACHE_DIR, PACKAGE_DOWNLOAD_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
LOCAL_MBTILES = Path(os.environ.get("GREEKOS_MBTILES") or (GREEKOS_HOME / "greece.mbtiles")).expanduser()

PROXY_ALLOW_HOSTS = {
    "tiles.openfreemap.org",
    "tiles.mapterhorn.com",
    "unpkg.com",
    "api.tomtom.com",
    "router.project-osrm.org",
    "nominatim.openstreetmap.org",
    "opendata.cityofathens.gr",
    "download.geonames.org",
    "overpass-api.de",
}

_db_lock = threading.Lock()
_jobs_lock = threading.Lock()
_jobs: dict[str, dict] = {}
_network_lock = threading.Lock()
_network_offline_until: dict[str, float] = {}


def db_conn():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    with _db_lock:
        conn = db_conn()
        try:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                name TEXT,
                display_name TEXT,
                aliases TEXT,
                lat REAL,
                lon REAL,
                type TEXT,
                category TEXT,
                address_json TEXT,
                source TEXT,
                updated REAL
            );
            CREATE INDEX IF NOT EXISTS idx_places_name ON places(name);
            CREATE INDEX IF NOT EXISTS idx_places_display ON places(display_name);
            CREATE TABLE IF NOT EXISTS api_cache (
                key TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                created REAL NOT NULL
            );
            """)
            conn.commit()
        finally:
            conn.close()
    seed_featured_places()


def seed_featured_places():
    rows=[]
    now=time.time()
    for key, name_el, name_en, lat, lon, rank in FEATURED_PLACES:
        wifi=WIFI_DATA_PLACES.get(key)
        aliases=" ".join(dict.fromkeys([name_el, name_en, key.replace("_", " ")]))
        address={"country":"Greece","country_code":"gr","featured":True,"rank":rank}
        if wifi:
            address["wifi_data"] = wifi
        rows.append((f"featured:{key}",name_el,f"{name_el} / {name_en}, Greece",aliases,lat,lon,"city","place",json.dumps(address,ensure_ascii=False),"greekos-featured",now))
    with _db_lock:
        conn=db_conn()
        try:
            conn.executemany("""
            INSERT INTO places(key,name,display_name,aliases,lat,lon,type,category,address_json,source,updated)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(key) DO UPDATE SET name=excluded.name,display_name=excluded.display_name,aliases=excluded.aliases,lat=excluded.lat,lon=excluded.lon,type=excluded.type,category=excluded.category,address_json=excluded.address_json,source=excluded.source,updated=excluded.updated
            """, rows)
            conn.commit()
        finally:
            conn.close()


def api_cache_get(key: str, max_age: float | None = None):
    with _db_lock:
        conn = db_conn()
        try:
            row = conn.execute("SELECT payload, updated FROM api_cache WHERE key=?", (key,)).fetchone()
        finally:
            conn.close()
    if not row:
        return None
    if max_age is not None and time.time() - float(row["updated"]) > max_age:
        return None
    try:
        return json.loads(row["payload"])
    except Exception:
        return None


def api_cache_set(key: str, value):
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    with _db_lock:
        conn = db_conn()
        try:
            conn.execute(
                "INSERT INTO api_cache(key,payload,updated) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET payload=excluded.payload, updated=excluded.updated",
                (key, payload, time.time()),
            )
            conn.commit()
        finally:
            conn.close()


def remember_places(items, source="search"):
    rows = []
    for item in items or []:
        try:
            lat, lon = float(item.get("lat")), float(item.get("lon"))
        except Exception:
            continue
        name = str(item.get("name") or (item.get("display_name") or "").split(",")[0]).strip()
        display = str(item.get("display_name") or name).strip()
        aliases = " ".join(filter(None, [name, display, json.dumps(item.get("address") or {}, ensure_ascii=False)]))
        key = str(item.get("place_id") or f"{source}:{lat:.6f}:{lon:.6f}:{name.lower()}")
        rows.append((key, name, display, aliases, lat, lon, str(item.get("type") or ""), str(item.get("category") or ""), json.dumps(item.get("address") or {}, ensure_ascii=False), source, time.time()))
    if not rows:
        return
    with _db_lock:
        conn = db_conn()
        try:
            conn.executemany("""
            INSERT INTO places(key,name,display_name,aliases,lat,lon,type,category,address_json,source,updated)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(key) DO UPDATE SET name=excluded.name,display_name=excluded.display_name,aliases=excluded.aliases,
              lat=excluded.lat,lon=excluded.lon,type=excluded.type,category=excluded.category,address_json=excluded.address_json,
              source=excluded.source,updated=excluded.updated
            """, rows)
            conn.commit()
        finally:
            conn.close()


def _fold_text(value: str) -> str:
    text=unicodedata.normalize("NFKD", str(value or "")).casefold()
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def local_search_places(query: str, limit: int = 20):
    q = query.strip().lower()
    if not q:
        return []
    like = f"%{q}%"
    with _db_lock:
        conn = db_conn()
        try:
            rows = conn.execute("""
                SELECT name,display_name,lat,lon,type,category,address_json,source
                FROM places
                WHERE lower(name) LIKE ? OR lower(display_name) LIKE ? OR lower(aliases) LIKE ?
                ORDER BY CASE WHEN lower(name)=? THEN 0 WHEN lower(name) LIKE ? THEN 1 ELSE 2 END,
                         updated DESC
                LIMIT ?
            """, (like, like, like, q, q + "%", limit)).fetchall()
        finally:
            conn.close()
    if len(rows) < limit:
        # SQLite's built-in lower() is ASCII-oriented on many systems. Add a
        # Unicode/case/accent-insensitive pass over the compact built-in place list.
        folded=_fold_text(query)
        with _db_lock:
            conn=db_conn()
            try:
                extras=conn.execute("""
                    SELECT name,display_name,lat,lon,type,category,address_json,source,aliases
                    FROM places WHERE source='greekos-featured' LIMIT 200
                """).fetchall()
            finally:
                conn.close()
        seen={(float(r["lat"]),float(r["lon"]),str(r["name"])) for r in rows}
        matches=[]
        for r in extras:
            hay=_fold_text(" ".join([str(r["name"] or ""),str(r["display_name"] or ""),str(r["aliases"] or "")]))
            if folded and folded in hay:
                key=(float(r["lat"]),float(r["lon"]),str(r["name"]))
                if key not in seen:
                    matches.append(r); seen.add(key)
        rows=list(rows)+matches[:max(0,limit-len(rows))]
    out=[]
    for row in rows:
        try: address=json.loads(row["address_json"] or "{}")
        except Exception: address={}
        out.append({"display_name":row["display_name"],"name":row["name"],"lat":row["lat"],"lon":row["lon"],"type":row["type"],"category":row["category"],"addresstype":row["type"],"address":address,"boundingbox":[],"offline":True,"source":row["source"]})
    return out


def nearest_cached_place(lat: float, lon: float):
    # Fast approximate nearest search within ~0.5 degree, then exact distance.
    with _db_lock:
        conn = db_conn()
        try:
            rows = conn.execute("SELECT name,display_name,lat,lon,address_json FROM places WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ? LIMIT 500", (lat-.5, lat+.5, lon-.5, lon+.5)).fetchall()
        finally:
            conn.close()
    best=None
    for row in rows:
        d=(float(row["lat"])-lat)**2 + (float(row["lon"])-lon)**2
        if best is None or d<best[0]: best=(d,row)
    if not best: return None
    row=best[1]
    return {"display_name":row["display_name"],"name":row["name"],"lat":row["lat"],"lon":row["lon"]}


def _http_cache_paths(url: str):
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return HTTP_CACHE_DIR / (digest + ".bin"), HTTP_CACHE_DIR / (digest + ".json")


def disk_http_get(url: str, *, accept="*/*", timeout=25, max_age: float | None = None, allow_stale=True):
    data_path, meta_path = _http_cache_paths(url)
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    cached = None
    meta = {}
    if data_path.exists() and meta_path.exists():
        try:
            cached = data_path.read_bytes()
            meta = json.loads(meta_path.read_text("utf-8"))
        except Exception:
            cached = None
            meta = {}
    fresh = cached is not None and (max_age is None or time.time() - float(meta.get("saved", 0)) <= max_age)
    if fresh:
        return cached, str(meta.get("content_type") or "application/octet-stream"), True
    with _network_lock:
        offline_now = time.time() < _network_offline_until.get(host, 0.0)
    if offline_now:
        if cached is not None and allow_stale:
            return cached, str(meta.get("content_type") or "application/octet-stream"), True
        raise urllib.error.URLError("GreekOS network circuit is temporarily offline")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept, "Accept-Language": "el,en;q=0.8"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
            ctype = response.headers.get_content_type() or "application/octet-stream"
            charset = response.headers.get_content_charset()
            if charset and ctype.startswith("text/"):
                ctype += f"; charset={charset}"
        tmp = data_path.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(data_path)
        meta_path.write_text(json.dumps({"saved":time.time(),"content_type":ctype}, separators=(",",":")), "utf-8")
        with _network_lock:
            _network_offline_until.pop(host, None)
        return data, ctype, False
    except Exception:
        with _network_lock:
            _network_offline_until[host] = time.time() + 8.0
        if cached is not None and allow_stale:
            return cached, str(meta.get("content_type") or "application/octet-stream"), True
        raise


def find_installed_maplibre_asset(name: str):
    candidates=[SCRIPT_DIR / "runtime" / "vendor" / name]
    env_dir=os.environ.get("GREEKOS_MAPLIBRE_DIR")
    if env_dir: candidates.append(Path(env_dir)/name)
    candidates += [Path.cwd()/"node_modules"/"maplibre-gl"/"dist"/name]
    try:
        npm=shutil.which("npm")
        if npm:
            root=subprocess.check_output([npm,"root","-g"],text=True,stderr=subprocess.DEVNULL,timeout=3).strip()
            if root: candidates.append(Path(root)/"maplibre-gl"/"dist"/name)
    except Exception:
        pass
    for c in candidates:
        try:
            if c.exists() and c.stat().st_size > 1024: return c
        except OSError: pass
    return None


def ensure_vendor_asset(name: str, url: str):
    path = VENDOR_DIR / name
    if path.exists() and path.stat().st_size > 1024:
        return path
    installed=find_installed_maplibre_asset(name)
    if installed:
        try:
            shutil.copy2(installed,path)
            return path
        except Exception:
            return installed
    try:
        data, _, _ = disk_http_get(url, timeout=15, max_age=30*24*3600)
        path.write_bytes(data)
    except Exception:
        pass
    return path


def mbtiles_metadata():
    if not LOCAL_MBTILES.exists(): return None
    try:
        conn=sqlite3.connect(LOCAL_MBTILES)
        rows=dict(conn.execute("SELECT name,value FROM metadata").fetchall())
        conn.close()
        fmt=(rows.get("format") or "pbf").lower()
        return {"format":fmt,"minzoom":int(rows.get("minzoom") or 0),"maxzoom":int(rows.get("maxzoom") or 14),"bounds":rows.get("bounds") or "18.0,34.5,30.0,42.3","name":rows.get("name") or "GreekOS local Greece"}
    except Exception:
        return None


def mbtiles_tile(z:int,x:int,y:int):
    meta=mbtiles_metadata()
    if not meta: return None,None,None
    tms_y=(1<<z)-1-y
    conn=sqlite3.connect(LOCAL_MBTILES)
    try:
        row=conn.execute("SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",(z,x,tms_y)).fetchone()
    finally:
        conn.close()
    if not row: return None,None,None
    data=bytes(row[0]); fmt=meta["format"]
    ctype={"pbf":"application/x-protobuf","mvt":"application/x-protobuf","png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","webp":"image/webp"}.get(fmt,"application/octet-stream")
    enc="gzip" if data[:2]==b"\x1f\x8b" else None
    return data,ctype,enc


def warm_core_assets():
    """Populate small app/style assets so a later offline launch can still start."""
    ensure_vendor_asset("maplibre-gl.js", MAPLIBRE_JS_URL)
    ensure_vendor_asset("maplibre-gl.css", MAPLIBRE_CSS_URL)
    for style_url in ("https://tiles.openfreemap.org/styles/dark", "https://tiles.openfreemap.org/styles/bright"):
        try:
            raw, _, _ = disk_http_get(style_url, accept="application/json", timeout=15, max_age=7*24*3600)
            style = json.loads(raw.decode("utf-8", "replace"))
            # Cache source TileJSON documents.
            for source in (style.get("sources") or {}).values():
                if isinstance(source, dict) and str(source.get("url") or "").startswith("http"):
                    try: disk_http_get(str(source["url"]), accept="application/json", timeout=12, max_age=7*24*3600)
                    except Exception: pass
            # Cache sprite sheets used by the base styles.
            sprite = style.get("sprite")
            if isinstance(sprite, str) and sprite.startswith("http"):
                for suffix in (".json", ".png", "@2x.json", "@2x.png"):
                    try: disk_http_get(sprite + suffix, timeout=12, max_age=30*24*3600)
                    except Exception: pass
            # Cache common Latin + Greek glyph ranges for fonts used in the style.
            glyphs = style.get("glyphs")
            if isinstance(glyphs, str) and glyphs.startswith("http"):
                fonts=set()
                for layer in style.get("layers") or []:
                    layout=(layer or {}).get("layout") or {}
                    f=layout.get("text-font")
                    if isinstance(f, list):
                        for name in f:
                            if isinstance(name, str): fonts.add(name)
                fonts.update({"Noto Sans Regular", "Noto Sans Bold"})
                for font in list(fonts)[:12]:
                    for rng in ("0-255", "256-511", "768-1023"):
                        url=glyphs.replace("{fontstack}", urllib.parse.quote(font, safe="")).replace("{range}", rng)
                        try: disk_http_get(url, timeout=12, max_age=90*24*3600)
                        except Exception: pass
        except Exception:
            continue
    try: disk_http_get("https://tiles.mapterhorn.com/tilejson.json", accept="application/json", timeout=12, max_age=7*24*3600)
    except Exception: pass


def cache_stats():
    total=0; count=0
    for f in HTTP_CACHE_DIR.glob("*.bin"):
        try: total += f.stat().st_size; count += 1
        except OSError: pass
    return {"files":count,"bytes":total,"megabytes":round(total/1024/1024,1)}


def xyz_range(west, south, east, north, z):
    n = 2 ** z
    def xt(lon): return int((lon + 180.0) / 360.0 * n)
    def yt(lat):
        lat=max(min(lat,85.05112878),-85.05112878)
        r=math.radians(lat)
        return int((1.0 - math.asinh(math.tan(r))/math.pi)/2.0*n)
    x0,x1=sorted((max(0,min(n-1,xt(west))),max(0,min(n-1,xt(east)))))
    y0,y1=sorted((max(0,min(n-1,yt(north))),max(0,min(n-1,yt(south)))))
    return range(x0,x1+1), range(y0,y1+1)


def cache_bbox_places(west: float, south: float, east: float, north: float):
    """Cache searchable POIs/shops/addresses for a small saved offline area."""
    if east - west > 1.2 or north - south > 1.2:
        return 0
    bbox=f"{south:.6f},{west:.6f},{north:.6f},{east:.6f}"
    query=("[out:json][timeout:35];("
           f'nwr["shop"]({bbox});'
           f'nwr["amenity"]({bbox});'
           f'nwr["tourism"]({bbox});'
           f'nwr["office"]({bbox});'
           f'nwr["healthcare"]({bbox});'
           f'nwr["addr:housenumber"]({bbox});'
           ");out center tags;")
    try:
        url=OVERPASS+"?"+urllib.parse.urlencode({"data":query})
        data=http_json(url, timeout=45, max_age=30*24*3600)
    except Exception:
        return 0
    items=[]
    for el in data.get("elements") or []:
        tags=el.get("tags") or {}
        lat=el.get("lat"); lon=el.get("lon")
        if lat is None or lon is None:
            center=el.get("center") or {}; lat=center.get("lat"); lon=center.get("lon")
        try: lat=float(lat); lon=float(lon)
        except Exception: continue
        name=tags.get("name:el") or tags.get("name") or tags.get("name:en")
        street=tags.get("addr:street") or tags.get("addr:place") or ""
        number=tags.get("addr:housenumber") or ""
        if not name:
            name=(street+" "+number).strip()
        if not name: continue
        city=tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:village") or ""
        category=""
        typ=""
        for k in ("shop","amenity","tourism","office","healthcare","leisure","craft"):
            if tags.get(k): category=k; typ=str(tags.get(k)); break
        if not typ and number: category="address"; typ="house"
        address={k[5:]:v for k,v in tags.items() if k.startswith("addr:")}
        display=", ".join(x for x in [name, (street+" "+number).strip() if (street or number) and name!=(street+" "+number).strip() else "", city, "Greece"] if x)
        items.append({"place_id":f"osm:{el.get('type')}:{el.get('id')}","name":name,"display_name":display,"lat":lat,"lon":lon,"type":typ,"category":category,"address":address})
    remember_places(items,"overpass-offline-pack")
    return len(items)


def discover_tile_template(tilejson_url: str):
    raw, _, _ = disk_http_get(tilejson_url, accept="application/json", timeout=20, max_age=7*24*3600)
    obj=json.loads(raw.decode("utf-8","replace"))
    tiles=obj.get("tiles") or []
    return str(tiles[0]) if tiles else None


def _github_repo_slug():
    env=(os.environ.get("GITHUB_REPOSITORY") or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", env):
        return env
    try:
        remote=subprocess.check_output(["git","-C",str(SCRIPT_DIR.parent.parent),"config","--get","remote.origin.url"],text=True,stderr=subprocess.DEVNULL,timeout=3).strip()
        m=re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", remote)
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""



def load_package_catalog():
    default={
        "schema":1,
        "release_tag":PACKAGE_RELEASE_TAG,
        "chunk_mib":128,
        "tiers":[
            {"id":"lite","label":"Lite","target_gb":10,"manifest_asset":"greek-map-lite-manifest.json","description":"Core offline Greece map, roads, places and addresses."},
            {"id":"standard","label":"Standard","target_gb":15,"manifest_asset":"greek-map-standard-manifest.json","description":"More local detail and offline coverage."},
            {"id":"enhanced","label":"Enhanced","target_gb":20,"manifest_asset":"greek-map-enhanced-manifest.json","description":"Higher-detail buildings, roads and POIs."},
            {"id":"detailed","label":"Detailed","target_gb":25,"manifest_asset":"greek-map-detailed-manifest.json","description":"Denser local detail for more of Greece."},
            {"id":"full","label":"Full","target_gb":30,"manifest_asset":"greek-map-full-manifest.json","description":"Maximum offline package published for Greek Map."},
        ],
    }
    try:
        if PACKAGE_CATALOG_FILE.exists():
            data=json.loads(PACKAGE_CATALOG_FILE.read_text(encoding="utf-8"))
            if isinstance(data,dict) and isinstance(data.get("tiers"),list):
                return data
    except Exception:
        pass
    return default


def _catalog_tier(tier_id: str):
    for tier in load_package_catalog().get("tiers",[]):
        if str(tier.get("id")) == str(tier_id):
            return tier
    return None


def _release_asset_url(asset_name: str, tag: str | None = None):
    slug=_github_repo_slug()
    if not slug or not asset_name:
        return ""
    return f"https://github.com/{slug}/releases/download/{tag or PACKAGE_RELEASE_TAG}/{asset_name}"


def package_manifest_url(tier_id: str):
    tier=_catalog_tier(tier_id)
    if not tier:
        return ""
    explicit=str(tier.get("manifest_url") or "").strip()
    if explicit:
        return explicit
    tag=str(load_package_catalog().get("release_tag") or PACKAGE_RELEASE_TAG)
    return _release_asset_url(str(tier.get("manifest_asset") or f"greek-map-{tier_id}-manifest.json"), tag)


def installed_package_info():
    try:
        if PACKAGE_INSTALL_FILE.exists():
            data=json.loads(PACKAGE_INSTALL_FILE.read_text(encoding="utf-8"))
            if isinstance(data,dict):
                return data
    except Exception:
        pass
    return {}


def package_catalog_info():
    installed=installed_package_info()
    out=[]
    for tier in load_package_catalog().get("tiers",[]):
        t=dict(tier)
        t["manifest_url"]=package_manifest_url(str(t.get("id") or ""))
        t["installed"]=bool(installed.get("tier") == t.get("id") and LOCAL_MBTILES.exists())
        out.append(t)
    return {"tiers":out,"installed":installed,"chunk_mib":load_package_catalog().get("chunk_mib",128)}


def _read_remote_json(url: str):
    data,ctype,_stale=disk_http_get(url, accept="application/json", timeout=35, max_age=3600)
    return json.loads(data.decode("utf-8"))


def _sha256_file(path: Path, chunk_size=4*1024*1024):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(chunk_size),b""):
            h.update(b)
    return h.hexdigest()


def _download_one_chunk(url: str, part_path: Path, expected_size: int, job_id: str, base_done: int, total_bytes: int):
    part_path.parent.mkdir(parents=True,exist_ok=True)
    attempt=0
    while attempt < 6:
        attempt += 1
        existing=part_path.stat().st_size if part_path.exists() else 0
        if expected_size and existing > expected_size:
            part_path.unlink(missing_ok=True); existing=0
        headers={"User-Agent":USER_AGENT,"Accept":"application/octet-stream"}
        if existing:
            headers["Range"]=f"bytes={existing}-"
        try:
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=60) as r:
                code=getattr(r,"status",200)
                if existing and code != 206:
                    part_path.unlink(missing_ok=True); existing=0
                mode="ab" if existing else "wb"
                started=time.time(); start_bytes=existing; last=0.0
                with part_path.open(mode) as f:
                    while True:
                        b=r.read(1024*1024)
                        if not b: break
                        f.write(b)
                        now=time.time()
                        if now-last >= .15:
                            cur=part_path.stat().st_size
                            overall=base_done+cur
                            elapsed=max(.001,now-started)
                            speed=int(max(0,(cur-start_bytes)/elapsed))
                            pct=(overall*100/total_bytes) if total_bytes else 0.0
                            with _jobs_lock:
                                _jobs[job_id].update(status="running",doneBytes=overall,totalBytes=total_bytes,percent=round(min(100,pct),1),speedBps=speed)
                            last=now
                if expected_size and part_path.stat().st_size != expected_size:
                    raise RuntimeError(f"chunk size mismatch ({part_path.stat().st_size}/{expected_size})")
                return
        except Exception:
            if attempt >= 6:
                raise
            time.sleep(min(12,1.5*attempt))


def package_download_job(job_id: str, tier_id: str):
    tier=_catalog_tier(tier_id)
    try:
        if not tier:
            raise RuntimeError("unknown map package tier")
        manifest_url=package_manifest_url(tier_id)
        if not manifest_url:
            raise RuntimeError("package manifest URL is not available for this repository")
        manifest=_read_remote_json(manifest_url)
        chunks=manifest.get("chunks") or []
        if not isinstance(chunks,list) or not chunks:
            raise RuntimeError("package manifest has no chunks")
        if len(chunks) > 1000:
            raise RuntimeError("package has too many chunks")
        release_tag=str(manifest.get("release_tag") or load_package_catalog().get("release_tag") or PACKAGE_RELEASE_TAG)
        total_bytes=int(manifest.get("final_bytes") or sum(int(c.get("bytes") or 0) for c in chunks))
        expected_final_sha=str(manifest.get("final_sha256") or "").lower()
        assembly=GREEKOS_HOME / f"greece-{tier_id}.mbtiles.assembling"
        state_path=GREEKOS_HOME / f"greece-{tier_id}.download-state.json"
        # If the weekly package changed while a user had a partial download,
        # never append new chunks to an old assembly. Start clean instead.
        try:
            old_state=json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        except Exception:
            old_state={}
        if assembly.exists() and old_state and (
            (old_state.get("final_sha256") and expected_final_sha and old_state.get("final_sha256") != expected_final_sha)
            or (old_state.get("total_bytes") and int(old_state.get("total_bytes")) != total_bytes)
        ):
            assembly.unlink(missing_ok=True)
            shutil.rmtree(PACKAGE_DOWNLOAD_DIR / tier_id, ignore_errors=True)
            state_path.unlink(missing_ok=True)
        # Determine how many complete chunk boundaries are already assembled.
        assembled=assembly.stat().st_size if assembly.exists() else 0
        boundary=0; next_index=0
        for i,c in enumerate(chunks):
            sz=int(c.get("bytes") or 0)
            if assembled == boundary:
                next_index=i; break
            if assembled == boundary+sz:
                boundary += sz; next_index=i+1; continue
            if assembled < boundary+sz:
                # Never trust a partial append; truncate back to last verified boundary.
                with assembly.open("r+b") as f: f.truncate(boundary)
                assembled=boundary; next_index=i; break
            boundary += sz; next_index=i+1
        if assembled > boundary and next_index >= len(chunks):
            with assembly.open("r+b") as f: f.truncate(boundary)
            assembled=boundary
        done_bytes=assembly.stat().st_size if assembly.exists() else 0
        with _jobs_lock:
            _jobs[job_id].update(status="running",tier=tier_id,totalBytes=total_bytes,doneBytes=done_bytes,percent=round(done_bytes*100/total_bytes,1) if total_bytes else 0.0,currentChunk=next_index+1,totalChunks=len(chunks))
        for i in range(next_index,len(chunks)):
            c=chunks[i]
            name=str(c.get("name") or f"greek-map-{tier_id}.part{i:04d}")
            size=int(c.get("bytes") or 0)
            sha=str(c.get("sha256") or "").lower()
            url=str(c.get("url") or "").strip() or _release_asset_url(name,release_tag)
            if not url:
                raise RuntimeError(f"missing URL for chunk {name}")
            part=PACKAGE_DOWNLOAD_DIR / tier_id / (name+".part")
            base_done=assembly.stat().st_size if assembly.exists() else 0
            with _jobs_lock:
                _jobs[job_id].update(currentChunk=i+1,totalChunks=len(chunks),message=name)
            _download_one_chunk(url,part,size,job_id,base_done,total_bytes)
            if sha and _sha256_file(part) != sha:
                part.unlink(missing_ok=True)
                raise RuntimeError(f"checksum failed for {name}")
            with assembly.open("ab") as out, part.open("rb") as src:
                shutil.copyfileobj(src,out,1024*1024)
                out.flush(); os.fsync(out.fileno())
            part.unlink(missing_ok=True)
            state={"tier":tier_id,"next_chunk":i+1,"assembled_bytes":assembly.stat().st_size,"final_sha256":expected_final_sha,"total_bytes":total_bytes,"updated":time.time()}
            state_path.write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
        if total_bytes and assembly.stat().st_size != total_bytes:
            raise RuntimeError(f"assembled size mismatch ({assembly.stat().st_size}/{total_bytes})")
        if expected_final_sha and _sha256_file(assembly) != expected_final_sha:
            raise RuntimeError("final package checksum failed")
        # Basic MBTiles validation before replacing a working install.
        test=sqlite3.connect(assembly)
        try:
            test.execute("SELECT 1 FROM metadata LIMIT 1").fetchone()
            test.execute("SELECT 1 FROM tiles LIMIT 1").fetchone()
        finally:
            test.close()
        os.replace(assembly,LOCAL_MBTILES)
        state_path.unlink(missing_ok=True)
        info={"tier":tier_id,"label":tier.get("label"),"target_gb":tier.get("target_gb"),"bytes":LOCAL_MBTILES.stat().st_size,"installed_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"manifest_url":manifest_url}
        PACKAGE_INSTALL_FILE.write_text(json.dumps(info,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        with _jobs_lock:
            _jobs[job_id].update(status="done",doneBytes=LOCAL_MBTILES.stat().st_size,totalBytes=LOCAL_MBTILES.stat().st_size,percent=100.0,speedBps=0,message="")
    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id].update(status="error",message=str(exc))


def start_package_download(tier_id: str):
    tier_id=str(tier_id or "").strip().lower()
    if not _catalog_tier(tier_id):
        return {"status":"error","message":"unknown package tier"}
    with _jobs_lock:
        for job in _jobs.values():
            if job.get("kind")=="package" and job.get("status") in {"queued","running"}:
                return dict(job)
        job_id=uuid.uuid4().hex[:10]
        _jobs[job_id]={"id":job_id,"kind":"package","tier":tier_id,"status":"queued","doneBytes":0,"totalBytes":0,"percent":0.0,"speedBps":0,"message":"","currentChunk":0,"totalChunks":0}
    threading.Thread(target=package_download_job,args=(job_id,tier_id),daemon=True).start()
    return get_job(job_id)

def full_map_download_url():
    explicit=(os.environ.get("GREEKOS_FULL_MAP_URL") or "").strip()
    if explicit:
        return explicit
    try:
        if FULL_MAP_SOURCE_FILE.exists():
            data=json.loads(FULL_MAP_SOURCE_FILE.read_text(encoding="utf-8"))
            url=str(data.get("url") or "").strip()
            if url:
                return url
    except Exception:
        pass
    slug=_github_repo_slug()
    if slug:
        return f"https://github.com/{slug}/releases/download/{FULL_MAP_RELEASE_TAG}/{FULL_MAP_FILENAME}"
    return ""


def full_map_info():
    meta=mbtiles_metadata()
    size=LOCAL_MBTILES.stat().st_size if LOCAL_MBTILES.exists() else 0
    return {
        "installed": bool(meta),
        "path": str(LOCAL_MBTILES),
        "bytes": size,
        "megabytes": round(size/1024/1024,1),
        "metadata": meta,
        "downloadAvailable": bool(full_map_download_url()),
        "source": full_map_download_url(),
    }


def full_map_download_job(job_id: str):
    url=full_map_download_url()
    part=LOCAL_MBTILES.with_suffix(LOCAL_MBTILES.suffix+".part")
    try:
        if not url:
            raise RuntimeError("full Greece map package URL is not configured yet")
        LOCAL_MBTILES.parent.mkdir(parents=True,exist_ok=True)
        existing=part.stat().st_size if part.exists() else 0
        headers={"User-Agent":USER_AGENT,"Accept":"application/octet-stream"}
        if existing>0:
            headers["Range"]=f"bytes={existing}-"
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=45) as r:
            code=getattr(r,"status",200)
            if existing and code != 206:
                existing=0
                try: part.unlink()
                except OSError: pass
            clen=int(r.headers.get("Content-Length") or 0)
            total=clen+existing if clen else 0
            mode="ab" if existing else "wb"
            done=existing
            started=time.time()
            last=time.time()
            with part.open(mode) as f:
                while True:
                    chunk=r.read(1024*1024)
                    if not chunk: break
                    f.write(chunk); done += len(chunk)
                    now=time.time()
                    if now-last >= .15:
                        elapsed=max(.001,now-started)
                        pct=(done*100/total) if total else 0.0
                        with _jobs_lock:
                            _jobs[job_id].update(status="running",doneBytes=done,totalBytes=total,percent=round(min(100,pct),1),speedBps=int(max(0,(done-existing)/elapsed)))
                        last=now
        if total and done < total:
            raise RuntimeError(f"download incomplete ({done}/{total} bytes)")
        # Basic validation before replacing a working map.
        test=sqlite3.connect(part)
        try:
            test.execute("SELECT 1 FROM metadata LIMIT 1").fetchone()
            test.execute("SELECT 1 FROM tiles LIMIT 1").fetchone()
        finally:
            test.close()
        os.replace(part,LOCAL_MBTILES)
        meta=mbtiles_metadata()
        if not meta:
            raise RuntimeError("downloaded file is not a valid MBTiles map")
        with _jobs_lock:
            _jobs[job_id].update(status="done",doneBytes=done,totalBytes=done,percent=100.0,speedBps=0,message="")
    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id].update(status="error",message=str(exc))


def start_full_map_download():
    # Reuse an active full-map job instead of starting duplicates.
    with _jobs_lock:
        for job in _jobs.values():
            if job.get("kind")=="full-map" and job.get("status") in {"queued","running"}:
                return dict(job)
        job_id=uuid.uuid4().hex[:10]
        _jobs[job_id]={"id":job_id,"kind":"full-map","status":"queued","doneBytes":0,"totalBytes":0,"percent":0.0,"speedBps":0,"message":""}
    threading.Thread(target=full_map_download_job,args=(job_id,),daemon=True).start()
    return get_job(job_id)


def preload_area_job(job_id: str, bounds, zmin: int, zmax: int):
    west,south,east,north=bounds
    try:
        vector_tpl=discover_tile_template("https://tiles.openfreemap.org/planet")
        terrain_tpl=discover_tile_template("https://tiles.mapterhorn.com/tilejson.json")
        tasks=[]
        for z in range(zmin,zmax+1):
            xs,ys=xyz_range(west,south,east,north,z)
            for x in xs:
                for y in ys:
                    if vector_tpl: tasks.append(vector_tpl.replace("{z}",str(z)).replace("{x}",str(x)).replace("{y}",str(y)))
                    if terrain_tpl and z <= 14: tasks.append(terrain_tpl.replace("{z}",str(z)).replace("{x}",str(x)).replace("{y}",str(y)))
        # Avoid accidental multi-gigabyte downloads from a huge viewport.
        if len(tasks) > 1800:
            raise RuntimeError(f"offline area too large ({len(tasks)} tiles); zoom in or use fewer zoom levels")
        with _jobs_lock:
            _jobs[job_id].update(total=len(tasks),status="running")
        for i,url in enumerate(tasks,1):
            try: disk_http_get(url, timeout=20, max_age=30*24*3600)
            except Exception:
                with _jobs_lock: _jobs[job_id]["errors"] += 1
            with _jobs_lock: _jobs[job_id]["done"] = i
        indexed = cache_bbox_places(west, south, east, north)
        with _jobs_lock:
            _jobs[job_id]["status"]="done"
            _jobs[job_id]["indexedPlaces"] = indexed
    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id]["status"]="error"; _jobs[job_id]["message"]=str(exc)


def start_preload(bounds, zmin, zmax):
    job_id=uuid.uuid4().hex[:10]
    with _jobs_lock:
        _jobs[job_id]={"id":job_id,"status":"queued","done":0,"total":0,"errors":0,"message":""}
    threading.Thread(target=preload_area_job,args=(job_id,bounds,zmin,zmax),daemon=True).start()
    return _jobs[job_id].copy()


def get_job(job_id):
    with _jobs_lock: return dict(_jobs.get(job_id) or {})

_cache_lock = threading.Lock()
_cache: dict[str, tuple[float, object]] = {}
_nominatim_lock = threading.Lock()
_nominatim_last = 0.0


def cache_get(key: str, ttl: float):
    with _cache_lock:
        item = _cache.get(key)
        if not item:
            return None
        stamp, value = item
        if time.time() - stamp > ttl:
            _cache.pop(key, None)
            return None
        return value


def cache_set(key: str, value):
    with _cache_lock:
        _cache[key] = (time.time(), value)


def http_get(url: str, *, accept: str = "application/json", timeout: int = 25, max_age: float | None = 3 * 3600) -> bytes:
    data, _ctype, _stale = disk_http_get(url, accept=accept, timeout=timeout, max_age=max_age)
    return data


def http_json(url: str, timeout: int = 25, max_age: float | None = 3 * 3600):
    return json.loads(http_get(url, timeout=timeout, max_age=max_age).decode("utf-8", "replace"))


def ckan_action(action: str, **params):
    query = urllib.parse.urlencode({k: str(v) for k, v in params.items()})
    body = http_json(f"{ATHENS_CKAN}/api/3/action/{action}?{query}")
    if not body.get("success"):
        raise RuntimeError(f"CKAN {action} returned success=false")
    return body.get("result") or {}


def fetch_datastore(resource_id: str):
    records = []
    offset = 0
    total = 1
    for _ in range(20):
        if offset >= total:
            break
        result = ckan_action("datastore_search", resource_id=resource_id, limit=5000, offset=offset)
        batch = result.get("records") or []
        records.extend(batch)
        total = int(result.get("total") or len(records))
        if not batch:
            break
        offset += len(batch)
    return records


def normalize_records_container(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("records", "data", "results"):
            if isinstance(payload.get(key), list):
                return payload[key]
        result = payload.get("result")
        if isinstance(result, dict) and isinstance(result.get("records"), list):
            return result["records"]
    return []


def fetch_resource_records(resource: dict):
    if resource.get("datastore_active") and resource.get("id"):
        return fetch_datastore(str(resource["id"]))
    url = resource.get("url")
    if not url:
        raise RuntimeError("Athens JSON resource URL missing")
    raw = http_get(urllib.parse.urljoin(ATHENS_CKAN, str(url)), accept="application/json,text/plain,*/*")
    text = raw.decode("utf-8", "replace")
    try:
        return normalize_records_container(json.loads(text))
    except Exception:
        out = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
        return out


def find_key(record: dict, patterns):
    for pattern in patterns:
        rx = re.compile(pattern, re.I)
        for key in record.keys():
            if rx.search(str(key)):
                return key
    return None


def to_number(value):
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return None


def normalize_date(value):
    if value in (None, ""):
        return None
    text = str(value).strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return None


def record_coordinate(record: dict):
    lat_key = find_key(record, [r"^lat$", r"latitude", r"y_?coord"])
    lon_key = find_key(record, [r"^lon$", r"^lng$", r"longitude", r"x_?coord"])
    lat = to_number(record.get(lat_key)) if lat_key else None
    lon = to_number(record.get(lon_key)) if lon_key else None
    if lat is not None and lon is not None and 37 < lat < 39 and 22 < lon < 25:
        return [lon, lat]
    return None


def normalize_tracking_record(record: dict):
    station_key = find_key(record, [r"^station_?id$", r"station.*id", r"^id_?station", r"wifi.*station.*id"])
    date_key = find_key(record, [r"^date$", r"measurement.*date", r"record.*date", r"datum", r"ημερομην", r"^day$", r"timestamp", r"datetime"])
    name_key = find_key(record, [r"station.*name", r"location.*name", r"^name$", r"title", r"σημειο", r"σταθμ"])
    value_key = find_key(record, [r"highest.*visitor", r"max.*visitor", r"unique.*visitor", r"visitor.*count", r"visitors", r"device.*count", r"traffic", r"επισκεψ", r"συσκευ", r"^count$", r"^value$"])
    station_id = to_number(record.get(station_key)) if station_key else None
    date = normalize_date(record.get(date_key)) if date_key else None
    value = to_number(record.get(value_key)) if value_key else None
    if station_id is None or date is None or value is None:
        return None
    return {
        "stationId": int(station_id),
        "date": date,
        "value": value,
        "name": str(record.get(name_key) or "") if name_key else "",
        "coordinate": record_coordinate(record),
    }


def station_id_from_package(pkg: dict):
    text = f"{pkg.get('name','')} {pkg.get('title','')} {pkg.get('notes','')}"
    m = re.search(r"station[_\s-]*id\s*[:=]?\s*(\d{1,4})", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"visitors-(\d{2,4})-", str(pkg.get("name") or ""), re.I)
    return int(m.group(1)) if m else None


def station_name_from_package(pkg: dict):
    title = str(pkg.get("title") or "")
    parts = re.split(r"\s+[—–-]\s+", title)
    return (parts[-1] if parts else title).strip() or str(pkg.get("name") or "")


def geo_point_from_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text or not ("coordinates" in text or text.startswith("{") or text.startswith("[")):
            return None
        try:
            return geo_point_from_value(json.loads(text))
        except Exception:
            return None
    if isinstance(value, list):
        if len(value) >= 2 and all(isinstance(x, (int, float)) for x in value[:2]):
            lon, lat = float(value[0]), float(value[1])
            if 22 < lon < 25 and 37 < lat < 39:
                return [lon, lat]
        for item in value:
            point = geo_point_from_value(item)
            if point:
                return point
        return None
    if not isinstance(value, dict):
        return None
    if value.get("type") == "Point":
        return geo_point_from_value(value.get("coordinates"))
    if value.get("type") in ("Polygon", "MultiPolygon"):
        coords = []
        def collect(node):
            if isinstance(node, list) and len(node) >= 2 and all(isinstance(v, (int, float)) for v in node[:2]):
                lon, lat = float(node[0]), float(node[1])
                if 22 < lon < 25 and 37 < lat < 39:
                    coords.append([lon, lat])
            elif isinstance(node, list):
                for child in node:
                    collect(child)
        collect(value.get("coordinates"))
        if coords:
            return [(min(x[0] for x in coords) + max(x[0] for x in coords)) / 2,
                    (min(x[1] for x in coords) + max(x[1] for x in coords)) / 2]
    preferred = [v for k, v in value.items() if re.search(r"centroid|spatial|geometry|geom|coordinate", str(k), re.I)]
    for child in preferred + list(value.values()):
        point = geo_point_from_value(child)
        if point:
            return point
    return None


def geo_point_from_package(pkg: dict):
    extras = pkg.get("extras") if isinstance(pkg.get("extras"), list) else []
    for extra in extras:
        if re.search(r"centroid|spatial|geometry|geom", str(extra.get("key") or ""), re.I):
            point = geo_point_from_value(extra.get("value"))
            if point:
                return point
    return geo_point_from_value(pkg)


def get_athens_wifi():
    cached = cache_get("athens-wifi", 15 * 60)
    if cached is not None:
        return cached

    all_pkg = ckan_action("package_show", id=ATHENS_DATASET)
    search = ckan_action("package_search", fq="tags:highest-visitors", rows=120)
    resources = all_pkg.get("resources") or []
    resource = next((x for x in resources if str(x.get("format") or "").upper() == "JSON"), resources[0] if resources else None)
    if not resource:
        raise RuntimeError("Athens all-stations resource not found")

    records = []
    for raw in fetch_resource_records(resource):
        if isinstance(raw, dict):
            item = normalize_tracking_record(raw)
            if item:
                records.append(item)
    if not records:
        raise RuntimeError("Athens Wi-Fi feed returned no usable records")

    stations = {}
    for pkg in search.get("results") or []:
        if pkg.get("name") == ATHENS_DATASET or re.search(r"all-stations", str(pkg.get("name") or ""), re.I):
            continue
        station_id = station_id_from_package(pkg)
        if station_id is None:
            continue
        stations[station_id] = {
            "stationId": station_id,
            "name": station_name_from_package(pkg),
            "coordinate": geo_point_from_package(pkg),
        }
    for rec in records:
        station = stations.get(rec["stationId"]) or {
            "stationId": rec["stationId"],
            "name": rec.get("name") or f"Station {rec['stationId']}",
            "coordinate": None,
        }
        if not station.get("name") and rec.get("name"):
            station["name"] = rec["name"]
        if not station.get("coordinate") and rec.get("coordinate"):
            station["coordinate"] = rec["coordinate"]
        stations[rec["stationId"]] = station

    dates = sorted(set(rec["date"] for rec in records))
    result = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": f"{ATHENS_CKAN}/dataset/{ATHENS_DATASET}",
        "dates": dates,
        "stations": list(stations.values()),
        "records": records,
    }
    cache_set("athens-wifi", result)
    return result


def nominatim_throttle():
    global _nominatim_last
    with _nominatim_lock:
        delay = 1.05 - (time.monotonic() - _nominatim_last)
        if delay > 0:
            time.sleep(delay)
        _nominatim_last = time.monotonic()


def search_greece(query: str, lang: str = "el"):
    key = f"search:{lang}:{query.lower()}"
    persisted = api_cache_get(key, 30 * 24 * 60 * 60)
    cached = cache_get(key, 24 * 60 * 60)
    if cached is not None:
        return cached
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "namedetails": 1,
        "limit": 18,
        "countrycodes": "gr",
        "accept-language": "el,en" if lang == "el" else "en,el",
    }
    try:
        nominatim_throttle()
        data = http_json(f"{NOMINATIM}/search?{urllib.parse.urlencode(params)}", timeout=7, max_age=7 * 24 * 3600)
        result = []
        for item in data if isinstance(data, list) else []:
            try:
                lat = float(item.get("lat")); lon = float(item.get("lon"))
            except Exception:
                continue
            names = item.get("namedetails") or {}
            result.append({
                "place_id": item.get("place_id"),
                "display_name": item.get("display_name") or "",
                "name": item.get("name") or names.get("name:el") or names.get("name:en") or (item.get("display_name") or "").split(",")[0],
                "lat": lat,
                "lon": lon,
                "type": item.get("type") or "",
                "category": item.get("category") or item.get("class") or "",
                "addresstype": item.get("addresstype") or "",
                "address": item.get("address") or {},
                "boundingbox": item.get("boundingbox") or [],
                "offline": False,
                "source": "nominatim",
            })
        if result:
            remember_places(result, "nominatim")
            api_cache_set(key, result)
            cache_set(key, result)
            return result
    except Exception:
        pass
    if persisted:
        return persisted
    return local_search_places(query, 18)


def reverse_greece(lat: float, lon: float, lang: str = "el"):
    key = f"reverse:{lang}:{lat:.5f}:{lon:.5f}"
    cached = cache_get(key, 24 * 60 * 60)
    if cached is not None:
        return cached
    persisted = api_cache_get(key, 90 * 24 * 60 * 60)
    params = {
        "lat": f"{lat:.7f}",
        "lon": f"{lon:.7f}",
        "format": "jsonv2",
        "addressdetails": 1,
        "namedetails": 1,
        "zoom": 18,
        "accept-language": "el,en" if lang == "el" else "en,el",
    }
    try:
        nominatim_throttle()
        result = http_json(f"{NOMINATIM}/reverse?{urllib.parse.urlencode(params)}", timeout=7, max_age=7 * 24 * 3600)
        if isinstance(result, dict):
            result["offline"] = False
            api_cache_set(key, result)
            cache_set(key, result)
            remember_places([{
                "place_id": result.get("place_id"),
                "display_name": result.get("display_name") or "",
                "name": result.get("name") or (result.get("display_name") or "").split(",")[0],
                "lat": result.get("lat", lat), "lon": result.get("lon", lon),
                "type": result.get("type") or "", "category": result.get("category") or "",
                "address": result.get("address") or {},
            }], "reverse")
            return result
    except Exception:
        pass
    if persisted:
        persisted["offline"] = True
        return persisted
    nearest = nearest_cached_place(lat, lon)
    return nearest or {"display_name": f"{lat:.5f}, {lon:.5f}", "lat": lat, "lon": lon, "offline": True}


def route_greece(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    key = f"route:{start_lon:.5f},{start_lat:.5f}:{end_lon:.5f},{end_lat:.5f}"
    persisted = api_cache_get(key, 30 * 24 * 3600)
    url = (f"{OSRM}/route/v1/driving/{start_lon:.6f},{start_lat:.6f};{end_lon:.6f},{end_lat:.6f}"
           "?overview=full&geometries=geojson&steps=true&alternatives=false")
    try:
        data = http_json(url, timeout=9, max_age=24 * 3600)
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            out = {
                "distance": route.get("distance", 0),
                "duration": route.get("duration", 0),
                "geometry": route.get("geometry"),
                "steps": [
                    {
                        "name": st.get("name") or "",
                        "distance": st.get("distance", 0),
                        "duration": st.get("duration", 0),
                        "instruction": (st.get("maneuver") or {}).get("type", ""),
                        "modifier": (st.get("maneuver") or {}).get("modifier", ""),
                    }
                    for leg in route.get("legs") or [] for st in leg.get("steps") or []
                ][:80],
                "offline": False,
            }
            api_cache_set(key, out)
            return out
    except Exception:
        pass
    if persisted:
        persisted["offline"] = True
        return persisted
    raise RuntimeError("route unavailable and not cached")


def geonames_import():
    # Small country-wide settlement index. It is not an address database, but gives
    # GreekOS a useful offline nationwide place-name search after one online run.
    marker = api_cache_get("geonames:gr:loaded")
    if marker:
        return
    try:
        raw, _, _ = disk_http_get(GEONAMES_GR_URL, accept="application/zip", timeout=45, max_age=30*24*3600)
        zf = zipfile.ZipFile(io.BytesIO(raw))
        txt_name = next(n for n in zf.namelist() if n.endswith(".txt"))
        batch=[]
        with zf.open(txt_name) as f:
            for line in io.TextIOWrapper(f, encoding="utf-8", errors="replace"):
                parts=line.rstrip("\n").split("\t")
                if len(parts) < 19: continue
                geoid,name,asciiname,alternates,lat,lon,fclass,fcode,country,*rest=parts
                if country != "GR": continue
                try: latf=float(lat); lonf=float(lon)
                except Exception: continue
                # Settlement/admin/landmark classes are most useful offline.
                if fclass not in {"P","A","S","T","L"}: continue
                disp=name
                aliases=" ".join([name,asciiname,alternates])
                batch.append((f"geonames:{geoid}",name,disp,aliases,latf,lonf,fcode.lower(),fclass.lower(),"{}","geonames",time.time()))
                if len(batch)>=2000:
                    with _db_lock:
                        conn=db_conn(); conn.executemany("""
                        INSERT INTO places(key,name,display_name,aliases,lat,lon,type,category,address_json,source,updated)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET name=excluded.name,display_name=excluded.display_name,aliases=excluded.aliases,lat=excluded.lat,lon=excluded.lon,type=excluded.type,category=excluded.category,source=excluded.source,updated=excluded.updated
                        """,batch); conn.commit(); conn.close()
                    batch=[]
        if batch:
            with _db_lock:
                conn=db_conn(); conn.executemany("""
                INSERT INTO places(key,name,display_name,aliases,lat,lon,type,category,address_json,source,updated)
                VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET name=excluded.name,display_name=excluded.display_name,aliases=excluded.aliases,lat=excluded.lat,lon=excluded.lon,type=excluded.type,category=excluded.category,source=excluded.source,updated=excluded.updated
                """,batch); conn.commit(); conn.close()
        api_cache_set("geonames:gr:loaded", {"at":time.time()})
    except Exception:
        return



HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#07090d">
<title>GreekOS</title>
<link rel="stylesheet" href="/vendor/maplibre-gl.css">
<style>
:root{color-scheme:dark;--bg:#07090d;--panel:rgba(8,11,16,.88);--panel2:rgba(18,22,29,.92);--text:#f7f8fb;--muted:#9aa3b0;--line:rgba(255,255,255,.13);--accent:#70b7ff;--building:#f1f4f8;--shadow:0 12px 34px rgba(0,0,0,.32)}
body.light{color-scheme:light;--bg:#f5f6f8;--panel:rgba(255,255,255,.93);--panel2:rgba(244,246,249,.96);--text:#11151b;--muted:#59616e;--line:rgba(0,0,0,.14);--accent:#1768c5;--building:#252a31;--shadow:0 12px 34px rgba(0,0,0,.16)}
*{box-sizing:border-box}html,body,#app,#map{margin:0;width:100%;height:100%;overflow:hidden}body{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--text)}button,input{font:inherit}.glass{background:var(--panel);border:1px solid var(--line);box-shadow:var(--shadow);backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px)}
#map{position:fixed;inset:0}.top{position:absolute;z-index:20;top:max(10px,env(safe-area-inset-top));left:10px;right:10px;display:flex;align-items:center;gap:8px;pointer-events:none}.brand{height:46px;min-width:46px;border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:24px;pointer-events:auto}.search-wrap{position:relative;flex:1;max-width:620px;pointer-events:auto}.searchbar{height:46px;border-radius:15px;display:flex;align-items:center;padding:0 8px}.searchbar input{min-width:0;flex:1;height:40px;border:0;outline:0;background:transparent;color:var(--text);font-size:16px;padding:0 8px}.searchbar button{width:38px;height:38px;border:0;background:transparent;color:var(--text);font-size:20px}.results{position:absolute;top:52px;left:0;right:0;max-height:min(52vh,430px);overflow:auto;border-radius:15px;padding:5px;display:none}.results.open{display:block}.result{width:100%;border:0;border-bottom:1px solid var(--line);background:transparent;color:var(--text);text-align:left;padding:10px 11px;border-radius:10px}.result:last-child{border-bottom:0}.result strong{display:block;font-size:14px}.result small{display:block;color:var(--muted);font-size:11px;margin-top:3px;line-height:1.25}.top-actions{display:flex;gap:6px;pointer-events:auto}.pill{height:46px;border-radius:15px;display:flex;align-items:center;padding:4px}.pill button{height:36px;min-width:38px;padding:0 9px;border:0;border-radius:11px;background:transparent;color:var(--muted);font-weight:800}.pill button.active{background:rgba(112,183,255,.17);color:var(--text)}.icon-btn{width:46px;height:46px;border-radius:15px;border:1px solid var(--line);background:var(--panel);color:var(--text);display:grid;place-items:center;font-size:20px;box-shadow:var(--shadow)}
.city-chip{position:absolute;z-index:15;top:max(66px,calc(env(safe-area-inset-top) + 66px));left:10px;max-width:260px;border-radius:16px;padding:10px 12px;display:none}.city-chip.open{display:block}.city-chip small{display:block;color:var(--accent);font-weight:800;letter-spacing:.13em;font-size:9px}.city-chip strong{display:block;font-size:18px;margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.city-chip button{margin-top:9px;width:100%;height:36px;border-radius:11px;border:1px solid var(--line);background:var(--panel2);color:var(--text);font-weight:700}
.controls{position:absolute;z-index:18;right:10px;bottom:max(14px,env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(2,46px);gap:7px}.controls button{width:46px;height:46px;border-radius:14px;border:1px solid var(--line);background:var(--panel);color:var(--text);box-shadow:var(--shadow);font-size:19px}.controls button.active{outline:2px solid var(--accent);outline-offset:-2px}.controls button:disabled{opacity:.4}
.joy{position:absolute;z-index:17;left:10px;bottom:max(14px,env(safe-area-inset-bottom));width:124px;height:124px;border-radius:50%;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);padding:7px;gap:3px}.joy button{border:0;background:transparent;color:var(--text);border-radius:50%;font-size:18px}.joy button:active{background:rgba(112,183,255,.17)}.joy .topview{font-size:10px;font-weight:900;letter-spacing:.08em;color:var(--accent)}
.toast{position:absolute;z-index:30;left:50%;bottom:max(150px,calc(env(safe-area-inset-bottom) + 150px));transform:translateX(-50%);max-width:min(560px,calc(100% - 24px));padding:10px 34px 10px 12px;border-radius:13px;font-size:12px;display:none}.toast.open{display:block}.toast button{position:absolute;right:5px;top:5px;width:26px;height:26px;border:0;background:transparent;color:var(--text);font-size:19px}.wifi-panel{position:absolute;z-index:19;left:50%;bottom:max(12px,env(safe-area-inset-bottom));transform:translateX(-50%);width:min(620px,calc(100% - 156px));border-radius:15px;padding:10px;display:none}.wifi-panel.open{display:block}.wifi-head{display:flex;align-items:center;gap:8px}.wifi-head strong{flex:1}.wifi-head button{border:0;background:transparent;color:var(--text);font-size:20px}.wifi-row{display:flex;align-items:center;gap:7px;margin-top:8px}.wifi-row input{min-width:0;flex:1;height:36px;border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:10px;padding:0 8px}.wifi-row button{height:36px;border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:10px;padding:0 12px}.legend{display:flex;flex-wrap:wrap;gap:7px;margin-top:8px;color:var(--muted);font-size:10px}.legend span{display:flex;align-items:center;gap:4px}.dot{width:9px;height:9px;border-radius:50%}.wifi-msg{font-size:11px;color:var(--muted);margin-top:7px}.location-card{position:absolute;z-index:16;left:10px;bottom:148px;max-width:min(330px,calc(100% - 20px));border-radius:14px;padding:9px 11px;display:none;font-size:12px}.location-card.open{display:block}.location-card strong{display:block}.location-card small{color:var(--muted)}
.route-panel{position:absolute;z-index:19;right:112px;bottom:max(14px,env(safe-area-inset-bottom));width:min(330px,calc(100% - 260px));border-radius:15px;padding:10px;display:none}.route-panel.open{display:block}.route-head{display:flex;align-items:center;gap:8px}.route-head strong{flex:1}.route-head button{border:0;background:transparent;color:var(--text);font-size:19px}.route-summary{font-size:12px;color:var(--muted);margin-top:6px}.route-steps{margin-top:6px;max-height:120px;overflow:auto;font-size:11px;color:var(--muted)}.route-steps div{padding:4px 0;border-top:1px solid var(--line)}.net-badge{height:42px;min-width:42px;padding:0 9px;border-radius:14px;border:1px solid var(--line);background:var(--panel);color:var(--muted);box-shadow:var(--shadow);font-size:10px;font-weight:800}.net-badge.offline{color:#f59e0b}.net-badge.online{color:#22c55e}
.offline-panel{position:absolute;z-index:24;left:50%;top:50%;transform:translate(-50%,-50%);width:min(520px,calc(100% - 24px));border-radius:18px;padding:14px;display:none}.offline-panel.open{display:block}.offline-head{display:flex;align-items:center;gap:8px}.offline-head strong{flex:1;font-size:16px}.offline-head button{width:34px;height:34px;border:0;background:transparent;color:var(--text);font-size:22px}.offline-copy{font-size:12px;color:var(--muted);line-height:1.45;margin:8px 0 10px}.offline-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.offline-actions button{min-height:44px;border-radius:12px;border:1px solid var(--line);background:var(--panel2);color:var(--text);font-weight:750}.package-list{display:grid;gap:7px;margin-top:10px}.package-card{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;padding:10px;border-radius:12px;border:1px solid var(--line);background:var(--panel2)}.package-card strong{display:block;font-size:13px}.package-card small{display:block;color:var(--muted);font-size:10px;margin-top:2px}.package-card button{min-height:38px;border-radius:10px;border:1px solid var(--line);background:var(--accent-soft);color:var(--text);font-weight:800;padding:0 11px}.package-card.installed{border-color:var(--accent)}.full-progress{margin-top:12px;display:none}.full-progress.open{display:block}.full-progress progress{width:100%;height:15px;accent-color:var(--accent)}.full-progress-line{display:flex;justify-content:space-between;gap:8px;margin-top:6px;font-size:11px;color:var(--muted)}.featured-badge{font-size:10px;color:var(--muted)}
.maplibregl-ctrl-bottom-left,.maplibregl-ctrl-bottom-right{display:none!important}.maplibregl-popup-content{background:var(--panel)!important;color:var(--text)!important;border:1px solid var(--line);border-radius:12px!important;box-shadow:var(--shadow)!important}.maplibregl-popup-tip{border-top-color:var(--panel)!important}
@media(max-width:680px){.top{align-items:flex-start}.brand{display:none}.top-actions{position:absolute;right:0;top:52px}.search-wrap{max-width:none}.city-chip{top:max(118px,calc(env(safe-area-inset-top) + 118px));max-width:210px}.controls{grid-template-columns:repeat(2,44px)}.controls button{width:44px;height:44px}.joy{width:112px;height:112px}.wifi-panel{left:132px;right:108px;transform:none;width:auto;bottom:max(12px,env(safe-area-inset-bottom))}}
@media(max-width:430px){.offline-actions{grid-template-columns:1fr}.searchbar{height:43px}.pill,.icon-btn{height:42px}.city-chip{max-width:185px}.wifi-panel{left:8px;right:8px;bottom:136px}.location-card{bottom:136px}.route-panel{left:8px;right:8px;bottom:136px;width:auto}.net-badge{display:none}}
</style>
</head>
<body>
<main id="app">
<div id="map"></div>
<div class="top">
  <div class="brand glass">🇬🇷</div>
  <div class="search-wrap">
    <form id="searchForm" class="searchbar glass"><input id="searchInput" autocomplete="off" placeholder="Αναζήτηση διεύθυνσης, δρόμου, καταστήματος, πόλης…"><button aria-label="Search">⌕</button></form>
    <div id="results" class="results glass"></div>
  </div>
  <div class="top-actions">
    <div class="pill glass"><button id="elBtn" class="active">ΕΛ</button><button id="enBtn">EN</button></div>
    <button id="themeBtn" class="icon-btn" title="Theme">☀</button><button id="netBadge" class="net-badge" type="button" title="Offline cache">CACHE</button>
  </div>
</div>
<div id="cityChip" class="city-chip glass"><small>LOCAL 3D</small><strong id="cityName">—</strong><button id="backBtn">Πίσω στην Ελλάδα</button></div>
<div class="controls">
  <button id="homeBtn" title="Greece">⌂</button>
  <button id="locateBtn" title="My location">◎</button>
  <button id="wifiBtn" title="Wi-Fi/data">⌁</button>
  <button id="trafficBtn" title="Traffic" disabled>≋</button>
  <button id="routeBtn" title="Navigate">➤</button>
  <button id="offlineBtn" title="Save current area offline">⇩</button>
</div>
<div class="joy glass" aria-label="3D camera joystick">
  <span></span><button data-joy="up">▲</button><span></span>
  <button data-joy="left">◀</button><button class="topview" data-joy="top">TOP</button><button data-joy="right">▶</button>
  <span></span><button data-joy="down">▼</button><span></span>
</div>
<div id="offlinePanel" class="offline-panel glass">
  <div class="offline-head"><strong id="offlineTitle">Offline Maps</strong><button id="offlineClose" type="button">×</button></div>
  <div id="offlineCopy" class="offline-copy">Save the visible area or install a resumable offline Greece package.</div>
  <div class="offline-actions"><button id="offlineAreaBtn" type="button">Save current area</button></div>
  <div id="packageList" class="package-list"></div>
  <div id="fullProgress" class="full-progress"><progress id="fullProgressBar" max="100" value="0"></progress><div class="full-progress-line"><strong id="fullProgressPct">0%</strong><span id="fullProgressText">Waiting…</span></div></div>
</div>
<div id="wifiPanel" class="wifi-panel glass">
  <div class="wifi-head"><strong id="wifiTitle">Athens Wi-Fi activity</strong><button id="wifiClose">×</button></div>
  <div class="wifi-row"><button id="wifiPlay">▶</button><input id="wifiDate" type="date"></div>
  <div class="legend"><span><i class="dot" style="background:#3b82f6"></i>Low</span><span><i class="dot" style="background:#22c55e"></i>Moderate</span><span><i class="dot" style="background:#eab308"></i>Busy</span><span><i class="dot" style="background:#f97316"></i>High</span><span><i class="dot" style="background:#ef4444"></i>Very high</span></div>
  <div id="wifiMsg" class="wifi-msg"></div>
</div>
<div id="routePanel" class="route-panel glass"><div class="route-head"><strong id="routeTitle">Navigation</strong><button id="routeClose">×</button></div><div id="routeSummary" class="route-summary"></div><div id="routeSteps" class="route-steps"></div></div>
<div id="locationCard" class="location-card glass"><strong id="locationTitle">GPS</strong><small id="locationText"></small></div>
<div id="toast" class="toast glass"><span id="toastText"></span><button id="toastClose">×</button></div>
</main>
<script src="/vendor/maplibre-gl.js"></script>
<script>
(()=>{
const STYLE={dark:'/api/style?theme=dark',light:'/api/style?theme=light'};
const ATHENS=[23.7275,37.9838];
const DATA_CITIES=[
 {id:'athens',name:'Αθήνα',en:'Athens',c:[23.7275,37.9838],kind:'feed'},
 {id:'patras',name:'Πάτρα',en:'Patras',c:[21.7346,38.2466],kind:'dashboard'},
 {id:'drama',name:'Δράμα',en:'Drama',c:[24.1473,41.1499],kind:'dashboard'},
 {id:'alexandroupoli',name:'Αλεξανδρούπολη',en:'Alexandroupoli',c:[25.8744,40.8457],kind:'dashboard'},
 {id:'lamia',name:'Λαμία',en:'Lamia',c:[22.4341,38.8993],kind:'system'}
];
const FEATURED_PLACES=[
 {id:'athens',name:'Αθήνα',en:'Athens',c:[23.7275,37.9838],rank:1},{id:'piraeus',name:'Πειραιάς',en:'Piraeus',c:[23.6469,37.9420],rank:1},
 {id:'thessaloniki',name:'Θεσσαλονίκη',en:'Thessaloniki',c:[22.9444,40.6401],rank:1},{id:'patras',name:'Πάτρα',en:'Patras',c:[21.7346,38.2466],rank:1},
 {id:'heraklion',name:'Ηράκλειο',en:'Heraklion',c:[25.1442,35.3387],rank:1},{id:'larissa',name:'Λάρισα',en:'Larissa',c:[22.4191,39.6390],rank:1},
 {id:'volos',name:'Βόλος',en:'Volos',c:[22.9426,39.3610],rank:1},{id:'ioannina',name:'Ιωάννινα',en:'Ioannina',c:[20.8537,39.6650],rank:1},
 {id:'chania',name:'Χανιά',en:'Chania',c:[24.0180,35.5138],rank:1},{id:'rhodes',name:'Ρόδος',en:'Rhodes',c:[28.2176,36.4349],rank:1},
 {id:'corfu',name:'Κέρκυρα',en:'Corfu',c:[19.9217,39.6243],rank:1},{id:'kavala',name:'Καβάλα',en:'Kavala',c:[24.4069,40.9396],rank:2},
 {id:'alexandroupoli',name:'Αλεξανδρούπολη',en:'Alexandroupoli',c:[25.8744,40.8457],rank:2},{id:'serres',name:'Σέρρες',en:'Serres',c:[23.5475,41.0856],rank:2},
 {id:'drama',name:'Δράμα',en:'Drama',c:[24.1473,41.1499],rank:2},{id:'kozani',name:'Κοζάνη',en:'Kozani',c:[21.7889,40.3007],rank:2},
 {id:'katerini',name:'Κατερίνη',en:'Katerini',c:[22.5025,40.2719],rank:2},{id:'trikala',name:'Τρίκαλα',en:'Trikala',c:[21.7679,39.5553],rank:2},
 {id:'lamia',name:'Λαμία',en:'Lamia',c:[22.4341,38.8993],rank:2},{id:'chalkida',name:'Χαλκίδα',en:'Chalkida',c:[23.6028,38.4635],rank:2},
 {id:'agrinio',name:'Αγρίνιο',en:'Agrinio',c:[21.4078,38.6214],rank:2},{id:'kalamata',name:'Καλαμάτα',en:'Kalamata',c:[22.1142,37.0389],rank:2},
 {id:'tripoli',name:'Τρίπολη',en:'Tripoli',c:[22.3794,37.5089],rank:2},{id:'nafplio',name:'Ναύπλιο',en:'Nafplio',c:[22.8016,37.5673],rank:2},
 {id:'sparta',name:'Σπάρτη',en:'Sparta',c:[22.4303,37.0745],rank:2},{id:'rethymno',name:'Ρέθυμνο',en:'Rethymno',c:[24.4822,35.3656],rank:2},
 {id:'agios_nikolaos',name:'Άγιος Νικόλαος',en:'Agios Nikolaos',c:[25.7152,35.1911],rank:2},{id:'mytilene',name:'Μυτιλήνη',en:'Mytilene',c:[26.5553,39.1079],rank:2},
 {id:'chios',name:'Χίος',en:'Chios',c:[26.1350,38.3687],rank:2},{id:'ermoupoli',name:'Ερμούπολη',en:'Ermoupoli',c:[24.9429,37.4447],rank:2},
 {id:'fira',name:'Φηρά',en:'Fira',c:[25.4315,36.4167],rank:2},{id:'mykonos',name:'Μύκονος',en:'Mykonos',c:[25.3289,37.4467],rank:2},
 {id:'naxos',name:'Νάξος',en:'Naxos',c:[25.3764,37.1036],rank:2},{id:'parikia',name:'Παροικιά',en:'Parikia',c:[25.1484,37.0853],rank:2},
 {id:'zakynthos',name:'Ζάκυνθος',en:'Zakynthos',c:[20.8999,37.7870],rank:2},{id:'argostoli',name:'Αργοστόλι',en:'Argostoli',c:[20.4890,38.1754],rank:2},
 {id:'nea_makri',name:'Νέα Μάκρη',en:'Nea Makri',c:[23.9770,38.0850],rank:3},{id:'kalambaka',name:'Καλαμπάκα',en:'Kalambaka',c:[21.6269,39.7044],rank:3},
 {id:'metsovo',name:'Μέτσοβο',en:'Metsovo',c:[21.1828,39.7694],rank:3},{id:'parga',name:'Πάργα',en:'Parga',c:[20.4009,39.2859],rank:3},
 {id:'nafpaktos',name:'Ναύπακτος',en:'Nafpaktos',c:[21.8275,38.3917],rank:3},{id:'monemvasia',name:'Μονεμβασιά',en:'Monemvasia',c:[23.0553,36.6876],rank:3},
 {id:'arachova',name:'Αράχωβα',en:'Arachova',c:[22.5835,38.4796],rank:3},{id:'meteora',name:'Μετέωρα',en:'Meteora',c:[21.6306,39.7217],rank:3},{id:'olympia',name:'Ολυμπία',en:'Olympia',c:[21.6300,37.6380],rank:3},
 {id:'delphi',name:'Δελφοί',en:'Delphi',c:[22.5010,38.4824],rank:3}
];
const T={
 el:{search:'Αναζήτηση διεύθυνσης, δρόμου, καταστήματος, πόλης…',back:'Πίσω στην Ελλάδα',gps:'Η τοποθεσία μου',gpsWait:'Αναζήτηση ακριβούς θέσης…',gpsDenied:'Η άδεια τοποθεσίας απορρίφθηκε. Ενεργοποίησέ την από τις ρυθμίσεις του browser.',gpsFail:'Δεν μπόρεσε να βρεθεί η τοποθεσία.',noResults:'Δεν βρέθηκαν αποτελέσματα στην Ελλάδα.',wifi:'Δημόσια Wi-Fi / visitor activity',wifiLoad:'Φόρτωση δημόσιων συγκεντρωτικών δεδομένων Αθήνας…',wifiFail:'Δεν μπόρεσαν να φορτωθούν τα δημόσια δεδομένα Wi-Fi αυτή τη στιγμή.',wifiReady:'Ύψος και χρώμα = σχετική χρήση ανά δημοτικό Wi-Fi σημείο.',trafficOff:'Για live traffic βάλε GREEKOS_TOMTOM_API_KEY πριν τρέξεις το GreekOS.py.',routeNeedGps:'Χρειάζεται πρώτα η τοποθεσία σου για πλοήγηση.',routeLoad:'Υπολογισμός διαδρομής…',routeFail:'Η διαδρομή δεν είναι διαθέσιμη και δεν υπάρχει στην offline cache.',offlineStart:'Αποθήκευση της τρέχουσας περιοχής για offline χρήση…',offlineDone:'Η περιοχή αποθηκεύτηκε για offline χρήση.',offlineFail:'Η offline αποθήκευση απέτυχε.',offlineMaps:'Offline χάρτες',offlineCopy:'Αποθήκευσε την τρέχουσα περιοχή ή εγκατέστησε πακέτο offline Ελλάδας με ασφαλή συνέχιση.',saveArea:'Αποθήκευση τρέχουσας περιοχής',fullMap:'Λήψη όλης της Ελλάδας',fullMapDownloading:'Λήψη πλήρους χάρτη Ελλάδας…',fullMapDone:'Ο πλήρης offline χάρτης εγκαταστάθηκε.',fullMapFail:'Η λήψη του πλήρους χάρτη απέτυχε.',fullMapInstalled:'Πλήρης offline χάρτης εγκατεστημένος',install:'Εγκατάσταση',installed:'Εγκατεστημένο',chunk:'κομμάτι',cached:'cache'},
 en:{search:'Search address, road, shop, town…',back:'Back to Greece',gps:'My location',gpsWait:'Finding precise location…',gpsDenied:'Location permission was denied. Enable it in the browser settings.',gpsFail:'Could not get your location.',noResults:'No results found in Greece.',wifi:'Public Wi-Fi / visitor activity',wifiLoad:'Loading Athens public aggregate data…',wifiFail:'Public Wi-Fi data could not be loaded right now.',wifiReady:'Height and color = relative activity at each municipal Wi-Fi point.',trafficOff:'For live traffic set GREEKOS_TOMTOM_API_KEY before running GreekOS.py.',routeNeedGps:'Your location is needed first for navigation.',routeLoad:'Calculating route…',routeFail:'Route is unavailable and is not in the offline cache.',offlineStart:'Saving the current area for offline use…',offlineDone:'Area saved for offline use.',offlineFail:'Offline save failed.',offlineMaps:'Offline Maps',offlineCopy:'Save the visible area or install a resumable offline Greece package.',saveArea:'Save current area',fullMap:'Download all Greece',fullMapDownloading:'Downloading full Greece map…',fullMapDone:'Full offline Greece map installed.',fullMapFail:'Full map download failed.',fullMapInstalled:'Full offline map installed',install:'Install',installed:'Installed',chunk:'chunk',cached:'cache'}
};
let lang='el',theme='dark',mode='2d',map,currentPlace='',currentCenter=ATHENS,styleReady=false,wifiOnly=false,trafficOn=false,trafficAvailable=false;
let wifiState=null,wifiTimer=null,gpsWatch=null,gpsFollow=false,gpsMarker=null,gpsAccuracy=null,gpsCoord=null,selectedTarget=ATHENS,pendingRoute=false,routeActive=false;
let symbolCache=new Map();
const $=id=>document.getElementById(id);
function tr(k){return T[lang][k]||k}function toast(s){$('toastText').textContent=s;$('toast').classList.add('open')}function closeToast(){$('toast').classList.remove('open')}
$('toastClose').onclick=closeToast;
function distanceKm(a,b){const r=Math.PI/180,dlat=(b[1]-a[1])*r,dlon=(b[0]-a[0])*r,x=Math.sin(dlat/2)**2+Math.cos(a[1]*r)*Math.cos(b[1]*r)*Math.sin(dlon/2)**2;return 6371*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x))}
function isAthens(c){return distanceKm(c,ATHENS)<25}
function labelExpr(){return ['coalesce',['get',lang==='el'?'name:el':'name:en'],['get','name:el'],['get','name'],['get','name:en']]}
function textColor(){return theme==='dark'?'#f5f7fb':'#14181e'}function haloColor(){return theme==='dark'?'#07090d':'#ffffff'}function buildingColor(){return theme==='dark'?'#f1f4f8':'#2c3138'}
function safeRemoveLayer(id){if(map.getLayer(id))map.removeLayer(id)}function safeRemoveSource(id){if(map.getSource(id))map.removeSource(id)}
function addDetailedLayers(){
 if(!map.getSource('openmaptiles'))return;
 const before=(map.getStyle().layers||[]).find(l=>l.type==='symbol')?.id;
 const add=(layer)=>{if(!map.getLayer(layer.id))map.addLayer(layer,before)};
 add({id:'gos-neighborhoods',type:'symbol',source:'openmaptiles','source-layer':'place',minzoom:9,filter:['in',['get','class'],['literal',['suburb','quarter','neighbourhood','borough','city','town','village','hamlet']]],layout:{'text-field':labelExpr(),'text-size':['interpolate',['linear'],['zoom'],9,11,16,16],'text-font':['Noto Sans Regular'],'text-allow-overlap':false,'text-padding':3},paint:{'text-color':textColor(),'text-halo-color':haloColor(),'text-halo-width':1.2}});
 add({id:'gos-roadnames',type:'symbol',source:'openmaptiles','source-layer':'transportation_name',minzoom:12,layout:{'symbol-placement':'line','text-field':labelExpr(),'text-size':['interpolate',['linear'],['zoom'],12,10,18,15],'text-font':['Noto Sans Regular'],'text-keep-upright':true,'text-letter-spacing':.01},paint:{'text-color':textColor(),'text-halo-color':haloColor(),'text-halo-width':1.3}});
 add({id:'gos-pois',type:'symbol',source:'openmaptiles','source-layer':'poi',minzoom:14,layout:{'text-field':labelExpr(),'text-size':['interpolate',['linear'],['zoom'],14,10,18,13],'text-font':['Noto Sans Regular'],'text-offset':[0,.7],'text-optional':true},paint:{'text-color':textColor(),'text-halo-color':haloColor(),'text-halo-width':1.2}});
 add({id:'gos-housenumbers',type:'symbol',source:'openmaptiles','source-layer':'housenumber',minzoom:16,layout:{'text-field':['to-string',['coalesce',['get','housenumber'],['get','house_number'],['get','name']]],'text-size':11,'text-font':['Noto Sans Regular']},paint:{'text-color':textColor(),'text-halo-color':haloColor(),'text-halo-width':1.1}});
}
function addTerrainAndBuildings(){
 if(!map.getSource('gos-dem'))map.addSource('gos-dem',{type:'raster-dem',url:'https://tiles.mapterhorn.com/tilejson.json',tileSize:512,maxzoom:14});
 map.setTerrain({source:'gos-dem',exaggeration:1.08});
 const before=(map.getStyle().layers||[]).find(l=>l.type==='symbol')?.id;
 if(!map.getLayer('gos-buildings'))map.addLayer({id:'gos-buildings',type:'fill-extrusion',source:'openmaptiles','source-layer':'building',minzoom:12.7,paint:{'fill-extrusion-color':['interpolate',['linear'],['to-number',['coalesce',['get','render_height'],['get','height'],8]],0,buildingColor(),35,theme==='dark'?'#d8e0e8':'#343b44',120,theme==='dark'?'#b9c6d2':'#4a5562'],'fill-extrusion-height':['to-number',['coalesce',['get','render_height'],['get','height'],8]],'fill-extrusion-base':['to-number',['coalesce',['get','render_min_height'],['get','min_height'],0]],'fill-extrusion-opacity':.93,'fill-extrusion-vertical-gradient':true}},before);
 addDetailedLayers();
}
function remove3D(){map.setTerrain(null);['gos-buildings','gos-neighborhoods','gos-roadnames','gos-pois','gos-housenumbers','gos-wifi-columns'].forEach(safeRemoveLayer);['gos-dem','gos-wifi-columns-src'].forEach(safeRemoveSource);$('wifiPanel').classList.remove('open');if(wifiTimer){clearInterval(wifiTimer);wifiTimer=null}}
function addFeaturedPlaces(){
 const data={type:'FeatureCollection',features:FEATURED_PLACES.map(x=>({type:'Feature',properties:{id:x.id,name:lang==='el'?x.name:x.en,rank:x.rank},geometry:{type:'Point',coordinates:x.c}}))};
 if(!map.getSource('gos-featured-places'))map.addSource('gos-featured-places',{type:'geojson',data});else map.getSource('gos-featured-places').setData(data);
 if(!map.getLayer('gos-featured-places'))map.addLayer({id:'gos-featured-places',type:'symbol',source:'gos-featured-places',minzoom:4.5,maxzoom:11.5,filter:['<=',['get','rank'],['step',['zoom'],1,6.3,2,8.8,3]],layout:{'text-field':['get','name'],'text-size':['interpolate',['linear'],['zoom'],5,11,9,14],'text-font':['Noto Sans Bold'],'text-allow-overlap':false,'text-padding':5},paint:{'text-color':textColor(),'text-halo-color':haloColor(),'text-halo-width':1.4}});
}
function addAvailability(){
 const data={type:'FeatureCollection',features:DATA_CITIES.map(x=>({type:'Feature',properties:{id:x.id,name:lang==='el'?x.name:x.en,kind:x.kind},geometry:{type:'Point',coordinates:x.c}}))};
 if(!map.getSource('gos-data-cities'))map.addSource('gos-data-cities',{type:'geojson',data});else map.getSource('gos-data-cities').setData(data);
 if(!map.getLayer('gos-data-cities'))map.addLayer({id:'gos-data-cities',type:'circle',source:'gos-data-cities',paint:{'circle-radius':['interpolate',['linear'],['zoom'],5,7,12,11],'circle-color':['match',['get','kind'],'feed','#22c55e','dashboard','#eab308','#9ca3af'],'circle-stroke-color':theme==='dark'?'#ffffff':'#111827','circle-stroke-width':2,'circle-opacity':.92}});
 if(!map.getLayer('gos-data-city-labels'))map.addLayer({id:'gos-data-city-labels',type:'symbol',source:'gos-data-cities',minzoom:5,layout:{'text-field':['get','name'],'text-size':11,'text-offset':[0,1.35],'text-font':['Noto Sans Regular'],'text-allow-overlap':true},paint:{'text-color':textColor(),'text-halo-color':haloColor(),'text-halo-width':1.2}});
}
function setWifiOnly(on){wifiOnly=on;$('wifiBtn').classList.toggle('active',on);if(mode==='3d'){if(isAthens(currentCenter)){$('wifiPanel').classList.toggle('open',on||!!wifiState);if(!wifiState)loadAthensWifi()}return}
 if(on){symbolCache=new Map();for(const l of map.getStyle().layers||[]){if(l.type==='symbol'&&!l.id.startsWith('gos-')){const v=map.getLayoutProperty(l.id,'visibility')||'visible';symbolCache.set(l.id,v);map.setLayoutProperty(l.id,'visibility','none')}}if(map.getLayer('gos-featured-places'))map.setLayoutProperty('gos-featured-places','visibility','none');addAvailability()}else{for(const [id,v] of symbolCache){if(map.getLayer(id))map.setLayoutProperty(id,'visibility',v)}symbolCache.clear();if(map.getLayer('gos-featured-places'))map.setLayoutProperty('gos-featured-places','visibility','visible');addFeaturedPlaces();addAvailability()}}
function buildCustom(){styleReady=true;if(mode==='3d'){addTerrainAndBuildings()}else{addDetailedLayers()}addFeaturedPlaces();addAvailability();if(wifiOnly)setWifiOnly(true);if(trafficOn)addTraffic();if(gpsCoord)renderGps(gpsCoord[0],gpsCoord[1],gpsCoord[2]);if(mode==='3d'&&isAthens(currentCenter)&&wifiState)renderWifiDate($('wifiDate').value||wifiState.dates.at(-1))}
function switchTheme(){theme=theme==='dark'?'light':'dark';document.body.classList.toggle('light',theme==='light');$('themeBtn').textContent=theme==='dark'?'☀':'☾';styleReady=false;map.setStyle(STYLE[theme],{diff:false});map.once('style.load',buildCustom)}
function setLang(next){lang=next;$('elBtn').classList.toggle('active',lang==='el');$('enBtn').classList.toggle('active',lang==='en');$('searchInput').placeholder=tr('search');$('backBtn').textContent=tr('back');if(currentPlace)$('cityName').textContent=currentPlace;buildLanguageRefresh()}
function buildLanguageRefresh(){if(styleReady){['gos-neighborhoods','gos-roadnames','gos-pois'].forEach(id=>{if(map.getLayer(id))map.setLayoutProperty(id,'text-field',labelExpr())});addFeaturedPlaces();addAvailability()}}
function home(){mode='2d';currentPlace='';currentCenter=ATHENS;$('cityChip').classList.remove('open');remove3D();map.easeTo({center:[23.45,38.55],zoom:5.15,pitch:0,bearing:0,duration:900});addAvailability()}
function enter3D(name,c,zoom=14.5){mode='3d';currentPlace=name||'';currentCenter=c;selectedTarget=c;$('cityName').textContent=currentPlace;$('cityChip').classList.add('open');addTerrainAndBuildings();map.easeTo({center:c,zoom:Math.max(zoom,map.getZoom()),pitch:58,bearing:-18,duration:950});if(isAthens(c)){loadAthensWifi()}else{$('wifiPanel').classList.remove('open')}}
function joy(dir){if(dir==='top'){map.easeTo({pitch:0,bearing:0,duration:350});return}let p=map.getPitch(),b=map.getBearing();if(dir==='up')p=Math.min(80,p+10);if(dir==='down')p=Math.max(0,p-10);if(dir==='left')b-=18;if(dir==='right')b+=18;map.easeTo({pitch:p,bearing:b,duration:180})}
function addTraffic(){if(!trafficAvailable)return;if(!map.getSource('gos-traffic'))map.addSource('gos-traffic',{type:'raster',tiles:[location.origin+'/api/traffic/{z}/{x}/{y}.png'],tileSize:256,maxzoom:22});if(!map.getLayer('gos-traffic'))map.addLayer({id:'gos-traffic',type:'raster',source:'gos-traffic',paint:{'raster-opacity':.78}})}
function toggleTraffic(){if(!trafficAvailable){toast(tr('trafficOff'));return}trafficOn=!trafficOn;$('trafficBtn').classList.toggle('active',trafficOn);if(trafficOn)addTraffic();else safeRemoveLayer('gos-traffic')}
function quantile(sorted,q){if(!sorted.length)return 0;return sorted[Math.min(sorted.length-1,Math.floor((sorted.length-1)*q))]}
function square(lon,lat,m){const dy=m/111320,dx=m/(111320*Math.cos(lat*Math.PI/180));return [[[lon-dx,lat-dy],[lon+dx,lat-dy],[lon+dx,lat+dy],[lon-dx,lat+dy],[lon-dx,lat-dy]]]}
function renderWifiDate(date){if(!wifiState)return;const stations=new Map(wifiState.stations.map(s=>[Number(s.stationId),s]));const rows=wifiState.records.filter(r=>r.date===date&&stations.get(Number(r.stationId))?.coordinate);if(!rows.length){$('wifiMsg').textContent=tr('wifiFail');return}const vals=rows.map(r=>Number(r.value)||0).sort((a,b)=>a-b),q=[.2,.4,.6,.8].map(x=>quantile(vals,x)),max=Math.max(...vals,1);const colors=['#3b82f6','#22c55e','#eab308','#f97316','#ef4444'];const features=rows.map(r=>{const s=stations.get(Number(r.stationId)),v=Number(r.value)||0;let band=v<=q[0]?0:v<=q[1]?1:v<=q[2]?2:v<=q[3]?3:4;const h=45+520*Math.sqrt(v/max);return {type:'Feature',properties:{name:s.name||('Station '+r.stationId),value:v,height:h,color:colors[band],band},geometry:{type:'Polygon',coordinates:square(s.coordinate[0],s.coordinate[1],22)}}});const data={type:'FeatureCollection',features};if(!map.getSource('gos-wifi-columns-src'))map.addSource('gos-wifi-columns-src',{type:'geojson',data});else map.getSource('gos-wifi-columns-src').setData(data);if(!map.getLayer('gos-wifi-columns'))map.addLayer({id:'gos-wifi-columns',type:'fill-extrusion',source:'gos-wifi-columns-src',paint:{'fill-extrusion-color':['get','color'],'fill-extrusion-height':['get','height'],'fill-extrusion-base':0,'fill-extrusion-opacity':.92,'fill-extrusion-vertical-gradient':true}});$('wifiDate').value=date;$('wifiMsg').textContent=tr('wifiReady')}
async function loadAthensWifi(){if(wifiState){$('wifiPanel').classList.add('open');renderWifiDate($('wifiDate').value||wifiState.dates.at(-1));return}$('wifiPanel').classList.add('open');$('wifiTitle').textContent=tr('wifi');$('wifiMsg').textContent=tr('wifiLoad');try{const r=await fetch('/api/athens-wifi',{cache:'no-store'});if(!r.ok)throw 0;wifiState=await r.json();if(!wifiState.dates?.length)throw 0;$('wifiDate').min=wifiState.dates[0];$('wifiDate').max=wifiState.dates.at(-1);renderWifiDate(wifiState.dates.at(-1))}catch(e){$('wifiMsg').textContent=tr('wifiFail')}}
function toggleWifiPlay(){if(!wifiState?.dates?.length)return;if(wifiTimer){clearInterval(wifiTimer);wifiTimer=null;$('wifiPlay').textContent='▶';return}$('wifiPlay').textContent='Ⅱ';wifiTimer=setInterval(()=>{const dates=wifiState.dates,cur=$('wifiDate').value,i=Math.max(0,dates.indexOf(cur));const next=dates[(i+1)%dates.length];renderWifiDate(next)},900)}
async function doSearch(q){q=q.trim();if(!q)return;$('results').innerHTML='<button class="result"><strong>…</strong></button>';$('results').classList.add('open');try{const r=await fetch('/api/search?q='+encodeURIComponent(q)+'&lang='+lang);const items=await r.json();$('results').innerHTML='';if(!items.length){$('results').innerHTML='<button class="result"><strong>'+tr('noResults')+'</strong></button>';return}items.forEach(x=>{const b=document.createElement('button');b.className='result';b.type='button';b.innerHTML='<strong></strong><small></small>';b.querySelector('strong').textContent=x.name||x.display_name.split(',')[0];b.querySelector('small').textContent=x.display_name;b.onclick=()=>{$('results').classList.remove('open');$('searchInput').value=x.name||'';let z=['house','building','shop','amenity','road'].includes(x.addresstype)||['house','shop','amenity','highway'].includes(x.category)?17:14.5;enter3D(x.name||x.display_name.split(',')[0],[x.lon,x.lat],z)};$('results').appendChild(b)})}catch(e){$('results').innerHTML='<button class="result"><strong>'+tr('noResults')+'</strong></button>'}}
function renderGps(lon,lat,acc){gpsCoord=[lon,lat,acc];if(gpsMarker)gpsMarker.remove();const el=document.createElement('div');el.style.cssText='width:18px;height:18px;border-radius:50%;background:#2f80ed;border:3px solid white;box-shadow:0 0 0 5px rgba(47,128,237,.25)';gpsMarker=new maplibregl.Marker({element:el}).setLngLat([lon,lat]).addTo(map);const steps=48,coords=[];const r=Math.min(Math.max(acc||20,10),1200);for(let i=0;i<=steps;i++){const a=i/steps*2*Math.PI,dy=(r/111320)*Math.sin(a),dx=(r/(111320*Math.cos(lat*Math.PI/180)))*Math.cos(a);coords.push([lon+dx,lat+dy])}const data={type:'Feature',geometry:{type:'Polygon',coordinates:[coords]},properties:{}};if(!map.getSource('gos-gps-accuracy'))map.addSource('gos-gps-accuracy',{type:'geojson',data});else map.getSource('gos-gps-accuracy').setData(data);if(!map.getLayer('gos-gps-accuracy'))map.addLayer({id:'gos-gps-accuracy',type:'fill',source:'gos-gps-accuracy',paint:{'fill-color':'#2f80ed','fill-opacity':.12,'fill-outline-color':'#2f80ed'}});if(gpsFollow)map.easeTo({center:[lon,lat],zoom:Math.max(map.getZoom(),16.5),pitch:mode==='3d'?55:35,duration:500})}
async function updateGpsCard(lat,lon,acc){$('locationCard').classList.add('open');$('locationTitle').textContent=tr('gps');$('locationText').textContent=lat.toFixed(5)+', '+lon.toFixed(5)+' · ±'+Math.round(acc||0)+' m';try{const r=await fetch('/api/reverse?lat='+lat+'&lon='+lon+'&lang='+lang);const x=await r.json();if(x.display_name)$('locationText').textContent=x.display_name+' · ±'+Math.round(acc||0)+' m'}catch(e){}}
function locate(){if(!navigator.geolocation){toast(tr('gpsFail'));return}gpsFollow=true;$('locateBtn').classList.add('active');toast(tr('gpsWait'));const ok=p=>{closeToast();const {longitude,latitude,accuracy}=p.coords;renderGps(longitude,latitude,accuracy);updateGpsCard(latitude,longitude,accuracy);if(mode==='2d'&&!pendingRoute)enter3D(lang==='el'?'Η τοποθεσία μου':'My location',[longitude,latitude],17);if(pendingRoute)setTimeout(startRoute,120)};const fail=e=>{gpsFollow=false;$('locateBtn').classList.remove('active');toast(e.code===1?tr('gpsDenied'):tr('gpsFail'))};navigator.geolocation.getCurrentPosition(ok,fail,{enableHighAccuracy:true,timeout:20000,maximumAge:0});if(gpsWatch===null)gpsWatch=navigator.geolocation.watchPosition(ok,fail,{enableHighAccuracy:true,timeout:30000,maximumAge:2000})}
function clearRoute(){routeActive=false;$('routePanel').classList.remove('open');safeRemoveLayer('gos-route-line');safeRemoveLayer('gos-route-casing');safeRemoveSource('gos-route-src')}
function routeStepText(s){let t=(s.instruction||'').replaceAll('_',' ');if(s.modifier)t+=' '+s.modifier;if(s.name)t+=' · '+s.name;return t||s.name||'Continue'}
async function startRoute(){if(!gpsCoord){pendingRoute=true;toast(tr('routeNeedGps'));locate();return}pendingRoute=false;toast(tr('routeLoad'));const [slon,slat]=gpsCoord,[elon,elat]=selectedTarget||currentCenter;try{const r=await fetch('/api/route?slon='+slon+'&slat='+slat+'&elon='+elon+'&elat='+elat);if(!r.ok)throw 0;const x=await r.json();if(!x.geometry)throw 0;closeToast();const data={type:'Feature',properties:{},geometry:x.geometry};if(!map.getSource('gos-route-src'))map.addSource('gos-route-src',{type:'geojson',data});else map.getSource('gos-route-src').setData(data);if(!map.getLayer('gos-route-casing'))map.addLayer({id:'gos-route-casing',type:'line',source:'gos-route-src',paint:{'line-color':theme==='dark'?'#0b1220':'#ffffff','line-width':['interpolate',['linear'],['zoom'],8,5,16,10],'line-opacity':.9}});if(!map.getLayer('gos-route-line'))map.addLayer({id:'gos-route-line',type:'line',source:'gos-route-src',paint:{'line-color':'#2f80ed','line-width':['interpolate',['linear'],['zoom'],8,3,16,6],'line-opacity':.95}});routeActive=true;$('routePanel').classList.add('open');$('wifiPanel').classList.remove('open');const km=(Number(x.distance||0)/1000).toFixed(1),mins=Math.max(1,Math.round(Number(x.duration||0)/60));$('routeTitle').textContent=lang==='el'?'Πλοήγηση':'Navigation';$('routeSummary').textContent=km+' km · '+mins+' min'+(x.offline?' · OFFLINE':'');$('routeSteps').innerHTML='';(x.steps||[]).slice(0,14).forEach((s,i)=>{const d=document.createElement('div');d.textContent=(i+1)+'. '+routeStepText(s);$('routeSteps').appendChild(d)});const coords=x.geometry.coordinates||[];if(coords.length){const b=new maplibregl.LngLatBounds(coords[0],coords[0]);coords.forEach(c=>b.extend(c));map.fitBounds(b,{padding:{top:120,bottom:150,left:40,right:40},duration:700})}}catch(e){closeToast();toast(tr('routeFail'))}}
function formatBytes(n){n=Number(n||0);if(!n)return '0 MB';const u=['B','KB','MB','GB'];let i=0;while(n>=1024&&i<u.length-1){n/=1024;i++}return n.toFixed(i>=2?2:i?1:0)+' '+u[i]}
function formatSpeed(n){return n?formatBytes(n)+'/s':'—'}
async function openOfflinePanel(){
 $('offlinePanel').classList.add('open');$('offlineTitle').textContent=tr('offlineMaps');$('offlineCopy').textContent=tr('offlineCopy');$('offlineAreaBtn').textContent=tr('saveArea');
 const list=$('packageList');list.innerHTML='';
 try{const x=await (await fetch('/api/offline/packages')).json();(x.tiers||[]).forEach(t=>{const row=document.createElement('div');row.className='package-card'+(t.installed?' installed':'');const copy=document.createElement('div');const title=document.createElement('strong');title.textContent=(t.label||t.id)+' · '+t.target_gb+' GB';const sub=document.createElement('small');sub.textContent=t.description||'';copy.append(title,sub);const b=document.createElement('button');b.type='button';b.textContent=t.installed?tr('installed'):tr('install');b.disabled=!!t.installed;b.onclick=()=>startPackageDownload(t.id,t.label||t.id,t.target_gb);row.append(copy,b);list.appendChild(row)});if(x.installed&&x.installed.tier){$('fullProgress').classList.add('open');$('fullProgressBar').value=100;$('fullProgressPct').textContent='100%';$('fullProgressText').textContent=tr('installed')+' · '+(x.installed.label||x.installed.tier)+' · '+formatBytes(x.installed.bytes||0)}}catch(e){list.textContent=tr('fullMapFail')}
}
function closeOfflinePanel(){$('offlinePanel').classList.remove('open')}
async function startPackageDownload(tier,label,targetGb){
 $('fullProgress').classList.add('open');$('fullProgressBar').value=0;$('fullProgressPct').textContent='0%';$('fullProgressText').textContent=(label||tier)+' · '+targetGb+' GB';
 try{const r=await fetch('/api/offline/package/start?tier='+encodeURIComponent(tier));const j=await r.json();if(!r.ok||!j.id)throw new Error(j.message||j.error||'start failed');const poll=async()=>{try{const x=await (await fetch('/api/offline/job?id='+encodeURIComponent(j.id))).json();const pct=Number(x.percent||0);$('fullProgressBar').value=pct;$('fullProgressPct').textContent=pct.toFixed(1)+'%';const done=formatBytes(x.doneBytes||0),total=x.totalBytes?formatBytes(x.totalBytes):'?',speed=formatSpeed(x.speedBps||0),chunks=x.totalChunks?(' · '+tr('chunk')+' '+(x.currentChunk||0)+'/'+x.totalChunks):'';$('fullProgressText').textContent=done+' / '+total+' · '+speed+chunks;if(x.status==='done'){$('fullProgressBar').value=100;$('fullProgressPct').textContent='100%';$('fullProgressText').textContent=tr('fullMapDone')+' · '+formatBytes(x.doneBytes||0);toast(tr('fullMapDone'));setTimeout(()=>location.reload(),900);return}if(x.status==='error'){$('fullProgressText').textContent=tr('fullMapFail')+' '+(x.message||'');return}setTimeout(poll,700)}catch(e){$('fullProgressText').textContent=tr('fullMapFail')}};poll()}catch(e){$('fullProgressText').textContent=tr('fullMapFail')+' '+e.message}
}
async function cacheArea(){const b=map.getBounds(),z=Math.round(map.getZoom()),zmin=Math.max(5,z-1),zmax=Math.min(16,z+1);toast(tr('offlineStart'));try{const u='/api/offline/preload?west='+b.getWest()+'&south='+b.getSouth()+'&east='+b.getEast()+'&north='+b.getNorth()+'&zmin='+zmin+'&zmax='+zmax;const r=await fetch(u);if(!r.ok)throw 0;const j=await r.json();const id=j.id;const poll=async()=>{const x=await (await fetch('/api/offline/job?id='+encodeURIComponent(id))).json();if(x.status==='done'){closeToast();toast(tr('offlineDone')+' '+x.done+'/'+x.total);refreshCacheBadge();return}if(x.status==='error'){closeToast();toast(tr('offlineFail')+' '+(x.message||''));return}$('toastText').textContent=tr('offlineStart')+' '+(x.done||0)+'/'+(x.total||'?');setTimeout(poll,700)};poll()}catch(e){closeToast();toast(tr('offlineFail'))}}
async function refreshCacheBadge(){try{const x=await (await fetch('/api/offline/status')).json();$('netBadge').textContent=(navigator.onLine?'● ':'○ ')+(x.megabytes||0)+' MB';$('netBadge').classList.toggle('online',navigator.onLine);$('netBadge').classList.toggle('offline',!navigator.onLine)}catch(e){}}
function featureLabel(f){const p=f?.properties||{};return (lang==='el'?(p['name:el']||p.name):(p['name:en']||p.name))||p.ref||p.housenumber||p.house_number||''}
async function showPointInfo(e,feats){selectedTarget=e.lngLat.toArray();const detail=feats.find(f=>['poi','housenumber','transportation_name','building'].includes(f.sourceLayer)&&featureLabel(f));if(detail){const p=detail.properties||{},name=featureLabel(detail),parts=[p['addr:street']||p.street,p['addr:housenumber']||p.housenumber,p.class,p.subclass].filter(Boolean);new maplibregl.Popup({closeButton:true,maxWidth:'300px'}).setLngLat(e.lngLat).setHTML('<strong>'+String(name).replace(/[<>&]/g,'')+'</strong><br><small>'+parts.map(x=>String(x).replace(/[<>&]/g,'')).join(' · ')+'</small>').addTo(map);return}try{const r=await fetch('/api/reverse?lat='+e.lngLat.lat+'&lon='+e.lngLat.lng+'&lang='+lang);const x=await r.json();if(x.display_name)new maplibregl.Popup({maxWidth:'320px'}).setLngLat(e.lngLat).setText(x.display_name+(x.offline?' · OFFLINE':'')).addTo(map)}catch(_){} }
function handleMapClick(e){const feats=map.queryRenderedFeatures(e.point);const place=feats.find(f=>f.source==='openmaptiles'&&f.sourceLayer==='place'&&['city','town','village','hamlet','suburb','quarter','neighbourhood','borough'].includes(f.properties?.class));if(place&&mode==='2d'){const c=place.geometry.type==='Point'?place.geometry.coordinates:e.lngLat.toArray();const n=(lang==='el'?(place.properties['name:el']||place.properties.name):(place.properties['name:en']||place.properties.name))||'Place';enter3D(n,c,14.5);return}const featured=feats.find(f=>f.layer?.id==='gos-featured-places');if(featured&&mode==='2d'){const city=FEATURED_PLACES.find(x=>x.id===featured.properties.id);if(city)enter3D(lang==='el'?city.name:city.en,city.c,14.5);return}const data=feats.find(f=>f.layer?.id==='gos-data-cities');if(data&&mode==='2d'){const id=data.properties.id,city=DATA_CITIES.find(x=>x.id===id);if(city)enter3D(lang==='el'?city.name:city.en,city.c,14.5);return}if(mode==='3d')showPointInfo(e,feats)}
map=new maplibregl.Map({container:'map',style:STYLE[theme],center:[23.45,38.55],zoom:5.15,pitch:0,bearing:0,minZoom:4,maxZoom:20,maxPitch:82,maxBounds:[[16,32.2],[32.7,44.2]],renderWorldCopies:false,antialias:true,attributionControl:true,transformRequest:(url,type)=>{if(/^https?:\/\//i.test(url))return {url:'/api/proxy?url='+encodeURIComponent(url)};return {url}}});
map.on('load',()=>{buildCustom();fetch('/api/config').then(r=>r.json()).then(c=>{trafficAvailable=!!c.traffic;$('trafficBtn').disabled=!trafficAvailable;refreshCacheBadge()}).catch(()=>{})});map.on('style.load',()=>{if(!styleReady)buildCustom()});map.on('click',handleMapClick);map.on('dragstart',()=>{gpsFollow=false;$('locateBtn').classList.remove('active')});
$('themeBtn').onclick=switchTheme;$('elBtn').onclick=()=>setLang('el');$('enBtn').onclick=()=>setLang('en');$('homeBtn').onclick=home;$('backBtn').onclick=home;$('locateBtn').onclick=locate;$('wifiBtn').onclick=()=>setWifiOnly(!wifiOnly);$('trafficBtn').onclick=toggleTraffic;$('routeBtn').onclick=startRoute;$('offlineBtn').onclick=openOfflinePanel;$('offlineClose').onclick=closeOfflinePanel;$('offlineAreaBtn').onclick=()=>{closeOfflinePanel();cacheArea()};$('routeClose').onclick=clearRoute;$('netBadge').onclick=refreshCacheBadge;$('wifiClose').onclick=()=>$('wifiPanel').classList.remove('open');$('wifiPlay').onclick=toggleWifiPlay;$('wifiDate').onchange=e=>renderWifiDate(e.target.value);document.querySelectorAll('[data-joy]').forEach(b=>b.onclick=()=>joy(b.dataset.joy));$('searchForm').onsubmit=e=>{e.preventDefault();doSearch($('searchInput').value)};document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap'))$('results').classList.remove('open')});window.addEventListener('online',refreshCacheBadge);window.addEventListener('offline',refreshCacheBadge);
setLang('el');
})();
</script>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    server_version = f"GreekOS/{VERSION}"

    def log_message(self, fmt, *args):
        sys.stdout.write("[GreekOS] " + (fmt % args) + "\n")

    def send_bytes(self, data: bytes, content_type: str, status: int = 200, extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store" if content_type.startswith("application/json") else "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, status=200):
        self.send_bytes(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        try:
            if path in ("/", "/index.html"):
                self.send_bytes(HTML.encode("utf-8"), "text/html; charset=utf-8")
                return
            if path == "/vendor/maplibre-gl.js":
                asset = ensure_vendor_asset("maplibre-gl.js", MAPLIBRE_JS_URL)
                if asset.exists():
                    self.send_bytes(asset.read_bytes(), "text/javascript; charset=utf-8", extra_headers={"Cache-Control":"public, max-age=31536000"})
                else:
                    self.send_bytes(b"console.error('GreekOS: MapLibre asset is not cached and internet is unavailable.');", "text/javascript; charset=utf-8", 503)
                return
            if path == "/vendor/maplibre-gl.css":
                asset = ensure_vendor_asset("maplibre-gl.css", MAPLIBRE_CSS_URL)
                if asset.exists():
                    self.send_bytes(asset.read_bytes(), "text/css; charset=utf-8", extra_headers={"Cache-Control":"public, max-age=31536000"})
                else:
                    self.send_bytes(b"", "text/css; charset=utf-8", 503)
                return
            if path == "/api/style":
                theme = (qs.get("theme") or ["dark"])[0]
                remote = "https://tiles.openfreemap.org/styles/bright" if theme == "light" else "https://tiles.openfreemap.org/styles/dark"
                try:
                    data, ctype, stale = disk_http_get(remote, accept="application/json", timeout=25, max_age=7*24*3600)
                    meta = mbtiles_metadata()
                    if meta and meta.get("format") in ("pbf","mvt"):
                        try:
                            style=json.loads(data.decode("utf-8","replace"))
                            if isinstance(style.get("sources"),dict) and "openmaptiles" in style["sources"]:
                                style["sources"]["openmaptiles"]={"type":"vector","tiles":["/api/mbtiles/{z}/{x}/{y}.pbf"],"minzoom":meta["minzoom"],"maxzoom":meta["maxzoom"],"attribution":"© OpenStreetMap contributors"}
                                data=json.dumps(style,ensure_ascii=False,separators=(",",":")).encode("utf-8")
                        except Exception:
                            pass
                    self.send_bytes(data, "application/json; charset=utf-8", extra_headers={"X-GreekOS-Cache":"stale" if stale else "fresh"})
                except Exception as exc:
                    self.send_json({"error":f"map style unavailable: {exc}"}, 503)
                return
            m = re.fullmatch(r"/api/mbtiles/(\d+)/(\d+)/(\d+)\.(?:pbf|mvt|png|jpg|jpeg|webp)", path)
            if m:
                z,x,y=map(int,m.groups())
                data,ctype,enc=mbtiles_tile(z,x,y)
                if data is None:
                    self.send_bytes(b"", "application/octet-stream", 404); return
                headers={"Cache-Control":"public, max-age=31536000"}
                if enc: headers["Content-Encoding"]=enc
                self.send_bytes(data,ctype,extra_headers=headers); return
            if path == "/api/proxy":
                target = (qs.get("url") or [""])[0]
                try:
                    parsed_target = urllib.parse.urlparse(target)
                    host = (parsed_target.hostname or "").lower()
                    allowed = host in PROXY_ALLOW_HOSTS or any(host.endswith("." + h) for h in PROXY_ALLOW_HOSTS)
                    if parsed_target.scheme not in ("http","https") or not allowed:
                        self.send_json({"error":"proxy host not allowed"}, 403); return
                    # Map vector/terrain/font/sprite resources are cacheable for offline reuse.
                    data, ctype, stale = disk_http_get(target, timeout=30, max_age=30*24*3600)
                    self.send_bytes(data, ctype, extra_headers={"Cache-Control":"public, max-age=86400", "X-GreekOS-Cache":"stale" if stale else "fresh"})
                except Exception as exc:
                    self.send_json({"error":f"resource unavailable offline: {exc}"}, 502)
                return
            if path == "/api/config":
                stats = cache_stats()
                self.send_json({"version": VERSION, "traffic": bool(TRAFFIC_KEY), "cache": stats, "home": str(GREEKOS_HOME), "mbtiles": bool(mbtiles_metadata()), "nominatim": NOMINATIM, "router": OSRM, "fullMap": full_map_info()})
                return
            if path == "/api/search":
                q = (qs.get("q") or [""])[0].strip()
                lang = (qs.get("lang") or ["el"])[0]
                if len(q) < 2:
                    self.send_json([])
                else:
                    self.send_json(search_greece(q[:160], lang))
                return
            if path == "/api/reverse":
                lat = float((qs.get("lat") or ["0"])[0])
                lon = float((qs.get("lon") or ["0"])[0])
                lang = (qs.get("lang") or ["el"])[0]
                if not (32 < lat < 44.5 and 16 < lon < 33):
                    self.send_json({"error": "outside Greece bounds"}, 400)
                else:
                    self.send_json(reverse_greece(lat, lon, lang))
                return
            if path == "/api/route":
                slon=float((qs.get("slon") or ["0"])[0]); slat=float((qs.get("slat") or ["0"])[0])
                elon=float((qs.get("elon") or ["0"])[0]); elat=float((qs.get("elat") or ["0"])[0])
                if not all((16 < slon < 33, 32 < slat < 44.5, 16 < elon < 33, 32 < elat < 44.5)):
                    self.send_json({"error":"route outside Greece bounds"},400)
                else:
                    try: self.send_json(route_greece(slon,slat,elon,elat))
                    except Exception as exc: self.send_json({"error":str(exc)},502)
                return
            if path == "/api/offline/packages":
                self.send_json(package_catalog_info()); return
            if path == "/api/offline/package/start":
                tier=(qs.get("tier") or ["lite"])[0]
                job=start_package_download(tier)
                status=200 if job.get("status") != "error" else 400
                self.send_json(job,status); return
            if path == "/api/offline/full-map/info":
                self.send_json(full_map_info()); return
            if path == "/api/offline/full-map/start":
                job=start_full_map_download()
                status=200 if job.get("status") != "error" else 503
                self.send_json(job,status); return
            if path == "/api/offline/status":
                self.send_json(cache_stats()); return
            if path == "/api/offline/preload":
                west=float((qs.get("west") or ["0"])[0]); south=float((qs.get("south") or ["0"])[0])
                east=float((qs.get("east") or ["0"])[0]); north=float((qs.get("north") or ["0"])[0])
                zmin=max(4,min(16,int((qs.get("zmin") or ["10"])[0]))); zmax=max(zmin,min(16,int((qs.get("zmax") or ["12"])[0])))
                if not (-180 <= west <= 180 and -180 <= east <= 180 and -85 <= south <= 85 and -85 <= north <= 85):
                    self.send_json({"error":"invalid bounds"},400)
                else:
                    self.send_json(start_preload((west,south,east,north),zmin,zmax))
                return
            if path == "/api/offline/job":
                job=get_job((qs.get("id") or [""])[0])
                self.send_json(job if job else {"error":"job not found"}, 200 if job else 404); return
            if path == "/api/athens-wifi":
                try:
                    self.send_json(get_athens_wifi())
                except Exception as exc:
                    self.send_json({"error": str(exc)}, 502)
                return
            m = re.fullmatch(r"/api/traffic/(\d+)/(\d+)/(\d+)\.png", path)
            if m:
                if not TRAFFIC_KEY:
                    self.send_json({"error": "traffic API key not configured"}, 404)
                    return
                z, x, y = m.groups()
                url = f"https://api.tomtom.com/traffic/map/4/tile/flow/relative0/{z}/{x}/{y}.png?tileSize=256&key={urllib.parse.quote(TRAFFIC_KEY)}"
                tile, ctype, stale = disk_http_get(url, accept="image/png", timeout=15, max_age=90)
                self.send_bytes(tile, ctype if ctype.startswith("image/") else "image/png", extra_headers={"Cache-Control": "public, max-age=60", "X-GreekOS-Cache":"stale" if stale else "fresh"})
                return
            self.send_json({"error": "not found"}, 404)
        except urllib.error.HTTPError as exc:
            self.send_json({"error": f"upstream HTTP {exc.code}"}, 502)
        except urllib.error.URLError as exc:
            self.send_json({"error": f"upstream unavailable: {exc.reason}"}, 502)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)


def pick_port(preferred=DEFAULT_PORT):
    for port in [preferred, 0]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
            chosen = sock.getsockname()[1]
            return chosen
        except OSError:
            pass
        finally:
            sock.close()
    raise RuntimeError("No local port available")


def open_browser(url: str):
    def runner():
        time.sleep(0.7)
        try:
            if shutil.which("termux-open-url"):
                subprocess.Popen(["termux-open-url", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            if shutil.which("am") and os.environ.get("ANDROID_ROOT"):
                subprocess.Popen(["am", "start", "-a", "android.intent.action.VIEW", "-d", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            webbrowser.open(url, new=2)
        except Exception:
            pass
    threading.Thread(target=runner, daemon=True).start()


def main():
    init_db()
    # Build a useful offline nationwide settlement index in the background after
    # the first successful online run. The app never blocks startup waiting for it.
    threading.Thread(target=geonames_import, daemon=True).start()
    threading.Thread(target=warm_core_assets, daemon=True).start()
    port = pick_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    # localhost is treated as a trustworthy browser origin and is the most
    # reliable local origin for Geolocation permissions across desktop/mobile.
    url = f"http://localhost:{port}/"
    stats = cache_stats()
    print(f"\n{APP_NAME} {VERSION}")
    print(f"Open: {url}")
    print("Offline-first: map/vector/terrain/font/sprite resources are cached as you use them.")
    print(f"Project map assets: {GREEKOS_HOME} ({stats['megabytes']} MB, {stats['files']} resources)")
    print("Search: live Greece-wide addresses/roads/shops/places when online + cached results/GeoNames offline.")
    print("Navigation: live OSRM routing when online + previously calculated routes offline.")
    if TRAFFIC_KEY:
        print("Live traffic: enabled (recent tiles are also cached temporarily)")
    else:
        print("Live traffic: optional (set GREEKOS_TOMTOM_API_KEY before launch)")
    print("Use the ⇩ map button for offline options: save the current area or install Lite/Standard/Enhanced/Detailed/Full Greece packages.")
    print("Press Ctrl+C to stop.\n")
    open_browser(url)
    try:
        server.serve_forever(poll_interval=0.4)
    except KeyboardInterrupt:
        print("\nStopping GreekOS…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
