from groq import Groq
import streamlit as st

# Ambil API key dari secrets.toml
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Inisialisasi client Groq
client = Groq(api_key=GROQ_API_KEY)

def chatAI(history):
    try:
        chat_completion = client.chat.completions.create(
            messages=history,
            model="llama-3.3-70b-versatile",
            stream=False
        )
        ai_answer = chat_completion.choices[0].message.content.strip()
        return ai_answer
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
