# app.py — RoboMind Multilingual Chatbot (text + mic), business-tuned

import os
import base64
import datetime
import tempfile
import streamlit as st
import google.generativeai as genai

# ---------- CONFIG ----------
st.set_page_config(page_title="RoboMind AI", page_icon="🤖", layout="centered")

# Secure API key (set in Streamlit Cloud: Settings → Secrets)
API_KEY = st.secrets.get("GOOGLE_API_KEY", None)
if not API_KEY:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets. Go to Manage app → Settings → Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# Business-tuned system prompt (multilingual, local context)
SYSTEM_PROMPT = """
You are RoboMind AI — a polite, concise, and practical assistant for Pakistani businesses.
Core behaviors:
- Detect the user's language (Urdu, Roman Urdu, Punjabi, Sindhi, English) and reply in the same language.
- Be helpful for business use-cases (pricing, FAQs, service details, lead collection).
- If asked for date/time/day, return the exact current value for Asia/Karachi.
- Be brief but clear. Use bullet points for steps/checklists when helpful.
- If user speaks via audio, first transcribe accurately then answer in the same language.
"""

# Gemini model (supports text + audio)
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# ---------- STYLES ----------
st.markdown("""
<style>
body { background: #F9FAFB; }
.header {
  background:#0A192F; color:#E2E8F0; padding:18px 20px; border-radius:16px;
  display:flex; align-items:center; gap:12px; margin-bottom:12px;
}
.header h1 { font-size:20px; margin:0; }
.header small { color:#94A3B8; }
.bubble-user {
  text-align:right; margin:6px 0;
}
.bubble-user span{
  background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
  color:white; padding:12px 14px; border-radius:14px; display:inline-block; max-width:75%;
  box-shadow:0 6px 18px rgba(79,70,229,0.25);
  word-wrap:break-word; white-space:pre-wrap;
}
.bubble-bot {
  text-align:left; margin:6px 0;
}
.bubble-bot span{
  background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
  color:white; padding:12px 14px; border-radius:14px; display:inline-block; max-width:75%;
  box-shadow:0 6px 18px rgba(16,185,129,0.25);
  word-wrap:break-word; white-space:pre-wrap;
}
.disclaimer {
  font-size:12px; color:#64748B; margin-top:6px;
}
.toolbar {
  display:flex; gap:8px; align-items:center; margin:6px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
  <div>🤖</div>
  <div>
    <h1>RoboMind AI — Smart Multilingual Chatbot</h1>
    <small>Built for Pakistani businesses • Urdu / Punjabi / Sindhi / English • Text & Voice</small>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []   # each: {"role": "user"|"assistant", "content": "text"}

# ---------- HELPERS ----------
def show_message(text: str, role: str):
    if role == "user":
        st.markdown(f"<div class='bubble-user'><span>{text}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bubble-bot'><span>{text}</span></div>", unsafe_allow_html=True)

def special_date_time_answer(user_text: str) -> str | None:
    """Return date/time/day answers for Asia/Karachi if the user asks."""
    lower = user_text.lower()
    if any(k in lower for k in ["time", "وقت"]):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)))  # Asia/Karachi UTC+5
        return f"⏰ {now.strftime('%I:%M %p')} (Asia/Karachi)"
    if any(k in lower for k in ["date", "تاریخ", "tarikh"]):
        today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)))
        return f"📅 {today.strftime('%A, %d %B %Y')} (Asia/Karachi)"
    if any(k in lower for k in ["day", "آج کون سا دن", "din"]):
        today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)))
        return f"📆 Today is {today.strftime('%A')} (Asia/Karachi)"
    return None

def run_model_with_text(prompt: str) -> str:
    chat = model.start_chat(history=[
        {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages
    ])
    resp = chat.send_message(prompt)
    return resp.text

def run_model_with_audio(wav_path: str) -> str:
    # Upload and let Gemini transcribe + respond
    file = genai.upload_file(wav_path)
    # Ask Gemini to transcribe and answer in same language
    prompt = "Please transcribe this audio, then answer the user in the same language. If it’s a general query, respond helpfully."
    resp = model.generate_content([file, prompt])
    # Cleanup uploaded file reference (optional)
    try:
        genai.delete_file(file.name)
    except Exception:
        pass
    return resp.text

# ---------- UI: Microphone (record in browser) ----------
# Uses streamlit-mic-recorder (add to requirements.txt)
try:
    from streamlit_mic_recorder import mic_recorder
    mic_available = True
except Exception:
    mic_available = False

with st.container():
    st.markdown("<div class='toolbar'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 5], vertical_alignment="center")
    with col1:
        if mic_available:
            audio = mic_recorder(
                start_prompt="🎙️ Record",
                stop_prompt="🛑 Stop",
                just_once=False,
                use_container_width=True,
                key="mic"
            )
        else:
            audio = None
    with col2:
        user_text = st.chat_input("Type your message… (or use mic)")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- PROCESS: Text input ----------
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    show_message(user_text, "user")

    # Date/Time smart answers first
    dt = special_date_time_answer(user_text)
    if dt:
        bot = dt
    else:
        bot = run_model_with_text(user_text)

    st.session_state.messages.append({"role": "assistant", "content": bot})
    show_message(bot, "assistant")

# ---------- PROCESS: Audio input ----------
if mic_available and audio and isinstance(audio, dict) and audio.get("bytes"):
    # Save temp wav, send to Gemini
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio["bytes"])
        wav_path = tmp.name

    # Show an inline "voice received" message
    st.session_state.messages.append({"role": "user", "content": "🎤 (voice message sent) Translating…"})
    show_message("🎤 (voice message sent) Translating…", "user")

    try:
        bot = run_model_with_audio(wav_path)
    except Exception as e:
        bot = "⚠️ Could not process audio. Please type your message instead."
    finally:
        try:
            os.remove(wav_path)
        except Exception:
            pass

    st.session_state.messages.append({"role": "assistant", "content": bot})
    show_message(bot, "assistant")

# ---------- HISTORY RENDER (on first load) ----------
if not (user_text or (mic_available and audio)):
    for m in st.session_state.messages:
        show_message(m["content"], m["role"])

st.markdown("<div class='disclaimer'>Tip: You can ask in Urdu/Punjabi/English. Try: \"آج کون سا دن ہے؟\" or \"Price list bhej do\".</div>", unsafe_allow_html=True)
