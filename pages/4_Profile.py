import streamlit as st
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.supabase_client import SupabaseManager

st.set_page_config(page_title="My Profile - Starwalk Dining", page_icon="👤", layout="wide")

st.logo("assets/logo.png", size="large")

# Load CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if not st.session_state.get("logged_in", False):
    st.warning("Please Login to view profile.")
    st.stop()

db = SupabaseManager()

st.title("👤 My Profile")

with st.container():
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.subheader("Your Reservations")
    
    bookings = db.get_user_bookings(st.session_state.user['email'])
    
    if bookings:
        # Convert to nice DataFrame
        df = pd.DataFrame(bookings)
        
        # Rename for display
        df = df.rename(columns={
            "reservation_date": "Date",
            "reservation_time": "Time", 
            "party_size": "Party Size",
            "status": "Status", 
            "special_requests": "Requests"
        })
        
        # Select columns if available
        cols_to_show = ["Date", "Time", "Party Size", "Status", "Requests"]
        # Filter existing columns
        cols = [c for c in cols_to_show if c in df.columns]
        
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
    else:
        st.info("You have no past reservations.")
    
    st.markdown('</div>', unsafe_allow_html=True)
