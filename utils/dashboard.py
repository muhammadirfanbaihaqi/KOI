import streamlit as st
import plotly.express as px


def buat_metric_card(icon_url, title, value, color=None):
    """Membuat komponen metric card yang reusable"""
    style = f"color:{color};" if color else ""
    return f"""
    <div class="metric-card">
        <div class="left-content">
            <img src="{icon_url}" width="50" height="50">
            <div class="metric-title">{title}</div>
        </div>
        <div class="metric-value">{value}</div>
    </div>
    """

def buat_grafik(df, kolom, judul, satuan):
    """Fungsi untuk membuat grafik yang reusable"""
    st.markdown('---')
    st.subheader(f"📈 Grafik {kolom}")
    fig = px.line(df, x=df.index, y=kolom, title=judul)
    fig.update_layout(
        xaxis_title='Waktu',
        yaxis_title=f'{kolom.split("(")[0].strip()} ({satuan})',
        hovermode="x unified",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
def tampil_ringkasan_statistik(df, kolom, nama_param, satuan):
    """Menampilkan statistik ringkasan untuk parameter tertentu"""
    st.markdown(f"#### {nama_param}")
    cols = st.columns(4)
    cols[0].metric("Maksimum", f"{df[kolom].max():.1f}{satuan}")
    cols[1].metric("Minimum", f"{df[kolom].min():.1f}{satuan}")
    cols[2].metric("Rata-rata", f"{df[kolom].mean():.1f}{satuan}")
    cols[3].metric("Jumlah Data", len(df))
    st.markdown('---')