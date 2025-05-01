
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

def monitoring_page():
    # ================ ISI HALAMAN ================

    ESP32_SNAPSHOT_URL = "http://192.168.25.43/capture"
    ESP32_STREAM_URL = "http://192.168.25.43:81/stream"
    FLASK_API_URL = "https://flask-koi-production.up.railway.app/detect"  # URL API Flask

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

    st.title("📷 Live Stream dari ESP32-CAM")
    st.markdown("Berikut ini adalah tampilan kamera secara langsung dari ESP32-CAM:")

    import time

    frame_placeholder = st.empty()

    if st.button("▶️ Mulai Stream"):
        st.info("Streaming dimulai. Tekan Stop Stream untuk berhenti.")
        stop = st.button("⏹️ Stop Stream")

        while not stop:
            try:
                # Ambil snapshot dari ESP32-CAM
                response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    frame_placeholder.image(img, caption="Live Stream dari ESP32-CAM", use_column_width=True)
                else:
                    frame_placeholder.error("Gagal mengambil snapshot dari kamera.")
            except Exception as e:
                frame_placeholder.error(f"Terjadi error: {e}")
            time.sleep(1)  # jeda 1 detik antar snapshot


    st.markdown("---")

    if st.button("📸 Ambil Gambar & Deteksi Ikan"):
        try:
            st.info("Mengambil gambar dari kamera...")
            response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)

            if response.status_code == 200:
                # Baca image langsung dari bytes
                image = Image.open(BytesIO(response.content)).convert("RGB")

                # Mengirim gambar ke Flask API
                files = {'image': response.content}
                response_api = requests.post(FLASK_API_URL, files=files)

                if response_api.status_code == 200:
                    result = response_api.json()

                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        # Menampilkan jumlah ikan
                        num_fish = result["num_fish"]
                        st.success(f"✅ Deteksi selesai! Jumlah ikan terdeteksi: {num_fish}")

                        # Mengubah image dari hex string kembali ke byte
                        result_img_bytes = bytes.fromhex(result["image"])

                        # Menampilkan gambar hasil deteksi
                        st.image(result_img_bytes, caption=f"Hasil Deteksi Ikan: {num_fish} ikan", use_column_width=True)

                else:
                    st.error("❌ Gagal menerima hasil dari API Flask.")

            else:
                st.error("❌ Gagal mengambil gambar dari ESP32-CAM.")

        except Exception as e:
            st.error(f"⚠️ Terjadi error saat mengambil gambar atau memproses deteksi: {e}")


