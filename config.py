"""
Archivo de configuración para el sitio de Instituto
Modificá estos valores para personalizar el sitio sin tocar build.py
"""

# ===== CONFIGURACIÓN DE CONTENIDO =====

# Cantidad de items a mostrar de cada feed
LIMITE_NOTICIAS = 9  # Mostrará con y sin fotos de forma elegante
LIMITE_FOTOS = 3
LIMITE_AGENDA = 6  # 2 filas de 3 elementos

# URLs de los feeds RSS (se descargan automáticamente al ejecutar build.py)
FEED_URLS = {
    'noticias': 'https://institutoacc.com.ar/index.php/feed/',
    'fotos': 'https://institutoacc.com.ar/index.php/category/galeria-de-fotos/feed/',
    'agenda': 'https://institutoacc.com.ar/index.php/category/agenda-deportiva/feed/'
}
# TODO otros a revisar
# Liga cordobesa de futbol: https://futboldecordoba.com.ar/tag/instituto-atletico-central-cordoba/feed/

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
COLUMNAS_NOTICIAS = 4  # 3 columnas
COLUMNAS_FOTOS = 4     # 3 columnas
COLUMNAS_AGENDA = 4     # 3 columnas

# ===== CONFIGURACIÓN AVANZADA =====

# Longitud máxima de descripción (caracteres)
MAX_DESCRIPCION = 200

# Habilitar/deshabilitar secciones
MOSTRAR_NOTICIAS = True
MOSTRAR_FOTOS = True
# La agenda deportiva no se actualiza hace años, la quitamos temporalmente
MOSTRAR_AGENDA = False  # Mostrar agenda deportiva

# Filtros de contenido
SOLO_NOTICIAS_CON_IMAGEN = False  # Mostrar todas las noticias (con y sin imagen)
SOLO_FOTOS_CON_IMAGEN = False     # Las galerías siempre tienen imágenes
SOLO_AGENDA_CON_IMAGEN = False    # Algunos eventos pueden no tener imagen

# ===== META TAGS (SEO) =====

META_DESCRIPTION = 'Sitio no oficial de Instituto con las últimas noticias y fotos del club'
META_KEYWORDS = 'Instituto, Instituto, La Gloria, Fútbol, Córdoba'
META_AUTHOR = 'Hincha de Instituto'

# ===== REDES SOCIALES (Open Graph) =====

OG_TITLE = 'Instituto - Sitio del Hincha'
OG_DESCRIPTION = 'Las últimas noticias del albirrojo'
OG_IMAGE = 'https://institutoacc.com.ar/wp-content/uploads/2023/logo-instituto.png'  # Cambiar por tu logo

# ===== CONFIGURACIÓN DEL SITIO =====

# URL base del sitio (para sitemap.xml)
# Cambiá esto por tu URL real cuando despliegues el sitio
SITE_URL = 'https://instituto.com.ar'  # Dominio personalizado (ver CNAME)

# ===== CONFIGURACIÓN DE VIDEOS DE YOUTUBE =====

# Cantidad de videos a mostrar en total (11 + 1 bloque BrizuelAMP = 12 elementos)
LIMITE_VIDEOS = 15  # Se muestra 1 bloque promocional adicional

# Canales de YouTube - Mapeo de handles a channel_ids
# IMPORTANTE: Los channel_ids reales deben obtenerse con el script: bash obtener_channel_ids.sh
YOUTUBE_CHANNELS = {
    # Canal oficial - TODOS los videos (sin filtrar)
    'InstitutoACC': {
        'channel_id': 'UCvv_C1t_9MO0i2uFnQUdRKQ',
        'filter_keywords': False,
        'name': 'Instituto ACC Oficial'
    },

    # Canales de medios - SOLO videos con "Instituto" o "La Gloria" en el título
    'pablochucrel7': {
        'channel_id': 'UCi7YRXPr9usUa8e1sj-17aQ',
        'filter_keywords': True,
        'name': 'Pablo Chucrel'
    },
    'joavalenzuela': {
        'channel_id': 'UCATmn2iTqouCLhW2iQP47iA',
        'filter_keywords': True,
        'name': 'Joa Valenzuela'
    },
    'TNTSportsAR': {
        'channel_id': 'UCI5RY8G0ar-hLIaUJvx58Lw',
        'filter_keywords': True,
        'name': 'TNT Sports Argentina'
    },
    'tycsports': {
        'channel_id': 'UC72ZaBKI-Bo5fjmWEYonhJw',
        'filter_keywords': True,
        'name': 'TyC Sports'
    },
    'RadioSuquia': {
        'channel_id': 'UCcl6jt4C1zpWjYsOHhDjNhQ',
        'filter_keywords': True,
        'name': 'Radio Suquía'
    },
    'cadena3': {
        'channel_id': 'UCNxohbqfDp8YxW_Mji2XMHA',
        'filter_keywords': True,
        'name': 'Cadena 3'
    },
    'showsports': {  # https://www.youtube.com/@CanalShowsportOficial
        'channel_id': 'UC39LQlfIVgrVjlyjf4f4xiw',
        'filter_keywords': True,
        'name': 'ShowSports'
    },
    'lavoz': {  # https://www.youtube.com/lavozcomar
        'channel_id': 'UCluV_ArZV6NOdQIWiXTJx3g',
        'filter_keywords': True,
        'name': 'La Voz'
    },
    'golandpop': {  # https://www.youtube.com/@golandpop
        'channel_id': 'UCcXLIwBDN3UewgfqzVSoCnw',
        'filter_keywords': True,
        'name': 'Gol&Pop'
    },
    'ultimajugada': {  # https://www.youtube.com/@UltimaJugadaCBA
        'channel_id': 'UCyE25hxg_D2PeyJpJ4T9cVA',
        'filter_keywords': True,
        'name': 'Última Jugada'
    },
    'peladoglorioso': {  # https://www.youtube.com/@PelaGlorioso
        'channel_id': 'UCdiDaGTyiAOXW1sU38QlKEQ',
        'filter_keywords': False,
        'name': 'Pelado Glorioso'
    },
    'ESPNFans': {  # https://www.youtube.com/@ESPNFans
        'channel_id': 'UCFmMw7yTuLTCuMhpZD5dVsg',
        'filter_keywords': True,
        'name': 'ESPN Fans'
    }
}

# Palabras clave para filtrar (case-insensitive, OR lógico)
VIDEO_FILTER_KEYWORDS = ['Instituto', 'La Gloria']

# Videos a buscar por canal antes de filtrar (para canales con filter_keywords=True)
YOUTUBE_VIDEOS_PER_CHANNEL_FETCH = 15

# Toggle para habilitar/deshabilitar sección
MOSTRAR_VIDEOS = True

# Textos de la sección
TITULO_VIDEOS = 'Videos de Instituto'
TEXTO_BOTON_VIDEOS = 'Ver en YouTube →'

# Layout
COLUMNAS_VIDEOS = 3  # 12/3 = 4 columnas
ALTURA_IMAGEN_VIDEO = 180

# ===== NOTAS =====
#
# Para aplicar los cambios:
# 1. Modificá los valores en este archivo
# 2. Ejecutá: python3 build.py
# 3. El sitio se regenerará con la nueva configuración
#
# Si necesitás más personalización, revisá PERSONALIZACION.md
