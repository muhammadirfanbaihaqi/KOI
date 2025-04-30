import streamlit_authenticator as stauth
password = 'ipan123'
hasher = stauth.Hasher([password])
hashed_password = hasher.generate()[0]
print(f"Hashed Password: {hashed_password}")
