# 🚀 Inicio Rápido

## Generar el sitio

El script descarga automáticamente los feeds desde institutoacc.com.ar:

```bash
python3 build.py
```

Esto descarga los feeds RSS y genera el sitio en `output/index.html`

## Ver el sitio

```bash
xdg-open output/index.html
```

## Actualizar con nuevos feeds

```bash
./actualizar.sh
```

## Ver localmente con servidor

```bash
./servir.sh
# Luego abrí: http://localhost:8000/index.html
```

## Personalizar

Editá `config.py` para cambiar:
- Cantidad de noticias/fotos
- Colores del club
- Textos y títulos
- Diseño de tarjetas

Después de modificar `config.py`, ejecutá:
```bash
python3 build.py
```

## Publicar

1. **GitHub Pages**: Copiá `output/` a `docs/` en tu repo
2. **Netlify/Vercel**: Arrastrá la carpeta `output/`
3. **Servidor propio**: Subí `output/` via FTP/SFTP

---

¡Vamos La Gloria! 
