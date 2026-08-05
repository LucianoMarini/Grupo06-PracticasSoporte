# AGENTS.md

Voice assistant (mic → STT → Gemini → gTTS → pygame), single script `main.py`. Python 3.14, Windows.

## Critical dependency constraints
- Use `pygame-ce` (not `pygame`): official `pygame` has **no wheels for Python 3.14** and fails to build from source. `pygame-ce` imports as `pygame`. Do not swap it back.
- Mic input uses `sounddevice` (not PyAudio, which also lacks 3.14 wheels). `SpeechRecognition.Microphone` requires PyAudio, so audio is captured with `sounddevice` and fed to the recognizer via a manually built `sr.AudioData`.
- AI uses the current `google-genai` SDK (`from google import genai`). The old `google-generativeai` package is deprecated — do not reintroduce it.

## Gemini model gotcha
Older models are unavailable to new accounts: `gemini-2.0-flash` returns 429 quota-0, `gemini-2.5-flash`/`gemini-1.5-flash` return 404. Use `gemini-flash-latest` (stable alias). It lives in `.env` as `GEMINI_MODEL` and as the default in `main.py`.

## Config / secrets
- `GEMINI_API_KEY` is required; loaded from `.env` via `python-dotenv` (`load_dotenv()` runs at import, so the `.env` must sit in the repo root / CWD).
- `.env` is gitignored — never commit it. `.env.example` is the shareable template. A real key is present in the local `.env`; don't print it or reference it in docs.

## Run / verify
- No tests and no linter configured. Verify via: `python -m py_compile main.py`, `python main.py --list-devices`, then `echo "mensaje" | python main.py --text` (piped input ends the loop via EOFError → clean exit).
- Commands: `python main.py` (voice), `python main.py --text` (no mic), `python main.py --list-devices`.
- On the Windows console, accented output may render garbled (cp1252 vs UTF-8); cosmetic only — source files stay UTF-8.

## Flow
`record_audio()` (sounddevice, VAD by RMS, 0.2 s blocks, silence cutoff ~1.5 s, max 8 s) → `listen_and_recognize()` (`recognize_google`, es-AR) → `ask_ai()` (`chats.create` with system_instruction; keeps conversation memory) → `speak()` (gTTS to temp mp3, `pygame.mixer.music` plays it, temp deleted in `finally`).
