# 🏠 Perancang Sketsa Rumah (AI+) — Streamlit

Aplikasi ini membuat **site plan + denah konseptual (SVG)** dari ukuran lahan, jumlah lantai, dan fitur pilihan; menampilkan **estimasi luas ruang**; serta bisa **generate render AI** (opsional) via OpenAI Images atau Replicate SDXL.

## ✨ Fitur
- Input ukuran lahan (m/cm), jumlah lantai, fitur (halaman, kolam, toilet, ruang tamu, parkir, pagar).
- Site plan & denah per lantai (multi-tab), **unduh SVG**.
- **Estimasi luas** per fungsi ruang (otomatis).
- **Prompt** rekomendasi untuk generator gambar AI.
- (Opsional) **AI Render** via:
  - **OpenAI Images** (`OPENAI_API_KEY`)
  - **Replicate SDXL** (`REPLICATE_API_TOKEN`)

## 🛠️ Jalankan Lokal
```bash
pip install -r requirements.txt
streamlit run rumah_ai_app.py
```

## ☁️ Deploy (Streamlit Community Cloud)
1. Buat repo Public, upload tiga file:
   - `rumah_ai_app.py`
   - `requirements.txt`
   - `README.md`
2. Di Streamlit Cloud → New app → pilih repo & branch → **Main file path**: `rumah_ai_app.py` → Deploy.

### 🔐 Secrets (opsional, untuk AI Render)
Di Streamlit Cloud, buka **App → Settings → Secrets**, isi:
```toml
OPENAI_API_KEY = "sk-..."
REPLICATE_API_TOKEN = "r8_..."
```