# 🎙️ Local Transcriber

A free, offline audio/video transcription app that runs entirely on your own
computer. No uploads, no API keys, no per-minute fees. Powered by
[Whisper](https://github.com/openai/whisper) via
[faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## How to launch

- **Easiest:** double-click `run-transcriber.bat`.
- **Or** from a terminal in this folder: `python app.py`

A browser tab opens automatically (usually at http://127.0.0.1:7860).

## How to use

1. Drag any audio or video file into the upload box (mp3, wav, m4a, mp4, mpeg…).
2. Pick a **model**:
   - `tiny` / `base` / `small` — faster, less accurate.
   - `medium` — good default for clear speech.
   - `large-v3` — best accuracy (names, accents, foreign terms), but slow on CPU.
3. Leave **language** on `auto-detect`, or pick one to force it.
4. Choose an output format (timestamped text, plain text, or `.srt` subtitles).
5. Click **Transcribe** and watch the progress bar.
6. Copy the text or download the file.

## Notes

- The first time you use a model size it downloads once (~75 MB for `tiny`
  up to ~3 GB for `large-v3`), then it's cached at
  `C:\Users\HP\.cache\huggingface\` and reused instantly.
- This machine has no GPU, so transcription runs on the CPU. Expect roughly
  real-time-ish for `medium` and several times slower for `large-v3`.
- Transcripts are written to your temp folder and offered as a download.
  Nothing ever leaves your computer.

## Requirements (already installed)

- Python 3.11
- `faster-whisper`
- `gradio`

Re-install if needed: `python -m pip install -U faster-whisper gradio`
