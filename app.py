import streamlit as st
import google.generativeai as genai
import datetime
import time
import os

# 🔑 API Key (make sure GOOGLE_API_KEY is in secrets/environment)
genai.configure(api_key=os.getenv("AIzaSyBeRlo9dDomco6D0YZ7qg84mgyY8P2BUUU"))

# Initialize model
model = genai.GenerativeModel("gemini-pro")

# --- Page Settings ---
st.set_page_config(page_title="RoboMind Chatbot", page_icon="🤖")
st.title("💬 RoboMind Chatbot")
st.caption("WhatsApp-style chatbot with date, time, and reminders ⏰")

# Keep chat history in session
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history like WhatsApp
for role, msg in st.session_state["messages"]:
    with st.chat_message(role):
        st.markdown(msg)

# User input at bottom
if prompt := st.chat_input("Type your message..."):
    # Save user message
    st.session_state["messages"].append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- BOT RESPONSE HANDLER ---
    if "time" in prompt.lower():
        bot_response = f"⏰ The current time is: {datetime.datetime.now().strftime('%H:%M:%S')}"
    elif "date" in prompt.lower():
        bot_response = f"📅 Today's date is: {datetime.datetime.now().strftime('%Y-%m-%d')}"
    elif "remind" in prompt.lower():
        bot_response = "🔔 Reminder set! (This is a prototype — it will beep in 5 seconds)"
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        time.sleep(5)
        st.balloons()
        st.audio("https://www.soundjay.com/buttons/beep-07.wav")
    else:
        response = model.generate_content(prompt)
        bot_response = response.text

    # Save bot response
    st.session_state["messages"].append(("assistant", bot_response))
    with st.chat_message("assistant"):
        st.markdown(bot_response)
