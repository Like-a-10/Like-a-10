# like_a_10_combined.py

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os
import pyttsx3
import re
from pydub import AudioSegment
import pygame
import threading
import uuid

# 🌍 Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

# 🔊 Init pygame mixer
pygame.mixer.init()

# 🧹 Clean markdown text for TTS
def clean_markdown(text):
    text = re.sub(r"^\s*[\*\-•]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return text

# 🎤 Generate TTS
def generate_tts(text, rate=150, voice_gender="Default"):
    global AUDIO_FILE
    AUDIO_FILE = f"tts_{uuid.uuid4().hex}.wav"

    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('volume', 1.0)

    voices = engine.getProperty('voices')
    if voice_gender == "Male":
        for voice in voices:
            if "male" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
    elif voice_gender == "Female":
        for voice in voices:
            if "female" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

    cleaned = clean_markdown(text)
    engine.save_to_file(cleaned, "raw_tts.wav")
    engine.runAndWait()

    sound = AudioSegment.from_file("raw_tts.wav", format="wav")
    sound.export(AUDIO_FILE, format="wav")

# ▶️ Play TTS
def play_audio():
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()

# ⏹️ Stop TTS
def stop_audio():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

# ⚙️ LangChain setup
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please provide a helpful response to the user queries."),
    ("user", "Question: {question}")
])
output_parser = StrOutputParser()

def get_llm(mode):
    if mode == "🛰️ Online":
        return ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=api_key,
            model="mistralai/mistral-7b-instruct",
            temperature=0.8
        )
    else:
        return OllamaLLM(model="gemma3", model_kwargs={"num_predict": 150}, temperature=0.8)

# 🌐 Streamlit UI
st.set_page_config(page_title="Like-a-10", page_icon="🧠")
st.title("🧠 Like-a-10: Smart Explainer Bot 🤖")

input_text = st.text_input("💬 Enter your question here:")

llm_mode = st.radio("🌍 Choose Mode:", ["🛰️ Online", "💻 Offline"], horizontal=True)

mode = st.radio("🎨 Choose Explanation Style:", [
    "💡 Default", "🧒 Child-Friendly", "📚 Examples Only", "🧠 Expert"
], horizontal=True)

rate = st.slider("🎚️ Speaking Speed", min_value=100, max_value=250, value=150, step=10)
voice_choice = st.selectbox("🎤 Voice Choice", ["Default", "Male", "Female"])

if input_text:
    st.success("✅ Input received!")

    with st.spinner("⏳ Thinking... Generating the best response for you..."):
        if "Child-Friendly" in mode:
            final_prompt = f"Explain '{input_text}' like I am 10 years old using real-life examples."
            subheading = "🧒 Explaining like you're 10..."
        elif "Examples Only" in mode:
            final_prompt = f"Explain '{input_text}' with examples only!"
            subheading = "📚 Explaining using examples..."
        elif "Expert" in mode:
            final_prompt = f"Explain '{input_text}' using technical and complex terminology."
            subheading = "🧠 Explaining like a Pro..."
        else:
            final_prompt = input_text
            subheading = "💡 Standard Explanation"

        llm = get_llm(llm_mode)
        chain = prompt | llm | output_parser
        response = chain.invoke({"question": final_prompt})

        st.subheader(subheading)
        st.write(response)

        col1, col2 = st.columns(2)
        if col1.button("🔊 Play Explanation"):
            generate_tts(response, rate, voice_choice)
            threading.Thread(target=play_audio).start()

        if col2.button("⏹️ Stop Explanation"):
            stop_audio()
