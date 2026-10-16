#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export VANO_TOOLS="${VANO_TOOLS:-/workspace/tools}"
export BLENDER_USER_CONFIG="$VANO_TOOLS/blender-config"
export DOTNET_CLI_HOME="$VANO_TOOLS/dotnet-home" NUGET_PACKAGES="$VANO_TOOLS/nuget"
PY="$VANO_TOOLS/venv/bin/python"
"$PY" scripts/texturas.py
VANO_SKIP_RENDERS=1 blender -b -t 4 --python-exit-code 1 --python scripts/construir.py
AP_SKIP_RENDERS=1 blender -b -t 4 --python-exit-code 1 --python scripts/finalizar.py
"$PY" scripts/preparar_meta.py
"$VANO_TOOLS/dotnet/dotnet" build scripts/compilador -c Release -m:2 -p:CodeWalkerRoot="$VANO_TOOLS/CodeWalker"
"$VANO_TOOLS/dotnet/dotnet" scripts/compilador/bin/Release/net8.0/vano_compilador.dll . "$VANO_TOOLS"
"$PY" scripts/validar_gta.py
blender -b -t 2 --python-exit-code 1 --python scripts/validar_blender.py
blender -b -t 2 --python-exit-code 1 --python scripts/validar_blender.py -- --colisao-compilada
blender -b --python-exit-code 1 --python scripts/salvar_pecas.py
if [ "${AP_RENDER:-0}" = 1 ]; then
 blender -b -t 4 --python-exit-code 1 --python scripts/renderizar.py
fi
