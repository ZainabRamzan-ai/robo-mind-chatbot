import streamlit as st
import google.generativeai as genai

# Configure your API key
genai.configure(api_key="AIzaSyBeRlo9dDomco6D0YZ7qg84mgyY8P2BUUU")

# Make Streamlit UI
st.title("🤖 Robo Mind Chatbot")
st.write("Ask me anything about business & AI.")

# User input
user_input = st.text_input("You:", "")

if user_input:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(user_input)
    st.text_area("🤖 Bot:", value=response.text, height=200)
