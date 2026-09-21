#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

is_termux() {
    [[ "${PREFIX:-}" == *com.termux* ]] || [[ -d /data/data/com.termux ]]
}

install_termux() {
    pkg update -y
    pkg install -y python mpv ffmpeg espeak-ng termux-api
    python -m pip install -r requirements.txt
    if command -v termux-setup-storage >/dev/null 2>&1 && [[ ! -d "$HOME/storage/pictures" ]]; then
        termux-setup-storage || true
    fi
}

install_desktop() {
    if [[ "$(id -u)" -eq 0 ]]; then
        APT=(apt-get)
    elif command -v sudo >/dev/null 2>&1; then
        APT=(sudo apt-get)
    else
        echo "sudo is required to install system packages on this Linux system."
        exit 1
    fi

    "${APT[@]}" update
    "${APT[@]}" install -y python3 python3-venv python3-pip mpv ffmpeg espeak xdg-utils alsa-utils

    python3 -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
}

if is_termux; then
    echo "Setting up Ghost Project for Termux..."
    install_termux
else
    if [[ ! -f /etc/os-release ]]; then
        echo "This setup supports Termux, Ubuntu, Kali Linux, and Linux Mint."
        exit 1
    fi

    . /etc/os-release
    case "${ID:-}" in
        ubuntu|kali|linuxmint)
            echo "Setting up Ghost Project for ${PRETTY_NAME:-Linux}..."
            install_desktop
            ;;
        *)
            if [[ "${ID_LIKE:-}" == *debian* ]] || [[ "${ID_LIKE:-}" == *ubuntu* ]]; then
                echo "Setting up Ghost Project on Debian/Ubuntu-compatible Linux..."
                install_desktop
            else
                echo "This setup supports Termux, Ubuntu, Kali Linux, and Linux Mint."
                exit 1
            fi
            ;;
    esac
fi

chmod +x Run.sh Setup.sh

echo "Setup complete."
echo "Run Ghost Project with: ./Run.sh"
