# 🎨 Guía de Personalización

Esta guía te muestra cómo personalizar el sitio de Instituto según tus necesidades.

## 🎨 Cambiar Colores

Los colores del club están definidos en el archivo `build.py` dentro de la función `generate_html()`:

```css
:root {
    --instituto-rojo: #E30613;
    --instituto-blanco: #FFFFFF;
}
```

### Ejemplo: Usar tonos más oscuros

```css
:root {
    --instituto-rojo: #B30510;  /* Rojo más oscuro */
    --instituto-blanco: #F5F5F5;  /* Blanco roto */
}
```

## 📰 Cambiar Cantidad de Noticias

En el archivo `build.py`, función `main()`:

```python
# Mostrar 2 noticias (default)
noticias = parse_feed('feeds/noticias--noticias-de-futbol-profesional.xml', limit=2)

# Cambiar a 4 noticias
noticias = parse_feed('feeds/noticias--noticias-de-futbol-profesional.xml', limit=4)
```

## 📸 Agregar Más Feeds

### 1. Agregar Agenda Deportiva

En `build.py`, función `main()`:

```python
# Agregar después de las otras secciones
print("📅 Parseando agenda deportiva...")
agenda = parse_feed('feeds/agenda-deportiva.xml', limit=3)
```

Luego modificar la llamada a `generate_html()`:

```python
html = generate_html(noticias, fotos, agenda)
```

Y actualizar la función `generate_html()` para aceptar el parámetro:

```python
def generate_html(noticias, fotos, agenda=None):
    # ... código existente ...

    # Agregar sección de agenda antes del footer
    if agenda:
        html_content += '''
        <h2 class="section-title">📅 Agenda Deportiva</h2>
        <div class="row g-4 mb-5">
        '''
        for evento in agenda:
            # ... similar a las otras secciones ...
```

### 2. Agregar Feed de Fútbol Femenino

Si el sitio oficial tiene un feed para fútbol femenino:

```python
femenino = parse_feed('feeds/futbol-femenino.xml', limit=2)
```

## 🖼️ Personalizar el Diseño de las Tarjetas

### Cambiar altura de imágenes

En el CSS del `build.py`:

```css
.card-img-top {
    height: 250px;  /* Cambiar a 300px o el valor que prefieras */
    object-fit: cover;
}
```

### Agregar bordes a las tarjetas

```css
.card {
    border: 2px solid var(--instituto-rojo);  /* Agregar borde rojo */
    /* ... resto del código ... */
}
```

### Cambiar disposición de las tarjetas

En el HTML generado, las clases de columnas:

```html
<!-- 2 columnas en desktop (actual) -->
<div class="col-md-6">

<!-- 3 columnas en desktop -->
<div class="col-md-4">

<!-- 4 columnas en desktop -->
<div class="col-md-3">
```

## 🔤 Cambiar Textos y Títulos

### Título principal

En `generate_html()`:

```html
<h1>INSTITUTO</h1>
```

Cambiar a:

```html
<h1>LA GLORIA</h1>
<h1>Instituto - Sitio del Hincha</h1>
<h1>Instituto Atlético Central Córdoba</h1>
```

### Subtítulo

```html
<p class="subtitle">Sitio No Oficial - Por los Hinchas de La Gloria</p>
```

### Títulos de secciones

```python
html_content += '''
    <h2 class="section-title">📰 Últimas Noticias</h2>
'''
```

Cambiar emojis o texto:

```python
<h2 class="section-title">⚽ Novedades del Equipo</h2>
<h2 class="section-title">🗞️ Prensa</h2>
```

## 🎭 Cambiar Patrón de Rayas

### Header con rayas más finas

```css
.header-instituto {
    background: repeating-linear-gradient(
        90deg,
        var(--instituto-rojo) 0px,
        var(--instituto-rojo) 15px,    /* Era 30px */
        var(--instituto-blanco) 15px,  /* Era 30px */
        var(--instituto-blanco) 30px   /* Era 60px */
    );
}
```

### Rayas diagonales

```css
.header-instituto {
    background: repeating-linear-gradient(
        45deg,  /* Cambiar de 90deg a 45deg */
        var(--instituto-rojo) 0px,
        var(--instituto-rojo) 30px,
        var(--instituto-blanco) 30px,
        var(--instituto-blanco) 60px
    );
}
```

### Footer sin rayas

```css
.footer {
    background: var(--instituto-rojo);  /* Color sólido */
    /* ... remover repeating-linear-gradient ... */
}

.footer-content {
    color: white;  /* Ajustar color del texto */
}
```

## 📱 Ajustar Diseño Móvil

### Cambiar tamaños de fuente en móvil

```css
@media (max-width: 768px) {
    h1 {
        font-size: 1.5rem;  /* Más pequeño en móvil */
    }

    .card-title {
        font-size: 1rem;
    }

    .card-img-top {
        height: 200px;  /* Imágenes más pequeñas */
    }
}
```

## 🔗 Personalizar Botones

### Cambiar texto del botón

```python
<a href="{noticia['link']}" class="btn-instituto">
    Leer más en institutoacc.com.ar →
</a>
```

Cambiar a:

```python
<a href="{noticia['link']}" class="btn-instituto">
    Ver completo →
</a>
<a href="{noticia['link']}" class="btn-instituto">
    Ir al sitio oficial
</a>
```

### Cambiar estilo del botón

```css
.btn-instituto {
    background: linear-gradient(45deg, #E30613, #b30510);  /* Gradiente */
    border-radius: 5px;  /* Bordes menos redondeados */
    /* ... */
}
```

## 🌐 Agregar Meta Tags para SEO

En la sección `<head>` del HTML:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Agregar estos meta tags -->
    <meta name="description" content="Sitio no oficial de Instituto con las últimas noticias y fotos del club">
    <meta name="keywords" content="Instituto, Instituto, La Gloria, Fútbol, Córdoba">
    <meta property="og:title" content="Instituto - Sitio del Hincha">
    <meta property="og:description" content="Las últimas noticias del albirrojo">
    <meta property="og:type" content="website">

    <title>Instituto - Sitio del Hincha</title>
    <!-- ... -->
</head>
```

## 📊 Agregar Google Analytics

Si querés trackear visitas:

```html
<!-- Antes del cierre de </body> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=TU-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'TU-ID');
</script>
```

## 💡 Ejemplos Rápidos

### Sitio minimalista (sin rayas)

```css
.header-instituto {
    background: var(--instituto-rojo);  /* Color sólido */
    /* ... */
}

.footer {
    background: #333;  /* Gris oscuro */
    /* ... */
}
```

### Sitio con más énfasis en fotos

```python
# Más fotos, menos noticias
noticias = parse_feed('feeds/noticias--noticias-de-futbol-profesional.xml', limit=1)
fotos = parse_feed('feeds/galeria-de-fotos.xml', limit=6)
```

```css
/* Imágenes más grandes */
.card-img-top {
    height: 350px;
}
```

### Modo oscuro

```css
body {
    background: #1a1a1a;
    color: #fff;
}

.card {
    background: #2a2a2a;
    color: #fff;
}

.card-text {
    color: #ccc;
}
```

## 🛠️ Tips Generales

1. **Siempre probá en múltiples navegadores** (Chrome, Firefox, Safari)
2. **Verificá la responsividad** usando las DevTools (F12)
3. **Optimizá las imágenes** si el sitio carga lento
4. **Guardá backups** antes de hacer cambios grandes
5. **Usá variables CSS** para facilitar cambios globales

## 📞 ¿Necesitás Ayuda?

Si te trabás con alguna personalización, revisá el código del `build.py` o consultá la documentación de:
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/)
- [CSS Gradients](https://cssgradient.io/)
- [Python XML](https://docs.python.org/3/library/xml.etree.elementtree.html)

---

**¡Vamos La Gloria! **
