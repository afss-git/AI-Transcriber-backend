# CLAUDE.md — Project Context & Agent Instructions

> This file briefs any AI agent (Claude Code) that opens this folder. Read it fully
> before doing anything. The user's #1 goal right now: **deploy this app to a live
> cloud server (NOT their PC) and test it.** Your job is to guide them through it
> step by step, beginner-style.

---

## 1. What this project is

A **free, local + deployable audio/video transcription web app**. It turns speech
into text. Built with **Gradio** (the web UI) on top of **faster-whisper** (an
optimized version of OpenAI's open-source Whisper speech-to-text model). Everything
runs locally / offline — no API keys, no per-minute fees.

It was built to transcribe long lectures (including **mixed Arabic + English**) and
has been hardened to be **disconnect-proof**.

## 2. Who the user is (important context)

- **Beginner at deployment** — has never deployed a model/app before. Explain things
  in plain language, avoid jargon, give exact click-by-click steps, set expectations.
- Is a **content creator**, comfortable enough to run files but not a DevOps person.
- **Hardware:** Windows 11, Intel i5-8350U (4 cores), **no GPU**. CPU-only.
- Has prior **Next.js** experience (built other web projects), but this app is Python/Gradio.
- Speaks English; sometimes uses **Nigerian Pidgin**. Be warm and clear.

## 3. The deployment goal & chosen path

- The user explicitly wants: **a real live server, NOT their PC, with a clean UI anyone can use.**
- **Chosen platform: Hugging Face Spaces** (free, cloud-hosted, no command line / no git
  needed — files are uploaded through the website).
- The full beginner walkthrough already exists in **`DEPLOY.md`** — follow it with them.
- Deploy path summary: free HF account → create a **Gradio** Space on **CPU (free)**,
  **Public** → upload `app.py` + `requirements.txt` → wait for "Running" → test → share link.

## 4. Files in this folder

| File | Purpose |
|---|---|
| `app.py` | The whole app (Gradio UI + transcription logic). The entry point. |
| `requirements.txt` | Dependencies for the cloud to install (just `faster-whisper`; Gradio is provided by the HF Space SDK). |
| `DEPLOY.md` | **Beginner step-by-step deployment guide.** The human-facing instructions. |
| `README.md` | How to run/use the app locally. |
| `run-transcriber.bat` | Double-click to launch the app locally (for testing before deploy). |
| `CLAUDE.md` | This file — agent context. |

## 5. How to TEST locally before deploying (do this first)

Confirm it still works on the user's machine before pushing live:
```bash
cd "C:/Users/HP/AI-Transcriber"
python -m pip install -U faster-whisper gradio   # if not already installed
python app.py
```
A browser opens at `http://127.0.0.1:7860`. Or the user can double-click
`run-transcriber.bat`. Test with a short clip + the `small` model.

> If launching as a background process to verify it started, check that port 7860
> returns HTTP 200, then tell the user the link. Don't block the terminal.

## 6. How the app works (technical notes for the agent)

- **Gradio 6.x API** (note: in v6, `theme=` goes in `demo.launch()`, not `gr.Blocks()`;
  `gr.Textbox` has no `show_copy_button`). If you edit the UI, respect v6 conventions.
- **Models:** `tiny`/`base`/`small`/`medium`/`large-v3`. On CPU, `small` is the sweet
  spot. `medium`/`large-v3` are slow on CPU (and on HF free tier). Models download once,
  then cache.
- **Multilingual toggle** → passes `multilingual=True` to faster-whisper, which
  re-detects language per ~30s chunk. This is what makes **Arabic + English** lectures
  transcribe in their correct scripts. (Limitation: a single foreign word mid-sentence
  may get absorbed into the surrounding language. `small` can also produce repetition-loop
  artifacts during dense recitation — flag, don't pretend it's perfect.)
- **Disconnect-proof design:** transcription runs in a **background worker thread** and
  writes each line to disk in `outputs/` immediately (with flush). A `JOBS` registry +
  a polling generator drive the live progress UI. So closing the browser/losing the
  network never loses progress; a "Recover" panel reloads any saved transcript.
- **VAD** (`vad_filter=True`) skips silence for speed. `cpu_threads=4` tuned to the
  user's CPU.
- `outputs/` is recreated at runtime; it is NOT needed for deployment and should not be
  uploaded. On HF free tier it's ephemeral (wiped on restart) — that's fine; users
  download their transcript.

## 7. Deployment gotchas to watch for

- On HF Spaces, **don't pin `gradio` in `requirements.txt`** — the Space SDK controls
  the Gradio version. Tell the user to pick the **latest Gradio version (6.x)** when
  creating the Space. `requirements.txt` should stay as just `faster-whisper`.
- When uploading, HF may have auto-created a placeholder `app.py` — **overwrite it**.
- First transcription on the Space is slow (model download). Normal. Use a small model
  + short clip to test.
- Free Spaces **sleep** after inactivity; first visit wakes them (~30s).
- If the build fails: open the Space's **Logs** tab, read the last lines, diagnose from there.

## 8. Optional upgrades the user may ask about later

- **Password:** `demo.launch(auth=("user","password"))`.
- **Speed/scale:** upgrade the Space to a paid GPU (hourly; set to sleep when idle).
- **Persistent storage:** HF Spaces add-on if transcripts must survive restarts.

## 9. How you (the agent) should behave here

- **Guide, don't dump.** Walk the user through deployment one step at a time; after each
  step ask what they see on screen before moving on.
- When they hit an error, ask for the **Logs** output (last ~15 lines) and diagnose.
- Keep it beginner-friendly and encouraging. Set honest expectations about free-tier speed.
- Verify locally first (Section 5), then deploy (Section 3 / `DEPLOY.md`), then test the
  live link together.

---

**START HERE when the user opens this folder:** confirm they want to deploy, do a quick
local test (Section 5), then open `DEPLOY.md` and walk them through Hugging Face Spaces
step by step.
