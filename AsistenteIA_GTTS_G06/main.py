import os
import sys
import tempfile

import numpy as np
import pygame
import sounddevice as sd
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
TTS_LANG = os.getenv("TTS_LANG", "es")
SPEECH_LANG = os.getenv("SPEECH_LANG", "es-AR")

SAMPLE_RATE = 16000
BLOCK_SECONDS = 0.2
MAX_SECONDS = 8.0
SILENCE_SECONDS = 1.5
RMS_THRESHOLD = 0.01

EXIT_WORDS = {"salir", "exit", "chau", "quit", "q"}

SYSTEM_PROMPT = (
    "Sos un asistente conversacional amigable en español. "
    "Respondés de forma natural, clara y breve (2 o 3 oraciones, salvo que pidan más detalle). "
    "Respondés en el idioma en el que te hablen."
)

ai_client = None
chat = None


def init_ai():
    global ai_client, chat
    ai_client = genai.Client(api_key=API_KEY)
    chat = ai_client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )


def record_audio():
    block_frames = int(SAMPLE_RATE * BLOCK_SECONDS)
    max_blocks = int(MAX_SECONDS / BLOCK_SECONDS)
    max_silence = int(SILENCE_SECONDS / BLOCK_SECONDS)
    frames = []
    silence_blocks = 0
    started = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=block_frames
    ) as stream:
        for _ in range(max_blocks):
            data, _ = stream.read(block_frames)
            rms = float(np.sqrt(np.mean(data**2)))
            if rms >= RMS_THRESHOLD:
                started = True
                silence_blocks = 0
            elif started:
                silence_blocks += 1
                if silence_blocks >= max_silence:
                    break
            if started:
                frames.append(data)

    if not started or not frames:
        return None
    return np.concatenate(frames)


def listen_and_recognize():
    print("  Escuchando... ", end="", flush=True)
    try:
        audio = record_audio()
    except sd.PortAudioError as exc:
        print(f"\n  No se pudo usar el micrófono: {exc}")
        print("  Probá con 'python main.py --list-devices' para ver los dispositivos.")
        return None

    if audio is None:
        print("no detecté voz.")
        return None

    print("procesando...")
    int16 = (audio * 32767).astype(np.int16)
    audio_data = sr.AudioData(int16.tobytes(), sample_rate=SAMPLE_RATE, sample_width=2)
    recognizer = sr.Recognizer()
    try:
        return recognizer.recognize_google(audio_data, language=SPEECH_LANG)
    except sr.UnknownValueError:
        print("  No te entendí. Repetilo, por favor.")
        return None
    except sr.RequestError as exc:
        print(f"  No se pudo conectar con el servicio de reconocimiento: {exc}")
        return None


def ask_ai(user_text):
    response = chat.send_message(user_text)
    return response.text.strip()


def speak(text):
    tts = gTTS(text=text, lang=TTS_LANG)
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        tts.save(path)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    finally:
        os.remove(path)


def main():
    if "--list-devices" in sys.argv:
        print("Dispositivos de audio detectados:")
        print(sd.query_devices())
        return

    if not API_KEY:
        print("Falta la clave de Gemini (GEMINI_API_KEY).")
        print("Creala gratis en https://aistudio.google.com/apikey")
        print("y guardala en un archivo .env (usá .env.example como plantilla).")
        return

    text_mode = "--text" in sys.argv

    init_ai()
    pygame.mixer.init()

    print("==================================================")
    print(" Asistente Conversacional por Voz (gTTS + Gemini)")
    print("==================================================")
    if text_mode:
        print(" Modo texto: escribí tu mensaje y presioná Enter.")
    else:
        print(" Presioná Enter (vacío) para hablar por el micrófono,")
        print(" escribí algo para mandar un mensaje, o 'salir' para terminar.")
    print("--------------------------------------------------")

    while True:
        try:
            raw = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n¡Chau!")
            break

        if raw.lower() in EXIT_WORDS:
            print("¡Chau!")
            break

        if raw:
            user_text = raw
        elif text_mode:
            continue
        else:
            user_text = listen_and_recognize()
            if user_text is None:
                continue

        print(f"  Tú: {user_text}")
        try:
            print("  Pensando...")
            response = ask_ai(user_text)
        except Exception as exc:
            print(f"  Error al consultar la IA: {exc}")
            continue
        print(f"  IA: {response}")

        try:
            print("  Hablando...")
            speak(response)
        except Exception as exc:
            print(f"  Error al reproducir la voz: {exc}")


if __name__ == "__main__":
    main()
