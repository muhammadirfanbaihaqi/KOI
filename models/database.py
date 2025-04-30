import mysql.connector
from mysql.connector import Error
import streamlit as st
import streamlit_authenticator as stauth
import os

# from dotenv import load_dotenv
# load_dotenv()


import streamlit as st
import mysql.connector
from mysql.connector import Error
import mysql.connector
from urllib.parse import urlparse

# Connection URL yang diberikan oleh Railway
connection_url = "mysql://root:JWWprfxEjxyJCLjIyxKnyoYfdCIjOLFT@caboose.proxy.rlwy.net:30550/railway"

# Mengurai URL untuk mendapatkan detail koneksi
url = urlparse(connection_url)

# Mengonfigurasi koneksi
db_config = {
    "host": url.hostname,
    "user": url.username,
    "password": url.password,
    "database": url.path[1:],  # Mengambil nama database (tanpa '/')
    "port": url.port
}

# def create_connection():
#     try:
#         connection = mysql.connector.connect(
#             host = st.secrets["DB_HOST"],
#             port = int(st.secrets["DB_PORT"]),
#             user = st.secrets["DB_USER"],
#             password = st.secrets["DB_PASSWORD"],
#             database = st.secrets["DB_NAME"]
#         )
#         if connection.is_connected():
#             print("✅ Berhasil konek ke MySQL via Railway")
#         return connection
#     except Error as e:
#         st.error(f"❌ Error koneksi ke MySQL: {e}")
#         return None


# def create_connection():
#     """Membuat koneksi ke MySQL"""
#     try:
#         connection = mysql.connector.connect(
#             host=os.getenv("DB_HOST"),
#             port=int(os.getenv("DB_PORT")),
#             user=os.getenv("DB_USER"),
#             password=os.getenv("DB_PASSWORD"),
#             database=os.getenv("DB_NAME")
#         )
#         return connection
#     except Error as e:
#         st.error(f"Error connecting to MySQL: {e}")
#         return None
    
def insert_user(username, name, password):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO users (username, name, password)
            VALUES (%s, %s, %s)
            """, 
            (username, name, password)
        )
        conn.commit()    
    except Error as e:
        print(f"Terjadi kesalahan : {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def insert_jadwal_pakan(jam, menit):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO jadwal_pakan (jam, menit)
            VALUES (%s, %s)
            """, 
            (jam, menit)
        )
        conn.commit()    
    except Error as e:
        print(f"Terjadi kesalahan : {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
def ambil_semua_users():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT username, name, password
            FROM users
            """
        )
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            user = {
                "key": row[0],       
                "name": row[1],      
                "password": row[2]   
            }
            users.append(user)
        
        return users
    except Error as e:
        print(f"Terjadi kesalahan : {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
        
        
        
if __name__ == "__main__":
    # names = ['Hafizh', 'Aji']
    # usernames = ['Hapis', 'Ajik']
    # passwords = ['admin123', 'admin456']
    # hashed_password = stauth.Hasher(passwords).generate()
    
    # for (username, name, hash_password) in zip(usernames, names, hashed_password):
    #     insert_user(username, name, hash_password)
    
    users = ambil_semua_users()
    print(users)

    usernames = [user['key'] for user in users]
    names = [user['name'] for user in users]
    passwords = [user['password'] for user in users]