#!/usr/bin/env python3
"""
Generador de sitio estático para Instituto
Lee feeds RSS del sitio oficial y genera un sitio HTML estático
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import re
import html
import urllib.request
import urllib.error
import unicodedata

# Importar configuración (si existe, sino usar valores por defecto)
from config import *


def download_feed(url, output_path):
    """Descarga un feed RSS desde una URL y lo guarda localmente"""
    if not DOWNLOAD_FEED:
        print(f"  → Omitiendo descarga de feed (DOWNLOAD_FEED=False)")
        return False

    try:
        print(f"  → Descargando desde {url}...")

        # Configurar headers para simular un navegador
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
        )

        # Descargar el contenido
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')

        # Guardar el archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Guardado en {output_path}")
        return True

    except urllib.error.URLError as e:
        print(f"  ✗ Error al descargar: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error inesperado: {e}")
        return False

def parse_feed(feed_file, limit=3, require_image=False):
    """Parsea un feed RSS y retorna los primeros N items

    Args:
        feed_file: Ruta al archivo XML del feed
        limit: Cantidad máxima de items a retornar
        require_image: Si es True, solo retorna items que tengan imágenes
    """
    # Leer y limpiar el archivo XML
    with open(feed_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Encontrar el inicio del XML y eliminar espacios/líneas previas
    xml_start = content.find('<?xml')
    if xml_start > 0:
        content = content[xml_start:]

    # Parsear el XML limpio
    root = ET.fromstring(content)

    items = []
    # Si require_image=True, parseamos más items para encontrar suficientes con imágenes
    max_items_to_check = limit * 5 if require_image else limit

    for item in root.findall('.//item')[:max_items_to_check]:
        title = item.find('title').text or ''
        link = item.find('link').text or ''
        description = item.find('description').text or ''
        pub_date = item.find('pubDate').text or ''

        # Extraer contenido HTML
        content_elem = item.find('.//{http://purl.org/rss/1.0/modules/content/}encoded')
        content = content_elem.text if content_elem is not None else ''

        # Extraer primera imagen del contenido
        image_url = extract_first_image(content)

        # Si require_image=True, saltar items sin imagen
        if require_image and not image_url:
            continue

        # Limpiar descripción HTML
        clean_desc = clean_html(description)

        items.append({
            'title': clean_html(title),
            'link': link,
            'description': clean_desc[:MAX_DESCRIPCION] + '...' if len(clean_desc) > MAX_DESCRIPCION else clean_desc,
            'pub_date': format_date(pub_date),
            'image': image_url
        })

        # Si ya tenemos suficientes items, parar
        if len(items) >= limit:
            break

    return items


def parse_youtube_feed(feed_file, channel_info, limit=15):
    """Parsea un feed Atom de YouTube y retorna videos

    Args:
        feed_file: Ruta al archivo XML del feed
        channel_info: Dict con 'filter_keywords', 'name' del canal
        limit: Videos a buscar antes de filtrar

    Returns:
        Lista de dicts con: title, link, description, pub_date, pub_date_raw,
                           image, author, video_id
    """
    try:
        with open(feed_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Limpiar contenido (igual que parse_feed)
        xml_start = content.find('<?xml')
        if xml_start > 0:
            content = content[xml_start:]

        root = ET.fromstring(content)

        # Namespaces de YouTube Atom feed
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'media': 'http://search.yahoo.com/mrss/',
            'yt': 'http://www.youtube.com/xml/schemas/2015'
        }

        videos = []
        entries = root.findall('atom:entry', ns)[:limit]

        for entry in entries:
            # Extraer datos
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text if title_elem is not None else ''

            link_elem = entry.find('atom:link[@rel="alternate"]', ns)
            link = link_elem.get('href') if link_elem is not None else ''

            published_elem = entry.find('atom:published', ns)
            published = published_elem.text if published_elem is not None else ''

            author_elem = entry.find('atom:author/atom:name', ns)
            author = author_elem.text if author_elem is not None else channel_info['name']

            thumbnail_elem = entry.find('.//media:thumbnail', ns)
            thumbnail_url = thumbnail_elem.get('url') if thumbnail_elem is not None else None

            desc_elem = entry.find('.//media:description', ns)
            description = desc_elem.text if desc_elem is not None else ''

            video_id_elem = entry.find('yt:videoId', ns)
            video_id = video_id_elem.text if video_id_elem is not None else ''

            # Fallback para thumbnail
            if not thumbnail_url and video_id:
                thumbnail_url = f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'

            # Filtrar por keywords si es necesario
            if channel_info['filter_keywords']:
                title_lower = title.lower()
                if not any(keyword.lower() in title_lower for keyword in VIDEO_FILTER_KEYWORDS):
                    continue

            # Limpiar descripción
            clean_desc = clean_html(description)

            videos.append({
                'title': title,
                'link': link,
                'description': clean_desc[:MAX_DESCRIPCION] + '...' if len(clean_desc) > MAX_DESCRIPCION else clean_desc,
                'pub_date': format_youtube_date(published),
                'pub_date_raw': published,  # Para ordenamiento
                'image': thumbnail_url,
                'author': author,
                'video_id': video_id
            })

        return videos

    except FileNotFoundError:
        print(f"  ⚠ Feed no encontrado: {feed_file}")
        return []
    except ET.ParseError as e:
        print(f"  ⚠ Error parseando XML: {e}")
        return []
    except Exception as e:
        print(f"  ⚠ Error: {e}")
        return []

def extract_first_image(html_content):
    """Extrae la URL de la primera imagen del contenido HTML"""
    if not html_content:
        return None

    # Buscar primera imagen en el contenido
    img_match = re.search(r'src=["\']([^"\']+\.(?:jpg|jpeg|png|gif))["\']', html_content, re.IGNORECASE)
    if img_match:
        return img_match.group(1)
    return None

def clean_html(text):
    """Elimina tags HTML y decodifica entidades"""
    if not text:
        return ''
    # Decodificar entidades HTML
    text = html.unescape(text)
    # Eliminar tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Limpiar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_date(date_str):
    """Formatea fecha RSS a formato legible"""
    if not date_str:
        return ''
    try:
        # Formato: Wed, 04 Feb 2026 17:29:45 +0000
        dt = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
        return dt.strftime('%d/%m/%Y')
    except:
        return date_str

def format_youtube_date(date_str):
    """Formatea fecha ISO 8601 de YouTube a formato legible

    YouTube usa: 2026-02-09T21:35:27+00:00
    Retorna: 09/02/2026
    """
    if not date_str:
        return ''
    try:
        # Eliminar timezone y parsear
        date_clean = date_str.split('+')[0].split('Z')[0]
        dt = datetime.strptime(date_clean, '%Y-%m-%dT%H:%M:%S')
        return dt.strftime('%d/%m/%Y')
    except:
        return date_str

def create_slug(text):
    """Crea un slug URL-friendly desde un texto

    Convierte "Mi Título Con Ñ" -> "mi-titulo-con-n"
    """
    # Normalizar unicode (ñ -> n, á -> a, etc.)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Convertir a minúsculas y reemplazar espacios/caracteres especiales con guiones
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)

    # Limitar longitud y quitar guiones al inicio/final
    text = text[:100].strip('-')

    return text

def generate_video_page(video, slug):
    """Genera una página HTML individual para un video de YouTube

    Args:
        video: Dict con información del video (title, video_id, author, pub_date, description)
        slug: Slug URL-friendly para la página

    Returns:
        String con el HTML completo de la página
    """
    # Calcular ancho total de rayas
    ancho_total_rayas = ANCHO_RAYA_ROJA + ANCHO_RAYA_BLANCA

    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{video['title']} - Instituto</title>
    <meta name="description" content="{video['description'][:160]}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {{
            --instituto-rojo: {COLOR_ROJO};
            --instituto-blanco: {COLOR_BLANCO};
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            min-height: 100vh;
        }}

        .header-instituto {{
            background: repeating-linear-gradient(
                90deg,
                var(--instituto-rojo) 0px,
                var(--instituto-rojo) {ANCHO_RAYA_ROJA}px,
                var(--instituto-blanco) {ANCHO_RAYA_ROJA}px,
                var(--instituto-blanco) {ancho_total_rayas}px
            );
            padding: 2rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header-content {{
            background: rgba(255, 255, 255, 0.95);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}

        .header-content h1 {{
            color: var(--instituto-rojo);
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
            text-transform: uppercase;
        }}

        .video-container {{
            position: relative;
            width: 100%;
            padding-bottom: 56.25%; /* Aspect ratio 16:9 */
            margin: 2rem 0;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .video-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }}

        .video-info {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }}

        .video-title {{
            color: var(--instituto-rojo);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            line-height: 1.3;
        }}

        .video-meta {{
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid #f0f0f0;
        }}

        .video-meta span {{
            display: inline-block;
            margin-right: 1.5rem;
        }}

        .video-description {{
            color: #555;
            font-size: 1rem;
            line-height: 1.6;
            white-space: pre-wrap;
        }}

        .btn-instituto {{
            background: var(--instituto-rojo);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin-top: 1.5rem;
        }}

        .btn-instituto:hover {{
            background: #b30510;
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(227, 6, 19, 0.3);
            color: white;
        }}

        .btn-secondary {{
            background: #666;
            margin-left: 1rem;
        }}

        .btn-secondary:hover {{
            background: #444;
        }}
    </style>
</head>
<body>
    <div class="header-instituto">
        <div class="container">
            <div class="header-content text-center">
                <h1>INSTITUTO - {TITULO_VIDEOS}</h1>
            </div>
        </div>
    </div>

    <div class="container py-4">
        <div class="row">
            <div class="col-lg-10 offset-lg-1">
                <!-- Video embed -->
                <div class="video-container">
                    <iframe
                        src="https://www.youtube.com/embed/{video['video_id']}?rel=0"
                        title="{video['title']}"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                    </iframe>
                </div>

                <!-- Video information -->
                <div class="video-info">
                    <h1 class="video-title">{video['title']}</h1>
                    <div class="video-meta">
                        <span>📺 <strong>{video['author']}</strong></span>
                        <span>📅 {video['pub_date']}</span>
                    </div>
                    <div class="video-description">{video['description']}</div>

                    <div class="mt-4">
                        <a href="/" class="btn-instituto">← Volver al inicio</a>
                        <a href="{video['link']}" class="btn-instituto btn-secondary" target="_blank" rel="noopener">
                            Ver en YouTube ↗
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

    return html

def generate_sitemap(base_url, video_slugs):
    """Genera un sitemap.xml con todas las páginas del sitio

    Args:
        base_url: URL base del sitio (ej: https://ejemplo.com)
        video_slugs: Lista de slugs de videos

    Returns:
        String con el XML del sitemap
    """
    # Fecha actual en formato ISO
    today = datetime.now().strftime('%Y-%m-%d')

    sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''

    # Página principal
    sitemap += f'''    <url>
        <loc>{base_url}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
'''

    # Páginas de videos
    for slug in video_slugs:
        sitemap += f'''    <url>
        <loc>{base_url}/videos/{slug}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
'''

    sitemap += '</urlset>'

    return sitemap

def generate_html(noticias, fotos, agenda=[], videos=[]):
    """Genera el HTML del sitio"""

    # Calcular ancho total de rayas
    ancho_total_rayas = ANCHO_RAYA_ROJA + ANCHO_RAYA_BLANCA

    # Generar CSS con valores de configuración
    css_content = f"""
        :root {{
            --instituto-rojo: {COLOR_ROJO};
            --instituto-blanco: {COLOR_BLANCO};
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            min-height: 100vh;
        }}

        /* Header con rayas verticales */
        .header-instituto {{
            background: repeating-linear-gradient(
                90deg,
                var(--instituto-rojo) 0px,
                var(--instituto-rojo) {ANCHO_RAYA_ROJA}px,
                var(--instituto-blanco) {ANCHO_RAYA_ROJA}px,
                var(--instituto-blanco) {ancho_total_rayas}px
            );
            padding: 3rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}

        .header-instituto::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--instituto-rojo);
        }}

        .header-content {{
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
        }}

        h1 {{
            color: var(--instituto-rojo);
            font-weight: 800;
            margin: 0;
            font-size: 2.5rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        .subtitle {{
            color: #666;
            font-size: 1.1rem;
            margin-top: 0.5rem;
        }}

        .section-title {{
            color: var(--instituto-rojo);
            font-weight: 700;
            margin: 3rem 0 1.5rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--instituto-rojo);
            font-size: 1.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .card {{
            border: none;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            height: 100%;
            background: white;
        }}

        .card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 25px rgba(227, 6, 19, 0.2);
        }}

        .card-img-top {{
            height: {ALTURA_IMAGEN_NOTICIA}px;
            object-fit: cover;
            background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
        }}

        .card-body {{
            padding: 1.5rem;
        }}

        .card-title {{
            color: var(--instituto-rojo);
            font-weight: 700;
            font-size: 1.2rem;
            margin-bottom: 1rem;
            line-height: 1.4;
        }}

        .card-text {{
            color: #555;
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        .card-date {{
            color: #666;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 0.8rem;
            display: block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .card-date-top {{
            color: var(--instituto-rojo);
            font-size: 0.85rem;
            font-weight: 700;
            display: block;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.8;
        }}

        .btn-instituto {{
            background: var(--instituto-rojo);
            color: white;
            border: none;
            padding: 0.6rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin-top: 1rem;
        }}

        .btn-instituto:hover {{
            background: #b30510;
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(227, 6, 19, 0.3);
            color: white;
        }}

        .footer {{
            background: repeating-linear-gradient(
                90deg,
                var(--instituto-rojo) 0px,
                var(--instituto-rojo) {ANCHO_RAYA_ROJA}px,
                var(--instituto-blanco) {ANCHO_RAYA_ROJA}px,
                var(--instituto-blanco) {ancho_total_rayas}px
            );
            padding: 2rem 0;
            margin-top: 4rem;
            position: relative;
        }}

        .footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--instituto-rojo);
        }}

        .footer-content {{
            background: rgba(255, 255, 255, 0.95);
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }}

        .footer-content p {{
            margin: 0.5rem 0;
            color: #555;
        }}

        .footer-content a {{
            color: var(--instituto-rojo);
            font-weight: 600;
            text-decoration: none;
        }}

        .footer-content a:hover {{
            text-decoration: underline;
        }}

        .gallery-card .card-body {{
            padding: 1rem;
        }}

        .gallery-card .card-title {{
            font-size: 1rem;
        }}

        /* Estilos para noticias sin imágenes */
        .noticia-sin-imagen {{
            min-height: 200px;
            background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
            border-left: 4px solid var(--instituto-rojo);
        }}

        .noticia-sin-imagen .card-body {{
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
        }}

        .noticia-sin-imagen .card-title {{
            font-size: 1.15rem;
            margin-bottom: 1rem;
            line-height: 1.4;
        }}

        .noticia-sin-imagen .card-text {{
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
            flex-grow: 1;
            line-height: 1.6;
        }}

        /* Estilos para agenda sin imágenes */
        .agenda-card {{
            min-height: 200px;
            border-left: 4px solid var(--instituto-rojo);
        }}

        .agenda-card .card-body {{
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
        }}

        .agenda-card .card-title {{
            font-size: 1.15rem;
            margin-bottom: 1rem;
            line-height: 1.4;
        }}

        .agenda-card .card-text {{
            font-size: 0.95rem;
            margin-bottom: 1rem;
            flex-grow: 1;
            line-height: 1.6;
        }}

        .agenda-card .card-date {{
            margin-top: auto;
        }}

        /* Estilos para videos */
        .video-card {{
            min-height: 340px;
        }}

        .video-card .card-img-top {{
            height: {ALTURA_IMAGEN_VIDEO}px;
            object-fit: cover;
            background: #000;
        }}

        .video-card .card-body {{
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
        }}

        .video-card .card-title {{
            font-size: 1rem;
            margin-bottom: 0.5rem;
            line-height: 1.3;
            flex-grow: 1;
        }}

        .video-card .text-muted {{
            font-size: 0.85rem;
            margin-bottom: 0.75rem;
        }}

        .video-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 25px rgba(227, 6, 19, 0.25);
        }}

        .video-card:hover .card-img-top {{
            opacity: 0.9;
        }}

        /* Estilos para bloque promocional BrizuelAMP */
        .promo-card {{
            min-height: 340px;
            background: linear-gradient(135deg, #fff8f0 0%, #fff5e8 100%);
            border: 2px solid rgba(227, 6, 19, 0.1);
        }}

        .promo-card .card-img-top {{
            height: {ALTURA_IMAGEN_VIDEO}px;
            object-fit: cover;
        }}

        .promo-card .card-body {{
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
        }}

        .promo-card .card-title {{
            font-size: 1rem;
            margin-bottom: 0.5rem;
            line-height: 1.3;
            flex-grow: 1;
            color: var(--instituto-rojo);
        }}

        .promo-card .text-muted {{
            font-size: 0.85rem;
            margin-bottom: 0.75rem;
        }}

        .promo-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 25px rgba(227, 6, 19, 0.25);
            background: linear-gradient(135deg, #fffaf5 0%, #fff7ed 100%);
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8rem;
            }}

            .section-title {{
                font-size: 1.4rem;
            }}
        }}
    """

    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instituto - Sitio del Hincha</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        {css_content}
    </style>
</head>
<body>

    <!-- Header -->
    <div class="header-instituto">
        <div class="container">
            <div class="header-content text-center">
                <h1>{TITULO_PRINCIPAL}</h1>
                <p class="subtitle">{SUBTITULO}</p>
            </div>
        </div>
    </div>

    <div class="container py-4">
'''

    # Agregar sección de videos (PRIMERO - arriba del todo)
    if MOSTRAR_VIDEOS and videos:
        html_content += f'''
        <!-- Videos Section -->
        <h2 class="section-title">{TITULO_VIDEOS}</h2>
        <div class="row g-4 mb-5">
'''
        for idx, video in enumerate(videos):
            # Thumbnail del video
            if video['image']:
                img_html = f'<img src="{video["image"]}" class="card-img-top" alt="{video["title"]}">'
            else:
                img_html = '<div class="card-img-top d-flex align-items-center justify-content-center bg-dark"><span style="font-size: 3rem; filter: brightness(1.2);">▶️</span></div>'

            # Generar slug para la URL interna del video
            video_slug = create_slug(video['title'])
            video_url = f"/videos/{video_slug}/"

            html_content += f'''
            <div class="col-md-{COLUMNAS_VIDEOS}">
                <div class="card video-card">
                    {img_html}
                    <div class="card-body">
                        <small class="card-date-top">{video['pub_date']}</small>
                        <h5 class="card-title">{video['title']}</h5>
                        <p class="text-muted">📺 {video['author']}</p>
                        <a href="{video_url}" class="btn-instituto">
                            Ver video →
                        </a>
                    </div>
                </div>
            </div>
'''

            # Insertar bloque de BrizuelAMP después del primer video
            if idx == 0:
                html_content += f'''
            <div class="col-md-{COLUMNAS_VIDEOS}">
                <div class="card promo-card">
                    <img src="/imgs/brizuelamp.png" class="card-img-top" alt="Vivi los partidos sin subtitulos">
                    <div class="card-body">
                        <h5 class="card-title">¿Te cansaste de los relatores porteños en la TV?</h5>
                        <p class="text-muted">📻 Brizuelamp</p>
                        <a href="https://brizuelamp.com.ar" class="btn-instituto" target="_blank" rel="noopener">
                            Ir a BrizuelAMP →
                        </a>
                    </div>
                </div>
            </div>
'''

        html_content += '''
        </div>
'''

    # Agregar sección de noticias
    if MOSTRAR_NOTICIAS and noticias:
        html_content += f'''
        <!-- Noticias Section -->
        <h2 class="section-title">{TITULO_NOTICIAS}</h2>
        <div class="row g-4 mb-5">
'''
        for noticia in noticias:
            if noticia['image']:
                # Noticia con imagen - diseño completo
                html_content += f'''
            <div class="col-md-{COLUMNAS_NOTICIAS}">
                <div class="card">
                    <img src="{noticia['image']}" class="card-img-top" alt="{noticia['title']}">
                    <div class="card-body">
                        <h5 class="card-title">{noticia['title']}</h5>
                        <p class="card-text">{noticia['description']}</p>
                        <small class="card-date">{noticia['pub_date']}</small>
                        <a href="{noticia['link']}" class="btn-instituto" target="_blank" rel="noopener">
                            {TEXTO_BOTON}
                        </a>
                    </div>
                </div>
            </div>
'''
            else:
                # Noticia sin imagen - diseño compacto tipo agenda
                html_content += f'''
            <div class="col-md-{COLUMNAS_NOTICIAS}">
                <div class="card noticia-sin-imagen">
                    <div class="card-body">
                        <small class="card-date-top">{noticia['pub_date']}</small>
                        <h5 class="card-title">{noticia['title']}</h5>
                        <p class="card-text">{noticia['description']}</p>
                        <a href="{noticia['link']}" class="btn-instituto" target="_blank" rel="noopener">
                            {TEXTO_BOTON}
                        </a>
                    </div>
                </div>
            </div>
'''
        html_content += '''
        </div>
'''

    # Agregar sección de fotos
    if MOSTRAR_FOTOS and fotos:
        html_content += f'''
        <!-- Galería Section -->
        <h2 class="section-title">{TITULO_FOTOS}</h2>
        <div class="row g-4 mb-5">
'''
        for foto in fotos:
            if foto['image']:
                img_html = f'<img src="{foto["image"]}" class="card-img-top" alt="{foto["title"]}">'
            else:
                img_html = '<div class="card-img-top d-flex align-items-center justify-content-center bg-light"><span style="font-size: 3rem;">📷</span></div>'

            html_content += f'''
            <div class="col-md-{COLUMNAS_FOTOS}">
                <div class="card gallery-card">
                    {img_html}
                    <div class="card-body">
                        <h5 class="card-title">{foto['title']}</h5>
                        <small class="card-date">{foto['pub_date']}</small>
                        <a href="{foto['link']}" class="btn-instituto" target="_blank" rel="noopener">
                            {TEXTO_BOTON_FOTOS}
                        </a>
                    </div>
                </div>
            </div>
'''
        html_content += '''
        </div>
'''

    # Agregar sección de agenda
    if MOSTRAR_AGENDA and agenda:
        html_content += f'''
        <!-- Agenda Section -->
        <h2 class="section-title">{TITULO_AGENDA}</h2>
        <div class="row g-4 mb-5">
'''
        for evento in agenda:
            # Agenda sin imágenes, solo contenido de texto
            html_content += f'''
            <div class="col-md-{COLUMNAS_AGENDA}">
                <div class="card agenda-card">
                    <div class="card-body">
                        <h5 class="card-title">{evento['title']}</h5>
                        <p class="card-text">{evento['description']}</p>
                        <small class="card-date">{evento['pub_date']}</small>
                        <a href="{evento['link']}" class="btn-instituto" target="_blank" rel="noopener">
                            Ver más →
                        </a>
                    </div>
                </div>
            </div>
'''
        html_content += '''
        </div>
'''

    html_content += '''
    </div>

    <!-- Footer -->
    <div class="footer">
        <div class="container">
            <div class="footer-content">
                <p><strong>Sitio No Oficial - Hecho por Hinchas para Hinchas</strong></p>
                <p>Todo el contenido es propiedad de <a href="https://institutoacc.com.ar" target="_blank" rel="noopener">Instituto</a></p>
                <p>Visitá el sitio oficial: <a href="https://institutoacc.com.ar" target="_blank" rel="noopener">institutoacc.com.ar</a></p>
                <p style="margin-top: 1rem; color: #888; font-size: 0.9rem;">
                    ⚪ Generado automáticamente desde los feeds oficiales ⚪
                </p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

    return html_content

def main():
    """Función principal"""
    print("🔴⚪ Generando sitio de Instituto...")

    # Crear directorios si no existen
    output_dir = Path('docs')
    feeds_dir = Path('feeds')
    output_dir.mkdir(exist_ok=True)
    feeds_dir.mkdir(exist_ok=True)

    # Descargar feeds
    print("\n📥 Descargando feeds desde institutoacc.com.ar...")

    feed_files = {
        'noticias': feeds_dir / 'feed-general.xml',
        'fotos': feeds_dir / 'galeria-de-fotos.xml',
        'agenda': feeds_dir / 'agenda-deportiva.xml'
    }

    # Descargar cada feed
    for feed_name, feed_url in FEED_URLS.items():
        output_file = feed_files[feed_name]
        download_feed(feed_url, output_file)

    # Descargar feeds de YouTube
    youtube_feed_files = {}
    if MOSTRAR_VIDEOS:
        print("\n📥 Descargando feeds de YouTube...")
        youtube_feeds_dir = feeds_dir / 'youtube'
        youtube_feeds_dir.mkdir(exist_ok=True)

        for handle, info in YOUTUBE_CHANNELS.items():
            channel_id = info['channel_id']
            feed_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
            output_file = youtube_feeds_dir / f'{handle}.xml'

            print(f"\n  Canal: {info['name']}")
            download_feed(feed_url, output_file)

            # Guardar referencia si el archivo existe (descarga exitosa o caché)
            if output_file.exists():
                youtube_feed_files[handle] = output_file

    print()

    # Parsear feeds
    noticias = []
    fotos = []
    agenda = []

    if MOSTRAR_NOTICIAS and feed_files['noticias'].exists():
        print("📰 Parseando noticias...")
        if SOLO_NOTICIAS_CON_IMAGEN:
            print("   (Filtrando solo noticias con imágenes)")
        noticias = parse_feed(feed_files['noticias'], limit=LIMITE_NOTICIAS, require_image=SOLO_NOTICIAS_CON_IMAGEN)

    if MOSTRAR_FOTOS and feed_files['fotos'].exists():
        print("📸 Parseando galería de fotos...")
        if SOLO_FOTOS_CON_IMAGEN:
            print("   (Filtrando solo galerías con imágenes)")
        fotos = parse_feed(feed_files['fotos'], limit=LIMITE_FOTOS, require_image=SOLO_FOTOS_CON_IMAGEN)

    if MOSTRAR_AGENDA and feed_files['agenda'].exists():
        print("📅 Parseando agenda deportiva...")
        if SOLO_AGENDA_CON_IMAGEN:
            print("   (Filtrando solo eventos con imágenes)")
        agenda = parse_feed(feed_files['agenda'], limit=LIMITE_AGENDA, require_image=SOLO_AGENDA_CON_IMAGEN)

    # Parsear videos de YouTube
    videos = []
    if MOSTRAR_VIDEOS:
        print("\n🎥 Parseando videos de YouTube...")

        all_videos = []
        for handle, feed_file in youtube_feed_files.items():
            channel_info = YOUTUBE_CHANNELS[handle]
            print(f"  → {channel_info['name']}...", end=' ')

            videos_from_channel = parse_youtube_feed(
                feed_file,
                channel_info,
                limit=YOUTUBE_VIDEOS_PER_CHANNEL_FETCH
            )

            filter_status = "(filtrado)" if channel_info['filter_keywords'] else "(todos)"
            print(f"{len(videos_from_channel)} videos {filter_status}")

            all_videos.extend(videos_from_channel)

        # Ordenar por fecha (más nuevos primero) y limitar
        all_videos.sort(key=lambda x: x['pub_date_raw'], reverse=True)
        videos = all_videos[:LIMITE_VIDEOS]

        print(f"\n  ✓ Total de videos a mostrar: {len(videos)}")

    # Generar HTML
    print("\n🔨 Generando HTML...")
    html = generate_html(noticias, fotos, agenda, videos)

    # Guardar archivo principal
    output_file = output_dir / 'index.html'
    output_file.write_text(html, encoding='utf-8')
    print(f"✓ Página principal generada")

    # Generar páginas individuales para cada video
    video_slugs = []
    if MOSTRAR_VIDEOS and videos:
        print("\n🎬 Generando páginas de videos...")
        videos_dir = output_dir / 'videos'
        videos_dir.mkdir(exist_ok=True)

        for video in videos:
            slug = create_slug(video['title'])
            video_slugs.append(slug)

            # Crear directorio para el video
            video_dir = videos_dir / slug
            video_dir.mkdir(exist_ok=True)

            # Generar HTML del video
            video_html = generate_video_page(video, slug)

            # Guardar archivo
            video_file = video_dir / 'index.html'
            video_file.write_text(video_html, encoding='utf-8')

        print(f"✓ {len(videos)} páginas de videos generadas en /videos/")

    # Generar sitemap.xml
    print("\n🗺️  Generando sitemap...")

    # Obtener URL base desde config (importado al inicio)
    try:
        base_url = SITE_URL.rstrip('/')
    except NameError:
        base_url = 'https://instituto.github.io'

    sitemap_xml = generate_sitemap(base_url, video_slugs)
    sitemap_file = output_dir / 'sitemap.xml'
    sitemap_file.write_text(sitemap_xml, encoding='utf-8')
    print(f"✓ Sitemap generado con {len(video_slugs) + 1} URLs")

    print(f"\n✅ Sitio generado exitosamente en: {output_dir.absolute()}")
    print(f"   📄 Página principal: {output_file}")
    print(f"   🎥 Videos: {len(video_slugs)} páginas en /videos/")
    print(f"   🗺️  Sitemap: {sitemap_file}")
    print(f"\n🌐 Abrí {output_file} en tu navegador para ver el resultado!")

if __name__ == '__main__':
    main()
