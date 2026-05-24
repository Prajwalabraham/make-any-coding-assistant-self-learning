#!/usr/bin/env bash
# Kept as a one-shot copy (no symlink, no submodule) so each target
# project owns its memory store and skills independently. Sharing the
# same .claude/ across repos would cross-contaminate learned context.
set -euo pipefail

target="${1:-}"
force="${2:-}"

if [[ -z "$target" ]]; then
  echo "usage: $0 <target-project-dir> [--force]" >&2
  exit 1
fi

src="$(cd "$(dirname "$0")" && pwd)/.claude"
dest="$(cd "$target" && pwd)/.claude"

if [[ -e "$dest" ]]; then
  if [[ "$force" != "--force" ]]; then
    echo "$dest already exists. Re-run with --force to overwrite." >&2
    exit 1
  fi
  rm -rf "$dest"
fi

cp -R "$src" "$dest"
chmod +x "$dest/hooks/"*.py 2>/dev/null || true
echo "Installed self-learning .claude/ into $dest"
echo "Next: open the project in Claude Code. The SessionStart hook will bootstrap."
