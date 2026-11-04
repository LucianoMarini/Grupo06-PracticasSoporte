import os
import sys
import tempfile
import time

import numpy as np
import pygame
import sounddevice as sd
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from gtts import gTTS

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
FALLBACK_MODELS = [
    name.strip()
    for name in os.getenv(
        "GEMINI_FALLBACK_MODELS", "gemini-3.5-flash-lite,gemini-3.5-flash"
    ).split(",")
    if name.strip()
]
TTS_LANG = os.getenv("TTS_LANG", "es")
SPEECH_LANG = os.getenv("SPEECH_LANG", "es-AR")

RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 1.5
TRANSIENT_CODES = {429, 500, 502, 503, 504}

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
history = []


class EmptyResponseError(Exception):
    pass


def init_ai():
    global ai_client
    ai_client = genai.Client(api_key=API_KEY)


def available_models():
    models = []
    for name in [MODEL, *FALLBACK_MODELS]:
        if name and name not in models:
            models.append(name)
    return models


def error_code(exc):
    if isinstance(exc, errors.APIError):
        return exc.code
    text = str(exc)
    for code in (400, 401, 403, 404, 429, 500, 502, 503, 504):
        if str(code) in text:
            return code
    return None


def is_transient(exc):
    return error_code(exc) in TRANSIENT_CODES


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
    global history
    last_exc = None

    for model in available_models():
        for attempt in range(RETRY_ATTEMPTS):
            try:
                chat = ai_client.chats.create(
                    model=model,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                    history=list(history),
                )
                response = chat.send_message(user_text)
                text = (response.text or "").strip()
                if not text:
                    raise EmptyResponseError("El modelo devolvió una respuesta vacía.")
                history.append(
                    types.Content(role="user", parts=[types.Part(text=user_text)])
                )
                history.append(
                    types.Content(role="model", parts=[types.Part(text=text)])
                )
                return text
            except EmptyResponseError as exc:
                last_exc = exc
                break
            except Exception as exc:
                code = error_code(exc)
                if code == 404:
                    last_exc = exc
                    print(f"  El modelo {model} no está disponible, probando otro...")
                    break
                if not is_transient(exc):
                    raise
                last_exc = exc
                if attempt < RETRY_ATTEMPTS - 1:
                    delay = RETRY_BASE_DELAY * (2**attempt)
                    print(f"  Servicio saturado, reintentando en {delay:.1f}s...")
                    time.sleep(delay)

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Ningún modelo de Gemini respondió.")


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
    try:
        pygame.mixer.init()
    except Exception as exc:
        print(f"  Advertencia: no se pudo iniciar el audio ({exc}). No se escuchará la voz.")

    print("==================================================")
    print(" Asistente Conversacional por Voz (gTTS + Gemini)")
    print("==================================================")
    print(f" Modelo: {MODEL} (respaldos: {', '.join(FALLBACK_MODELS) or 'ninguno'})")
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
