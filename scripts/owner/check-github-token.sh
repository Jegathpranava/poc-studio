#!/usr/bin/env bash
# Checks that GITHUB_TOKEN in .env can act for PoC Studio publishing. Never prints the token.
set -euo pipefail
cd "$(dirname "$0")/../.."
[ -f .env ] || { echo "No .env in $(pwd)"; exit 1; }
TOKEN=$(grep -E '^GITHUB_TOKEN=' .env | head -1 | cut -d= -f2- | tr -d '"'"'"'\r')
[ -n "$TOKEN" ] || { echo "GITHUB_TOKEN is empty in .env"; exit 1; }

hdr=$(mktemp); body=$(mktemp); trap 'rm -f "$hdr" "$body"' EXIT
code=$(curl -s -o "$body" -D "$hdr" -w '%{http_code}' \
  -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" https://api.github.com/user)
if [ "$code" != "200" ]; then echo "GitHub rejected the token (HTTP $code). Make a new one."; exit 1; fi

login=$(sed -n 's/.*"login": *"\([^"]*\)".*/\1/p' "$body" | head -1)
scopes=$(grep -i '^x-oauth-scopes:' "$hdr" | cut -d: -f2- | tr -d '\r' | xargs || true)
echo "Token belongs to: $login"
if [ -n "$scopes" ]; then
  echo "Classic token scopes: $scopes"
  case ",$scopes," in *",repo,"*|*", repo,"*) echo "OK: 'repo' scope covers repo create, contents and issues.";; *) echo "MISSING: 'repo' scope.";; esac
else
  echo "Fine-grained token (scopes are not listed by GitHub)."
  echo "Make sure it has: Repository access = All repositories; Administration, Contents, Issues = Read and write."
fi
[ "$login" = "Jegathpranava" ] || echo "Note: expected owner Jegathpranava."
