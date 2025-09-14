import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import speech_recognition as sr
import datetime

# 🔑 Configure API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="RoboMind MVP", page_icon="🤖", layout="centered")

st.title("🤖 RoboMind MVP")
st.write("🎤 Speak or type in **any Pakistani language** (Urdu, Punjabi, Sindhi, Saraiki, English).")

# Initialize recognizer for speech
recognizer = sr.Recognizer()

# Conversation history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Function: Handle speech input
def speech_to_text():
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now!")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="ur-PK")
            return text
        except sr.UnknownValueError:
            return "⚠️ Could not understand audio."
        except sr.RequestError:
            return "⚠️ Speech recognition service error."

# Input choice: speech or text
option = st.radio("Choose input method:", ["💬 Text", "🎤 Speech"])

if option == "💬 Text":
    user_input = st.text_input("Type your message here:")
elif option == "🎤 Speech":
    if st.button("🎙️ Record"):
        user_input = speech_to_text()
    else:
        user_input = ""

# Process input
if user_input:
    # Detect language & translate to English
    translated_input = GoogleTranslator(source="auto", target="en").translate(user_input)

    # Get response from Gemini
    response = model.generate_content(translated_input)
    reply = response.text

    # Translate reply back to user's language
    detected_lang = GoogleTranslator(source="auto", target="en").detect(user_input)
    final_reply = GoogleTranslator(source="en", target=detected_lang).translate(reply)

    # Save to history
    st.session_state["history"].append(("You", user_input))
    st.session_state["history"].append(("Bot", final_reply))

# Show conversation
st.subheader("💬 Chat History")
for sender, msg in st.session_state["history"]:
    st.markdown(f"**{sender}:** {msg}")

# Show date/time
st.sidebar.write("📅", datetime.datetime.now().strftime("%A, %d %B %Y %I:%M %p"))
