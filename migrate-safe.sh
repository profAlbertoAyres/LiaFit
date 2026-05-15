#!/bin/bash
# migrate-safe.sh — compatível com Bash 3.2 (macOS)

set -e

BACKUP_DIR="./backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r templates/ "$BACKUP_DIR/"
echo "📦 Backup criado em: $BACKUP_DIR"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_INPLACE=(-i '')
else
  SED_INPLACE=(-i)
fi

# Formato: "classe-antiga|classe-nova"
MIGRATIONS=(
  "lia-text-muted|text-muted"
  "lia-rounded|rounded"
)

echo "🔄 Iniciando migração..."
echo ""

for pair in "${MIGRATIONS[@]}"; do
  old="${pair%|*}"
  new="${pair#*|}"
  count_before=$(grep -rn "$old" templates/ 2>/dev/null | wc -l | tr -d ' ')
  echo "→ $old ($count_before ocorrências)  ➜  $new"
  find templates/ -name "*.html" -exec \
    sed -E "${SED_INPLACE[@]}" "s/\\b${old}\\b/${new}/g" {} \;
done

echo ""
echo "✅ Migração concluída."
echo ""
echo "🔍 Verificando resultado..."
for pair in "${MIGRATIONS[@]}"; do
  old="${pair%|*}"
  count_after=$(grep -rn "$old" templates/ 2>/dev/null | wc -l | tr -d ' ')
  echo "   $old → $count_after restantes"
done

