import streamlit as st
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AI_UseCase.db.supabase_client import SupabaseManager

st.set_page_config(page_title="Register - Starwalk Dining", page_icon="📝")

st.logo("assets/logo.png", size="large")

# Load CSS
try:
    with open('assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("📝 Register")

db = SupabaseManager()

with st.container():
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")
    
    # helper to check admin code
    is_admin_reg = st.checkbox("Register as Administrator")
    admin_secret = ""
    if is_admin_reg:
        admin_secret = st.text_input("Admin Secret Key", type="password")

    if st.button("Sign Up"):
        if email and password and name:
            if password != confirm_pass:
                st.error("Passwords do not match!")
            elif is_admin_reg and admin_secret != "starwalk2026": # Simple security
                 st.error("Invalid Admin Secret Key")
            else:
                with st.spinner("Creating account..."):
                    try:
                        # Direct client connection for robust environment handling
                        from supabase import create_client
                        import os
                        
                        d_url = os.environ.get("SUPABASE_URL")
                        d_key = os.environ.get("SUPABASE_KEY")
                        
                        if not d_url or not d_key:
                             # Fallback to config if env not direct (shouldn't happen with .env loaded)
                             from AI_UseCase.config.config import Config
                             d_url = Config.SUPABASE_URL
                             d_key = Config.SUPABASE_KEY

                        # Init direct client
                        direct_client = create_client(d_url, d_key)
                        
                        # Register user
                        res = direct_client.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "data": { 
                                    "full_name": name,
                                    "is_admin": is_admin_reg
                                } 
                            }
                        })
                        
                        if res.user:
                             role = "Admin" if is_admin_reg else "Guest"
                             st.success(f"{role} Account created! You can now Login.")
                             time.sleep(2)
                             st.switch_page("pages/1_Login.py")
                        else:
                             st.error("Registration failed. Please try again.")
                             
                    except Exception as e:
                         st.error(f"Registration failed: {str(e)}")
        else:
            st.warning("Please fill in all fields")
    st.markdown('</div>', unsafe_allow_html=True)

st.info("Already have an account? Go to **Login** page.")
