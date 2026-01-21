import streamlit as st
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.supabase_client import SupabaseManager

st.set_page_config(page_title="Login - Starwalk Dining", page_icon="🔑")

st.logo("assets/logo.png", size="large")

# Load CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("🔑 Login")

if "user" in st.session_state:
    # Use name if available
    name = st.session_state.user.get('name', st.session_state.user['email'])
    st.success(f"You are logged in as {name}")
    if st.button("Logout"):
        del st.session_state["user"]
        st.session_state.logged_in = False
        st.rerun()
else:
    db = SupabaseManager()

    with st.container():
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Sign In"):
            if email and password:
                with st.spinner("Authenticating..."):
                    res = db.sign_in(email, password)
                    if res["success"]:
                        user = res["data"].user
                        # Extract name and admin status from metadata
                        full_name = user.user_metadata.get('full_name', email)
                        is_admin = user.user_metadata.get('is_admin', False)

                        st.session_state.user = {"email": user.email, "id": user.id, "name": full_name}
                        st.session_state.logged_in = True
                        st.session_state.is_admin = is_admin

                        st.success(f"Welcome back, {full_name}!")
                        time.sleep(1)
                        if is_admin:
                             st.switch_page("pages/5_Admin.py")
                        else:
                             st.switch_page("pages/3_Chat.py")
                    else:
                        st.error(f"Login failed: {res['error']}")
            else:
                st.warning("Please fill in all fields")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.info("Don't have an account? Go to **Register** page.")
