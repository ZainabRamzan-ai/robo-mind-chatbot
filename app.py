import streamlit as st
import google.generativeai as genai
import datetime
import speech_recognition as sr
from deep_translator import GoogleTranslator

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="RoboMind Chatbot", page_icon="🤖", layout="centered")

# Load API Key from Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize Gemini model
model = genai.GenerativeModel("gemini-pro")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# -------------------------
# TRANSLATION FUNCTION
# -------------------------
def translate_text(text, target_lang="en"):
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except:
        return text

# -------------------------
# MICROPHONE
