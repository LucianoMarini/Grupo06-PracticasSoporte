# -*- coding: utf-8 -*-
"""Mide la precision del modelo ONNX sobre el dataset local.

Uso:
    python probar_modelo.py
    python probar_modelo.py --limite 100
"""

import argparse
import random
from pathlib import Path

import cv2

from clasificador_opencv import CLASES, NOMBRES, clasificar, cargar_modelo

RUTA_DATASET = Path("dataset-resized/dataset-resized")
EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def juntar_imagenes():
    imagenes = []
    for clase in CLASES:
        carpeta = RUTA_DATASET / clase
        for archivo in carpeta.iterdir():
            if archivo.suffix.lower() in EXTENSIONES:
                imagenes.append((archivo, clase))
    return imagenes


def main():
    parser = argparse.ArgumentParser(description="Evalua el modelo sobre el dataset")
    parser.add_argument(
        "--limite", type=int, default=300,
        help="Cantidad maxima de imagenes a evaluar (0 = todas)"
    )
    args = parser.parse_args()

    net = cargar_modelo()
    imagenes = juntar_imagenes()
    random.seed(123)
    random.shuffle(imagenes)

    if args.limite > 0:
        imagenes = imagenes[:args.limite]

    aciertos = 0
    por_clase = {clase: [0, 0] for clase in CLASES}

    for numero, (ruta, clase_real) in enumerate(imagenes, start=1):
        frame = cv2.imread(str(ruta))
        if frame is None:
            continue

        clase_predicha, _, _ = clasificar(net, frame)
        correcto = clase_predicha == clase_real
        aciertos += int(correcto)
        por_clase[clase_real][0] += int(correcto)
        por_clase[clase_real][1] += 1

        if numero % 50 == 0:
            print(f"Procesadas: {numero}/{len(imagenes)}")

    total = sum(valores[1] for valores in por_clase.values())
    if total == 0:
        raise RuntimeError("No se encontraron imagenes para evaluar.")

    print(f"\nPrecision total: {aciertos / total * 100:.2f}% ({aciertos}/{total})")
    print("\nPrecision por clase:")
    for clase in CLASES:
        correctos, cantidad = por_clase[clase]
        if cantidad:
            print(f"  {NOMBRES[clase]:<10} {correctos / cantidad * 100:5.1f}%  ({correctos}/{cantidad})")


if __name__ == "__main__":
    main()
