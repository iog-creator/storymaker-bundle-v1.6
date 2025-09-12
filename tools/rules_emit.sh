#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
src_dir="$root/docs/SSOT/rules"
dst_dir="$root/.cursor/rules"

[ -d "$src_dir" ] || { echo "::error ::missing rules source dir $src_dir"; exit 1; }
mkdir -p "$dst_dir"

# Mirror *.mdc → .cursor/rules/*.mdc (convert underscores to hyphens for Cursor)
shopt -s nullglob
count=0
for f in "$src_dir"/*.mdc; do
  base="$(basename "${f%.mdc}")"
  # Convert underscores to hyphens for Cursor rules, keep .mdc extension
  cursor_name="$(echo "$base" | sed 's/_/-/g').mdc"
  cp -f "$f" "$dst_dir/$cursor_name"
  count=$((count+1))
done

# Write simple manifest to help guards
if [ $count -gt 0 ]; then
  (
    cd "$src_dir"
    sha256sum *.mdc 2>/dev/null | sed 's/\.mdc$/.md/' | sort -k2
  ) > "$dst_dir/.manifest"
  echo "::notice ::rules emitted: $count → $dst_dir"
else
  echo "::warning ::no .mdc rules found in $src_dir"
fi

echo "rules_emit ok"
