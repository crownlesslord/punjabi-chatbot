import streamlit as st
from gtts import gTTS
from groq import Groq
from langchain_groq import ChatGroq
import os

from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    st.stop()

system_message = """ 
ਤੁਸੀਂ ਇੱਕ ਪੇਸ਼ੇਵਰ ਅਤੇ ਜ਼ਿੰਮੇਵਾਰ ਮੈਡੀਕਲ ਸਹਾਇਕ ਚੈਟਬਾਟ ਹੋ। 
ਹਮੇਸ਼ਾਂ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ। 
...
"""

st.set_page_config(page_title="MEDICAL CHATBOT", page_icon="🩺", layout="centered")
st.title("🩺 MEDICAL CHATBOT")

if "history" not in st.session_state:
    st.session_state.history = []

# 1️⃣ JS + HTML for browser speech recognition
st.markdown("### 🎤 CLICK AND SPEAK")

components_code = """
<button style="padding: 10px; font-size: 16px; border-radius: 5px; background-color:#4CAF50; color:white;" onclick="startDictation()">Record</button>
<p id="transcript" style="margin-top:10px; font-weight:bold;"></p>
<script>
function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition')) {
        var recognition = new webkitSpeechRecognition();
        recognition.lang = "pa-IN";
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.start();

        recognition.onresult = function(e) {
            var transcript = e.results[0][0].transcript;
            document.getElementById('transcript').innerText = transcript;
            var inputBox = document.getElementById('stTextInput');
            if(inputBox) { inputBox.value = transcript; inputBox.dispatchEvent(new Event('input')); }
        };
        recognition.onerror = function(e) {
            console.log(e.error);
            alert("Error: " + e.error);
        }
    }
}
</script>
"""

st.components.v1.html(components_code, height=150)

# 2️⃣ User input text (filled automatically by JS)
user_prompt = st.text_input("Recognized text will appear here:", key="stTextInput")

# 3️⃣ Generate LLM response
def get_response(user_prompt):
    try:
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant"
        )
        messages = [{"role": "system", "content": system_message}]
        for chat in st.session_state.history:
            messages.append({"role": "user", "content": chat["user"]})
            messages.append({"role": "assistant", "content": chat["bot"]})
        messages.append({"role": "user", "content": user_prompt})
        response = llm.invoke(messages)
        return getattr(response, "content", response)
    except Exception as e:
        return f"Error: {e}"

# 4️⃣ TTS
def text_to_speech(text, filename="Recording.mp3"):
    tts = gTTS(text=text, lang="pa")
    tts.save(filename)
    return filename

# 5️⃣ When user presses Send
if st.button("📤 Send"):
    if user_prompt:
        response_text = get_response(user_prompt)
        st.session_state.history.append({"user": user_prompt, "bot": response_text})

# 6️⃣ Display chat history with bubbles
st.markdown("### 💬 CHAT HISTORY")

for idx, chat in enumerate(st.session_state.history):
    st.markdown(
        f"<div style='background-color:#DCF8C6; padding:10px; border-radius:10px; margin-bottom:5px;'>"
        f"<b>YOU:</b> {chat['user']}</div>", 
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='background-color:#F1F0F0; padding:10px; border-radius:10px; margin-bottom:10px;'>"
        f"<b>BOT:</b> {chat['bot']}</div>", 
        unsafe_allow_html=True
    )

    # Generate TTS if not exists
    audio_file = f"response_{idx}.mp3"
    if not os.path.exists(audio_file):
        text_to_speech(chat["bot"], filename=audio_file)
    audio_bytes = open(audio_file, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")
