
import streamlit as st
import replicate

# Judul aplikasi
st.title("🏠 AI Sketsa Rumah")
st.write("Masukkan detail rumah impian Anda, dan AI akan membuatkan gambaran sketsanya.")

# Input ukuran rumah
panjang = st.number_input("Panjang tanah", min_value=1.0, step=0.5, format="%.2f")
lebar = st.number_input("Lebar tanah", min_value=1.0, step=0.5, format="%.2f")
satuan = st.selectbox("Satuan ukuran", ["cm", "m", "hektar"])

# Jumlah tingkat
tingkat = st.number_input("Jumlah tingkat", min_value=1, step=1)

# Fitur tambahan
st.subheader("Fitur Tambahan")
fitur_list = [
    "Halaman rumah",
    "Kolam renang",
    "Toilet dalam",
    "Toilet luar",
    "Ruang tamu",
    "Tempat parkir kendaraan",
    "Pagar rumah"
]
fitur_dipilih = st.multiselect("Pilih fitur yang diinginkan", fitur_list)

# Tombol generate
if st.button("Buat Sketsa AI"):
    with st.spinner("Menghasilkan sketsa rumah..."):
        try:
            # Ambil token Replicate dari secrets
            replicate_token = st.secrets["REPLICATE_API_TOKEN"]
            replicate.Client(api_token=replicate_token)

            # Buat prompt deskripsi
            prompt = f"Architectural sketch of a {panjang} x {lebar} {satuan} house with {tingkat} floors"
            if fitur_dipilih:
                prompt += ", including: " + ", ".join(fitur_dipilih)
            prompt += ", top view and perspective, clean design, high detail, blueprint style"

            # Panggil model Stable Diffusion XL
            output = replicate.run(
                "stability-ai/sdxl:5fca5cf47f7a7cf6e48a72f3aa7b50bcf6d888af34c0485e2290a99046b6f9e7",
                input={
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1024
                }
            )

            # Tampilkan hasil gambar
            if output:
                st.image(output[0], caption="Sketsa AI Rumah", use_column_width=True)
            else:
                st.error("Gagal membuat sketsa. Coba lagi.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
