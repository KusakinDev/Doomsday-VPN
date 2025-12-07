#!/bin/bash

URLS_FILE=""

for arg in "$@"; do
  case "$arg" in
    --file=*) URLS_FILE="${arg#--file=}" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$URLS_FILE" ]; then
  URLS_FILE="$SCRIPT_DIR/../urls.txt"
fi

mapfile -t URLS < <(sed -e 's/^\s\+//;s/\s\+$//' "$URLS_FILE" | grep -v '^$' | grep -v '^#')

best_host=""
best_score=-9999999

for host in "${URLS[@]}"; do
  # Ping: try to get avg ms. Support Linux and macOS output.
  avg_ms=""
  ping_out=$(ping -c 2 "$host" 2>/dev/null)
  if [ -n "$ping_out" ]; then
    avg_ms=$(printf "%s" "$ping_out" | awk -F'/' '/rtt|round-trip/ {print $5; exit}')
    if [ -z "$avg_ms" ]; then
      # fallback: parse first reply time
      avg_ms=$(printf "%s" "$ping_out" | awk -F'time=' '/time=/ {print $2; exit}' | awk '{print $1}')
    fi
  fi

  # Normalize avg_ms to a number (remove trailing ms)
  avg_ms=$(printf '%s' "$avg_ms" | sed 's/ms$//')
  if [ -z "$avg_ms" ]; then
    avg_ms=999999
  fi

  # HTTPS check: prefer 2xx/3xx codes
  http_code=$(curl -sI --connect-timeout 3 -m 5 "https://$host" 2>/dev/null | head -n1 | awk '{print $2}')
  https_up=0
  if [ -n "$http_code" ]; then
    case "$http_code" in
      2*|3*) https_up=1 ;;
    esac
  fi

  # Score: reachable HTTPS gets a big bonus; lower avg_ms is better
  # We compute: score = (https_up ? 100000 : 0) - avg_ms
  score=$(( (https_up * 100000) - (avg_ms + 0) ))

  # Debug: uncomment to see per-host stats
  # printf "%s: https=%s avg=%s score=%s\n" "$host" "$https_up" "$avg_ms" "$score"

  if [ "$score" -gt "$best_score" ]; then
    best_score=$score
    best_host=$host
  fi
done

if [ -z "$best_host" ]; then
  echo "No reachable hosts found." >&2
  exit 3
fi

echo "$best_host"

exit 0
