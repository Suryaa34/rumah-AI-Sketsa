import streamlit as st
import replicate
import openai
import os

# ======================
# Ambil API Key dari Streamlit Secrets
# ======================
REPLICATE_API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN", None)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)

if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
else:
    st.error("⚠️ REPLICATE_API_TOKEN belum diatur di Secrets Streamlit.")
    st.stop()

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    st.warning("⚠️ OPENAI_API_KEY belum diatur. Fitur OpenAI mungkin tidak berfungsi.")

# ======================
# UI Aplikasi
# ======================
st.title("🏡 Rumah AI Sketsa")
st.write("Masukkan detail rumah dan dapatkan sketsa AI sesuai ukuran dan fitur pilihan Anda.")

# Input ukuran tanah
ukuran_tanah = st.number_input("Masukkan ukuran tanah", min_value=1.0, step=1.0)
satuan_tanah = st.selectbox("Pilih satuan", ["cm", "m", "hektar"])

# Jumlah lantai
jumlah_lantai = st.number_input("Jumlah lantai rumah", min_value=1, step=1)

# Fitur tambahan
fitur_tambahan = st.multiselect(
    "Pilih fitur tambahan:",
    ["Halaman rumah", "Kolam renang", "Toilet dalam", "Toilet luar", "Ruang tamu", "Tempat parkir", "Pagar rumah"]
)

# ======================
# Fungsi Generate Gambar
# ======================
def generate_sketsa(ukuran, satuan, lantai, fitur):
    prompt = f"Sketsa rumah {lantai} lantai dengan ukuran tanah {ukuran} {satuan}, dilengkapi {', '.join(fitur)}."
    try:
        output = replicate.run(
            "stability-ai/stable-diffusion:db21e45e1de...ganti_dengan_version_ID",
            input={
                "prompt": prompt,
                "width": 512,
                "height": 512
            }
        )
        return output
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memanggil Replicate API: {str(e)}")
        return None

# ======================
# Tombol Generate
# ======================
if st.button("🔍 Buat Sketsa"):
    if not fitur_tambahan:
        st.warning("Pilih minimal satu fitur tambahan rumah.")
    else:
        st.info("⏳ Membuat sketsa AI, harap tunggu...")
        result = generate_sketsa(ukuran_tanah, satuan_tanah, jumlah_lantai, fitur_tambahan)
        if result:
            st.image(result, caption="Sketsa AI", use_column_width=True)
