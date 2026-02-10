#!/bin/bash

# Script de actualización automática del sitio de Instituto
# Descarga los feeds más recientes y regenera el sitio

echo "🔴⚪ Actualizando sitio de Instituto..."

# Ir al directorio del proyecto
cd "$(dirname "$0")"

# Ejecutar build.py (descarga feeds automáticamente y genera el sitio)
python3 build.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Sitio actualizado exitosamente!"
    echo "📍 Ubicación: $(pwd)/output/index.html"
    echo "🕐 Última actualización: $(date '+%Y-%m-%d %H:%M:%S')"
else
    echo "❌ Error al generar el sitio"
    exit 1
fi
