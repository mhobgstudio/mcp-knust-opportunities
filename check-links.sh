#!/usr/bin/env bash
# Re-verify every URL cited in the MCP report. Reports non-200s.
# Usage: bash check-links.sh [report.tex]
set -u
unset all_proxy ALL_PROXY http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
TEX="${1:-mcp-knust-workshops-report.tex}"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
TMP="$(mktemp -d)"
grep -oE 'https?://[^{}\\ ]+' "$TEX" | sed 's/[),.;:]*$//' | sort -u > "$TMP/urls.txt"
echo "Checking $(wc -l < "$TMP/urls.txt") unique URLs..."
cat "$TMP/urls.txt" | xargs -P 14 -I{} sh -c \
  'code=$(curl -sL -o /dev/null --max-time 18 -A "'"$UA"'" -w "%{http_code}" "{}" 2>/dev/null); echo "$code {}"' \
  > "$TMP/results.txt" 2>/dev/null
echo "--- summary ---"
awk '{print $1}' "$TMP/results.txt" | sort | uniq -c | sort -rn
echo "--- non-200 ---"
awk '$1!=200' "$TMP/results.txt" | sort -n
echo "--- done ($(date -Iseconds)) ---"
rm -rf "$TMP"
