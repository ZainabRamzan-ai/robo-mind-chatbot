import streamlit as st
import google.generativeai as genai
import datetime
import speech_recognition as sr
from googletrans import Translator

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(page_title="RoboMind Chatbot", layout="centered")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")
translator = Translator()

# ==============================
# SESSION STATE INIT
# ==============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ==============================
# STYLES
# ==============================
st.markdown("""
<style>
.user-msg {
    background-color: #DCF8C6;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: right;
}
.bot-msg {
    background-color: #EDEDED;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: left;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# FUNCTIONS
# ==============================
def detect_and_translate(text, target="en"):
    """Detect language and translate if needed."""
    detected = translator.detect(text).lang
    if detected != target:
        translated = translator.translate(text, src=detected, dest=target)
        return translated.text, detected
    return text, detected

def record_voice():
    """Capture audio from microphone and return text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... please speak.")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio, language="ur-PK")  # Urdu by default
    except:
        return "Sorry, I could not understand the audio."

def handle_bot_response(user_text):
    """Generate a bot response with special cases for date/time."""
    lower_text = user_text.lower()

    # Date/time handling
    if "date" in lower_text or "day" in lower_text:
        return f"📅 Today is {datetime.datetime.now().strftime('%A, %d %B %Y (%I:%M %p)')}"
    if "time" in lower_text:
        return f"⏰ Current time: {datetime.datetime.now().strftime('%I:%M %p')}"

    # AI model response
    response = model.generate_content(user_text)
    return response.text

# ==============================
# INTERFACE
# ==============================
st.title("🤖 RoboMind Chatbot")
st.caption("Multilingual | Voice-enabled | Smart date & time answers")

# Display chat history
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"<div class='user-msg'>{chat['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>{chat['content']}</div>", unsafe_allow_html=True)

# Input area
col1, col2 = st.columns([3,1])
with col1:
    user_input = st.text_input("💬 Type your message:", value=st.session_state.user_input, key="input")
with col2:
    if st.button("🎤 Speak"):
        voice_text = record_voice()
        if voice_text:
            st.session_state.user_input = voice_text

# Send button
if st.button("Send"):
    if st.session_state.user_input.strip():
        translated_text, detected_lang = detect_and_translate(st.session_state.user_input, target="en")

        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": st.session_state.user_input})

        # Generate bot response
        bot_reply = handle_bot_response(translated_text)

        # Translate back to original language if not English
        if detected_lang != "en":
            bot_reply = translator.translate(bot_reply, src="en", dest=detected_lang).text

        # Add bot response
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

        # Clear input field
        st.session_state.user_input = ""

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("⚡ Powered by RoboMind Solution | Multilingual AI Chatbot for Pakistan")
