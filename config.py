"""
Archivo de configuración para el sitio de Instituto
Modificá estos valores para personalizar el sitio sin tocar build.py
"""

# ===== CONFIGURACIÓN DE CONTENIDO =====

# Cantidad de items a mostrar de cada feed
LIMITE_NOTICIAS = 3
LIMITE_FOTOS = 3
LIMITE_AGENDA = 3

# URLs de los feeds RSS (se descargan automáticamente al ejecutar build.py)
FEED_URLS = {
    'noticias': 'https://institutoacc.com.ar/index.php/feed/',
    'fotos': 'https://institutoacc.com.ar/index.php/category/galeria-de-fotos/feed/',
    'agenda': 'https://institutoacc.com.ar/index.php/category/agenda-deportiva/feed/'
}
DOWNLOAD_FEED = True

# ===== CONFIGURACIÓN DE COLORES =====

# Colores del club (formato hexadecimal)
COLOR_ROJO = '#E30613'
COLOR_BLANCO = '#FFFFFF'

# Colores adicionales
COLOR_FONDO = 'linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%)'
COLOR_TEXTO = '#555'
COLOR_TEXTO_CLARO = '#888'

# ===== CONFIGURACIÓN DE TEXTOS =====

# Título principal del sitio
TITULO_PRINCIPAL = 'INSTITUTO'
SUBTITULO = 'Sitio No Oficial - Por los Hinchas de La Gloria'

# Títulos de secciones
TITULO_NOTICIAS = '📰 Últimas Noticias'
TITULO_FOTOS = '📸 Galería de Fotos'
TITULO_AGENDA = '📅 Agenda Deportiva'

# Texto de botones
TEXTO_BOTON = 'Leer más en institutoacc.com.ar →'
TEXTO_BOTON_FOTOS = 'Ver galería completa →'

# ===== CONFIGURACIÓN DE DISEÑO =====

# Tamaños de imagen (en píxeles)
ALTURA_IMAGEN_NOTICIA = 250
ALTURA_IMAGEN_FOTO = 250

# Ancho de rayas en header/footer (en píxeles)
ANCHO_RAYA_ROJA = 120
ANCHO_RAYA_BLANCA = 120

# Layout de columnas (Bootstrap)
# Valores posibles: 12, 6, 4, 3 (12=1 col, 6=2 cols, 4=3 cols, 3=4 cols)
COLUMNAS_NOTICIAS = 6  # 2 columnas
COLUMNAS_FOTOS = 4     # 3 columnas

# ===== CONFIGURACIÓN DE FOOTER =====

TEXTO_FOOTER_LINEA1 = 'Sitio No Oficial - Hecho por Hinchas para Hinchas'
TEXTO_FOOTER_LINEA2 = 'Todo el contenido es propiedad de <a href="https://institutoacc.com.ar" target="_blank" rel="noopener">Instituto</a>'
TEXTO_FOOTER_LINEA3 = 'Visitá el sitio oficial: <a href="https://institutoacc.com.ar" target="_blank" rel="noopener">institutoacc.com.ar</a>'
MOSTRAR_FOOTER_RAYAS = True

# ===== CONFIGURACIÓN AVANZADA =====

# Longitud máxima de descripción (caracteres)
MAX_DESCRIPCION = 200

# Habilitar/deshabilitar secciones
MOSTRAR_NOTICIAS = True
MOSTRAR_FOTOS = True
MOSTRAR_AGENDA = False  # Cambiar a True para mostrar agenda

# ===== META TAGS (SEO) =====

META_DESCRIPTION = 'Sitio no oficial de Instituto con las últimas noticias y fotos del club'
META_KEYWORDS = 'Instituto, Instituto, La Gloria, Fútbol, Córdoba'
META_AUTHOR = 'Hincha de Instituto'

# ===== REDES SOCIALES (Open Graph) =====

OG_TITLE = 'Instituto - Sitio del Hincha'
OG_DESCRIPTION = 'Las últimas noticias del albirrojo'
OG_IMAGE = 'https://institutoacc.com.ar/wp-content/uploads/2023/logo-instituto.png'  # Cambiar por tu logo

# ===== NOTAS =====
#
# Para aplicar los cambios:
# 1. Modificá los valores en este archivo
# 2. Ejecutá: python3 build.py
# 3. El sitio se regenerará con la nueva configuración
#
# Si necesitás más personalización, revisá PERSONALIZACION.md
