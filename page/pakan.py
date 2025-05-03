import streamlit as st
import requests

def pakan_page():
    st.title("📅 Atur Jadwal Pakan Ikan Hias")

    # ======== SET JUMLAH BUKAAN SERVO ========
    banyak_bukaan = st.number_input("Jumlah Bukaan Pakan", min_value=1, max_value=30, step=1, value=3)

    if st.button("Kirim"):
        try:
            response = requests.post(
                "https://flask-koi-production.up.railway.app/set-jumlah-bukaan",
                json={"jumlah_bukaan": banyak_bukaan}
            )
            if response.ok:
                st.success(f"✅ Berhasil dikirim: {banyak_bukaan}x buka-tutup")
            else:
                st.error("❌ Gagal mengirim data ke server.")
        except Exception as e:
            st.error(f"⚠️ Error saat mengirim: {e}")

        # ======== TAMPILKAN JUMLAH BUKAAN SAAT INI ========
    try:
        response = requests.get("https://flask-koi-production.up.railway.app/get-jumlah-bukaan")
        if response.ok:
            data = response.json()
            current_bukaan = data.get("jumlah_bukaan", "Tidak diketahui")
            st.info(f"🔁 Jumlah bukaan servo saat ini: {current_bukaan}x buka-tutup")
        else:
            st.warning("⚠️ Gagal mengambil jumlah bukaan saat ini.")
    except Exception as e:
        st.warning(f"⚠️ Tidak bisa mengambil jumlah bukaan: {e}")

    st.markdown("---")

    # ======== JADWAL PAKAN ========
    API_URL = "https://flask-koi-production.up.railway.app/jadwal_pakan"

    jam = st.number_input("Jam", min_value=0, max_value=23, step=1)
    menit = st.number_input("Menit", min_value=0, max_value=59, step=1)

    if st.button("➕ Tambah ke Jadwal"):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                jadwal = data.get("jadwal", [])
                if [jam, menit] not in jadwal:
                    jadwal.append([jam, menit])
                    res = requests.post(API_URL, json={"jadwal": jadwal})
                    if res.status_code == 200:
                        st.success("✅ Jadwal berhasil diperbarui!")
                    else:
                        st.error("❌ Gagal memperbarui jadwal.")
                else:
                    st.info("ℹ️ Jadwal ini sudah ada.")
            else:
                st.error(f"⚠️ Gagal mengambil jadwal: {response.status_code}")
        except Exception as e:
            st.error(f"⚠️ Gagal terhubung ke server: {e}")

    st.markdown("---")
    st.subheader("🕒 Jadwal Saat Ini")

    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            jadwal = data.get("jadwal", [])
            if jadwal:
                for idx, (j, m) in enumerate(sorted(jadwal)):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"- {j:02d}:{m:02d}")
                    with col2:
                        if st.button("❌ Hapus", key=f"hapus_{idx}"):
                            jadwal.remove([j, m])
                            res = requests.post(API_URL, json={"jadwal": jadwal})
                            if res.status_code == 200:
                                st.success(f"✅ Jadwal {j:02d}:{m:02d} berhasil dihapus!")
                                st.rerun()
                            else:
                                st.error("❌ Gagal menghapus jadwal.")
            else:
                st.info("Belum ada jadwal.")
        else:
            st.warning(f"⚠️ Gagal mengambil jadwal: {response.status_code}")
    except Exception as e:
        st.warning(f"⚠️ Gagal mengambil jadwal: {e}")
