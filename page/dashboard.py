import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from datetime import datetime
from utils.dashboard import buat_metric_card, tampil_ringkasan_statistik, buat_grafik
from utils.chatbot import chatAI


def pemantauan_page():
    # ================ ISI HALAMAN ================

    # Data simulasi (di real project, data ini dari API/database)
    waktu = pd.date_range(end=pd.Timestamp.now(), periods=4*24*6, freq='10min')
    data = {
        'Waktu': waktu,
        'Suhu': np.random.uniform(20, 30, len(waktu)),
        'Pakan': np.random.uniform(0, 100, len(waktu)),
        'Pompa': np.random.choice([0, 1], len(waktu)),
        'pH': np.random.uniform(0, 14, len(waktu))
    }
    df = pd.DataFrame(data).set_index('Waktu')

    # Judul halaman
    st.title("🌡️ Pemantauan Suhu Air, Pakan & Kontrol Aerator")

    # # Data contoh (biasanya dari API)
    # suhu = 10
    # pakan = 50
    # pompa = False
    # pH = 6
    # timestamp = "N/A"

    flask_url = "https://flask-koi-production.up.railway.app/sensor"  # Ganti dengan URL Flask API kamu

    try:
        response = requests.get(flask_url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            st.success("✅ Data berhasil diambil dari server!")

            suhu = data.get("suhu", "N/A")
            pakan = data.get("pakan(%)", "N/A")
            pompa = data.get("pompa", False)
            pH = data.get("pH", "N/A")
            timestamp = data.get("timestamp", "N/A")
        else:
            st.error("❌ Gagal mengambil data dari server Flask.")
            
        # Tampilkan metric cards
        cols = st.columns(4)
        cols2 = st.columns(1)

        with cols[0]: st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/512/1684/1684375.png",
            "Suhu Air", f"{suhu} °C"), unsafe_allow_html=True)

        with cols[1]: st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/3737/3737660.png",
            "Pakan", f"{pakan} %"), unsafe_allow_html=True)

        with cols[2]: st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/15447/15447546.png",
            "Pompa", "Aktif" if pompa else "Mati",
            "#2ecc71" if pompa else "#e74c3c"), unsafe_allow_html=True)

        with cols[3]: st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/15359/15359371.png",
            "pH", f"{pH}/14"), unsafe_allow_html=True)

        with cols2[0]: st.markdown(buat_metric_card(
            "https://cdn-icons-png.flaticon.com/128/1601/1601884.png",
            "Last Update", timestamp), unsafe_allow_html=True)

        # Tombol Epik: minta saran dari AI
        if st.button("✨ Dapatkan Saran dari AI"):
            with st.spinner("Sedang memproses saran dari AI..."):
                history = [
                    {"role": "system", "content": "Kamu adalah asisten pintar untuk peternakan ikan."},
                    {"role": "user", "content": f"Suhu air saat ini adalah {suhu}°C, pH saat ini adalah {pH}, dan status aerator backup adalah {'aktif' if pompa else 'mati'}. Berikan saran agar ikan koi dapat sehat berdasarkan data tersebut."}
                ]
                saran = chatAI(history)
                st.success("🤖 Saran dari AI:")
                st.markdown(f"> {saran}")

        # Filter tanggal
        st.markdown("---")
        st.subheader("⏰ Pilih Rentang Waktu Monitoring")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1: 
            start_date = st.date_input("Tanggal Mulai", value=datetime.now())
        with col2: 
            end_date = st.date_input("Tanggal Selesai", value=datetime.now())
        with col3: 
            granularity = st.selectbox("Granularitas Data:", 
                                        ["Asli (10 menit)", "Per Jam", "Per 6 Jam", "Per 12 Jam", "Per Hari"])

        # Filter data berdasarkan tanggal
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        filtered_df = df[(df.index >= start_dt) & (df.index <= end_dt)]

        # Tampilkan ringkasan statistik dan grafik
        st.markdown("---")
        st.subheader("📊 Statistik Ringkasan")
        if not filtered_df.empty:
            if granularity != "Asli (10 menit)":
                freq_map = {"Per Jam": '1H', "Per 6 Jam": '6H', 
                            "Per 12 Jam": '12H', "Per Hari": 'D'}
                resampled_df = filtered_df.resample(freq_map[granularity]).mean()
            else:
                resampled_df = filtered_df
            
            # Tampilan ringkasan statistik
            tampil_ringkasan_statistik(filtered_df, 'Suhu', '🌡️ Suhu', '°C')
            tampil_ringkasan_statistik(filtered_df, 'Pakan', '🐟 Pakan', '%')
            tampil_ringkasan_statistik(filtered_df, 'pH', '⚗️ pH', '')
            
            # Tampilan statistik khusus Pompa
            st.markdown("#### 💧 Pompa")
            cols = st.columns(2)
            active_percent = filtered_df['Pompa'].mean() * 100
            cols[0].metric("Persentase Aktif", f"{active_percent:.1f}%")
            cols[1].metric("Persentase Mati", f"{100 - active_percent:.1f}%")
                
            # Tampilan grafik
            buat_grafik(resampled_df, 'Suhu', f'Grafik Suhu Air {start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}', '°C')
            buat_grafik(resampled_df, 'Pakan', f'Grafik Pakan {start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}', '%')
            buat_grafik(resampled_df, 'pH', f'Grafik pH {start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}', '')
            
            # Grafik pompa khusus karena berbeda
            st.markdown('---')
            st.subheader(f"📈 Grafik Pompa")
            fig_pompa = px.line(filtered_df, 
                                x=filtered_df.index, 
                                y='Pompa', 
                                title=f'Grafik Pompa {start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}', 
                                markers=True)
            fig_pompa.update_layout(height=500)
            st.plotly_chart(fig_pompa, use_container_width=True)
        else:
            st.warning("⚠️ Tidak ada data dalam rentang waktu yang dipilih.")
    except Exception as e:
        st.error(f"⚠️ Error saat koneksi ke server: {e}")

