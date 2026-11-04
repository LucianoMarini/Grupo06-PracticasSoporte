import speech_recognition as sr


def escuchar_y_transcribir():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Ajustando el ruido de fondo")
        r.adjust_for_ambient_noise(source, duration=1)

        print("Ya podés hablar")
        audio = r.listen(source)

    try:
        print("Procesando")
        texto = r.recognize_google(audio, language='es-AR')
        print(f"dijiste: '{texto}'")

    except sr.UnknownValueError:
        print("Perdón, no pude entender lo que dijiste.")
    except sr.RequestError as e:
        # Si hay un problema de conexión con internet
        print(f"Error al conectarse al servicio de Google: {e}")


if __name__ == "__main__":
    escuchar_y_transcribir()
