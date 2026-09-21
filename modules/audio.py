from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import webbrowser

from modules.platforms import install_system_packages, is_termux


def _msg(lang: str, en: str, el: str) -> str:
    return el if lang == "el" else en


def _run(cmd: list[str]) -> bool:
    try:
        return subprocess.run(cmd, check=False).returncode == 0
    except Exception:
        return False


def open_url(url: str) -> bool:
    if shutil.which("termux-open-url"):
        return _run(["termux-open-url", url])
    if shutil.which("xdg-open"):
        return _run(["xdg-open", url])
    try:
        return bool(webbrowser.open(url))
    except Exception:
        return False


def play_file(path: Path, lang: str = "en") -> tuple[bool, str]:
    if not path.exists():
        return False, _msg(lang, f"Audio file not found: {path}", f"Το αρχείο ήχου δεν βρέθηκε: {path}")

    if shutil.which("termux-media-player"):
        ok = _run(["termux-media-player", "play", str(path)])
        return ok, _msg(lang, "Started with Termux media player." if ok else "Termux media player failed.", "Ξεκίνησε με το Termux media player." if ok else "Το Termux media player απέτυχε.")

    if not any(shutil.which(x) for x in ("mpv", "ffplay", "play")):
        install_system_packages(["mpv"])

    for player in ("mpv", "ffplay", "play"):
        if shutil.which(player):
            cmd = ["ffplay", "-nodisp", "-autoexit", str(path)] if player == "ffplay" else [player, str(path)]
            ok = _run(cmd)
            return ok, _msg(lang, f"Played with {player}." if ok else f"{player} failed.", f"Αναπαραγωγή με {player}." if ok else f"Το {player} απέτυχε.")

    return False, _msg(lang, "No supported audio player is available.", "Δεν υπάρχει διαθέσιμο υποστηριζόμενο πρόγραμμα αναπαραγωγής ήχου.")


def play_entry_audio(root: Path, item: dict, lang: str = "en") -> tuple[bool, str]:
    candidates = [("original", item.get("audio_original")), ("narration", item.get("audio_narration"))]
    missing = []
    for label, relative in candidates:
        if not relative:
            continue
        path = root / relative
        if path.exists():
            ok, msg = play_file(path, lang)
            if ok:
                lab = ("Αυθεντικός" if label == "original" else "Αφήγηση") if lang == "el" else label.title()
                return True, f"{lab} audio: {msg}"
            return False, msg
        missing.append(str(path))

    if missing:
        return False, _msg(lang, "No local audio found. Checked:\n  ", "Δεν βρέθηκε τοπικός ήχος. Ελέγχθηκαν:\n  ") + "\n  ".join(missing)
    return False, _msg(lang, "This entry has no configured audio.", "Αυτή η καταχώρηση δεν έχει ρυθμισμένο ήχο.")


def record_voice(root: Path, filename: str, lang: str = "en") -> tuple[bool, str]:
    safe = "".join(c for c in filename if c.isalnum() or c in "._-").strip(".")
    if not safe:
        return False, _msg(lang, "Invalid filename.", "Μη έγκυρο όνομα αρχείου.")

    target_dir = root / "audio" / "user"
    target_dir.mkdir(parents=True, exist_ok=True)

    if is_termux():
        if not safe.lower().endswith((".m4a", ".aac", ".mp3", ".wav")):
            safe += ".m4a"
        target = target_dir / safe
        if not shutil.which("termux-microphone-record"):
            install_system_packages(["termux-api"])
        if not shutil.which("termux-microphone-record"):
            return False, _msg(
                lang,
                "The Termux:API command is unavailable. Install the Termux:API Android companion app, then run Setup.sh again.",
                "Η εντολή Termux:API δεν είναι διαθέσιμη. Εγκατέστησε την εφαρμογή Termux:API στο Android και μετά τρέξε ξανά το Setup.sh.",
            )
        ok = _run(["termux-microphone-record", "-f", str(target)])
        if ok:
            return True, _msg(lang, f"Recording started: {target}\nStop it with: termux-microphone-record -q", f"Η ηχογράφηση ξεκίνησε: {target}\nΣταμάτησέ την με: termux-microphone-record -q")
        return False, _msg(lang, "Could not start recording. Check microphone permission for Termux:API.", "Δεν ήταν δυνατό να ξεκινήσει η ηχογράφηση. Έλεγξε την άδεια μικροφώνου για το Termux:API.")

    if not safe.lower().endswith(".wav"):
        safe += ".wav"
    target = target_dir / safe

    if shutil.which("ffmpeg"):
        command = ["ffmpeg", "-y", "-f", "pulse", "-i", "default", str(target)]
        try:
            subprocess.Popen(command)
            return True, _msg(lang, f"Recording started: {target}\nStop it with Ctrl+C in the ffmpeg process.", f"Η ηχογράφηση ξεκίνησε: {target}\nΣταμάτησέ την με Ctrl+C στη διεργασία ffmpeg.")
        except Exception:
            pass

    if shutil.which("arecord"):
        try:
            subprocess.Popen(["arecord", "-f", "cd", str(target)])
            return True, _msg(lang, f"Recording started: {target}\nStop the arecord process when finished.", f"Η ηχογράφηση ξεκίνησε: {target}\nΣταμάτησε τη διεργασία arecord όταν τελειώσεις.")
        except Exception:
            pass

    install_system_packages(["ffmpeg"])
    return False, _msg(lang, "No supported microphone recorder is available yet. Run Setup.sh and try again.", "Δεν υπάρχει ακόμη διαθέσιμο υποστηριζόμενο recorder μικροφώνου. Τρέξε το Setup.sh και δοκίμασε ξανά.")
