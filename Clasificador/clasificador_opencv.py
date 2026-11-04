# -*- coding: utf-8 -*-
"""Clasificador de materiales reciclables con OpenCV y camara.

Uso:
    python clasificador_opencv.py
    python clasificador_opencv.py --imagen ruta/foto.jpg
"""

import argparse
import time

import cv2
import numpy as np

RUTA_MODELO = "modelo_trashnet_grupo6.onnx"

CLASES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
NOMBRES = {
    "cardboard": "Carton",
    "glass": "Vidrio",
    "metal": "Metal",
    "paper": "Papel",
    "plastic": "Plastico",
    "trash": "Basura",
}
COLORES = {
    "cardboard": (42, 126, 165),
    "glass": (255, 170, 0),
    "metal": (180, 180, 180),
    "paper": (80, 200, 80),
    "plastic": (0, 200, 255),
    "trash": (60, 60, 220),
}

TAMANO = (224, 224)
CADA_N_FRAMES = 5


def cargar_modelo():
    return cv2.dnn.readNetFromONNX(RUTA_MODELO)


def recortar_cuadrado(frame):
    alto, ancho = frame.shape[:2]
    lado = min(alto, ancho)
    x = (ancho - lado) // 2
    y = (alto - lado) // 2
    return frame[y:y + lado, x:x + lado]


def preprocesar(frame):
    recorte = recortar_cuadrado(frame)
    imagen = cv2.resize(recorte, TAMANO, interpolation=cv2.INTER_AREA)
    return cv2.dnn.blobFromImage(
        imagen, 1.0, TAMANO, (0, 0, 0), swapRB=True, crop=False
    )


def clasificar(net, frame):
    net.setInput(preprocesar(frame))
    salida = net.forward()[0]
    indice = int(np.argmax(salida))
    return CLASES[indice], float(salida[indice]), salida


def dibujar_panel(frame, clase, confianza, probabilidades, fps=None):
    alto, ancho = frame.shape[:2]
    color = COLORES[clase]
    nombre = NOMBRES[clase]

    cv2.rectangle(frame, (0, 0), (ancho, 95), (20, 20, 20), -1)
    cv2.putText(
        frame, f"{nombre}  {confianza * 100:.1f}%", (18, 42),
        cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3
    )

    orden = np.argsort(probabilidades)[::-1][:3]
    y = 68
    for posicion, indice in enumerate(orden):
        clase_top = CLASES[int(indice)]
        valor = float(probabilidades[indice])
        texto = f"{NOMBRES[clase_top]}: {valor * 100:.0f}%"
        cv2.putText(
            frame, texto, (18 + posicion * 190, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1
        )

    if fps is not None:
        cv2.putText(
            frame, f"FPS: {fps:.1f}", (ancho - 130, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1
        )

    lado = min(alto, ancho)
    x1 = (ancho - lado) // 2
    y1 = (alto - lado) // 2
    cv2.rectangle(frame, (x1, y1), (x1 + lado, y1 + lado), color, 2)

    cv2.putText(
        frame, "[Q] Salir   [S] Guardar foto", (18, alto - 15),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1
    )


def modo_imagen(net, ruta):
    frame = cv2.imread(ruta)
    if frame is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {ruta}")

    clase, confianza, probabilidades = clasificar(net, frame)
    dibujar_panel(frame, clase, confianza, probabilidades)
    print(f"Prediccion: {NOMBRES[clase]} ({confianza * 100:.1f}%)")

    cv2.imshow("Clasificador de materiales", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def modo_camara(net, indice_camara):
    cap = cv2.VideoCapture(indice_camara)
    if not cap.isOpened():
        raise RuntimeError(
            "No se pudo abrir la camara. Proba con --camara 1 o revisa los permisos."
        )

    clase = "trash"
    confianza = 0.0
    probabilidades = np.zeros(len(CLASES), dtype=np.float32)
    contador = 0
    tiempo_anterior = time.time()
    fps = 0.0

    print("Camara lista. Presiona Q para salir.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("No se pudo leer un frame de la camara.")
            break

        frame = cv2.flip(frame, 1)

        if contador % CADA_N_FRAMES == 0:
            clase, confianza, probabilidades = clasificar(net, frame)

        contador += 1

        ahora = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / max(ahora - tiempo_anterior, 1e-6))
        tiempo_anterior = ahora

        dibujar_panel(frame, clase, confianza, probabilidades, fps)
        cv2.imshow("Clasificador de materiales", frame)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q"):
            break
        if tecla == ord("s"):
            nombre = f"captura_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(nombre, frame)
            print(f"Foto guardada: {nombre}")

    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Clasificador de materiales con OpenCV")
    parser.add_argument("--imagen", help="Clasificar una imagen en vez de usar la camara")
    parser.add_argument("--camara", type=int, default=0, help="Indice de la camara")
    args = parser.parse_args()

    net = cargar_modelo()

    if args.imagen:
        modo_imagen(net, args.imagen)
    else:
        modo_camara(net, args.camara)


if __name__ == "__main__":
    main()
