from __future__ import annotations

from pathlib import Path
import os
import platform
import shutil
import subprocess


def is_termux() -> bool:
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix or Path("/data/data/com.termux").exists()


def linux_distribution() -> str:
    if is_termux():
        return "termux"
    os_release = Path("/etc/os-release")
    if os_release.exists():
        values = {}
        for line in os_release.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value.strip().strip('"')
        distro = values.get("ID", "").lower()
        like = values.get("ID_LIKE", "").lower()
        if distro in {"ubuntu", "kali", "linuxmint"}:
            return distro
        if "ubuntu" in like or "debian" in like:
            return distro or "debian"
    return platform.system().lower() or "unknown"


def supported_platform_name() -> str:
    distro = linux_distribution()
    names = {
        "termux": "Termux",
        "ubuntu": "Ubuntu",
        "kali": "Kali Linux",
        "linuxmint": "Linux Mint",
    }
    return names.get(distro, distro)


def run_command(command: list[str], timeout: int = 300) -> bool:
    try:
        return subprocess.run(command, check=False, timeout=timeout).returncode == 0
    except Exception:
        return False


def install_system_packages(packages: list[str]) -> bool:
    packages = [p for p in packages if p]
    if not packages:
        return True

    if is_termux():
        if not shutil.which("pkg"):
            return False
        return run_command(["pkg", "install", "-y", *packages], timeout=600)

    if not shutil.which("apt-get"):
        return False

    command = ["apt-get", "install", "-y", *packages]
    if os.geteuid() != 0:
        if not shutil.which("sudo"):
            return False
        command.insert(0, "sudo")
    return run_command(command, timeout=900)


def pictures_directory() -> Path:
    if is_termux():
        return Path.home() / "storage" / "pictures"

    xdg = os.environ.get("XDG_PICTURES_DIR")
    if xdg:
        return Path(os.path.expandvars(os.path.expanduser(xdg)))

    user_dirs = Path.home() / ".config" / "user-dirs.dirs"
    if user_dirs.exists():
        for line in user_dirs.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("XDG_PICTURES_DIR="):
                value = line.split("=", 1)[1].strip().strip('"')
                value = value.replace("$HOME", str(Path.home()))
                return Path(os.path.expandvars(os.path.expanduser(value)))

    return Path.home() / "Pictures"
