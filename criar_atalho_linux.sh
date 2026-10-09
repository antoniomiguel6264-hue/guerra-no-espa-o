#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
executable="$project_dir/dist/GuerraNoEspaco/GuerraNoEspaco"
icon="$project_dir/icone.png"

if [[ ! -x "$executable" ]]; then
    printf 'Executável Linux não encontrado: %s\n' "$executable" >&2
    exit 1
fi

if [[ ! -f "$icon" ]]; then
    printf 'Ícone PNG não encontrado: %s\n' "$icon" >&2
    exit 1
fi

if command -v xdg-user-dir >/dev/null 2>&1; then
    desktop_dir="$(xdg-user-dir DESKTOP)"
else
    desktop_dir="$HOME/Desktop"
fi

if [[ -z "$desktop_dir" ]]; then
    desktop_dir="$HOME/Desktop"
fi

escape_exec_arg() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    value="${value//%/%%}"
    printf '"%s"' "$value"
}

write_launcher() {
    local launcher_path="$1"
    cat > "$launcher_path" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Guerra no Espaço
Comment=Jogo de batalha espacial
Exec=$(escape_exec_arg "$executable")
Path=$project_dir
Icon=$icon
Terminal=false
Categories=Game;
StartupNotify=true
EOF
    chmod +x "$launcher_path"
}

mkdir -p "$desktop_dir" "$HOME/.local/share/applications"
write_launcher "$desktop_dir/GuerraNoEspaco.desktop"
write_launcher "$HOME/.local/share/applications/GuerraNoEspaco.desktop"

printf 'Atalho criado na Área de trabalho e no menu de aplicativos.\n'
