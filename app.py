import streamlit as st
import google.generativeai as genai
from googletrans import Translator
from streamlit_mic_recorder import mic_recorder
import datetime

# ------------------ CONFIG ------------------
st.set_page_config(page_title="RoboMind Chatbot", page_icon="🤖", layout="wide")

# Configure API key (set in Streamlit Secrets)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Translator
translator = Translator()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ HEADER ------------------
st.markdown(
    """
    <style>
    .chat-container {
        max-width: 800px;
        margin: auto;
    }
    .bubble-user {
        text-align: right;
        margin: 10px;
    }
    .bubble-user span {
        background: linear-gradient(135deg, #4f46e5 0
