import cv2
import numpy as np

diccionario_aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parametros = cv2.aruco.DetectorParameters()
parametros.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX


# Ajustes que mejoran la detección en condiciones no ideales
parametros.adaptiveThreshWinSizeMin = 3
parametros.adaptiveThreshWinSizeMax = 53
parametros.adaptiveThreshWinSizeStep = 4
# detecta marcadores más pequeños/lejanos
parametros.minMarkerPerimeterRate = 0.02
parametros.maxMarkerPerimeterRate = 4.0

detector = cv2.aruco.ArucoDetector(diccionario_aruco, parametros)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se encontró la cámara.")
    exit()

# Subir resolución ayuda a la detección
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Buscando marcadores ArUco... Presiona 'q' para salir.")

imagen = cv2.imread("logo.jpeg")

if imagen is None:
    print("No se pudo cargar la imagen")
    exit()

h_img, w_img = imagen.shape[:2]

pts_origen = np.array([
    [0, 0],
    [w_img-1, 0],
    [w_img-1, h_img-1],
    [0, h_img-1]
], dtype=np.float32)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Ecualizar histograma mejora contraste en luz mala
    # frame_gris = cv2.equalizeHist(frame_gris)

    esquinas, ids, rechazados = detector.detectMarkers(frame_gris)

    if ids is not None:

        for marker in esquinas:

            pts_destino = marker[0].astype(np.float32)

            H, _ = cv2.findHomography(
                pts_origen,
                pts_destino
            )

            warp = cv2.warpPerspective(
                imagen,
                H,
                (frame.shape[1], frame.shape[0])
            )

            mask = np.zeros(frame.shape[:2], dtype=np.uint8)

            cv2.fillConvexPoly(
                mask,
                pts_destino.astype(int),
                255
            )

            frame_bg = cv2.bitwise_and(
                frame,
                frame,
                mask=cv2.bitwise_not(mask)
            )

            warp_fg = cv2.bitwise_and(
                warp,
                warp,
                mask=mask
            )

            frame = cv2.add(frame_bg, warp_fg)
    else:
        cv2.putText(
            frame,
            f"Rechazados: {len(rechazados)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    if ids is not None:
        # cv2.aruco.drawDetectedMarkers(frame, esquinas, ids)
        for i, marker_id in enumerate(ids.flatten()):
            print(f"Marcador detectado! ID: {marker_id}")
    else:
        # Útil para saber cuántos candidatos rechazó (casi-detecciones)
        cv2.putText(frame, f"Rechazados: {len(rechazados)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Detector de ArUco", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
