from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile

from modules.platforms import install_system_packages, is_termux, linux_distribution, run_command


def _msg(lang: str, en: str, el: str) -> str:
    return el if lang == "el" else en


def _pip_install(package: str, lang: str = "en") -> bool:
    print(_msg(
        lang,
        f"[Ghost Project] Installing missing Python package: {package}",
        f"[Ghost Project] Εγκατάσταση Python package που λείπει: {package}",
    ))
    try:
        return subprocess.run([sys.executable, "-m", "pip", "install", package], check=False).returncode == 0
    except Exception:
        return False


def _system_install(packages: list[str], lang: str = "en") -> bool:
    if not packages:
        return True
    print(_msg(
        lang,
        "[Ghost Project] Installing missing system package(s): " + ", ".join(packages),
        "[Ghost Project] Εγκατάσταση system package(s) που λείπουν: " + ", ".join(packages),
    ))
    return install_system_packages(packages)


def ensure_runtime(root: Path, lang: str = "en") -> None:
    if importlib.util.find_spec("rich") is None:
        _pip_install("rich", lang)
    if importlib.util.find_spec("PIL") is None:
        _pip_install("pillow", lang)

    missing = []
    if not any(shutil.which(x) for x in ("mpv", "ffplay", "play", "termux-media-player")):
        missing.append("mpv")

    if is_termux():
        if not shutil.which("termux-microphone-record"):
            missing.append("termux-api")
    else:
        if not any(shutil.which(x) for x in ("ffmpeg", "arecord")):
            missing.extend(["ffmpeg", "alsa-utils"])
        if not shutil.which("xdg-open"):
            missing.append("xdg-utils")

    if missing:
        _system_install(missing, lang)


def _ensure_tts_tools(lang: str = "en") -> bool:
    have_tts = bool(shutil.which("espeak") or shutil.which("espeak-ng"))
    have_ffmpeg = bool(shutil.which("ffmpeg"))

    packages = []
    if not have_tts:
        packages.append("espeak-ng" if is_termux() else "espeak")
    if not have_ffmpeg:
        packages.append("ffmpeg")

    if packages:
        _system_install(packages, lang)

    have_tts = bool(shutil.which("espeak") or shutil.which("espeak-ng"))
    have_ffmpeg = bool(shutil.which("ffmpeg"))


    return have_tts and have_ffmpeg


def _narration_jobs(root: Path):
    jobs = []
    specs = [
        ("stories.json", lambda x: f"{x['title']}. {x['summary']}"),
        ("missions.json", lambda x: f"Mission {x['order']}. {x['title']}. {x['summary']}"),
        ("rorke_files.json", lambda x: f"Rorke File {x['collectible_number']}. Mission: {x['mission']}. Archive summary. {x['summary']}"),
        ("extinction_intel.json", lambda x: f"{x['map']} intel. {x['title']}. {x['summary']}"),
    ]
    for filename, make_text in specs:
        path = root / "data" / filename
        if not path.exists():
            continue
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for item in items:
            relative = item.get("audio_narration")
            if relative:
                jobs.append((make_text(item), root / relative))
    return jobs


def ensure_narration(root: Path, lang: str = "en") -> bool:
    missing = [(text, path) for text, path in _narration_jobs(root) if not path.exists()]
    if not missing:
        return True

    print(_msg(
        lang,
        f"[Ghost Project] {len(missing)} narration file(s) are missing. Repairing audio...",
        f"[Ghost Project] Λείπουν {len(missing)} αρχεία αφήγησης. Γίνεται αποκατάσταση ήχου...",
    ))

    if not _ensure_tts_tools(lang):
        print(_msg(
            lang,
            "[Ghost Project] Could not install or find espeak and ffmpeg. The archive will still run without repaired narration.",
            "[Ghost Project] Δεν ήταν δυνατή η εγκατάσταση ή εύρεση των espeak και ffmpeg. Το αρχείο θα συνεχίσει να λειτουργεί χωρίς την αποκατάσταση της αφήγησης.",
        ))
        return False

    espeak = shutil.which("espeak") or shutil.which("espeak-ng")
    ffmpeg = shutil.which("ffmpeg")
    repaired = 0

    for text, out_path in missing:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with tempfile.TemporaryDirectory() as td:
                wav = Path(td) / "speech.wav"
                if not run_command([espeak, "-s", "142", "-p", "42", "-a", "165", "-w", str(wav), text]):
                    continue
                ok = run_command([
                    ffmpeg, "-y", "-loglevel", "error", "-i", str(wav),
                    "-codec:a", "libmp3lame", "-b:a", "48k", "-ac", "1", "-ar", "22050",
                    str(out_path),
                ])
                if ok and out_path.exists():
                    repaired += 1
        except Exception:
            pass

    print(_msg(
        lang,
        f"[Ghost Project] Repaired {repaired}/{len(missing)} narration file(s).",
        f"[Ghost Project] Αποκαταστάθηκαν {repaired}/{len(missing)} αρχεία αφήγησης.",
    ))
    return repaired == len(missing)
