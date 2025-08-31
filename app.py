import streamlit as st
import google.generativeai as genai
import datetime
import time

# ✅ Configure API Key
genai.configure(api_key=st.secrets["AIzaSyBeRlo9dDomco6D0YZ7qg84mgyY8P2BUUU"])

# Initialize model
model = genai.GenerativeModel("gemini-pro")

# ✅ Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "day_counter" not in st.session_state:
    st.session_state.day_counter = 1
if "reminders" not in st.session_state:
    st.session_state.reminders = []

# ✅ Function to check date/time
def get_datetime_response(user_input):
    now = datetime.datetime.now()
    if "time" in user_input.lower():
        return f"⏰ The current time is {now.strftime('%I:%M %p')}."
    elif "date" in user_input.lower():
        return f"📅 Today's date is {now.strftime('%A, %d %B %Y')}."
    elif "day" in user_input.lower():
        return f"📅 This is Day {st.session_state.day_counter} of RoboMind."
    return None

# ✅ Function to add reminders
def set_reminder(user_input):
    if "remind me" in user_input.lower():
        try:
            minutes = [int(s) for s in user_input.split() if s.isdigit()][0]
            reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            st.session_state.reminders.append(reminder_time)
            return f"⏰ Reminder set for {minutes} minutes from now!"
        except:
            return "⚠️ Couldn't set reminder. Please say like: 'Remind me in 2 minutes'."
    return None

# ✅ Streamlit layout
st.title("🤖 RoboMind Chatbot")
st.markdown("Your personal AI assistant with reminders, time/date, and chat history.")

chat_container = st.container()

# ✅ Display messages in WhatsApp-style
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div style='background:#DCF8C6; padding:8px; border-radius:8px; margin:4px; text-align:right'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#ECECEC; padding:8px; border-radius:8px; margin:4px; text-align:left'>{msg['content']}</div>", unsafe_allow_html=True)

# ✅ User input box
user_input = st.chat_input("Type your message here...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Check special cases (date/time/reminder)
    response = get_datetime_response(user_input)
    if not response:
        response = set_reminder(user_input)

    # If not special, use AI
    if not response:
        ai_response = model.generate_content(user_input)
        response = ai_response.text

    # Save bot response
    st.session_state.messages.append({"role": "bot", "content": response})

    # Refresh page to show new messages
    st.rerun()

# ✅ Check reminders
for reminder_time in list(st.session_state.reminders):
    if datetime.datetime.now() >= reminder_time:
        st.session_state.messages.append({"role": "bot", "content": "⏰ Reminder Alert! (Beep Beep 🔔)"})
        st.session_state.reminders.remove(reminder_time)
        st.rerun()
