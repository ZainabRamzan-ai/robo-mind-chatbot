# app.py – RoboMind Chatbot (multilingual + voice + datetime)

import streamlit as st
import google.generativeai as genai
import datetime
import speech_recognition as sr
from googletrans import Translator

# ------------------ CONFIG ------------------
st.set_page_config(page_title="RoboMind Chatbot", page_icon="🤖", layout="centered")

# API Key (set in Streamlit secrets for safety)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize model
def load_model():
    try:
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        return genai.GenerativeModel("gemini-1.5-pro")

model = load_model()

# Translator for multi-lingual support
translator = Translator()

# ------------------ STYLES ------------------
st.markdown("""
    <style>
    .user-bubble {
        background-color: #0078D7; 
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px;
        max-width: 70%;
        align-self: flex-end;
    }
    .bot-bubble {
        background-color: #F3F3F3; 
        color: black;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px;
        max-width: 70%;
        align-self: flex-start;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ------------------ FUNCTIONS ------------------
def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("📅 %A, %d %B %Y ⏰ %I:%M %p")

def process_input(user_text):
    # Handle datetime question
    if "date" in user_text.lower() or "time" in user_text.lower() or "day" in user_text.lower():
        return get_datetime()
    
    # Translate if not English
    detected = translator.detect(user_text).lang
    if detected != "en":
        user_text = translator.translate(user_text, src=detected, dest="en").text
    
    # Generate response
    response = model.generate_content(user_text)
    reply = response.candidates[0].content.parts[0].text
    
    # Translate back if needed
    if detected != "en":
        reply = translator.translate(reply, src="en", dest=detected).text
    
    return reply

def recognize_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... speak now!")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        text = r.recognize_google(audio, language="ur-PK")  # Urdu/Punjabi/Sindhi detection possible
        return text
    except:
        return "❌ Could not understand audio."

# ------------------ UI ------------------
st.title("🤖 RoboMind Multilingual Chatbot")

col1, col2 = st.columns([4,1])
with col1:
    user_input = st.text_input("💬 Type your message", key="input", placeholder="Ask me anything...")
with col2:
    if st.button("🎤 Voice"):
        voice_text = recognize_voice()
        if voice_text and "❌" not in voice_text:
            st.session_state["messages"].append({"role": "user", "text": voice_text})
            st.session_state["messages"].append({"role": "bot", "text": process_input(voice_text)})

# On submit
if user_input:
    st.session_state["messages"].append({"role": "user", "text": user_input})
    st.session_state["messages"].append({"role": "bot", "text": process_input(user_input)})
    st.session_state.input = ""  # clear box

# Display chat
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">{msg["text"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
