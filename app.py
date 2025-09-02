import streamlit as st
import google.generativeai as genai
import datetime
import speech_recognition as sr

# Configure API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Helper: Detect flood queries
def is_flood_query(text):
    keywords = ["flood", "barish", "selab", "flooding"]
    return any(word in text.lower() for word in keywords)

# Helper: Detect date/time queries
def is_time_query(text):
    keywords = ["date", "time", "waqt", "din", "roz"]
    return any(word in text.lower() for word in keywords)

# Page design
st.title("🌐 RoboMind Chatbot")
st.markdown("### Multilingual | Voice + Text | Smart Awareness")

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input("Type your message:", key="user_text")

with col2:
    if st.button("🎤 Speak"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        try:
            user_input = recognizer.recognize_google(audio, language="ur-PK")
            st.success(f"Voice detected: {user_input}")
        except:
            st.error("Sorry, could not understand audio")

# Process input
if user_input:
    # Save user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    if is_flood_query(user_input):
        reply = "🌊 Flood Update: Severe floods in Punjab have displaced millions. Over 1M evacuated. Relief efforts ongoing."
    elif is_time_query(user_input):
        now = datetime.datetime.now()
        reply = f"📅 Today is {now.strftime('%A, %d %B %Y')} | 🕒 Current time: {now.strftime('%I:%M %p')}"
    else:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_input)
        reply = response.text

    # Save bot reply
    st.session_state["messages"].append({"role": "assistant", "content": reply})

    # Show bot reply
    with st.chat_message("assistant"):
        st.markdown(reply)
