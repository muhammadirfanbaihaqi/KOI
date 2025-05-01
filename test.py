import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time

ESP32_SNAPSHOT_URL = "https://a951-114-10-150-29.ngrok-free.app/capture"  # Ganti jika perlu

st.title("📷 Live Stream dari ESP32-CAM (Simulasi)")

frame_rate = st.slider("Frame per detik", 1, 10, 3)
placeholder = st.empty()

if st.button("▶️ Mulai Stream"):
    st.info("Streaming dimulai... Klik Stop untuk berhenti.")
    run = True
    stop = st.button("⏹ Stop")
    
    while run and not stop:
        try:
            response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)
            img = Image.open(BytesIO(response.content))
            placeholder.image(img, use_column_width=True)
            time.sleep(1.0 / frame_rate)
        except Exception as e:
            st.error(f"Gagal ambil gambar: {e}")
            break
