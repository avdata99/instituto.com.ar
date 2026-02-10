# Sitio No Oficial de Instituto

Sitio estático generado automáticamente desde los feeds oficiales de Instituto Atlético Central Córdoba.

## 🎯 Descripción

Este proyecto genera un sitio web estático que muestra las últimas noticias y fotos del club Instituto, tomando el contenido directamente de los feeds RSS del sitio oficial. Todo el tráfico se dirige al sitio oficial del club.

## ✨ Características

- ✅ **100% Vanilla** - Solo Python estándar y Bootstrap 5 (CDN)
- ✅ **Sitio Estático** - HTML puro, sin backend necesario
- ✅ **Diseño Moderno** - Interfaz limpia con los colores del club (rojo y blanco)
- ✅ **Rayas Verticales** - Estética inspirada en la camiseta albirroja
- ✅ **Responsivo** - Se adapta a cualquier dispositivo
- ✅ **Enlaces al Sitio Oficial** - Todo el tráfico va a institutoacc.com.ar

## 📁 Estructura del Proyecto

```
instituto/
├── build.py                  # Script generador del sitio
├── feeds/                    # Feeds RSS descargados
│   ├── noticias--noticias-de-futbol-profesional.xml
│   └── galeria-de-fotos.xml
├── output/                   # Sitio generado (HTML estático)
│   └── index.html
└── README.md
```

## 🚀 Uso

### 1. Generar el Sitio

El script descarga automáticamente los feeds desde el sitio oficial y genera el sitio:

```bash
python3 build.py
```

Esto:
1. Descarga los feeds RSS más recientes desde institutoacc.com.ar
2. Los guarda en la carpeta `feeds/`
3. Genera el sitio en `output/index.html`

### 2. Ver el Sitio

Abrí el archivo en tu navegador:

```bash
# Linux
xdg-open output/index.html

# macOS
open output/index.html

# Windows
start output/index.html
```

O simplemente hacé doble click en `output/index.html`.

## 🌐 Publicar el Sitio

Podés publicar el sitio en cualquier servicio de hosting estático:

### GitHub Pages

```bash
# Copiá el contenido de output/ a tu repositorio
cp output/index.html docs/
git add docs/
git commit -m "Actualizar sitio"
git push
```

### Netlify / Vercel / Cloudflare Pages

Solo tenés que arrastrar la carpeta `output/` a la interfaz web.

### Servidor Web Tradicional

Subí el contenido de `output/` a tu servidor via FTP/SFTP.

## ⚙️ Configuración

Podés modificar el script `build.py` para:

- Cambiar la cantidad de noticias mostradas (parámetro `limit`)
- Agregar más feeds (agenda deportiva, etc.)
- Personalizar los estilos CSS
- Ajustar el diseño HTML

Ejemplo para mostrar 3 noticias:

```python
noticias = parse_feed('feeds/noticias--noticias-de-futbol-profesional.xml', limit=3)
```

## 🔄 Actualización Automática

Para mantener el sitio actualizado, podés usar el script `actualizar.sh` que descarga los feeds y regenera el sitio:

```bash
./actualizar.sh
```

O agregarlo al crontab para ejecutar cada 6 horas:

```bash
crontab -e
# Agregar esta línea:
0 */6 * * * cd /ruta/a/instituto && ./actualizar.sh >> logs/actualizar.log 2>&1
```

El sitio se actualizará automáticamente cada 6 horas descargando los feeds más recientes.

## 🎨 Personalización de Colores

Los colores del club están definidos como variables CSS en el HTML generado:

```css
--instituto-rojo: #E30613;
--instituto-blanco: #FFFFFF;
```

Podés modificarlos en la función `generate_html()` del archivo `build.py`.

## 📝 Requisitos

- Python 3.6 o superior (solo usa bibliotecas estándar)
- Conexión a internet para cargar Bootstrap 5 desde CDN
- Navegador web moderno

## 🤝 Créditos

- Todo el contenido es propiedad de [Instituto](https://institutoacc.com.ar)
- Sitio no oficial creado por hinchas para hinchas
- Bootstrap 5 para el diseño
- Sitio oficial: https://institutoacc.com.ar
- Asociate! https://portal.ourclub.io/iacc/
- Noticias de futbol profesional: noticias/noticias-de-futbol-profesional/feed/
- General feed: https://institutoacc.com.ar/index.php/feed/
- Feed de la agenda deportiva: https://institutoacc.com.ar/index.php/category/agenda-deportiva/feed/
- Galeria de fotos: https://institutoacc.com.ar/index.php/category/galeria-de-fotos/feed


## ⚖️ Licencia

Este es un proyecto de fan no oficial. Todo el contenido mostrado pertenece a Instituto Atlético Central Córdoba y se enlaza directamente al sitio oficial.

---

**¡Vamos La Gloria! **
