#!/usr/bin/env bash
# Bootstrap for the self-learning-agent installer.
#
# This script only exists so the public install line stays short:
#   curl -fsSL https://raw.githubusercontent.com/Prajwalabraham/make-any-coding-assistant-self-learning/main/install.sh | bash
#
# Everything substantive (interactive prompts, template emission, scope
# resolution) lives in `sla/sla`. The bootstrap downloads the repo
# tarball, drops it into a cache dir, links the `sla` runner onto PATH,
# and hands off to `sla init`.

set -euo pipefail

REPO="${SLA_REPO:-Prajwalabraham/make-any-coding-assistant-self-learning}"
REF="${SLA_REF:-main}"
CACHE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/self-learning-agent"
BIN_DIR="${SLA_BIN_DIR:-$HOME/.local/bin}"

say()  { printf '  \033[1;36m%s\033[0m %s\n' "$1" "$2"; }
fail() { printf '  \033[1;31merror\033[0m %s\n' "$1" >&2; exit 1; }

command -v curl >/dev/null 2>&1 || fail "curl is required."
command -v tar  >/dev/null 2>&1 || fail "tar is required."

say "==>" "Fetching $REPO@$REF"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$REF" \
  | tar -xz -C "$tmp"

src="$(find "$tmp" -maxdepth 1 -type d -name "*-$REF" | head -n1)"
[[ -n "$src" ]] || fail "extracted archive missing expected directory"

mkdir -p "$CACHE_DIR" "$BIN_DIR"
rm -rf "$CACHE_DIR/sla"
cp -R "$src/sla" "$CACHE_DIR/sla"
chmod +x "$CACHE_DIR/sla/sla"

ln -sf "$CACHE_DIR/sla/sla" "$BIN_DIR/sla"
say "==>" "Installed sla -> $BIN_DIR/sla"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) say "note" "Add $BIN_DIR to PATH to use 'sla' directly." ;;
esac

exec "$CACHE_DIR/sla/sla" init "$@"
