"""
AI Transcriber — FastAPI backend
Render deploy: build=pip install -r requirements.txt | start=uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import os
import re
import uuid
import threading
import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from faster_whisper import WhisperModel

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from docx import Document as DocxDoc
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.3-70b-versatile"

APP_DIR    = Path(__file__).parent
UPLOAD_DIR = APP_DIR / "uploads"
OUTPUT_DIR = APP_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
app = FastAPI(title="AI Transcriber API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)

# ---------------------------------------------------------------------------
# Whisper model cache
# ---------------------------------------------------------------------------
MODEL_CACHE: dict = {}

def get_model(size: str) -> WhisperModel:
    if size not in MODEL_CACHE:
        MODEL_CACHE[size] = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=4)
    return MODEL_CACHE[size]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
LINE_RE = re.compile(r"\[(\d+(?:\.\d+)?)s -> (\d+(?:\.\d+)?)s\]\s?(.*)")

def _plain_text(raw: str) -> str:
    parts = []
    for line in raw.splitlines():
        m = LINE_RE.match(line.strip())
        parts.append(m.group(3) if m else line.strip())
    return " ".join(p for p in parts if p)

def _srt_time(seconds: float) -> str:
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

# ---------------------------------------------------------------------------
# Background transcription worker
# ---------------------------------------------------------------------------
JOBS: dict = {}

def _worker(job_id: str, audio_path: str, model_size: str, lang, task: str, multilingual: bool, prompt):
    job = JOBS[job_id]
    try:
        model = get_model(model_size)
        segments, info = model.transcribe(
            audio_path,
            language=lang,
            task=task,
            multilingual=multilingual,
            initial_prompt=prompt,
            vad_filter=True,
        )
        total = getattr(info, "duration", 0) or 0
        job["total"] = total
        job["lang"]  = info.language
        with open(job["txt_path"], "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text.strip()}\n")
                f.flush()
                job["done"]     = seg.end
                job["progress"] = min(seg.end / total, 0.999) if total else 0.0
        job["progress"] = 1.0
        job["status"]   = "completed"
    except Exception as e:
        job["status"] = "error"
        job["error"]  = str(e)
    finally:
        try:
            os.remove(audio_path)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"status": "ok", "service": "AI Transcriber API"}


@app.post("/api/transcribe")
async def start_transcribe(
    file: UploadFile = File(...),
    model: str      = Form("small"),
    language: str   = Form("auto-detect"),
    multilingual: bool = Form(False),
    task: str       = Form("transcribe"),
    key_terms: str  = Form(""),
):
    ext       = Path(file.filename or "audio.mp3").suffix or ".audio"
    job_id    = str(uuid.uuid4())
    audio_path = str(UPLOAD_DIR / f"{job_id}{ext}")

    with open(audio_path, "wb") as f:
        f.write(await file.read())

    txt_path = str(OUTPUT_DIR / f"{job_id}.txt")
    lang     = None if (language == "auto-detect" or multilingual) else language
    prompt   = key_terms.strip() or None

    JOBS[job_id] = {
        "status":   "running",
        "progress": 0.0,
        "done":     0,
        "total":    0,
        "txt_path": txt_path,
        "error":    None,
        "lang":     None,
    }

    threading.Thread(
        target=_worker,
        args=(job_id, audio_path, model, lang, task, multilingual, prompt),
        daemon=True,
    ).start()

    return {"job_id": job_id}


@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    job = JOBS[job_id]
    transcript = ""
    if os.path.exists(job["txt_path"]):
        try:
            with open(job["txt_path"], encoding="utf-8") as f:
                transcript = f.read()
        except Exception:
            pass
    return {
        "job_id":     job_id,
        "status":     job["status"],
        "progress":   job["progress"],
        "done":       job["done"],
        "total":      job["total"],
        "lang":       job["lang"],
        "transcript": transcript,
        "error":      job.get("error"),
    }


# ---------------------------------------------------------------------------
# AI routes
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    transcript: str
    history:    List[ChatMessage] = []
    message:    str

@app.post("/api/ai/chat")
def ai_chat(req: ChatRequest):
    if not GROQ_AVAILABLE:
        raise HTTPException(status_code=500, detail="Groq package not installed on server.")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set.")
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="No transcript provided.")

    plain  = _plain_text(req.transcript)
    system = (
        "You are a professional document assistant. The user has transcribed an audio recording "
        "and wants help processing it into a useful document.\n\n"
        f"FULL TRANSCRIPT:\n---\n{plain[:12000]}\n---\n\n"
        "Help with whatever the user asks. Be clear, professional, and well-structured. "
        "Use markdown: ## for headings, **bold** for key terms, - for bullet lists."
    )

    messages = [{"role": "system", "content": system}]
    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    try:
        client = Groq(api_key=GROQ_API_KEY)
        resp   = client.chat.completions.create(
            model=GROQ_MODEL, messages=messages, max_tokens=4096, temperature=0.3
        )
        return {"reply": resp.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DocxRequest(BaseModel):
    content: str
    title:   str = "Document"

@app.post("/api/ai/docx")
def generate_docx(req: DocxRequest):
    if not DOCX_AVAILABLE:
        raise HTTPException(status_code=500, detail="python-docx not installed on server.")

    doc = DocxDoc()
    doc.add_heading(req.title, 0)

    for line in req.content.splitlines():
        line = line.strip()
        if not line:
            doc.add_paragraph()
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:], style="List Bullet")
        elif re.match(r"^\d+\.\s", line):
            doc.add_paragraph(re.sub(r"^\d+\.\s", "", line), style="List Number")
        else:
            p     = doc.add_paragraph()
            parts = re.split(r"\*\*(.*?)\*\*", line)
            for i, part in enumerate(parts):
                run      = p.add_run(part)
                run.bold = (i % 2 == 1)

    ts       = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = str(OUTPUT_DIR / f"document_{ts}.docx")
    doc.save(out_path)

    return FileResponse(
        out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"document_{ts}.docx",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)
