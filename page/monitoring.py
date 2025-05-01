# def monitoring_page():
#     import streamlit as st
#     import requests
#     from PIL import Image
#     import numpy as np
#     import cv2
#     from io import BytesIO
#     from ultralytics import YOLO

#     ESP32_SNAPSHOT_URL = "https://bdd6-114-10-150-29.ngrok-free.ap/capture"
#     ESP32_STREAM_URL = "https://bdd6-114-10-150-29.ngrok-free.app/stream"

#     st.markdown(
#         """
#         <style>
#             .main {
#                 display: flex;
#                 flex-direction: column;
#                 align-items: center;
#                 justify-content: center;
#             }
#             img {
#                 border-radius: 12px;
#                 box-shadow: 0 4px 8px rgba(0,0,0,0.3);
#             }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

#     st.title("📷 Live Stream dari ESP32-CAM")
#     st.markdown("Berikut ini adalah tampilan kamera secara langsung dari ESP32-CAM:")

#     st.markdown(
#         f"""
#         <div style="text-align: center;">
#             <img src="{ESP32_STREAM_URL}" width="640" height="480" />
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     st.markdown("---")

#     if st.button("📸 Ambil Gambar & Deteksi Ikan"):
#         try:
#             st.info("Mengambil gambar dari kamera...")
#             response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)

#             if response.status_code == 200:
#                 # Baca image langsung dari bytes
#                 image = Image.open(BytesIO(response.content)).convert("RGB")

#                 # Konversi ke format OpenCV (BGR)
#                 img_array = np.array(image)
#                 img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

#                 # Load YOLOv8 model
#                 model = YOLO("models/best (2).pt")  # Ganti sesuai path kamu

#                 # Prediksi
#                 results = model(img_bgr)
#                 result_img = results[0].plot()
#                 num_fish = len(results[0].boxes)

#                 st.success(f"✅ Deteksi selesai! Jumlah ikan terdeteksi: {num_fish}")
#                 st.image(result_img, caption=f"Hasil Deteksi Ikan: {num_fish} ikan", use_container_width=True)

#             else:
#                 st.error("❌ Gagal mengambil gambar dari ESP32-CAM.")

#         except Exception as e:
#             st.error(f"⚠️ Terjadi error saat mengambil gambar atau memproses deteksi: {e}")
def monitoring_page():
    import streamlit as st
    import requests
    from PIL import Image
    import numpy as np
    import cv2
    from io import BytesIO
    from ultralytics import YOLO
    import time

    # Ganti sesuai alamat ngrok ESP32 kamu
    ESP32_SNAPSHOT_URL = "https://722b-114-10-150-29.ngrok-free.app/capture"
    ESP32_STREAM_URL = "https://722b-114-10-150-29.ngrok-free.app/stream"

    st.title("📷 Live Stream dari ESP32-CAM (Real-Time Frame)")

    st.markdown("**Streaming langsung dari ESP32-CAM:**")

    # Tombol untuk mulai stream
    start = st.button("▶️ Mulai Stream")

    if start:
        cap = cv2.VideoCapture(ESP32_STREAM_URL)
        frame_placeholder = st.empty()
        st.info("Tekan `Stop` (di sidebar/kembali) untuk menghentikan stream.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.warning("⚠️ Gagal membaca frame dari stream.")
                break

            # Tampilkan frame ke Streamlit
            frame_placeholder.image(frame, channels="BGR", use_container_width=True)

            time.sleep(0.2)  # Sekitar 20 fps

        cap.release()

    st.markdown("---")
    st.markdown("**Ambil Gambar dan Deteksi Ikan**")

    if st.button("📸 Ambil Gambar & Deteksi Ikan"):
        try:
            st.info("Mengambil gambar dari kamera...")
            response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)

            if response.status_code == 200:
                image = Image.open(BytesIO(response.content)).convert("RGB")
                img_array = np.array(image)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

                model = YOLO("models/best (2).pt")  # Ganti path jika perlu
                results = model(img_bgr)
                result_img = results[0].plot()
                num_fish = len(results[0].boxes)

                st.success(f"✅ Deteksi selesai! Jumlah ikan terdeteksi: {num_fish}")
                st.image(result_img, caption=f"Hasil Deteksi: {num_fish} ikan", use_container_width=True)

            else:
                st.error("❌ Gagal mengambil gambar dari ESP32-CAM.")
        except Exception as e:
            st.error(f"⚠️ Terjadi error saat ambil gambar atau deteksi: {e}")
