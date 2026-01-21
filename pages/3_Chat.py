import streamlit as st
import os
import sys

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AI_UseCase.chat_logic import ChatLogic

st.set_page_config(page_title="Reservation - Starwalk Dining", page_icon="🍽️", layout="wide")

st.logo("assets/logo.png", size="large")

# Load CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Authentication Check
if not st.session_state.get("logged_in", False):
    st.warning("Please Login to make a reservation.")
    st.stop()

@st.cache_resource
def get_chat_logic():
    return ChatLogic()

logic = get_chat_logic()

# Use First Name
name = st.session_state.user.get('name', 'Guest')
first_name = name.split()[0] if name else "Guest"

st.title(f"Welcome, {first_name}")
st.header("🍽️ Make a Reservation")

# Sidebar for logout
with st.sidebar:
    st.write("---")
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("app.py")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
        # Reset simple chat history for RAG context if needed
        st.rerun()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("I'd like to book a table..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            lc_history = [] # simplify
            response = logic.process_message(st.session_state.session_id, prompt, lc_history)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
