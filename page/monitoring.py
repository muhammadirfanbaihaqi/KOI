# def monitoring_page():
#     import streamlit as st
#     import requests
#     from PIL import Image
#     import numpy as np
#     import cv2
#     from io import BytesIO
#     from ultralytics import YOLO
#     import time

#     ESP32_SNAPSHOT_URL = "https://722b-114-10-150-29.ngrok-free.app/capture"
#     ESP32_STREAM_URL = "https://722b-114-10-150-29.ngrok-free.app/stream"

#     st.title("📷 Live Stream dari ESP32-CAM")
#     st.markdown("Berikut ini adalah tampilan kamera secara langsung dari ESP32-CAM:")

#     placeholder = st.empty()

#     if st.button("▶️ Mulai Streaming"):
#         cap = cv2.VideoCapture(ESP32_STREAM_URL)
#         st.info("Streaming dimulai. Tekan Stop untuk menghentikan.")
#         stop = st.button("⏹ Stop")
#         while cap.isOpened() and not stop:
#             ret, frame = cap.read()
#             if not ret:
#                 st.warning("Tidak bisa membaca frame dari stream.")
#                 break
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             placeholder.image(frame, channels="RGB", caption="Live Stream", use_container_width=True)
#             time.sleep(0.1)  # Kurangi lag

#         cap.release()

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

    ESP32_SNAPSHOT_URL = "http://192.168.137.252/capture"

    st.title("📷 Pseudo Stream dari ESP32-CAM (Stable Mode)")
    st.markdown("Streaming stabil via snapshot setiap detik (tanpa MJPEG).")

    frame_rate = st.slider("Frame per detik", 1, 30, 1)
    placeholder = st.empty()

    if st.button("▶️ Mulai Pseudo Stream"):
        st.info("Streaming dimulai... Klik Stop untuk berhenti.")
        stop = st.button("⏹ Stop")
        run = True

        while run and not stop:
            try:
                response = requests.get(ESP32_SNAPSHOT_URL, timeout=5)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    placeholder.image(img, caption="Live View", use_container_width=True)
                    time.sleep(1.0 / frame_rate)
                else:
                    st.warning("Gagal mengambil snapshot.")
                    break
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                break

    st.markdown("---")

    # Tombol untuk deteksi dengan YOLOv8
    if st.button("📸 Ambil Gambar & Deteksi Ikan"):
        try:
            st.info("Mengambil gambar dari kamera...")
            response = requests.get(ESP32_SNAPSHOT_URL, timeout=10)

            if response.status_code == 200:
                # Baca image langsung dari bytes
                image = Image.open(BytesIO(response.content)).convert("RGB")

                # Konversi ke format OpenCV (BGR)
                img_array = np.array(image)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

                # Load YOLOv8 model
                model = YOLO("models/best (2).pt")  # Ganti dengan path model kamu

                # Prediksi
                results = model(img_bgr)
                result_img = results[0].plot()
                num_fish = len(results[0].boxes)

                st.success(f"✅ Deteksi selesai! Jumlah ikan terdeteksi: {num_fish}")
                st.image(result_img, caption=f"Hasil Deteksi Ikan: {num_fish} ikan", use_container_width=True)

            else:
                st.error("❌ Gagal mengambil gambar dari ESP32-CAM.")

        except Exception as e:
            st.error(f"⚠️ Terjadi error saat mengambil gambar atau memproses deteksi: {e}")
