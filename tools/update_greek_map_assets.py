#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "Map Assets" / "Greek Map"
RUNTIME = ASSET_ROOT / "runtime"
SCRIPT = ASSET_ROOT / "GreekOS.py"

RUNTIME.mkdir(parents=True, exist_ok=True)
(RUNTIME / "vendor").mkdir(parents=True, exist_ok=True)
(RUNTIME / "http-cache").mkdir(parents=True, exist_ok=True)

os.environ["GREEKOS_HOME"] = str(RUNTIME)
os.environ["GREEKOS_MAPLIBRE_DIR"] = str(RUNTIME / "vendor")
os.environ["GREEKOS_PROJECT_MODE"] = "1"

spec = importlib.util.spec_from_file_location("ghost_project_greekos", SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit("Could not load GreekOS.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

print("[Greek Map] Initializing local database...")
mod.init_db()

print("[Greek Map] Refreshing browser/runtime assets...")
mod.warm_core_assets()

print("[Greek Map] Refreshing Greece-wide offline place index...")
# Force a weekly refresh by clearing only the marker; ON CONFLICT keeps the DB compact.
try:
    with mod._db_lock:
        conn = mod.db_conn()
        conn.execute("DELETE FROM api_cache WHERE key='geonames:gr:loaded'")
        conn.commit()
        conn.close()
except Exception:
    pass
mod.geonames_import()

print("[Greek Map] Refreshing Athens public aggregate Wi-Fi snapshot...")
try:
    wifi = mod.get_athens_wifi()
    mod.api_cache_set("weekly:athens_wifi", wifi)
    wifi_status = {"ok": True, "stations": len(wifi.get("stations") or [])}
except Exception as exc:
    wifi_status = {"ok": False, "error": str(exc)}
    print(f"[Greek Map] Athens Wi-Fi refresh warning: {exc}")

stats = mod.cache_stats()
manifest = {
    "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "greekos_version": getattr(mod, "VERSION", "unknown"),
    "maplibre_js": (RUNTIME / "vendor" / "maplibre-gl.js").exists(),
    "maplibre_css": (RUNTIME / "vendor" / "maplibre-gl.css").exists(),
    "offline_database": (RUNTIME / "greekos.sqlite3").exists(),
    "cache_files": stats.get("files", 0),
    "cache_megabytes": stats.get("megabytes", 0),
    "athens_wifi": wifi_status,
    "optional_full_greece_mbtiles": (RUNTIME / "greece.mbtiles").exists(),
    "featured_places": len(getattr(mod, "FEATURED_PLACES", [])),
    "wifi_data_places": sorted(getattr(mod, "WIFI_DATA_PLACES", {}).keys()),
    "offline_package_tiers": [t.get("id") for t in mod.load_package_catalog().get("tiers", [])],
    "offline_package_release_tag": mod.load_package_catalog().get("release_tag"),
}
(ASSET_ROOT / "asset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2, ensure_ascii=False))
