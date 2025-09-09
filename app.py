# app.py - RoboMind Chatbot v2 (Multilingual + Mic Support, fixed translator)

import streamlit as st
import google.generativeai as genai
from datetime import datetime
from deep_translator import GoogleTranslator
from streamlit_mic_recorder import speech_to_text

# ------------------- CONFIG -------------------
st.set_page_config(page_title="RoboMind Chatbot", page_icon="🤖", layout="centered")

# Load Gemini API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------- APP HEADER -------------------
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🤖 RoboMind Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your AI Assistant in Urdu, Punjabi, Sindhi, Pashto & English</p>", unsafe_allow_html=True)

# ------------------- SESSION STATE -------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------- CHAT BUBBLES -------------------
def display_chat():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div style='background:#DCF8C6;padding:10px;border-radius:10px;margin:5px;text-align:right;'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#F1F0F0;padding:10px;border-radius:10px;margin:5px;text-align:left;'>{msg['content']}</div>", unsafe_allow_html=True)

display_chat()

# ------------------- USER INPUT -------------------
col1, col2 = st.columns([3,1])
with col1:
    user_input = st.text_input("Type your message:", key="input_text", label_visibility="collapsed")
with col2:
    st.write("")  # spacer
    mic_result = speech_to_text(language="ur-PK", use_container_width=True, just_once=True, key="STT")

if mic_result and mic_result.strip() != "":
    user_input = mic_result

# ------------------- PROCESS INPUT -------------------
if user_input:
    # Handle date/time locally
    if any(word in user_input.lower() for word in ["date", "time", "day", "waqt", "din", "تاریخ"]):
        now = datetime.now()
        bot_reply = f"📅 {now.strftime('%A, %d %B %Y')} ⏰ {now.strftime('%I:%M %p')}"
    else:
        # Translate input to English for Gemini
        translated_input = GoogleTranslator(source="auto", target="en").translate(user_input)
        response = model.generate_content(translated_input)

        # Translate back to user's language
        bot_reply = GoogleTranslator(source="en", target="auto").translate(response.text)

    # Save conversation
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

    st.experimental_rerun()

# ------------------- CLEAR CHAT -------------------
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()
