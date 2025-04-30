import sys
import types
import streamlit as st
import streamlit_authenticator as stauth
from models.database import ambil_semua_users

from page.dashboard import pemantauan_page
from page.pakan import pakan_page
from page.monitoring import monitoring_page
from page.chatbot import chatbot_page


# Hindari streamlit mencoba "watch" torch.classes
sys.modules['torch.classes'] = types.ModuleType('torch.classes')
sys.modules['torch.classes'].__path__ = []

# Set page config
st.set_page_config(page_title="Smart Fish Dashboard", layout="wide")

# Ambil semua users
users = ambil_semua_users()
usernames = [user['key'] for user in users]
names = [user['name'] for user in users]
passwords = [user['password'] for user in users]

authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords,
    'smart_fish_dashboard',
    'abcdef',
    cookie_expiry_days=30
)

# Tampilan Login
names, authentication_status, usernames = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username atau password salah")
    
if authentication_status is None:
    st.warning("Masukkan username dan password")
    
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    
    # ================ CUSTOM CSS ================

    st.markdown("""
        <style>
            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background-color: #2c3e50;
                color: white;
            }
            
            .sidebar .sidebar-content, .css-1v3fvcr {
                color: white !important;
                font-size: 22px;
                font-weight: 700;
            }
            
            .css-1lcbmhc {
                background-color: #2c3e50;
                color: white;
                min-height: 100vh;
                padding: 2rem 1rem;
                border-radius: 0 1rem 1rem 0;
                box-shadow: 4px 0 8px rgba(0,0,0,0.1);
            }
            .css-1lcbmhc h2, .css-1lcbmhc label, .css-1lcbmhc div {
                color: white;
            }
            div[role="radiogroup"] > label {
                width: 100%;
                background: #34495e;
                padding: 0.5rem 1rem;
                margin-bottom: 0.5rem;
                border-radius: 0.5rem;
                transition: background 0.3s;
                cursor: pointer;
            }
            div[role="radiogroup"] > label:hover {
                background: #3d566e;
            }
            div[role="radiogroup"] > label[data-selected="true"] {
                background: #1abc9c;
                color: white;
            }

            /* Metric Card styling */
            .metric-card {
                background-color: #34495e;
                padding: 1rem;
                border-radius: 1rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
                height: 150px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .metric-card h2 {
                font-size: 1.5rem;
                color: #333;
                margin-bottom: 0.5rem;
            }
            .metric-card p {
                font-size: 1.4rem;
                font-weight: bold;
                margin: 0;
                color: #007bff;
            }
            .metric-content {
                display: flex;
                align-items: center;
                width: 100%;
            }
            .metric-icon {
                width: 50px;
                height: 50px;
                margin-right: 1rem;
            }
            .metric-text {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .metric-title {
                font-size: 1rem;
                font-weight: semi-bold;
                color: white;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #1abc9c;
                text-align: right;
            }
            .left-content {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .left-content img {
                width: 50px;
                height: 50px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # ================ SIDEBAR ================

    # Bikin layout 2 kolom (sidebar dan main content)
    st.sidebar.title("🐟 Smart Fish Dashboard The King's Mercenary")
    menu = st.sidebar.radio("📂 Pilih Halaman:", [
        "Pemantauan Suhu, Pakan & Aerator",
        "Pemberi Pakan Otomatis",
        "Monitoring Kamera & YOLO",
        "Chatbot"
    ])
    
    if menu == "Pemantauan Suhu, Pakan & Aerator":
        pemantauan_page()
    elif menu == "Pemberi Pakan Otomatis":
        pakan_page()
    elif menu == "Monitoring Kamera & YOLO":
        monitoring_page()
    else:
        chatbot_page()