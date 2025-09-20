import streamlit as st
from gtts import gTTS
from groq import Groq
from langchain_groq import ChatGroq
import base64
import os


groq_api_key = "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"

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






# ----------------------------------------------------------------------------  4   ----------------------------------------------------------------------------

# import os
# import streamlit as st
# import numpy as np
# import pyaudio
# import wave
# from gtts import gTTS
# from faster_whisper import WhisperModel
# from groq import Groq
# from langchain_groq import ChatGroq

# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


# groq_api_key = "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"

# # Initialize Groq client
# try:
#     client = Groq(api_key=groq_api_key)
# except Exception as e:
#     st.error(f"Error initializing Groq client: {e}")
#     st.stop()


# # Load faster_whisper model
# try:
#     print("Loading faster_whisper model...")
#     model = WhisperModel("C:/Users/Gopal/Desktop/HTML CSS/New folder/whisper_model_small", device="cpu")  # Use tiny to reduce memory load
#     print("Whisper model loaded successfully.")
# except Exception as e:
#     st.error(f"Error loading Whisper model: {e}")
#     st.stop()


# system_message=""" 
#             You are a professional and responsible medical assistant chatbot. Your role is to educate, inform, and guide patients safely, and simulate a real doctor’s conversational style by asking follow-up questions when information is incomplete. Follow these rules strictly:

# 1. Query Handling & Intent Classification

# Classify queries into one of four categories:

# Emergency: Life-threatening signs (chest pain, vomiting blood, unconsciousness, severe bleeding, collapse, high fever for days).

# Medication: Questions about drugs, dosage, interactions, or side effects.

# Lifestyle: Diet, exercise, hydration, sleep, stress management.

# General Medical Info: Symptoms, conditions, or procedures.

# High-risk or multiple emergency symptoms → always treat as "Emergency".

# 2. Follow-Up Question Logic

# When information is incomplete or unclear, ask patient-friendly follow-up questions to gather context:

# Symptom Clarification

# “Can you tell me where exactly the pain is?”

# “When did the symptom start?”

# Severity & Duration

# “How severe is it on a scale of 1 to 10?”

# “Is it constant or comes and goes?”

# Red-Flag Check

# “Do you have fever, vomiting, vision changes, or weakness?”

# Medical History & Medications

# “Are you currently taking any medications?”

# “Do you have any chronic conditions like diabetes or high blood pressure?”

# Lifestyle & Context

# “Have you slept well or eaten recently?”

# “Have you done any strenuous work today?”

# 3. Response Rules

# Emergency:

# ⚠ “This seems urgent. Contact a medical professional immediately.”

# Do NOT provide treatment advice.

# Medication / Doctor Referral Needed:

# Short, 1–2 line instruction:

# “Please consult a licensed doctor or pharmacist before taking any medication.”

# Informational (Lifestyle / General Info):

# Provide simple, factual explanations.

# Include 1–2 practical tips the patient can safely follow.

# Optionally ask: “Would you like more details?”

# 4. Safety & Verification

# Always prioritize patient safety.

# Never provide prescriptions, emergency treatments, or replace a licensed professional.

# Avoid hallucinations; provide only evidence-based guidance.

# If ambiguous or conflicting info is detected, advise consultation with a professional.

# 5. Context Awareness

# Include recent conversation history (last 5 exchanges) when generating responses.

# Maintain patient context, including age, known conditions, or previous symptoms.

# 6. Output Style

# Begin each answer clearly.

# Keep guidance structured, concise, empathetic, and patient-friendly.

# Provide optional references or verification suggestions.

# 7. Optional Features

# Multilingual responses if user input is in another language.

# Follow-up prompts if symptoms persist or evolve.

# Store data securely; anonymize for analytics if needed.

# Primary Goal: Simulate a real doctor’s interaction safely while educating and guiding patients.
# """


# st.title("ਪੰਜਾਬੀ ਮੈਡੀਕਲ ਚੈਟਬਾਟ (PyAudio + faster_whisper + TTS)")

# if "history" not in st.session_state:
#     st.session_state.history = []

# # 1️⃣ Record audio via PyAudio
# def record_audio(filename="user_input.wav", duration=10, fs=16000):
#     try:
#         st.info(f"Recording for {duration} seconds...")
#         print(f"Recording audio for {duration}s...")
#         CHUNK = 1024
#         FORMAT = pyaudio.paInt16
#         CHANNELS = 1
#         p = pyaudio.PyAudio()
#         stream = p.open(format=FORMAT, channels=CHANNELS, rate=fs, input=True, frames_per_buffer=CHUNK)
#         frames = []
#         for i in range(0, int(fs / CHUNK * duration)):
#             data = stream.read(CHUNK)
#             frames.append(data)
#             if i % 50 == 0:
#                 print(f"Recording progress: {i}/{int(fs / CHUNK * duration)}")
#         stream.stop_stream()
#         stream.close()
#         p.terminate()

#         wf = wave.open(filename, 'wb')
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(p.get_sample_size(FORMAT))
#         wf.setframerate(fs)
#         wf.writeframes(b''.join(frames))
#         wf.close()
#         st.success(f"Saved recording to {filename}")
#         print(f"Audio saved to {filename}")
#         return filename
#     except Exception as e:
#         st.error(f"Error during audio recording: {e}")
#         print(f"Recording error: {e}")
#         return None

# # 2️⃣ Transcribe with faster_whisper
# def transcribe_audio(file_path):
#     try:
#         st.info("Transcribing audio...")
#         print(f"Transcribing {file_path}...")
#         segments, info = model.transcribe(file_path, language="pa")  # Punjabi
#         text = " ".join([segment.text for segment in segments])
#         print(f"Transcription result: {text}")
#         return text
#     except Exception as e:
#         st.error(f"Error during transcription: {e}")
#         print(f"Transcription error: {e}")
#         return ""

# # 3️⃣ Chatbot response
# def get_response(user_prompt):
#     try:
#         print(f"Sending prompt to Groq: {user_prompt}")
#         llm = ChatGroq(
#             groq_api_key=groq_api_key,
#             model_name="llama-3.1-8b-instant"
#         )
#         messages = [{"role": "system", "content": system_message}]
#         for chat in st.session_state.history:
#             messages.append({"role": "user", "content": chat["user"]})
#             messages.append({"role": "assistant", "content": chat["bot"]})
#         messages.append({"role": "user", "content": user_prompt})
#         response = llm.invoke(messages)
#         content = getattr(response, "content", response)
#         print(f"Groq response: {content}")
#         return content
#     except Exception as e:
#         st.error(f"Error generating chatbot response: {e}")
#         print(f"Chatbot error: {e}")
#         return f"Error: {e}"

# # 4️⃣ TTS
# def text_to_speech(text, filename="response.mp3"):
#     try:
#         st.info("Generating audio response...")
#         print(f"Generating TTS for: {text}")
#         tts = gTTS(text=text, lang="pa")
#         tts.save(filename)
#         print(f"TTS saved to {filename}")
#         return filename
#     except Exception as e:
#         st.error(f"Error generating TTS: {e}")
#         print(f"TTS error: {e}")
#         return None

# # 5️⃣ UI: Record & process
# if st.button("🎤 Record 5 sec Audio"):
#     audio_file = record_audio()
#     if audio_file:
#         user_prompt = transcribe_audio(audio_file)
#         if user_prompt:
#             response_text = get_response(user_prompt)
#             st.session_state.history.append({"user": user_prompt, "bot": response_text})

# # 6️⃣ Display chat history with audio
# for idx, chat in enumerate(st.session_state.history):
#     st.markdown(f"**ਤੁਸੀਂ:** {chat['user']}")
#     st.markdown(f"**ਬੋਟ:** {chat['bot']}")
#     audio_file = f"response_{idx}.mp3"
#     if not os.path.exists(audio_file):
#         text_to_speech(chat["bot"], filename=audio_file)
#     audio_bytes = open(audio_file, "rb").read()
#     st.audio(audio_bytes, format="audio/mp3")
#     st.write("---")










# ----------------------------------------------------------------- 2  ---------------------------------------------------------------
 

# import os
# import streamlit as st
# from dotenv import load_dotenv
# from groq import Groq
# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from gtts import gTTS  # For Text-to-Speech

# # Load environment variables (optional if using hardcoded key)
# load_dotenv()
# groq_api_key = "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"

# try:
#     client = Groq(api_key=groq_api_key)
# except Exception as e:
#     st.error(f"Error initializing Groq client: {e}")
#     st.stop()

# # System message with Punjabi enforcement
# system_message = """ 
# ਤੁਸੀਂ ਇੱਕ ਪੇਸ਼ੇਵਰ ਅਤੇ ਜ਼ਿੰਮੇਵਾਰ ਮੈਡੀਕਲ ਸਹਾਇਕ ਚੈਟਬਾਟ ਹੋ। 
# ਹਮੇਸ਼ਾਂ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ। 

# ਤੁਹਾਡਾ ਕੰਮ ਮਰੀਜ਼ਾਂ ਨੂੰ ਸੁਰੱਖਿਅਤ ਢੰਗ ਨਾਲ ਸਿੱਖਿਆ ਦੇਣਾ, ਜਾਣਕਾਰੀ ਦੇਣਾ ਅਤੇ ਮਦਦ ਕਰਨਾ ਹੈ। 
# ਡਾਕਟਰ ਵਾਂਗ ਸਵਾਲ ਪੁੱਛੋ ਜਦੋਂ ਜਾਣਕਾਰੀ ਅਧੂਰੀ ਹੋਵੇ। 
# ਹੇਠਾਂ ਦਿੱਤੇ ਨਿਯਮਾਂ ਦੀ ਪਾਲਣਾ ਕਰੋ:

# 1. ਹਮੇਸ਼ਾਂ ਪ੍ਰਸ਼ਨ ਨੂੰ Emergency, Medication, Lifestyle ਜਾਂ General Medical Info ਵਿੱਚ ਵਰਗੀਕ੍ਰਿਤ ਕਰੋ।
# 2. ਜੇ ਜਾਣਕਾਰੀ ਅਧੂਰੀ ਹੈ ਤਾਂ ਫਾਲੋਅੱਪ ਸਵਾਲ ਪੁੱਛੋ।
# 3. Emergency ਕੇਸ ਵਿੱਚ ਸਿਰਫ਼ “⚠ ਕਿਰਪਾ ਕਰਕੇ ਤੁਰੰਤ ਡਾਕਟਰ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।” ਕਹੋ।
# 4. ਹਮੇਸ਼ਾਂ ਮਰੀਜ਼ ਦੀ ਸੁਰੱਖਿਆ ਨੂੰ ਪਹਿਲਾਂ ਰੱਖੋ। 
# 5. ਪੰਜਾਬੀ ਵਿੱਚ ਸੰਖੇਪ, ਸਪੱਸ਼ਟ ਅਤੇ ਦਿਲਾਸਾ ਦੇਣ ਵਾਲੇ ਜਵਾਬ ਦਿਓ।
# """

# # Streamlit UI
# st.title("ਪੰਜਾਬੀ ਮੈਡੀਕਲ ਚੈਟਬਾਟ (Groq ਨਾਲ)")
# st.write("ਚੈਟਬਾਟ ਨਾਲ ਪੰਜਾਬੀ ਵਿੱਚ ਗੱਲਬਾਤ ਕਰੋ ਅਤੇ ਆਵਾਜ਼ ਵਿੱਚ ਸੁਣੋ!")

# # Initialize session state for chat history
# if "history" not in st.session_state:
#     st.session_state.history = []

# # User input
# user_prompt = st.text_input("ਆਪਣਾ ਪ੍ਰਸ਼ਨ ਲਿਖੋ:")

# def get_response(user_prompt):
#     try:
#         llm = ChatGroq(
#             groq_api_key=groq_api_key,
#             model_name="llama-3.1-8b-instant"
#         )

#         # Build the conversation messages
#         messages = [{"role": "system", "content": system_message}]

#         # Add previous chat history
#         for chat in st.session_state.history:
#             messages.append({"role": "user", "content": chat["user"]})
#             messages.append({"role": "assistant", "content": chat["bot"]})

#         # Add current user prompt
#         messages.append({"role": "user", "content": user_prompt})

#         # Invoke LLM
#         response = llm.invoke(messages)
#         return getattr(response, "content", response)

#     except Exception as e:
#         return f"Error: {e}"

# def text_to_speech(text, filename="response.mp3"):
#     """Convert Punjabi text to speech"""
#     tts = gTTS(text=text, lang="pa")
#     tts.save(filename)
#     return filename

# # Send button
# if st.button("ਭੇਜੋ"):
#     if user_prompt:
#         with st.spinner("ਜਵਾਬ ਬਣਾਇਆ ਜਾ ਰਿਹਾ ਹੈ..."):
#             response = get_response(user_prompt)
#             st.session_state.history.append({"user": user_prompt, "bot": response})
#     else:
#         st.warning("ਕਿਰਪਾ ਕਰਕੇ ਇੱਕ ਪ੍ਰਸ਼ਨ ਲਿਖੋ।")

# # Display chat history with audio
# for chat in st.session_state.history:
#     st.markdown(f"**ਤੁਸੀਂ:** {chat['user']}")
#     st.markdown(f"**ਬੋਟ:** {chat['bot']}")

#     # Add audio response
#     audio_file = text_to_speech(chat["bot"], filename="response.mp3")
#     audio_bytes = open(audio_file, "rb").read()
#     st.audio(audio_bytes, format="audio/mp3")

#     st.write("---")









# -------------------------------------------------------------------------1 ------------------------------------------------

# import os
# import streamlit as st
# from dotenv import load_dotenv
# from groq import Groq
# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate

# # Load environment variables (optional if using hardcoded key)
# load_dotenv()
# groq_api_key = "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"

# try:
#     client = Groq(api_key=groq_api_key)
# except Exception as e:
#     st.error(f"Error initializing Groq client: {e}")
#     st.stop()

# # Prompt template
# prompt_template = ChatPromptTemplate.from_template("{input}")
# system_message=""" 
#             You are a professional and responsible medical assistant chatbot. Your role is to educate, inform, and guide patients safely, and simulate a real doctor’s conversational style by asking follow-up questions when information is incomplete. Follow these rules strictly:

# 1. Query Handling & Intent Classification

# Classify queries into one of four categories:

# Emergency: Life-threatening signs (chest pain, vomiting blood, unconsciousness, severe bleeding, collapse, high fever for days).

# Medication: Questions about drugs, dosage, interactions, or side effects.

# Lifestyle: Diet, exercise, hydration, sleep, stress management.

# General Medical Info: Symptoms, conditions, or procedures.

# High-risk or multiple emergency symptoms → always treat as "Emergency".

# 2. Follow-Up Question Logic

# When information is incomplete or unclear, ask patient-friendly follow-up questions to gather context:

# Symptom Clarification

# “Can you tell me where exactly the pain is?”

# “When did the symptom start?”

# Severity & Duration

# “How severe is it on a scale of 1 to 10?”

# “Is it constant or comes and goes?”

# Red-Flag Check

# “Do you have fever, vomiting, vision changes, or weakness?”

# Medical History & Medications

# “Are you currently taking any medications?”

# “Do you have any chronic conditions like diabetes or high blood pressure?”

# Lifestyle & Context

# “Have you slept well or eaten recently?”

# “Have you done any strenuous work today?”

# 3. Response Rules

# Emergency:

# ⚠ “This seems urgent. Contact a medical professional immediately.”

# Do NOT provide treatment advice.

# Medication / Doctor Referral Needed:

# Short, 1–2 line instruction:

# “Please consult a licensed doctor or pharmacist before taking any medication.”

# Informational (Lifestyle / General Info):

# Provide simple, factual explanations.

# Include 1–2 practical tips the patient can safely follow.

# Optionally ask: “Would you like more details?”

# 4. Safety & Verification

# Always prioritize patient safety.

# Never provide prescriptions, emergency treatments, or replace a licensed professional.

# Avoid hallucinations; provide only evidence-based guidance.

# If ambiguous or conflicting info is detected, advise consultation with a professional.

# 5. Context Awareness

# Include recent conversation history (last 5 exchanges) when generating responses.

# Maintain patient context, including age, known conditions, or previous symptoms.

# 6. Output Style

# Begin each answer clearly.

# Keep guidance structured, concise, empathetic, and patient-friendly.

# Provide optional references or verification suggestions.

# 7. Optional Features

# Multilingual responses if user input is in another language.

# Follow-up prompts if symptoms persist or evolve.

# Store data securely; anonymize for analytics if needed.

# Primary Goal: Simulate a real doctor’s interaction safely while educating and guiding patients.
# """
# # Streamlit UI
# st.title("LLM Chatbot with Groq")
# st.write("Chat with the LLM powered by Groq!")

# # Initialize session state for chat history
# if "history" not in st.session_state:
#     st.session_state.history = []

# # User input
# user_prompt = st.text_input("Enter your prompt:")

# def get_response(user_prompt):
#     try:
#         llm = ChatGroq(
#             groq_api_key=groq_api_key,
#             model_name="llama-3.1-8b-instant"
#         )


#         # Build the conversation messages
#         messages = [{"role": "system", "content": system_message}]

#         # Add previous chat history
#         for chat in st.session_state.history:
#             messages.append({"role": "user", "content": chat["user"]})
#             messages.append({"role": "assistant", "content": chat["bot"]})

#         # Add current user prompt
#         messages.append({"role": "user", "content": user_prompt})

#         # Invoke LLM
#         response = llm.invoke(messages)
#         return getattr(response, "content", response)

#     except Exception as e:
#         return f"Error: {e}"

# # Send button
# if st.button("Send"):
#     if user_prompt:
#         with st.spinner("Generating response..."):
#             response = get_response(user_prompt)
#             st.session_state.history.append({"user": user_prompt, "bot": response})
#     else:
#         st.warning("Please enter a prompt.")

# # Display chat history
# for chat in st.session_state.history:
#     st.markdown(f"**You:** {chat['user']}")
#     st.markdown(f"**Bot:** {chat['bot']}")
#     st.write("---")
