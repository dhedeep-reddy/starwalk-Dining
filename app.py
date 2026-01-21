import streamlit as st
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Starwalk Dining", page_icon="🌟", layout="wide")

# Load CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.logo("assets/logo.png", size="large")

st.title("🌟 Starwalk Dining")
st.subheader("Experience the Art of Fine Dining")

with st.container():
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.write("Welcome to Starwalk Dining, where culinary excellence meets elegant atmosphere.")
    st.write("Please **Login** or **Register** to book a table or view your profile.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log In", use_container_width=True):
            st.switch_page("pages/1_Login.py")
    with col2:
        if st.button("Register", use_container_width=True):
            st.switch_page("pages/2_Register.py")
    st.markdown('</div>', unsafe_allow_html=True)

# Admin Link (hidden/subtle)
if st.sidebar.checkbox("Admin Access"):
    st.sidebar.info("Please login as Admin to access dashboard.")