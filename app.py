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
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
        color: white;
        padding: 12px 14px;
        border-radius: 14px;
        display: inline-block;
        box-shadow: 0 6px 18px rgba(147,51,234,0.25);
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .bubble-bot {
        text-align: left;
        margin: 10px;
    }
    .bubble-bot span {
        background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
        color: white;
        padding: 12px 14px;
        border-radius: 14px;
        display: inline-block;
        box-shadow: 0 6px 18px rgba(16,185,129,0.25);
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🤖 RoboMind Multilingual Chatbot")
st.caption(f"Today's Date: {datetime.datetime.now().strftime('%A, %d %B %Y')}")

# ------------------ MIC INPUT ------------------
audio = mic_recorder(
    start_prompt="🎤 Speak",
    stop_prompt="⏹️ Stop",
    just_once=True,
    use_container_width=True,
    key="recorder"
)

if audio:
    text = audio["text"]
    if text:
        st.session_state.messages.append({"role": "user", "content": text})

# ------------------ TEXT INPUT ------------------
user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

# ------------------ PROCESS & REPLY ------------------
if st.session_state.messages:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='bubble-user'><span>{msg['content']}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bubble-bot'><span>{msg['content']}</span></div>", unsafe_allow_html=True)

    # Only send last user message to Gemini
    if st.session_state.messages[-1]["role"] == "user":
        user_text = st.session_state.messages[-1]["content"]

        # Detect language & translate to English
        detected = translator.detect(user_text)
        if detected.lang != "en":
            user_text = translator.translate(user_text, dest="en").text

        # Call Gemini API
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_text)

        bot_reply = response.text

        # If original lang not English, translate back
        if detected.lang != "en":
            bot_reply = translator.translate(bot_reply, dest=detected.lang).text

        # Save bot reply
        st.session_state.messages.append({"role": "bot", "content": bot_reply})

        # Show bot reply
        st.markdown(f"<div class='bubble-bot'><span>{bot_reply}</span></div>", unsafe_allow_html=True)
