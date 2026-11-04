import cv2

diccionarios = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
}

cap = cv2.VideoCapture(0)

print("Mostrá el marcador a la cámara... Presioná 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for nombre, dict_id in diccionarios.items():
        diccionario = cv2.aruco.getPredefinedDictionary(dict_id)
        parametros = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(diccionario, parametros)
        esquinas, ids, _ = detector.detectMarkers(frame_gris)

        if ids is not None:
            print(
                f"✅ ENCONTRADO con diccionario: {nombre} — IDs: {ids.flatten()}")
            cv2.aruco.drawDetectedMarkers(frame, esquinas, ids)

    cv2.imshow("Buscando diccionario...", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
