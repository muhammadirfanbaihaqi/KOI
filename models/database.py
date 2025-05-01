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
from urllib.parse import urlparse
import bcrypt


# Connection URL yang diberikan oleh Railway
connection_url = "mysql://root:JWWprfxEjxyJCLjIyxKnyoYfdCIjOLFT@caboose.proxy.rlwy.net:30550/railway"

# Mengurai URL untuk mendapatkan detail koneksi
url = urlparse(connection_url)

# Fungsi untuk membuat koneksi
def create_connection():
    try:
        # Mengonfigurasi koneksi menggunakan parameter yang benar
        connection = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],  # Mengambil nama database (tanpa '/')
            port=url.port
        )
        if connection.is_connected():
            st.success("✅ Berhasil konek ke MySQL via Railway")
        return connection
    except Error as e:
        st.error(f"❌ Error koneksi ke MySQL: {e}")
        return None



def insert_user(username, name, plain_password):
    print(plain_password)
    # Membuat objek Hasher dengan password dalam list
# Menghasilkan salt secara acak
    salt = bcrypt.gensalt()

# Hash password
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    
    try:
        # Membuat koneksi ke database
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO users (username, name, password)
            VALUES (%s, %s, %s)
            """, 
            (username, name, hashed_password)
        )
        conn.commit()  # Menyimpan perubahan
    except Error as e:
        print(f"Terjadi kesalahan : {e}")  # Menampilkan error jika ada
    finally:
        if conn.is_connected():
            cursor.close()  # Menutup cursor
            conn.close()  # Menutup koneksi



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
        
        
# SEED USER
if __name__ == "__main__":
    names = 'ipan'
    usernames = 'ipan'
    passwords = 'ipan123'
    

    # Insert user dengan hashed password
    insert_user(usernames, names, passwords)


    
    users = ambil_semua_users()
    print("🔍 Mengambil data user dari database MySQL...")

    users = ambil_semua_users()

    if users:
        print("✅ Data user berhasil diambil:")
        for user in users:
            print(f" - Username: {user['key']}, Name: {user['name']}, Password (hash): {user['password']}")
    else:
        print("⚠️ Tidak ada data user yang ditemukan atau terjadi error.")



