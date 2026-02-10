#!/bin/bash
# Script para obtener los channel_ids de canales de YouTube
# Uso: bash obtener_channel_ids.sh

echo "Extrayendo channel IDs de YouTube..."
echo "====================================="
echo ""

# Array de canales
declare -a channels=(
    "@InstitutoACC"
    "@ESPNFans"
    "@pablochucrel7"
    "@joavalenzuela"
    "@TNTSportsAR"
    "@tycsports"
    "@lavozcomar"
    "@RadioSuquía-f7u"
    "@cadena3"
)

# Extraer channel_ids
for handle in "${channels[@]}"; do
  echo "Canal: $handle"
  channel_id=$(curl -s "https://www.youtube.com/$handle" | grep -o 'channel_id=[^"&]*' | head -1 | cut -d'=' -f2)

  if [ -n "$channel_id" ]; then
    echo "  → Channel ID: $channel_id"
  else
    echo "  → ⚠ No se pudo obtener el channel ID"
  fi
  echo ""
  sleep 1  # Pequeña pausa para no sobrecargar
done

echo "====================================="
echo "Copiá estos IDs al archivo config.py"
