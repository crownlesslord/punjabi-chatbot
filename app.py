import streamlit as st
from gtts import gTTS
from groq import Groq
from langchain_groq import ChatGroq
import os

# -------------------------
# Groq API Key
# -------------------------
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    st.stop()

# -------------------------
# System message
# -------------------------
system_message = """
ਤੁਸੀਂ ਇੱਕ ਪੇਸ਼ੇਵਰ ਅਤੇ ਜ਼ਿੰਮੇਵਾਰ ਮੈਡੀਕਲ ਸਹਾਇਕ ਚੈਟਬਾਟ ਹੋ।
ਹਮੇਸ਼ਾਂ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ।
"""

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Punjab Medical ChatBot",
    page_icon="🩺",
    layout="wide"
)

# -------------------------
# Sidebar (branding & info)
# -------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/medical-chatbot.png", width=96)
    st.markdown(
        "<h2 style='color:#0072bc;'>Medical Assistant</h2>"
        "<hr style='border:1px solid #0072bc;'>"
        "<p style='color:#555;'>AI-powered chatbot for your healthcare questions. <br> Powered by Llama-3 & Punjabi support.</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='color:#0072bc; font-size:16px; margin-top:20px;'>"
        "Disclaimer: Not a substitute for a doctor. For emergencies, consult a medical professional."
        "</div>",
        unsafe_allow_html=True
    )

# -------------------------
# Session state
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "user_input_text" not in st.session_state:
    st.session_state.user_input_text = ""

# -------------------------
# CSS for medical style
# -------------------------
st.markdown("""
<style>
body, .stApp, .block-container {
    background-color: #eaf4fc;
    font-family: 'Segoe UI', 'Montserrat', sans-serif;
}
.header {
    text-align: center;
    padding: 18px 0px;
    background: linear-gradient(to right, #0072bc 60%, #05c3de 100%);
    color: #fff;
    border-radius: 14px;
    margin-bottom: 20px;
    font-size: 28px;
    font-weight: 800;
    box-shadow: 0 2px 10px rgba(0,120,180,0.08);
}
.chat-container {
    max-height: 580px;
    overflow-y: auto;
    padding: 25px;
    border-radius: 16px;
    background-color: #fefefe;
    border: 2px solid #c4e3fa;
    box-shadow: 0 2px 16px rgba(0,80,100,0.13);
}
.user-bubble {
    background: linear-gradient(95deg,#05c3de 65%,#37b7f8 100%);
    color: white;
    padding: 13px 22px;
    border-radius: 18px 18px 0 18px;
    margin: 7px 0;
    max-width: 68%;
    text-align: right;
    float: right;
    clear: both;
    font-size: 17px;
    font-family: 'Montserrat', sans-serif;
    font-weight: 500;
}
.bot-bubble {
    background: linear-gradient(115deg,#f4fcff 60%,#99e3fa 100%);
    color: #0072bc;
    padding: 13px 22px;
    border-radius: 18px 18px 18px 0;
    margin: 7px 0;
    max-width: 68%;
    text-align: left;
    float: left;
    clear: both;
    font-size: 17px;
    font-family: 'Montserrat', sans-serif;
    font-weight: 500;
}
.input-row {
    display: flex;
    margin-top: 18px;
}
input[type="text"] {
    flex: 1;
    padding: 15px;
    font-size: 17px;
    border-radius: 14px;
    border: 2px solid #99e3fa;
    background-color: #fefefe;
    color:#000000;
}
button.send-btn {
    padding: 15px 32px;
    margin-left: 12px;
    background-color: #0072bc;
    color: white;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    font-weight: 700;
    font-size: 17px;
    box-shadow: 0 2px 6px rgba(0,120,180,0.14);
    transition: background 0.2s;
}
button.send-btn:hover {
    background-color: #05c3de;
}
::-webkit-scrollbar {
    width: 7px;
    background: #eaf4fc;
}
::-webkit-scrollbar-thumb {
    background: #99e3fa;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
st.markdown('<div class="header">🩺 Punjab Medical ChatBot</div>', unsafe_allow_html=True)

# -------------------------
# Chat container
# -------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for idx, chat in enumerate(st.session_state.history):
    st.markdown(f'<div class="user-bubble"><b>Patient:</b> {chat["user"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot-bubble"><b>Assistant:</b> {chat["bot"]}</div>', unsafe_allow_html=True)
    # TTS (Punjabi response)
    audio_file = f"response_{idx}.mp3"
    if not os.path.exists(audio_file):
        tts = gTTS(text=chat["bot"], lang="pa")
        tts.save(audio_file)
    audio_bytes = open(audio_file, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Input row
# -------------------------
input_col, send_col = st.columns([8,1])
with input_col:
    user_prompt = st.text_input(
        "",
        key="user_input_text",
        placeholder="Type your symptom or medical query here...",
        label_visibility="collapsed"
    )
with send_col:
    send_clicked = st.button("Send", key="send_btn", use_container_width=True)

# -------------------------
# LLM response function
# -------------------------
def get_response(prompt):
    try:
        llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
        messages = [{"role": "system", "content": system_message}]
        for chat in st.session_state.history:
            messages.append({"role": "user", "content": chat["user"]})
            messages.append({"role": "assistant", "content": chat["bot"]})
        messages.append({"role": "user", "content": prompt})
        response = llm.invoke(messages)
        return getattr(response, "content", response)
    except Exception as e:
        return f"Error: {e}"

# -------------------------
# Handle send
# -------------------------
if send_clicked and user_prompt.strip() != "":
    response_text = get_response(user_prompt)
    st.session_state.history.append({"user": user_prompt, "bot": response_text})
    st.experimental_rerun()
