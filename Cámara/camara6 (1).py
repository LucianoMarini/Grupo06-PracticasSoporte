import cv2
import os
import time

os.makedirs("mis_fotos", exist_ok=True)
os.makedirs("mis_videos", exist_ok=True)


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo conectar a la cámara.")
    exit()

ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30.0


grabando = False
salida_video = None
tiempo_inicio_grabacion = 0


duracion_timer = 3
inicio_timer = None
mostrar_flash = False
tiempo_flash = 0

print("Cámara lista.")
print("Controles: [ESPACIO] Foto (3s) | [R] Grabar/Parar | [Q] Salir")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer la cámara.")
        break

    frame = cv2.flip(frame, 1)

    display = frame.copy()

    if inicio_timer is not None:
        tiempo_transcurrido = time.time() - inicio_timer
        tiempo_restante = duracion_timer - tiempo_transcurrido

        if tiempo_restante > 0:
            texto_numero = str(int(tiempo_restante) + 1)
            cv2.putText(display, texto_numero, (ancho//2 - 50, alto//2 + 50),
                        cv2.FONT_HERSHEY_DUPLEX, 5, (0, 200, 255), 6)
        else:
            nombre_foto = f"mis_fotos/foto_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(nombre_foto, frame)
            print(f"Foto guardada: {nombre_foto}")

            inicio_timer = None
            mostrar_flash = True
            tiempo_flash = time.time()

    if grabando:
        salida_video.write(frame)

        segundos_grabados = int(time.time() - tiempo_inicio_grabacion)

        cv2.circle(display, (35, 40), 10, (0, 0, 255), -1)
        cv2.putText(display, f"REC {segundos_grabados}s", (55, 46),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.rectangle(display, (0, alto - 40), (ancho, alto), (0, 0, 0), -1)

    texto_estado = "Detener" if grabando else "Grabar"
    cv2.putText(display, f"[ESPACIO] Foto  |  [R] {texto_estado}  |  [Q] Salir",
                (15, alto - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Mi Proyecto de Camara grupo 6", display)

    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord('q'):  # Salir
        break

    elif tecla == ord(' ') and inicio_timer is None:  # Iniciar foto
        inicio_timer = time.time()
        print("Temporizador iniciado")

    elif tecla == ord('r'):
        if not grabando:
            nombre_video = f"mis_videos/video_{time.strftime('%Y%m%d_%H%M%S')}.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            salida_video = cv2.VideoWriter(
                nombre_video, fourcc, fps, (ancho, alto))
            grabando = True
            tiempo_inicio_grabacion = time.time()
            print(f" Grabando: {nombre_video}")
        else:
            grabando = False
            salida_video.release()
            print("Grabación finalizada.")


cap.release()
if salida_video is not None:
    salida_video.release()
cv2.destroyAllWindows()
