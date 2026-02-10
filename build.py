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

def generate_html(noticias, fotos, agenda=[]):
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

    # Generar HTML
    print("🔨 Generando HTML...")
    html = generate_html(noticias, fotos, agenda)

    # Guardar archivo
    output_file = output_dir / 'index.html'
    output_file.write_text(html, encoding='utf-8')

    print(f"✅ Sitio generado exitosamente en: {output_file.absolute()}")
    print(f"🌐 Abrí el archivo en tu navegador para ver el resultado!")

if __name__ == '__main__':
    main()
