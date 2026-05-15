#!/bin/bash
set -e

BK="./backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BK"

echo "📦 Criando backup..."
find . -type f -name "*.html" \
  -not -path "./.venv/*" \
  -not -path "./backup*/*" \
  -not -path "./.git/*" \
  -exec grep -lE "lia-text-muted|lia-rounded" {} \; | \
  while read f; do
    mkdir -p "$BK/$(dirname "$f")"
    cp "$f" "$BK/$f"
  done
echo "📦 Backup em: $BK"
echo ""

echo "🔄 Migrando (sem \b — compatível com BSD sed do macOS)..."
find . -type f -name "*.html" \
  -not -path "./.venv/*" \
  -not -path "./backup*/*" \
  -not -path "./.git/*" \
  -exec sed -i '' 's/lia-text-muted/text-muted/g; s/lia-rounded/rounded/g' {} \;

echo "✅ Migração concluída."
echo ""
echo "🔍 Restantes:"
grep -rn "lia-text-muted\|lia-rounded" . \
  --include="*.html" \
  --exclude-dir=".venv" --exclude-dir="backup*" --exclude-dir=".git" \
  | wc -l
