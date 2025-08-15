
import streamlit as st
import replicate
import openai
import os

# Judul aplikasi
st.title("🏡 Rumah AI Sketsa")
st.write("Buat gambaran sketsa rumah dengan AI berdasarkan ukuran tanah, jumlah lantai, dan fitur tambahan.")

# Input ukuran tanah
ukuran_tanah = st.text_input("Masukkan ukuran tanah (contoh: 10x20 meter atau 1000 cm² atau 0.5 hektar)")
jumlah_lantai = st.number_input("Jumlah lantai", min_value=1, max_value=10, value=1)

# Pilihan fitur tambahan
fitur = st.multiselect("Pilih fitur tambahan", [
    "Halaman rumah",
    "Kolam renang",
    "Toilet dalam",
    "Toilet luar",
    "Ruang tamu",
    "Tempat parkir",
    "Pagar rumah"
])

# API Keys
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Fungsi generate sketsa dengan Replicate
def generate_sketsa(prompt):
    model = "stability-ai/stable-diffusion-xl"
    output = replicate.run(
        model + ":9d7a5f6530d20e8ed1a7818a2355cf0c74208fcb1b31e2ba730c6c78d5d0e9f3",
        input={"prompt": prompt, "width": 512, "height": 512}
    )
    return output[0] if output else None

# Fungsi buat deskripsi gambar dengan OpenAI
def describe_image(image_url):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Deskripsikan gambar rumah ini secara singkat dan menarik."},
            {"role": "user", "content": f"Deskripsikan gambar berikut: {image_url}"}
        ]
    )
    return response.choices[0].message["content"]

# Fungsi buat rekomendasi denah
def recommend_layout(ukuran, lantai, fitur_list):
    fitur_text = ", ".join(fitur_list) if fitur_list else "tanpa fitur tambahan"
    prompt = f"Buat rekomendasi denah rumah ukuran {ukuran}, {lantai} lantai, dengan {fitur_text}."
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

# Tombol generate sketsa
if st.button("🎨 Generate Sketsa"):
    if not ukuran_tanah:
        st.warning("Masukkan ukuran tanah terlebih dahulu!")
    else:
        prompt_text = f"Sketsa arsitektur rumah ukuran {ukuran_tanah}, {jumlah_lantai} lantai, dengan fitur: {', '.join(fitur)}"
        image_url = generate_sketsa(prompt_text)
        if image_url:
            st.image(image_url, caption="Sketsa Rumah AI")
            st.session_state["generated_image"] = image_url
        else:
            st.error("Gagal membuat sketsa. Periksa API key Replicate Anda.")

# Tombol buat deskripsi dari sketsa
if st.button("📝 Buat Deskripsi dari Sketsa"):
    if "generated_image" in st.session_state:
        desc = describe_image(st.session_state["generated_image"])
        st.success(desc)
    else:
        st.warning("Buat sketsa dulu sebelum mendeskripsikannya.")

# Tombol buat rekomendasi denah
if st.button("📐 Buat Rekomendasi Denah"):
    if ukuran_tanah:
        denah = recommend_layout(ukuran_tanah, jumlah_lantai, fitur)
        st.info(denah)
    else:
        st.warning("Masukkan ukuran tanah terlebih dahulu.")
