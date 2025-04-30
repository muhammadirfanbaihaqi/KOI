import mysql.connector
from mysql.connector import Error
import streamlit as st
import streamlit_authenticator as stauth


# def create_connection():
#     """Membuat koneksi ke MySQL"""
#     try:
#         connection = mysql.connector.connect(
#             host = st.secrets["DB_HOST"],
#             user = st.secrets["DB_USER"],
#             password = st.secrets["DB_PASSWORD"],
#             database = st.secrets["DB_NAME"],
#             port = st.secrets["DB_PORT"]
#         )
#         return connection
#     except Error as e:
#         st.error(f"Error connecting to MySQL: {e}")
#         return None

def create_connection():
    """Membuat koneksi ke MySQL"""
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '',
            database = 'smart_fish',
            port = 3306
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None
    
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