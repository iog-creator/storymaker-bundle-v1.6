#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
src_dir="$root/docs/SSOT/rules"
dst_dir="$root/.cursor/rules"

[ -d "$src_dir" ] || { echo "::error ::missing $src_dir"; exit 1; }
[ -d "$dst_dir" ] || { echo "::error ::missing $dst_dir (run: make rules.emit)"; exit 1; }

shopt -s nullglob
src_rules=("$src_dir"/*.mdc)
[ ${#src_rules[@]} -gt 0 ] || { echo "::error ::no source rules (*.mdc) in $src_dir"; exit 1; }

err=0
for s in "${src_rules[@]}"; do
  base="$(basename "${s%.mdc}")"
  # Convert underscores to hyphens to match emitter, keep .mdc extension
  cursor_name="$(echo "$base" | sed 's/_/-/g').mdc"
  d="$dst_dir/$cursor_name"
  if [ ! -f "$d" ]; then
    echo "::error ::missing emitted rule: $d (run: make rules.emit)"
    err=1
    continue
  fi
  # Compare hashes (content is copied 1:1 by emitter)
  sh_s="$(sha256sum "$s" | cut -d' ' -f1)"
  sh_d="$(sha256sum "$d" | cut -d' ' -f1)"
  if [ "$sh_s" != "$sh_d" ]; then
    echo "::error ::rule content drift: $cursor_name"
    err=1
  fi
done

# Ensure no stale extras in .cursor/rules (ignore .manifest)
while IFS= read -r -d '' f; do
  b="$(basename "$f")"
  [ "$b" = ".manifest" ] && continue
  # Check if source file exists (either with underscores or hyphens)
  src_name_underscore="$(echo "${b%.mdc}" | sed 's/-/_/g').mdc"
  src_name_hyphen="${b%.mdc}.mdc"
  if [ -f "$src_dir/$src_name_underscore" ] || [ -f "$src_dir/$src_name_hyphen" ]; then
    : # Source exists, this is fine
  else
    echo "::error ::stale emitted rule: $b (delete or re-emit)"; err=1
  fi
done < <(find "$dst_dir" -maxdepth 1 -type f -name '*.mdc' -print0)

[ $err -eq 0 ] && echo "rules_presence_guard: OK" || exit 1
