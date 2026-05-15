#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

OS="$(uname -s)"

if [[ "$OS" == "Linux" ]]; then
    if ! dpkg -s libsdl2-dev &>/dev/null; then
        echo "Installing SDL2 system dependency..."
        sudo apt-get update -qq && sudo apt-get install -y libsdl2-dev
    fi
fi

echo "Installing dependencies..."
uv sync --all-groups --frozen

echo "Building executable..."
uv run pyinstaller asteroids.spec

case "$OS" in
    Linux|Darwin) OUTPUT="dist/asteroids" ;;
    MINGW*|CYGWIN*|MSYS*) OUTPUT="dist/asteroids.exe" ;;
    *) OUTPUT="dist/asteroids" ;;
esac

echo "Done. Output: $OUTPUT"
