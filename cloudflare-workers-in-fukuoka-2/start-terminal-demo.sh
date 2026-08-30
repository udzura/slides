#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SLIDES_PORT=${SLIDES_PORT:-8080}
TERMINAL_PORT=7681
TMUX_SESSION=uzumibi-demo
DECK_SOURCE=${DECK_SOURCE:-index-with-demo.md}
DECK_OUTPUT=${DECK_OUTPUT:-demo.html}
HTTP_PID=
TTYD_PID=

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Required command not found: %s\n' "$1" >&2
    return 1
  fi
}

cleanup() {
  if [ -n "$TTYD_PID" ]; then
    kill "$TTYD_PID" 2>/dev/null || true
  fi
  if [ -n "$HTTP_PID" ]; then
    kill "$HTTP_PID" 2>/dev/null || true
  fi
}

require_command marp
require_command python3
require_command tmux
if ! require_command ttyd; then
  printf 'Install it with: brew install ttyd\n' >&2
  exit 1
fi

if [ "$#" -gt 0 ]; then
  DEMO_CWD=$1
elif [ -n "${UZUMIBI_DEMO_CWD:-}" ]; then
  DEMO_CWD=$UZUMIBI_DEMO_CWD
elif command -v ghq >/dev/null 2>&1; then
  GHQ_ROOT=$(ghq root)
  DEMO_CWD=$GHQ_ROOT/github.com/mrubyedge/uzumibi
else
  DEMO_CWD=$SCRIPT_DIR
fi

if [ ! -d "$DEMO_CWD" ]; then
  printf 'Demo directory not found: %s\n' "$DEMO_CWD" >&2
  printf 'Pass it as the first argument or set UZUMIBI_DEMO_CWD.\n' >&2
  exit 1
fi

DEMO_CWD=$(CDPATH= cd -- "$DEMO_CWD" && pwd)

trap cleanup EXIT INT TERM HUP

cd "$SCRIPT_DIR"
printf 'Generating %s...\n' "$DECK_OUTPUT"
marp --html --allow-local-files --output "$DECK_OUTPUT" "$DECK_SOURCE"

printf 'Starting slide server on http://127.0.0.1:%s/%s\n' "$SLIDES_PORT" "$DECK_OUTPUT"
python3 -m http.server "$SLIDES_PORT" --bind 127.0.0.1 --directory "$SCRIPT_DIR" &
HTTP_PID=$!

printf 'Starting terminal server in %s\n' "$DEMO_CWD"
ttyd \
  --interface 127.0.0.1 \
  --port "$TERMINAL_PORT" \
  --writable \
  --check-origin \
  --max-clients 1 \
  --cwd "$DEMO_CWD" \
  tmux new-session -A -s "$TMUX_SESSION" &
TTYD_PID=$!

printf '\nReady:\n'
printf '  Slides:   http://127.0.0.1:%s/%s\n' "$SLIDES_PORT" "$DECK_OUTPUT"
printf '  Terminal: http://127.0.0.1:%s/\n' "$TERMINAL_PORT"
printf '  tmux:     %s\n' "$TMUX_SESSION"
printf '\nPress Ctrl-C to stop the HTTP and terminal servers.\n'

wait "$TTYD_PID"
