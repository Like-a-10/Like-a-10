import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os
import pyttsx3
import re
from pydub import AudioSegment
import pygame
import threading
import uuid

# Load environment variables
load_dotenv()
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Initialize pygame mixer
pygame.mixer.init()

# Cleanup markdown for smoother speech
def clean_markdown(text):
    text = re.sub(r"^\s*[\*\-•]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return text

# Generate TTS and save as audio file
def generate_tts(text, rate=150, voice_gender="Default"):
    global AUDIO_FILE
    AUDIO_FILE = f"tts_{uuid.uuid4().hex}.wav"  # unique name

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

# Play the audio file
def play_audio():
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()

# Stop playback
def stop_audio():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

# Langchain setup
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please provide a helpful response to the user queries."),
    ("user", "Question: {question}")
])
llm = OllamaLLM(model="gemma3", model_kwargs={"num_predict": 150}, temperature=0.8)
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Streamlit UI
st.set_page_config(page_title="Like-a-10", page_icon="🧠")
st.title("Like-a-10: Smart Explainer Bot")

input_text = st.text_input("Enter your question:")
mode = st.radio("Choose Explanation Style:", [
    "Default", "Child-Friendly", "Examples Only", "Expert"
])
rate = st.slider("Speaking Speed", min_value=100, max_value=250, value=150, step=10)
voice_choice = st.selectbox("Choose Voice", ["Default", "Male", "Female"])

if input_text:
    st.success("Input received!")

    with st.spinner("Generating explanation..."):
        if mode == "Child-Friendly":
            final_prompt = f"Explain '{input_text}' like I am 10 years old using real-life examples"
            subheading = "Explaining to a 10yr old..."
        elif mode == "Examples Only":
            final_prompt = f"Explain '{input_text}' with examples only!"
            subheading = "Explaining using examples..."
        elif mode == "Expert":
            final_prompt = f"Explain '{input_text}' using technical and complex terminology"
            subheading = "Explaining to an Expert..."
        else:
            final_prompt = input_text
            subheading = "Standard Explanation"

        response = chain.invoke({"question": final_prompt})
        st.subheader(subheading)
        st.write(response)

        col1, col2 = st.columns(2)
        if col1.button("🔊 Play Explanation"):
            generate_tts(response, rate, voice_choice)
            threading.Thread(target=play_audio).start()

        if col2.button("⏹️ Stop Explanation"):
            stop_audio()
