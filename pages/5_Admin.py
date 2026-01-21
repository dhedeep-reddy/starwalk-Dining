import streamlit as st
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AI_UseCase.db.supabase_client import SupabaseManager
from AI_UseCase.chat_logic import ChatLogic

st.set_page_config(page_title="Admin Dashboard - Starwalk Dining", page_icon="🔒", layout="wide")

st.logo("assets/logo.png", size="large")

# Load CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Admin Authorization Check
if not st.session_state.get("logged_in", False):
    st.error("Access Denied. Please Login.")
    st.stop()

# Simulating Admin Check (In real app, check role from DB/Auth)
# For now, we rely on the `is_admin` flag we set in Login.py (which is currently hardcoded/mocked)
# OR we check email here directly.
# if not st.session_state.get("is_admin", False) and st.session_state.user.get('email') != 'admin@lumiere.com': 
#    # Fallback email check if flag wasn't set or just to be safe
#    st.error("🚫 Access Restricted to Administrators.")
#    st.stop()
st.success(f"🔓 Admin Access Granted (Test Mode) for: {st.session_state.user.get('name', st.session_state.user.get('email'))}")

db = SupabaseManager()
# We need ChatLogic to access RAG ingestion
@st.cache_resource
def get_logic():
    return ChatLogic()

logic = get_logic()

st.title("🔒 Admin Dashboard")

tab1, tab2 = st.tabs(["📊 Reservations", "📚 Knowledge Base"])

with tab1:
    st.subheader("All Reservations")
    bookings = db.get_all_bookings()
    if bookings:
        # Flatten and Formatting
        import pandas as pd
        df = pd.DataFrame(bookings)
        
        # Flatten 'customers' dict if present
        if 'customers' in df.columns:
            # Safe extraction
            df['Customer Name'] = df['customers'].apply(lambda x: x.get('name') if isinstance(x, dict) else 'N/A')
            df['Email'] = df['customers'].apply(lambda x: x.get('email') if isinstance(x, dict) else 'N/A')
            df['Phone'] = df['customers'].apply(lambda x: x.get('phone') if isinstance(x, dict) else 'N/A')
        
        # Rename other columns
        df = df.rename(columns={
            "reservation_date": "Date",
            "reservation_time": "Time",
            "party_size": "Party Size",
            "special_requests": "Requests",
            "status": "Status",
            "id": "ID"
        })
        
        # Select and Order Columns
        cols = ["ID", "Customer Name", "Date", "Time", "Party Size", "Phone", "Email", "Requests", "Status"]
        # Filter only existing columns just in case
        cols = [c for c in cols if c in df.columns]
        
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
    else:
        st.info("No bookings found.")

with tab2:
    st.subheader("Manage Menu & Policies")
    st.info("Uploaded PDFs will be used by the AI to answer customer queries.")
    
    uploaded_file = st.file_uploader("Upload Menu/Policy PDF", type="pdf")
    if uploaded_file:
        button_key = "process_pdf_btn"
        if st.button("Process PDF", key=button_key):
             # Save temp
            with open("temp_admin.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Ingesting PDF to Vector Store..."):
                success, msg = logic.rag.ingest_pdf("temp_admin.pdf")
                if success:
                    st.success(f"Success! {msg}")
                else:
                    st.error(f"Failed: {msg}")
