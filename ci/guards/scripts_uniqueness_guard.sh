#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"

declare -A seen
err=0
while IFS= read -r -d '' path; do
  [ -f "$path" ] || continue
  base="$(basename "$path")"
  sum="$(sha256sum "$path" | cut -d' ' -f1)"
  if [[ -n "${seen[$base]:-}" && "${seen[$base]}" != "$sum" ]]; then
    echo "::warning ::duplicate script name with different content: $base"
    err=1
  else
    seen[$base]="$sum"
  fi
done < <(git -C "$root" ls-files 'scripts/**' -z; git -C "$root/.agentpm_workspace" ls-files 'scripts/**' -z 2>/dev/null || true)

[ $err -eq 0 ] && echo "scripts uniqueness ok" || { echo "scripts uniqueness issues"; exit 1; }
