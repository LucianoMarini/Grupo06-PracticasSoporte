import cv2
import numpy as np

diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

for marker_id in range(6):  # genera 6 marcadores
    marker_img = cv2.aruco.generateImageMarker(diccionario, marker_id, 300)

    # Agregar borde blanco (importante para la detección)
    marker_con_borde = cv2.copyMakeBorder(
        marker_img, 30, 30, 30, 30,
        cv2.BORDER_CONSTANT, value=255
    )

    cv2.imwrite(f"aruco_6x6_id{marker_id}.png", marker_con_borde)
    print(f"Guardado: aruco_6x6_id{marker_id}.png")

print("Listo! Imprimí estos archivos.")
