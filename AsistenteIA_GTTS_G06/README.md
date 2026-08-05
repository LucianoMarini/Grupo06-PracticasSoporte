# Asistente Conversacional por Voz (gTTS + Gemini)

Un bot con el que podés hablar usando el micrófono y que te responde con voz.
Flujo bidireccional: **voz → texto → IA → texto → voz**, todo en tiempo real y desde consola.

## Cómo funciona

```
Micrófono (sounddevice) → texto (SpeechRecognition) → Gemini (IA) → gTTS (mp3) → pygame (audio)
```

## Requisitos

- Python 3.14 (o 3.12+)
- Conexión a internet (el reconocimiento de voz, Gemini y gTTS son servicios en línea, todos gratuitos)

## Instalación

```bash
pip install -r requirements.txt
```

> Nota: se usa `pygame-ce` (fork comunitario de pygame) porque `pygame` oficial aún no tiene
> versiones para Python 3.14. Es 100% compatible: se importa como `import pygame`.
> Lo mismo con el micrófono: se usa `sounddevice` en lugar de `PyAudio`.

## Obtener la API key de Gemini

1. Entrá a https://aistudio.google.com/apikey
2. Iniciá sesión con tu cuenta de Google.
3. Hacé clic en **Create API key** → elegí un proyecto (o creá uno) → se genera la clave.
4. Copiala y pegala en el archivo `.env`.

## Configuración

Copiá la plantilla y completá tu clave:

```bash
copy .env.example .env
```

Editala:

```
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-flash-latest
TTS_LANG=es
SPEECH_LANG=es-AR
```

| Variable        | Descripción                                             |
|-----------------|---------------------------------------------------------|
| `GEMINI_API_KEY`| Clave de Google AI Studio (obligatoria)                 |
| `GEMINI_MODEL`  | Modelo de Gemini (`gemini-flash-latest` es el alias estable) |
| `TTS_LANG`      | Idioma de la voz generada con gTTS (`es`, `en`, ...)    |
| `SPEECH_LANG`   | Idioma del reconocimiento de voz (`es-AR`, `en-US`, ...)|

El `.env` está en `.gitignore`: no lo subas nunca.

## Uso

```bash
python main.py
```

En la consola:

- **Presioná Enter (vacío)** → empezás a hablar por el micrófono. La grabación corta sola al
  detectar silencio (~1.5 s) o tras 8 s.
- **Escribí algo** → se manda como mensaje directo (sin micrófono).
- **Escribí `salir`** (o `exit`, `chau`, `q`) → termina el programa.

### Flags útiles

```bash
python main.py --text        # modo solo texto: no usa el micrófono
python main.py --list-devices  # lista los micrófonos/altavoces detectados
```

## Solución de problemas

| Problema | Solución |
|----------|----------|
| "Falta la clave de Gemini" | Creá la key y completá `.env` |
| "No se pudo usar el micrófono" | Revisá que el micrófono no esté bloqueado y corré `python main.py --list-devices` |
| "No detecté voz" | Acercate al micrófono o hablá más fuerte; ajustá `RMS_THRESHOLD` en `main.py` |
| No se escucha la respuesta | Revisá el volumen del sistema y el dispositivo de salida |
| Error de red en la IA/reconocimiento | Verificá tu conexión a internet |

## Estructura

```
gTTS/
  main.py           # todo el flujo (grabar → texto → IA → voz)
  requirements.txt  # dependencias
  .env.example      # plantilla de configuración
  .gitignore        # excluye .env y caché
  README.md         # este archivo
```

## Etapas del flujo (referencia para el informe)

1. **Grabación** — `sounddevice` captura 16 kHz mono; detección de silencio por RMS
   (umbral de energía por bloque de 0,2 s).
2. **Reconocimiento** — `speech_recognition.recognize_google` convierte el audio en texto.
3. **IA** — `google-genai` (SDK oficial de Gemini) responde con memoria de conversación
   (la clase `chats` guarda el historial).
4. **Síntesis** — `gTTS` genera un `.mp3` temporal en español.
5. **Reproducción** — `pygame.mixer.music` lo reproduce sin abrir reproductores externos y
   borra el temporal al terminar.
