#!/usr/bin/env bash
# render.sh — Renderitza un mockup HTML a PNG amb Chromium headless local.
#
# Ús: ./render.sh <input.html> <output.png>
#   (accepta rutes relatives o absolutes; les converteix a absolutes)
#
# Comandament exacte executat:
#   "$BIN" --headless=new --disable-gpu --hide-scrollbars \
#     --force-device-scale-factor=2 --window-size=390,844 \
#     --screenshot="$OUT_ABS" "file://$IN_ABS"
#
# Sortida: 780×1688 (marc 390×844 a escala 2x).
# NOTA: no passar --user-data-dir (penja en aquest entorn).
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "ERROR: ús: $0 <input.html> <output.png>" >&2
  exit 1
fi

IN=$1
OUT=$2

if [[ ! -f "$IN" ]]; then
  echo "ERROR: el fitxer d'entrada no existeix: $IN" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"

# Rutes absolutes (resol .. i enllaços simbòlics)
IN_ABS=$(realpath "$IN")
OUT_ABS=$(realpath -m "$OUT")

# --- Detecció del navegador (en aquest ordre, mai un únic camí fix) ---
candidates=()
# a) binari al PATH
if c=$(command -v helium 2>/dev/null); then candidates+=("$c"); fi
# b) ruta coneguda d'Helium
candidates+=("/opt/helium-0.15.5.1-x86_64_linux/helium")
# c) glob d'instal·lacions d'Helium a /opt (primer executable que coincideixi)
for f in /opt/helium-*/helium; do
  [[ -x $f ]] && candidates+=("$f")
done
# d) Chromium de l'entorn local
candidates+=("/home/itram/.hermes/tools/chromium-1208/chrome-linux64/chrome")
# e) altres navegadors Chromium/Chrome al PATH
for b in chromium chromium-browser google-chrome google-chrome-stable chrome; do
  if c=$(command -v "$b" 2>/dev/null); then candidates+=("$c"); fi
done

BIN=""
for c in "${candidates[@]}"; do
  if [[ -n $c && -x $c ]]; then
    BIN=$c
    break
  fi
done

if [[ -z $BIN ]]; then
  echo "ERROR: no s'ha trobat cap navegador Chromium/Chrome headless (sense interfície)." >&2
  echo "Candidats provats (cap existeix o és executable):" >&2
  for c in "${candidates[@]}"; do
    echo "  - ${c:-<buit>}" >&2
  done
  exit 1
fi

# --- Renderització ---
CMD=("$BIN" --headless=new --disable-gpu --hide-scrollbars
     --force-device-scale-factor=2 --window-size=390,844
     --screenshot="$OUT_ABS" "file://$IN_ABS")

# evita acceptar un PNG antic si la render falla
rm -f "$OUT_ABS"

if ! "${CMD[@]}"; then
  echo "ERROR: la renderització ha fallat." >&2
  echo "Comandament executat: ${CMD[*]}" >&2
  exit 1
fi

if [[ ! -s $OUT_ABS ]]; then
  echo "ERROR: el PNG de sortida no existeix o té 0 bytes: $OUT_ABS" >&2
  echo "Comandament executat: ${CMD[*]}" >&2
  exit 1
fi

# --- Verificació de la sortida ---
SIZE=$(stat -c '%s' "$OUT_ABS")
DIMS="dimensions desconegudes"
if command -v file >/dev/null 2>&1; then
  f_out=$(file -b "$OUT_ABS") || true
  dim=$(sed -n 's/.*[ ,]\([0-9]\+\) *x *\([0-9]\+\),.*/\1x\2/p' <<<"$f_out" | tr -d ' ')
  [[ -n $dim ]] && DIMS=$dim
elif command -v identify >/dev/null 2>&1; then
  dim=$(identify -format '%wx%h' "$OUT_ABS" 2>/dev/null || true)
  [[ -n $dim ]] && DIMS=$dim
fi

if [[ $DIMS != 780x1688 ]]; then
  echo "WARNING: el contingut no cap exactament al marc 390×844 (s'ha obtingut $DIMS)." >&2
fi

echo "OK: $OUT_ABS ($DIMS, $SIZE bytes)"
