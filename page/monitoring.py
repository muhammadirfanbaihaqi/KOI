import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time

def monitoring_page():
    # ================ KONFIGURASI URL ================
    ESP32_SNAPSHOT_URL = "http://192.168.25.43/capture"
    FLASK_API_URL = "https://flask-koi-production.up.railway.app/detect"

    # ================ STYLE CSS ================
    st.markdown(
        """
        <style>
            .main {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            img {
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ================ JUDUL & KONTEN ================
    st.title("📷 Monitoring Kamera ESP32-CAM")
    st.markdown("Klik tombol di bawah ini untuk menampilkan live snapshot dari ESP32-CAM:")

    # Tempat untuk menampilkan frame dan hasil deteksi
    stream_placeholder = st.empty()
    result_placeholder = st.empty()

    # ================ LOGIKA STREAM ================
    if st.button("▶️ Mulai Stream"):
        st.info("Streaming dimulai. Klik 'Stop Stream' di sidebar untuk menghentikan.")
        stop_stream = st.sidebar.button("⏹️ Stop Stream")

        while not stop_stream:
            try:
                response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    stream_placeholder.image(img, caption="Live Stream ESP32-CAM", use_column_width=True)
                else:
                    stream_placeholder.error("❌ Gagal mengambil snapshot dari kamera.")
            except Exception as e:
                stream_placeholder.error(f"⚠️ Terjadi error: {e}")
            time.sleep(1)

    st.markdown("---")
    st.subheader("📸 Deteksi Ikan Koi")

    # ================ DETEKSI GAMBAR ================
    if st.button("📸 Ambil Gambar & Deteksi Ikan"):
        try:
            st.info("Mengambil gambar dari kamera...")
            response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)

            if response.status_code == 200:
                # Ambil gambar dari kamera
                image = Image.open(BytesIO(response.content)).convert("RGB")
                stream_placeholder.image(image, caption="Gambar Snapshot", use_column_width=True)

                # Kirim ke Flask API
                files = {'image': response.content}
                response_api = requests.post(FLASK_API_URL, files=files)

                if response_api.status_code == 200:
                    result = response_api.json()

                    if "error" in result:
                        result_placeholder.error(f"❌ Error dari API: {result['error']}")
                    else:
                        num_fish = result["num_fish"]
                        result_img_bytes = bytes.fromhex(result["image"])

                        result_placeholder.success(f"✅ Deteksi selesai! Jumlah ikan terdeteksi: {num_fish}")
                        result_placeholder.image(result_img_bytes, caption=f"Hasil Deteksi: {num_fish} ikan koi", use_column_width=True)

                else:
                    result_placeholder.error("❌ Gagal menerima hasil dari API Flask.")

            else:
                result_placeholder.error("❌ Gagal mengambil gambar dari ESP32-CAM.")

        except Exception as e:
            result_placeholder.error(f"⚠️ Terjadi error saat proses deteksi: {e}")
