import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from utils.dashboard import buat_metric_card, tampil_ringkasan_statistik, buat_grafik
from utils.chatbot import chatAI

def pemantauan_page():
    st.title("🌡️ Pemantauan Suhu Air, Pakan & Kontrol Aerator")

    flask_url = "https://flask-koi-production.up.railway.app"

    # ====== Ambil Data Realtime dari Flask ======
    try:
        response = requests.get(f"{flask_url}/sensor")
        if response.status_code == 200:
            data = response.json()
            st.success("✅ Data berhasil diambil dari server!")

            suhu = data.get("suhu", "N/A")
            pakan = data.get("pakan(%)", "N/A")
            pompa = data.get("pompa", False)
            ph = data.get("ph", "N/A")
            timestamp = data.get("timestamp", "N/A")
            # Konversi timestamp ke datetime dan ke zona waktu Asia/Jakarta (WIB)
            if timestamp != "N/A":
                timestamp = pd.to_datetime(timestamp, utc=True).dt.tz_convert('Asia/Jakarta').strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp = "N/A"
        else:
            st.error("❌ Gagal mengambil data dari server Flask.")
            return
    except Exception as e:
        st.error(f"⚠️ Error saat koneksi ke server: {e}")
        return

    # ====== Tampilkan Kartu Metrik ======
    cols = st.columns(4)
    cols2 = st.columns(1)

    with cols[0]:
        st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/512/1684/1684375.png",
            "Suhu Air", f"{suhu} °C"), unsafe_allow_html=True)

    with cols[1]:
        st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/3737/3737660.png",
            "Pakan", f"{pakan} %"), unsafe_allow_html=True)

    with cols[2]:
        st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/15447/15447546.png",
            "Pompa", "Aktif" if pompa else "Mati",
            "#2ecc71" if pompa else "#e74c3c"), unsafe_allow_html=True)

    with cols[3]:
        st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/15359/15359371.png",
            "ph", f"{ph}/14"), unsafe_allow_html=True)

    with cols2[0]:
        st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/1601/1601884.png",
            "Last Update", timestamp), unsafe_allow_html=True)

    # ====== Saran dari AI ======
    if st.button("✨ Dapatkan Saran dari AI"):
        with st.spinner("Sedang memproses saran dari AI..."):
            history = [
                {"role": "system", "content": "Kamu adalah asisten pintar untuk peternakan ikan."},
                {"role": "user", "content": f"Suhu air saat ini adalah {suhu}°C, ph saat ini adalah {ph}, dan status aerator backup adalah {'aktif' if pompa else 'mati'}. Berikan saran agar ikan koi dapat sehat berdasarkan data tersebut."}
            ]
            saran = chatAI(history)
            st.success("🤖 Saran dari AI:")
            st.markdown(f"> {saran}")

    # ====== Pilih Rentang Waktu ======
    st.markdown("---")
    st.subheader("⏰ Pilih Rentang Waktu Monitoring")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        start_date = st.date_input("Tanggal Mulai", value=datetime.now() - timedelta(days=1))
    with col2:
        end_date = st.date_input("Tanggal Selesai", value=datetime.now())
    with col3:
        granularity = st.selectbox("Granularitas Data:",
                                   ["Asli (10 menit)", "Per Jam", "Per 6 Jam", "Per 12 Jam", "Per Hari"])

    # ====== Ambil Data Historis dari API Flask ======
    try:
        history_response = requests.get(f"{flask_url}/sensor/history", params={
            "start": start_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d')
        })

        if history_response.status_code == 200:
            records = history_response.json()
            if not records:
                st.warning("⚠️ Tidak ada data dalam rentang waktu yang dipilih.")
                return

            # ⛑️ Cek & ubah jika timestamp masih dalam bentuk dict
            for rec in records:
                if isinstance(rec.get("timestamp"), dict) and "$date" in rec["timestamp"]:
                    rec["timestamp"] = rec["timestamp"]["$date"]
            df = pd.DataFrame(records)
            # df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)  # asumsikan dari Mongo adalah UTC
            df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Jakarta')  # ubah ke WIB
            df = df.rename(columns={"timestamp": "Waktu", "suhu": "Suhu", "pakan(%)": "Pakan", "ph": "ph", "pompa": "Pompa"})
            df = df.set_index("Waktu")
        else:
            st.error("❌ Gagal mengambil data historis dari Flask.")
            return
    except Exception as e:
        st.error(f"⚠️ Error saat mengambil data historis: {e}")
        return

    # ====== Resampling Berdasarkan Granularitas ======
    if granularity != "Asli (10 menit)":
        freq_map = {"Per Jam": '1H', "Per 6 Jam": '6H',
                    "Per 12 Jam": '12H', "Per Hari": '1D'}
        df = df.resample(freq_map[granularity]).mean()

    # ====== Statistik Ringkasan & Grafik ======
    st.markdown("---")
    st.subheader("📊 Statistik Ringkasan")

    tampil_ringkasan_statistik(df, 'Suhu', '🌡️ Suhu', '°C')
    tampil_ringkasan_statistik(df, 'Pakan', '🐟 Pakan', '%')
    tampil_ringkasan_statistik(df, 'ph', '⚗️ ph', '')

    st.markdown("#### 💧 Pompa")
    cols = st.columns(2)
    active_percent = df['Pompa'].mean() * 100
    cols[0].metric("Persentase Aktif", f"{active_percent:.1f}%")
    cols[1].metric("Persentase Mati", f"{100 - active_percent:.1f}%")

    # Grafik
    buat_grafik(df, 'Suhu', f'Grafik Suhu Air {start_date.strftime("%d %b")} - {end_date.strftime("%d %b")}', '°C')
    buat_grafik(df, 'Pakan', f'Grafik Pakan {start_date.strftime("%d %b")} - {end_date.strftime("%d %b")}', '%')
    buat_grafik(df, 'ph', f'Grafik ph {start_date.strftime("%d %b")} - {end_date.strftime("%d %b")}', '')

    st.markdown('---')
    st.subheader("📈 Grafik Pompa")
    fig_pompa = px.line(df, x=df.index, y='Pompa',
                        title=f'Grafik Pompa {start_date.strftime("%d %b")} - {end_date.strftime("%d %b")}',
                        markers=True)
    fig_pompa.update_layout(height=500)
    st.plotly_chart(fig_pompa, use_container_width=True)
