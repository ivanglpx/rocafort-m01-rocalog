#!/usr/bin/env python3
"""Redimensiona imágenes y las convierte a WebP."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Procesa imágenes de una carpeta: redimensiona a un tamaño objetivo "
            "y convierte a WebP."
        )
    )
    parser.add_argument("input_dir", type=Path, help="Carpeta de entrada")
    parser.add_argument("output_dir", type=Path, help="Carpeta de salida")
    parser.add_argument("width", type=int, help="Ancho objetivo en px")
    parser.add_argument("height", type=int, help="Alto objetivo en px")
    parser.add_argument("quality", type=int, help="Calidad WebP (0-100)")

    parser.add_argument(
        "--keep-aspect-ratio",
        action="store_true",
        help="Mantiene la relación de aspecto al redimensionar",
    )
    parser.add_argument(
        "--no-upscale",
        action="store_true",
        help="Evita ampliar imágenes que ya son más pequeñas que el tamaño objetivo",
    )
    parser.add_argument(
        "--lossless",
        action="store_true",
        help="Guarda en WebP sin pérdida",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribe archivos existentes en la carpeta de salida",
    )

    args = parser.parse_args()

    if args.width <= 0 or args.height <= 0:
        parser.error("El ancho y el alto deben ser enteros positivos")
    if not 0 <= args.quality <= 100:
        parser.error("La calidad debe estar entre 0 y 100")

    return args


def get_target_size(
    original_size: tuple[int, int],
    target_size: tuple[int, int],
    keep_aspect_ratio: bool,
    no_upscale: bool,
) -> tuple[int, int]:
    original_w, original_h = original_size
    target_w, target_h = target_size

    if keep_aspect_ratio:
        if original_w == 0 or original_h == 0:
            return original_size

        scale_w = target_w / original_w
        scale_h = target_h / original_h
        scale = min(scale_w, scale_h)

        if no_upscale:
            scale = min(scale, 1.0)

        resized_w = max(1, int(round(original_w * scale)))
        resized_h = max(1, int(round(original_h * scale)))
        return resized_w, resized_h

    resized_w, resized_h = target_w, target_h

    if no_upscale:
        resized_w = min(original_w, target_w)
        resized_h = min(original_h, target_h)

    return resized_w, resized_h


def process_image(
    input_path: Path,
    output_path: Path,
    target_size: tuple[int, int],
    quality: int,
    keep_aspect_ratio: bool,
    no_upscale: bool,
    lossless: bool,
) -> None:
    with Image.open(input_path) as img:
        icc_profile = img.info.get("icc_profile")
        target = get_target_size(
            img.size,
            target_size,
            keep_aspect_ratio=keep_aspect_ratio,
            no_upscale=no_upscale,
        )

        resized = ImageOps.exif_transpose(img).resize(target, resample=Image.Resampling.LANCZOS)

        save_kwargs = {
            "format": "WEBP",
            "quality": quality,
            "lossless": lossless,
            "method": 6,
        }
        if icc_profile is not None:
            save_kwargs["icc_profile"] = icc_profile

        resized.save(output_path, **save_kwargs)


def main() -> int:
    args = parse_args()

    if not args.input_dir.is_dir():
        print(f"Error: la carpeta de entrada no existe: {args.input_dir}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        p for p in args.input_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        print("No se encontraron imágenes JPG/JPEG/PNG en la carpeta de entrada.")
        return 0

    processed = 0
    skipped = 0
    errors = 0

    for input_path in files:
        output_name = f"{input_path.stem}.webp"
        output_path = args.output_dir / output_name

        if output_path.exists() and not args.overwrite:
            print(f"Saltando (existe y falta --overwrite): {output_path}")
            skipped += 1
            continue

        try:
            process_image(
                input_path=input_path,
                output_path=output_path,
                target_size=(args.width, args.height),
                quality=args.quality,
                keep_aspect_ratio=args.keep_aspect_ratio,
                no_upscale=args.no_upscale,
                lossless=args.lossless,
            )
            print(f"OK: {input_path.name} -> {output_path.name}")
            processed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"Error procesando {input_path.name}: {exc}", file=sys.stderr)
            errors += 1

    print(
        f"Finalizado. Procesadas: {processed}, saltadas: {skipped}, con error: {errors}."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
