#!/usr/bin/env bash
# facsim — atomic rebuild + publish.
#
# Builds into releases/<timestamp>, prints a diff against the live release,
# then atomically repoints the `current` symlink. Apache's DocumentRoot is
# `current`, so visitors only ever see a complete build. Old releases are
# pruned to the most recent $KEEP.
#
# Layout under $ROOT:
#   src/         the checkout (this repo) with config.yaml
#   releases/    timestamped build outputs
#   current ->   releases/<latest>   (symlink Apache serves)
#
# Usage:  ROOT=/opt/facsim deploy/rebuild.sh
# Cron/systemd set ROOT + ANTHROPIC_API_KEY in the environment.
set -euo pipefail

ROOT="${ROOT:-/opt/facsim}"
SRC="${SRC:-$ROOT/src}"
KEEP="${KEEP:-5}"
CONFIG="${CONFIG:-$SRC/config.yaml}"

ts="$(date -u +%Y%m%dT%H%M%SZ)"
releases="$ROOT/releases"
dest="$releases/$ts"
current="$ROOT/current"

mkdir -p "$releases"

# Diff against whatever is live now (skipped automatically on the first build).
diff_arg=()
if [ -L "$current" ] && [ -f "$current/manifest.json" ]; then
    diff_arg=(--diff-against "$current/manifest.json")
fi

echo "Building $ts into $dest ..."
python -m cache_gen --config "$CONFIG" --output "$dest" "${diff_arg[@]}"

# Atomic swap: build the new symlink beside `current`, then rename over it.
# `mv -T` on a symlink is atomic on Linux, so there is no window where
# `current` is missing or points at a partial tree.
ln -sfn "$dest" "$current.tmp"
mv -Tf "$current.tmp" "$current"
echo "Published -> $(readlink "$current")"

# Prune old releases, keeping the newest $KEEP (and never the live one).
live="$(readlink "$current")"
mapfile -t old < <(ls -1d "$releases"/*/ 2>/dev/null | sort -r | tail -n +$((KEEP + 1)))
for d in "${old[@]:-}"; do
    [ -z "$d" ] && continue
    d="${d%/}"
    [ "$d" = "$live" ] && continue
    echo "Pruning $d"
    rm -rf "$d"
done
