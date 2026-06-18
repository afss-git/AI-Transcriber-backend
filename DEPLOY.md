# 🚀 How to Put the Transcriber Online (Beginner's Guide)

> You've never deployed an app before — that's totally fine. This guide assumes
> **zero experience**. Follow it top to bottom and by the end you'll have a real
> website link you can send to anyone, running on a real server (NOT your PC).
> No coding, and **no command line / git required.**

---

## 1. What does "deploy" even mean?

Right now your Transcriber runs on **your laptop**. When you close it, it's gone,
and only you can reach it.

**Deploying** means putting it on a computer in the cloud (a "server") that:
- stays on 24/7 (your laptop can be off),
- has its own public web address (a link), and
- anyone in the world can open in their browser.

Think of it like the difference between cooking food in your kitchen (your laptop)
vs. opening a restaurant anyone can walk into (deployed).

---

## 2. What you'll end up with

A link like:
```
https://huggingface.co/spaces/yourname/transcriber
```
You send that link to a friend in another country, they open it, drag in an audio
file, and get a transcript — all without touching your computer. 🎉

---

## 3. The plan: Hugging Face Spaces (and why)

We'll use **Hugging Face Spaces**. It's a free platform built *specifically* for
hosting AI apps like this one. Why it's the right choice for you:

- ✅ **Free** to start.
- ✅ **Not your PC** — runs on their servers, always on.
- ✅ **No command line, no git** — you can upload files by clicking buttons.
- ✅ Built for exactly this (Gradio apps + Whisper models).

> There are other ways (Render, Railway, your own server) but they're harder and/or
> cost money. Spaces is the gentlest on-ramp. You can always move later.

---

## 4. Before you start — your checklist

You need just **two files** (both already prepared for you in this folder,
`C:\Users\HP\Transcriber\`):

| File | What it is |
|---|---|
| `app.py` | Your actual Transcriber app (the code). |
| `requirements.txt` | A list telling the server what to install (just `faster-whisper`). |

And you'll need:
- [ ] A **Hugging Face account** (free — we make it in Step 1).
- [ ] About **15 minutes**.

That's it. You do **not** need to upload the `outputs/` folder, the `.bat` file, or
this guide.

---

## 5. Step-by-step deployment

### STEP 1 — Create a free Hugging Face account
1. Go to **https://huggingface.co/join**
2. Sign up with your email (or Google). Confirm your email.
3. Pick a username — this becomes part of your app's link, so choose something clean
   (e.g. `harbours`, `yourname`). Lowercase, no spaces.

> 💡 Hugging Face is like "GitHub for AI" — a home for models and AI apps. Free account is all you need.

---

### STEP 2 — Create a new Space
1. Click your profile picture (top right) → **New Space**.
   (Or go straight to **https://huggingface.co/new-space**)
2. Fill in the form:
   - **Owner:** your username (leave as is).
   - **Space name:** `transcriber` (this becomes the link). Lowercase, no spaces.
   - **License:** choose **MIT** (means "anyone can use it" — simplest).
   - **Select the Space SDK:** click **Gradio**. ⬅️ *This is important — Gradio is what your app is built with.*
   - **Gradio version:** leave it on the **latest** offered (must be 6.x or newer).
   - **Space hardware:** choose **CPU basic — FREE**. (You can upgrade later for speed.)
   - **Visibility:** choose **Public** (so anyone can use it) — or **Private** if you only want yourself for now.
3. Click **Create Space**.

You now have an empty Space. Hugging Face automatically created the behind-the-scenes
config file for you — you don't have to touch it. 🎈

---

### STEP 3 — Upload your two files
1. On your new Space page, click the **Files** tab (near the top).
2. Click **+ Add file** → **Upload files**.
3. From `C:\Users\HP\Transcriber\`, drag in **`app.py`** and **`requirements.txt`**.
4. Scroll down, click **Commit changes to main** (the green button).

> ⚠️ If it asks about overwriting an existing `app.py` (Hugging Face makes a placeholder one),
> say **yes / overwrite**. You want YOUR app.py to win.

---

### STEP 4 — Watch it build
- The Space switches to a **"Building"** status and shows a log scrolling by.
  This is the server installing `faster-whisper` and everything it needs.
  **First build takes a few minutes — this is normal.** Go get water.
- When it's ready, the status turns to **"Running"** and your app appears.

---

### STEP 5 — Test it and share it
1. Click the **App** tab. Your Transcriber UI loads — same one you've been using.
2. Drop in a **short** audio clip first (30–60 sec) to test, pick the **`tiny`** or
   **`base`** model for the first test (fast), and click Transcribe.
3. The very first transcription is **slow** — the server has to download the model
   once. After that it's cached and faster.
4. Copy your link from the browser address bar and **send it to a friend.** Done. ✅

---

## 6. Important things to know (read this — it saves confusion)

- **🐢 The free server is slow-ish.** It's a modest cloud CPU (like a basic laptop).
  `tiny`/`base`/`small` work fine. `medium`/`large-v3` will be slow (same physics as
  your laptop, just someone else's machine). For most friends, **`small` is the sweet spot.**
- **😴 Free Spaces "go to sleep"** after ~48 hours of no use. The next visitor wakes it
  (takes ~30 seconds to start up). That's normal for free hosting.
- **🧹 Storage is temporary.** The `outputs/` folder on the server gets wiped when the
  Space restarts. That's fine — users **download** their transcript; it doesn't need to
  live on the server.
- **🌍 Public = anyone can use it.** Good for sharing, but strangers could upload big
  files and slow it down. See "Optional extras" below to add a password if you want.
- **💸 It stays free** unless YOU choose to upgrade the hardware. You won't be charged
  by accident.

---

## 7. How to update your app later
Changed something in `app.py`? Just:
1. Go to your Space → **Files** tab → click `app.py` → **Edit** (pencil icon), or
   re-upload the file the same way as Step 3.
2. Commit. The Space rebuilds itself automatically. No reinstalling anything.

---

## 8. Troubleshooting

| Problem | What to do |
|---|---|
| Status stuck on **"Building"** for 10+ min | Click the **Logs** tab and read the bottom. Usually it's still installing — wait. |
| **"Build failed"** / red error | Open **Logs**, copy the last red lines, and send them to me — I'll tell you the fix. Most often it's a typo in `requirements.txt`. |
| App loads but **"Error"** when transcribing | First run is just slow (downloading the model). Wait and retry. If it persists, check Logs. |
| Everything is **very slow** | Use a smaller model (`tiny`/`base`), or upgrade hardware (Section 9). |
| App tab shows a **blank/grey screen** | Hard-refresh the page (Ctrl+Shift+R). If still blank, check the Space is "Running." |

> Whenever you're stuck: the **Logs** tab is your friend. Copy the last 10–15 lines and
> send them to me — that's all I need to diagnose it.

---

## 9. Optional extras (do these later, not now)

- **🔒 Add a password** (so only people you trust can use it): in `app.py`, change the
  last line to `demo.launch(auth=("friend", "yourpassword"))`. Re-upload. Now it asks
  for a login.
- **⚡ Make it fast (paid GPU):** Space → **Settings** → **Hardware** → pick a GPU
  (~$0.40–0.60/hour). Set it to **sleep when idle** so you only pay while it's used.
  A GPU makes even `large-v3` faster than real-time.
- **💾 Permanent storage:** Space → Settings → add **Persistent Storage** (small monthly
  fee) if you ever want transcripts to survive restarts.
- **🏷️ Nicer link / custom domain:** possible later via Settings, once you're comfortable.

---

## 10. Cost summary
- **Today, as written:** **$0.** Free account, free CPU, public app.
- **Only if you choose to upgrade:** GPU hardware is hourly and optional; you control it.

---

## ✅ Your action list (the short version)
1. Make a free Hugging Face account.
2. New Space → name `transcriber`, SDK = **Gradio**, hardware = **CPU free**, **Public**.
3. Upload `app.py` + `requirements.txt`, commit.
4. Wait for **"Running."**
5. Test with a short clip + `small` model.
6. Share your link. 🎉

Stuck at any step? Tell me which step number and what you see on screen — I'll get you
through it.
