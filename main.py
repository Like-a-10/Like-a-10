import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os
import pyttsx3
import re
import threading

# Load environment variables
load_dotenv()
langchain_key = os.getenv("LANGCHAIN_API_KEY")
if langchain_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Clean markdown formatting
def clean_markdown(text):
    text = re.sub(r"^\s*[\*\-•]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return text

# TTS using pyttsx3 (non-interruptible)
def speak_text_async(text, rate=150, voice_gender="Default"):
    def run_tts():
        cleaned = clean_markdown(text)
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('volume', 1.0)

        voices = engine.getProperty('voices')
        if voice_gender == "Male":
            for voice in voices:
                if "male" in voice.name.lower() or "male" in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
        elif voice_gender == "Female":
            for voice in voices:
                if "female" in voice.name.lower() or "female" in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break

        engine.say(cleaned)
        engine.runAndWait()

    threading.Thread(target=run_tts).start()

# LangChain pipeline
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
    "Default",
    "Child-Friendly",
    "Examples Only",
    "Expert"
])

# TTS controls
st.markdown("### Text-to-Speech Settings")
rate = st.slider("Speaking Speed", min_value=100, max_value=250, value=150, step=10)
voice_choice = st.selectbox("Choose Voice", ["Default", "Male", "Female"])

if input_text:
    st.success("Input received!")

    with st.spinner("Generating your results..."):
        if mode == "Child-Friendly":
            final_question = f"Explain '{input_text}' like I am 10 years old using real-life examples"
            subtitle = "Explaining to a 10yr old..."
        elif mode == "Examples Only":
            final_question = f"Explain '{input_text}' with examples only!"
            subtitle = "Explaining using examples..."
        elif mode == "Expert":
            final_question = f"Explain '{input_text}' using technical and complex terminology"
            subtitle = "Explaining to an Expert..."
        else:
            final_question = input_text
            subtitle = "Standard Explanation"

        response = chain.invoke({"question": final_question})
        st.subheader(subtitle)
        st.write(response)

        if st.button("Play Explanation"):
            st.toast("Speaking...")
            speak_text_async(response, rate=rate, voice_gender=voice_choice)
