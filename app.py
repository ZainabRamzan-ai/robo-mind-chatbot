# app.py — RoboMind stable minimal chat (text-only, multi-language via system prompt)
import os
import re
import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import google.generativeai as genai

# -------------------- CONFIG --------------------
st.set_page_config(page_title="RoboMind Chat", page_icon="🤖", layout="centered")

# API key (secure): Streamlit Secrets or environment variable fallback
API_KEY = st.secrets.get("GOOGLE_API_KEY") if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("Missing API key. Add GOOGLE_API_KEY in Streamlit Secrets (Manage app → Settings → Secrets) or set env var.")
    st.stop()
genai.configure(api_key=API_KEY)

# Use a reliable Gemini model
MODEL_NAME = "gemini-1.5-flash"

# System prompt: instruct the model to detect language and reply in same language
SYSTEM_PROMPT = """
You are RoboMind — a concise, practical AI assistant for Pakistani users and businesses.
Behaviors:
- Detect user's language (Urdu, Punjabi, Sindhi, Pashto, Saraiki, English, Hindi).
- Always reply in the same language the user used.
- If user asks for the current date/time/day, answer using Asia/Karachi timezone (explicitly).
- Be brief and give practical next steps for business/market questions.
- When asked for live news or updates (e.g., 'floods', 'latest news'), reply: "I can fetch live headlines if you allow 'news' mode." (we'll add live news later).
"""

# -------------------- HELPERS --------------------
def now_in_karachi():
    tz = ZoneInfo("Asia/Karachi")
    return datetime.datetime.now(tz)

def is_datetime_query(text: str) -> bool:
    pattern = re.compile(r"\b(time|date|day|waqt|tarikh|aaj|کیا وقت|کیا تاریخ)\b", re.IGNORECASE)
    return bool(pattern.search(text or ""))

def safe_generate(prompt: str, system_prompt: str = SYSTEM_PROMPT, model_name: str = MODEL_NAME):
    """
    Call Gemini safely and return string text. Handles different response shapes defensively.
    """
    try:
        model = genai.GenerativeModel(model_name)
        # Send system + user as list of texts so the model sees the system instruction
        resp = model.generate_content([{"text": system_prompt}, {"text": prompt}])
    except Exception as e:
        # Catch and show a friendly message (but return a string)
        return f"⚠️ Model request failed: {str(e)}"

    # Extract text robustly
    # Newer responses often have `.text`; older structures may have `candidates`.
    if hasattr(resp, "text") and resp.text:
        return resp.text
    if getattr(resp, "candidates", None):
        try:
            # nested structure: candidates[0].content[0].text
            return resp.candidates[0].content[0].text
        except Exception:
            try:
                return resp.candidates[0].content.parts[0].text
            except Exception:
                return str(resp)
    return str(resp)

# -------------------- SESSION --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of dicts: {"role":"user"/"assistant", "text": "...", "ts": timestamp}

# -------------------- UI --------------------
st.title("🤖 RoboMind — Stable Chat")
st.caption("Text-first. Multilingual support via model instructions. (Mic/TTS will be added after this is stable.)")
st.markdown("---")

# Conversation area
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"<div style='text-align:right; background:linear-gradient(90deg,#6b46c1,#4f46e5); color:white; padding:10px; border-radius:12px; margin:6px 0;'> {m['text']} </div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:left; background:linear-gradient(90deg,#06b6d4,#10b981); color:#05121f; padding:10px; border-radius:12px; margin:6px 0;'> {m['text']} </div>", unsafe_allow_html=True)

# Input area
user_text = st.text_input("Type your message (or ask date/time):", key="input_text")

# Buttons row
col1, col2, col3 = st.columns([1,1,1])
with col1:
    send = st.button("Send")
with col2:
    clear = st.button("Clear Chat")
with col3:
    show_dt = st.button("Show Date/Time")

if clear:
    st.session_state.messages = []

if show_dt:
    dt = now_in_karachi()
    txt = f"📅 {dt.strftime('%A, %d %B %Y')}  ⏰ {dt.strftime('%I:%M %p')}"
    st.session_state.messages.append({"role":"assistant","text":txt,"ts": datetime.datetime.utcnow().isoformat()})

if send and user_text and user_text.strip():
    st.session_state.messages.append({"role":"user","text":user_text.strip(),"ts": datetime.datetime.utcnow().isoformat()})

    # 1) If the user explicitly asks for date/time -> reply locally (fast, accurate)
    if is_datetime_query(user_text):
        dt = now_in_karachi()
        reply = f"📅 {dt.strftime('%A, %d %B %Y')}  ⏰ {dt.strftime('%I:%M %p')}"
        st.session_state.messages.append({"role":"assistant","text":reply,"ts": datetime.datetime.utcnow().isoformat()})
    else:
        # 2) Normal AI flow — ask Gemini to detect language and answer in same language
        # We send only the user message as prompt (system prompt guides language behavior)
        reply = safe_generate(user_text)
        st.session_state.messages.append({"role":"assistant","text":reply,"ts": datetime.datetime.utcnow().isoformat()})

# Keep input cleared after send for ux
if send:
    st.session_state.input_text = ""

st.markdown("---")
st.caption("If this runs with no errors, tell me and I'll add optional mic + TTS next.")
