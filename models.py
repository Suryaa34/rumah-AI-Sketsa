# models.py
# Konfigurasi model Replicate untuk aplikasi sketsa rumah

# Nama model & versi dari Replicate
MODEL_NAME = "stability-ai/sdxl"
MODEL_VERSION = "1b12df7f34f5a4ef8d56cfae57dc3d0fbcfba0b7a2c5a4e64d0d1e3a76af4f4"

# Parameter default untuk generate gambar
DEFAULT_PARAMS = {
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 30,
    "guidance_scale": 7.5
}
