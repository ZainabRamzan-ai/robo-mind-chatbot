# app.py - RoboMind Chatbot with Date/Time + Conversation History

import streamlit as st
import google.generativeai as genai
import datetime

# 🔑 Load API key from Streamlit Secrets (secure way)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Chat model
model = genai.GenerativeModel("gemini-1.5-flash")

# Page config
st.set_page_config(page_title="🤖 RoboMind Chatbot", layout="centered")

st.title("🤖 RoboMind Chatbot")
st.write("Your AI assistant that remembers context, tells date/time, and chats like WhatsApp!")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
user_input = st.chat_input("Type your message...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Special: handle date & time
    if "time" in user_input.lower() or "date" in user_input.lower() or "day" in user_input.lower():
        now = datetime.datetime.now()
        bot_reply = f"📅 Today is **{now.strftime('%A, %d %B %Y')}** and the time is ⏰ **{now.strftime('%I:%M %p')}**."
    else:
        # Generate AI response
        chat = model.start_chat(history=[
            {"role": msg["role"], "parts": [msg["content"]]} for msg in st.session_state.messages
        ])
        response = chat.send_message(user_input)
        bot_reply = response.text

    # Save bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# Display chat messages (WhatsApp-style bubbles)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align: right; background:#DCF8C6; padding:8px; border-radius:10px; margin:4px;'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left; background:#ECECEC; padding:8px; border-radius:10px; margin:4px;'>{msg['content']}</div>", unsafe_allow_html=True)
