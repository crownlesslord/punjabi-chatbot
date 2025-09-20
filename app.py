import streamlit as st
from gtts import gTTS
from groq import Groq
from langchain_groq import ChatGroq
import base64
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

st.title("ਪੰਜਾਬੀ ਮੈਡੀਕਲ ਚੈਟਬਾਟ (Web Speech API + TTS)")

if "history" not in st.session_state:
    st.session_state.history = []

# 1️⃣ JS + HTML for browser speech recognition
st.write("🎤 Click the button and speak:")

components_code = """
<button onclick="startDictation()">Record</button>
<p id="transcript"></p>
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
user_prompt = st.text_input("Recognized text will appear here:")

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

# 5️⃣ When user presses Enter
if st.button("Send"):
    if user_prompt:
        response_text = get_response(user_prompt)
        st.session_state.history.append({"user": user_prompt, "bot": response_text})

# 6️⃣ Display chat history
for idx, chat in enumerate(st.session_state.history):
    st.markdown(f"**ਤੁਸੀਂ:** {chat['user']}")
    st.markdown(f"**ਬੋਟ:** {chat['bot']}")

    audio_file = f"response_{idx}.mp3"
    if not os.path.exists(audio_file):
        text_to_speech(chat["bot"], filename=audio_file)
    audio_bytes = open(audio_file, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")
    st.write("---")



