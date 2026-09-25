from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import time

_PROCESSES: list[subprocess.Popen] = []


def _msg(lang: str, en: str, el: str) -> str:
    return el if lang == "el" else en


def greek_map_paths(root: Path) -> tuple[Path, Path]:
    asset_root = root / "Map Assets" / "Greek Map"
    return asset_root, asset_root / "GreekOS.py"


def launch_greek_map(root: Path, lang: str = "en") -> tuple[bool, str]:
    asset_root, script = greek_map_paths(root)
    if not script.exists():
        return False, _msg(
            lang,
            f"Greek Map is missing: {script}",
            f"Λείπει το Greek Map: {script}",
        )

    runtime = asset_root / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GREEKOS_HOME"] = str(runtime)
    env["GREEKOS_MAPLIBRE_DIR"] = str(runtime / "vendor")
    env["GREEKOS_PROJECT_MODE"] = "1"

    # Keep the Ghost Project CLI available while the local map server runs.
    try:
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            cwd=str(root),
            env=env,
            stdout=None,
            stderr=None,
            start_new_session=(os.name != "nt"),
        )
        _PROCESSES.append(proc)
        time.sleep(0.35)
        if proc.poll() is not None:
            return False, _msg(
                lang,
                "Greek Map stopped during startup. Check the messages above.",
                "Το Greek Map σταμάτησε κατά την εκκίνηση. Έλεγξε τα μηνύματα πιο πάνω.",
            )
        return True, _msg(
            lang,
            "Greek Map is starting in your browser. The Ghost Project prompt stays available.",
            "Το Greek Map ανοίγει στον browser. Το prompt του Ghost Project παραμένει διαθέσιμο.",
        )
    except Exception as exc:
        return False, _msg(
            lang,
            f"Could not start Greek Map: {exc}",
            f"Δεν ήταν δυνατή η εκκίνηση του Greek Map: {exc}",
        )
