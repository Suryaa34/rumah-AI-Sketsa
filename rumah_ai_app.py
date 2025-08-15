import os
import io
import base64
import requests
from dataclasses import dataclass
from typing import List, Dict, Tuple

import streamlit as st

st.set_page_config(page_title="Perancang Sketsa Rumah (AI+)", page_icon="🏠", layout="wide")

# =========================
# Utilities & Data
# =========================

ROOM_PRESETS_GROUND = [
    "Ruang Tamu", "Ruang Keluarga", "Dapur", "Kamar Tidur Tamu",
    "Toilet (Dalam)", "Gudang/Service"
]
ROOM_PRESETS_UPPER = [
    "Kamar Tidur Utama", "Kamar Tidur Anak", "Kamar Tidur Anak 2",
    "Kamar Mandi", "Ruang Kerja", "Ruang Santai"
]

@dataclass
class Lot:
    width_m: float
    length_m: float
    floors: int

def to_meters(value: float, unit: str) -> float:
    if unit == "cm":
        return value / 100.0
    return value  # assume meters otherwise

def svg_wrap(content: str, width_px: int, height_px: int) -> str:
    style = """
.lot { fill: #f3f4f6; stroke: #111827; stroke-width: 2; }
.house { fill: #e5e7eb; stroke: #374151; stroke-width: 1.5; }
.garden { fill: #d1fae5; stroke: #065f46; stroke-width: 1.2; }
.pool { fill: #bfdbfe; stroke: #1e40af; stroke-width: 1.2; }
.parking { fill: #e5e7eb; stroke: #6b7280; stroke-dasharray: 4 3; stroke-width: 1.2; }
.fence { fill: none; stroke: #ef4444; stroke-dasharray: 6 4; stroke-width: 2; }
.room { fill: #fef3c7; stroke: #92400e; stroke-width: 1; }
text { fill: #111827; font-family: Arial, sans-serif; }
"""
    return f'''<svg width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}" xmlns="http://www.w3.org/2000/svg">
    <style>{style}</style>
    {content}
    </svg>'''

def make_site_svg(lot_w_m: float, lot_l_m: float, floors: int, features: List[str]):
    max_px = 900
    scale = min(max_px / lot_w_m, (max_px * 0.7) / lot_l_m) if lot_w_m > 0 and lot_l_m > 0 else 1.0
    pad = 20
    W = int(lot_w_m * scale)
    H = int(lot_l_m * scale)

    content = []
    content.append(f'<rect x="{pad}" y="{pad}" width="{W}" height="{H}" class="lot" />')
    content.append(f'<text x="{pad + 6}" y="{pad - 6 + 12}" font-size="12">Lahan: {lot_w_m:.2f} m x {lot_l_m:.2f} m (Luas: {lot_w_m*lot_l_m:.1f} m²)</text>')

    ix, iy = pad + 8, pad + 8
    iW, iH = W - 16, H - 16

    has_garden = "Halaman rumah" in features
    has_pool = "Kolam renang" in features
    has_parking = "Tempat parkir" in features
    has_fence = "Pagar rumah" in features

    if has_fence:
        content.append(f'<rect x="{pad+2}" y="{pad+2}" width="{W-4}" height="{H-4}" class="fence" />')

    g_h = int(iH * 0.15) if has_garden else 0
    if has_garden:
        content.append(f'<rect x="{ix}" y="{iy}" width="{iW}" height="{g_h}" class="garden" />')
        content.append(f'<text x="{ix + iW/2}" y="{iy + g_h/2}" text-anchor="middle" dominant-baseline="middle" font-size="12">Halaman</text>')

    ph = 0
    if has_parking:
        p_w = int(iW * 0.22)
        py = iy + g_h + 4
        ph = int(iH * 0.18)
        px = ix + iW - p_w
        content.append(f'<rect x="{px}" y="{py}" width="{p_w}" height="{ph}" class="parking" />')
        content.append(f'<text x="{px + p_w/2}" y="{py + ph/2}" text-anchor="middle" dominant-baseline="middle" font-size="12">Parkir</text>')

    hx = ix
    hy = iy + g_h + 4 + (ph + 6 if has_parking else 0)
    hW = iW
    hH = iH - g_h - (ph + 6 if has_parking else 0) - 8
    hH = max(60, hH)

    content.append(f'<rect x="{hx}" y="{hy}" width="{hW}" height="{hH}" class="house" />')
    content.append(f'<text x="{hx + 6}" y="{hy + 16}" font-size="12">Bangunan Utama (x{floors} lantai)</text>')

    if "Kolam renang" in features:
        pool_w, pool_h = int(iW*0.22), int(hH*0.25)
        px = hx + hW - pool_w - 10
        py = hy + hH - pool_h - 10
        content.append(f'<rect x="{px}" y="{py}" width="{pool_w}" height="{pool_h}" class="pool" />')
        content.append(f'<text x="{px + pool_w/2}" y="{py + pool_h/2}" text-anchor="middle" dominant-baseline="middle" font-size="12">Kolam</text>')

    width_px = W + pad*2
    height_px = H + pad*2
    svg = svg_wrap("\n".join(content), width_px, height_px)

    house_foot_m = {
        "x_m": (hx - 0) / scale,
        "y_m": (hy - 0) / scale,
        "w_m": hW / scale,
        "h_m": hH / scale,
        "area_m2": (hW / scale) * (hH / scale),
    }
    house_rect_px = {"x": hx, "y": hy, "w": hW, "h": hH, "scale": scale, "pad": pad, "canvasW": width_px, "canvasH": height_px}
    return svg, house_foot_m, house_rect_px

def make_floor_svg(house_rect_px, rooms, floor_label):
    hx, hy, hW, hH = house_rect_px["x"], house_rect_px["y"], house_rect_px["w"], house_rect_px["h"]
    grid_cols, grid_rows = 2, 3
    cell_w = hW / grid_cols
    cell_h = (hH - 24) / grid_rows

    content = [f'<text x="{hx + 6}" y="{hy + 16}" font-size="12">{floor_label}</text>']
    idx = 0
    for r in range(grid_rows):
        for c in range(grid_cols):
            x = hx + c*cell_w + 4
            y = hy + 20 + r*cell_h + 4
            w = cell_w - 8
            h = cell_h - 8
            content.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" class="room" />')
            if idx < len(rooms):
                content.append(f'<text x="{x + w/2:.1f}" y="{y + h/2:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="11">{rooms[idx]}</text>')
            idx += 1

    return "\n".join(content)

def build_prompt(lot_w_m, lot_l_m, floors, features, style):
    feature_list = ", ".join(features) if features else "fitur dasar"
    return (
        f"Architectural concept sketch, site plan and facade of a {floors}-storey residential house on a {lot_w_m:.2f}m x {lot_l_m:.2f}m lot "
        f"(approx {lot_w_m*lot_l_m:.0f} m²), style: {style}. Include: {feature_list}. "
        "Top-down floor plan zoning with clear proportions, realistic circulation, driveway/parking if selected, shaded garden/pool if present. "
        "Minimalist clean linework, light shading, professional architectural sketch style."
    )

def estimate_room_areas(foot_area_m2, floors, features):
    net_per_floor = foot_area_m2 * 0.85
    total_net = net_per_floor * floors

    has_garden = "Halaman rumah" in features
    has_pool = "Kolam renang" in features

    shares = {
        "Ruang Tamu": 0.10,
        "Ruang Keluarga": 0.12,
        "Dapur": 0.08,
        "Kamar Tidur Utama": 0.12,
        "Kamar Tidur Anak": 0.10,
        "Kamar Tidur Anak 2": 0.08,
        "Kamar Mandi": 0.06,
        "Ruang Kerja": 0.06,
        "Ruang Santai": 0.06,
        "Gudang/Service": 0.05,
        "Sirkulasi (koridor/tangga)": 0.17
    }
    if has_pool or has_garden:
        shares["Ruang Keluarga"] += 0.02
        shares["Ruang Santai"] += 0.02
    total_share = sum(shares.values())
    for k in shares:
        shares[k] = shares[k] / total_share
    return {k: v * total_net for k, v in shares.items()}

# =========================
# Sidebar — Inputs
# =========================
with st.sidebar:
    st.header("Input Lahan & Opsi")
    unit = st.selectbox("Satuan ukuran", ["m", "cm"])
    lot_w = st.number_input(f"Lebar lahan ({unit})", min_value=1.0, step=0.5, value=10.0)
    lot_l = st.number_input(f"Panjang lahan ({unit})", min_value=1.0, step=0.5, value=20.0)
    floors = st.number_input("Jumlah lantai", min_value=1, max_value=4, step=1, value=2)

    st.markdown("---")
    st.subheader("Fitur Tambahan")
    fitur = []
    if st.checkbox("Halaman rumah", value=True):
        fitur.append("Halaman rumah")
    if st.checkbox("Kolam renang", value=False):
        fitur.append("Kolam renang")
    if st.checkbox("Toilet dalam", value=True):
        fitur.append("Toilet dalam")
    if st.checkbox("Toilet luar", value=False):
        fitur.append("Toilet luar")
    if st.checkbox("Ruang tamu", value=True):
        fitur.append("Ruang tamu")
    if st.checkbox("Tempat parkir", value=True):
        fitur.append("Tempat parkir")
    if st.checkbox("Pagar rumah", value=False):
        fitur.append("Pagar rumah")

    st.markdown("---")
    style = st.selectbox("Gaya rumah (untuk prompt AI)", ["minimalis tropis", "modern", "klasik", "industrial", "skandinavia"])

    st.markdown("---")
    st.subheader("AI Render (opsional)")
    provider = st.selectbox("Provider", ["Tidak digunakan", "OpenAI Images", "Replicate SDXL"])
    prompt_boost = st.slider("Detail prompt tambahan", 0, 100, 40)
    gen_btn = st.button("🎨 Generate AI Render")

# =========================
# Compute site & floors
# =========================
lot_w_m = to_meters(lot_w, unit)
lot_l_m = to_meters(lot_l, unit)
site_svg, foot, rect_px = make_site_svg(lot_w_m, lot_l_m, int(floors), fitur)

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("🗺️ Site Plan & Footprint")
    st.components.v1.html(site_svg, height=min(900, int(rect_px['canvasH'])), scrolling=True)
    st.download_button("⬇️ Unduh Site Plan (SVG)", data=site_svg.encode("utf-8"), file_name="site_plan.svg", mime="image/svg+xml")

    tabs = st.tabs([f"Lantai {i+1}" for i in range(int(floors))])
    for i, t in enumerate(tabs):
        with t:
            rooms = ROOM_PRESETS_GROUND if i == 0 else ROOM_PRESETS_UPPER
            floor_svg_inner = make_floor_svg(rect_px, rooms, f"Zoning Lantai {i+1}")
            floor_svg = svg_wrap(floor_svg_inner, rect_px["canvasW"], rect_px["canvasH"])
            st.components.v1.html(floor_svg, height=min(900, int(rect_px['canvasH'])), scrolling=True)
            st.download_button(f"⬇️ Unduh Denah Lantai {i+1} (SVG)", data=floor_svg.encode("utf-8"),
                               file_name=f"denah_lantai_{i+1}.svg", mime="image/svg+xml")

with col2:
    st.subheader("🧮 Ringkasan")
    lot_area = lot_w_m * lot_l_m
    st.markdown(f'''
- **Luas Lahan**: {lot_area:.1f} m²
- **Jumlah Lantai**: {int(floors)}
- **Fitur**: {", ".join(fitur) if fitur else "Tidak ada"}
- **Perkiraan Footprint Bangunan**: {foot["area_m2"]:.1f} m² per lantai
''')

    st.markdown("---")
    st.subheader("📐 Estimasi Luas Ruang")
    est = estimate_room_areas(foot["area_m2"], int(floors), fitur)
    st.table({k: f"{v:.1f} m²" for k, v in est.items()})

    st.markdown("---")
    st.subheader("🧠 Prompt Rekomendasi")
    base_prompt = build_prompt(lot_w_m, lot_l_m, int(floors), fitur, style)
    if prompt_boost:
        base_prompt += " " + ("Detailed façade articulation, daylight, cross-ventilation, human scale, landscaping, realistic materials. " * (prompt_boost // 25))
    st.code(base_prompt, language="text")

    if provider != "Tidak digunakan" and gen_btn:
        if provider == "OpenAI Images":
            api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
            if not api_key:
                st.warning("Set dulu `OPENAI_API_KEY` sebagai Environment Variable atau di Secrets Streamlit.")
            else:
                try:
                    resp = requests.post(
                        "https://api.openai.com/v1/images/generations",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={"model": "gpt-image-1", "prompt": base_prompt, "size": "1024x1024", "n": 1}
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    b64 = data["data"][0]["b64_json"]
                    import base64 as _b64
                    img_bytes = _b64.b64decode(b64)
                    st.image(img_bytes, caption="AI Render (OpenAI)", use_container_width=True)
                    st.download_button("⬇️ Unduh Render (PNG)", data=img_bytes, file_name="render_openai.png", mime="image/png")
                except Exception as e:
                    st.error(f"Gagal generate via OpenAI: {e}")
        elif provider == "Replicate SDXL":
            token = os.getenv("REPLICATE_API_TOKEN") or st.secrets.get("REPLICATE_API_TOKEN", None)
            if not token:
                st.warning("Set dulu `REPLICATE_API_TOKEN` di Environment Variable atau Secrets Streamlit.")
            else:
                try:
                    req = requests.post(
                        "https://api.replicate.com/v1/predictions",
                        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
                        json={
                            "version": "e4e204a4b2a1d1d0aa0b3f6bbd2f5a0f650f9b6b03c2e8f0f0d27f8e1b7f2b5f",
                            "input": {"prompt": base_prompt, "width": 1024, "height": 1024}
                        }
                    )
                    req.raise_for_status()
                    pred = req.json()
                    status = pred["status"]
                    get_url = pred["urls"]["get"]
                    import time
                    while status in ("starting", "processing"):
                        time.sleep(2)
                        q = requests.get(get_url, headers={"Authorization": f"Token {token}"})
                        q.raise_for_status()
                        pred = q.json()
                        status = pred["status"]
                    if status == "succeeded":
                        out = pred["output"]
                        if isinstance(out, list) and out:
                            img_url = out[0]
                            st.image(img_url, caption="AI Render (Replicate SDXL)", use_container_width=True)
                            st.markdown(f"[Unduh gambar]({img_url})")
                        else:
                            st.error("Model tidak mengembalikan URL gambar.")
                    else:
                        st.error(f"Prediksi gagal: {status}")
                except Exception as e:
                    st.error(f"Gagal generate via Replicate: {e}")

st.markdown("---")
st.caption("Sketsa bersifat konseptual untuk diskusi desain. Untuk gambar kerja, konsultasikan dengan arsitek berlisensi.")