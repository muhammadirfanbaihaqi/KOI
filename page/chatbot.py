import streamlit as st
from utils.chatbot import chatAI


def chatbot_page():
    # ================ ISI HALAMAN ================

    st.title("💬 Chatbot Pakar Ikan Koi")

    # Inisialisasi history jika belum ada
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": (
                    "Kamu adalah seorang pakar ikan hias koi dengan pengalaman bertahun-tahun. "
                    "Jawablah semua pertanyaan dengan pengetahuan mendalam tentang koi."
                )
            }
        ]

    # Tampilkan riwayat chat
    for msg in st.session_state.chat_history[1:]:
        if msg["role"] == "user":
            st.markdown(f"🧑 **Kamu:** {msg['content']}")
        else:
            st.markdown(f"🤖 **KoiBot:** {msg['content']}")

    # Input pertanyaan
    user_input = st.text_input("Ketik pertanyaanmu di sini...", key="input_chat")
    if st.button("Kirim"):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            ai_reply = chatAI(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()