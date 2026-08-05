# Cómo probar el asistente

## 1. Conseguir tu API key de Gemini

Cada persona necesita **su propia key** (es gratuita):

1. Entrá a https://aistudio.google.com/apikey
2. Iniciá sesión con tu cuenta de Google.
3. Tocá **Create API key** → elegí un proyecto → copiá la clave.

## 2. Configurar el `.env`

Copiá la plantilla (te subo el `.env.example` para que te guíes):

```bash
copy .env.example .env
```

Abrí el `.env` y pegá tu key en `GEMINI_API_KEY`. Dejá el resto como está:

```
GEMINI_API_KEY=tu_key_aca
GEMINI_MODEL=gemini-flash-latest
TTS_LANG=es
SPEECH_LANG=es-AR
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Probar el asistente

Modo texto (sin micrófono):

```bash
python main.py --text
```

Modo voz completo (micrófono + audio):

```bash
python main.py
```

Dentro del programa:

- **Presioná Enter (vacío)** para empezar a hablar.
- **Escribí un mensaje** para mandarlo por texto.
- **Escribí `salir`** para terminar.

## Ver dispositivos de audio

```bash
python main.py --list-devices
```
