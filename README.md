# 🔐 Vaultix CDN Edition

**Vaultix** is a sleek, desktop-ready password and account manager built with Python + PyWebView, using modern HTML/CSS/JS delivered entirely via CDN.  
This version runs **without Node.js, npm, or any bundler** — no Vite, no Webpack. Just open, run, and go.

---

## 📦 Features

- 🔐 Master password login (real encryption with Fernet)
- 🧊 Beautiful UI with glassmorphism and gradient theming
- 🧠 Secure account vault with add/edit/delete
- 💾 Save/load encrypted data from disk
- ⚙️ Tray support and autostart (optional)
- 🌙 Light/dark styling (CSS only)
- ✨ Fully responsive design

- 🔑 Default "vaultix123"
---

## 🚀 How It Works

- Frontend is written in **vanilla HTML + CDN React** — no local build step.
- Backend is **pure Python** via [PyWebView](https://pywebview.flowrl.com/).
- Encrypted vault is stored locally using `cryptography.fernet`.

---

## ▶️ Running the App

```bash
pip install -r requirements.txt
python app.py
