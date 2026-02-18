# Conversor de imágenes a WebP

Script en Python para procesar imágenes (`jpg`, `jpeg`, `png`) de una carpeta y:

- redimensionarlas a un ancho/alto objetivo,
- convertirlas a WebP,
- y controlar el equilibrio calidad/tamaño.

## Dependencias

Solo necesita **Pillow**.

### Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
python3 image_to_webp.py <input_dir> <output_dir> <width> <height> <quality> [opciones]
```

### Parámetros obligatorios

- `input_dir`: carpeta de entrada.
- `output_dir`: carpeta de salida.
- `width`: ancho objetivo en píxeles.
- `height`: alto objetivo en píxeles.
- `quality`: calidad WebP (`0` a `100`).

### Opciones

- `--keep-aspect-ratio`: mantiene la relación de aspecto.
- `--no-upscale`: evita ampliar imágenes más pequeñas que el tamaño objetivo.
- `--lossless`: guarda en modo WebP sin pérdida.
- `--overwrite`: sobrescribe archivos existentes en salida.

## Ejemplo

```bash
python3 image_to_webp.py ./entrada ./salida 1920 1080 90 --keep-aspect-ratio --no-upscale
```

## Notas de calidad

- Se usa interpolación **LANCZOS** para redimensionado de alta calidad.
- La compresión WebP usa calidad configurable (`quality`) y permite modo `--lossless`.
- Se intenta conservar el perfil de color ICC cuando esté disponible en la imagen original.
