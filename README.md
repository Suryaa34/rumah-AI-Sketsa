
# 🏡 Rumah AI Sketsa

Aplikasi Streamlit untuk membuat **gambaran sketsa rumah** menggunakan AI (Replicate + OpenAI).

## 🚀 Fitur
- Input ukuran tanah (cm/m/hektar)
- Pilih jumlah lantai
- Pilih fitur tambahan rumah
- Generate gambar/sketsa AI dengan Replicate
- Deskripsi gambar menggunakan OpenAI
- Rekomendasi denah rumah menggunakan OpenAI

## 📦 Instalasi
1. Clone repo ini
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan:
   ```bash
   streamlit run app.py
   ```

## 🔑 API Keys
Tambahkan di **Streamlit Secrets** atau environment variables:
```
REPLICATE_API_TOKEN=token_anda
OPENAI_API_KEY=key_anda
```

## 📌 Deploy di Streamlit Cloud
1. Upload repo ke GitHub
2. Hubungkan ke Streamlit Cloud
3. Tambahkan Secrets seperti di atas
