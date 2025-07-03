from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import streamlit as st
import os

# 🌐 Load environment variables
load_dotenv()

# 🔐 Set environment keys
api_key = os.getenv("OPENROUTER_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# 🧠 Setup memory
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

memory = st.session_state.memory

# 🧠 Setup prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please provide a helpful response to the user queries."),
    ("user", "{question}")
])

# 🖥️ Streamlit UI
st.title("🧠 Like-a-10: Smart Explainer Bot 🤖")

input_text = st.text_input("💬 Enter your question here:")
llm_mode = st.radio("🌐 Choose your mode:", ["🛰️ Online", "💻 Offline"], horizontal=True)

mode = st.radio("🎨 Choose Explanation Style:", [
    "💡 Default",
    "🧒 Child-Friendly",
    "📚 Examples Only",
    "🧠 Expert"
], horizontal=True)

# 🔗 Choose LLM
def get_llm(mode):
    if mode == "Online":
        return ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=api_key,
            model="mistralai/mistral-7b-instruct",
            temperature=0.8
        )
    else:
        return OllamaLLM(model="gemma3", model_kwargs={"num_predict": 150}, temperature=0.8)

# 🔄 Chain setup
llm = get_llm(llm_mode)
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# 📥 Handle input
if input_text:
    st.success("✅ Input received! Let's generate your answer...")

    with st.spinner("⏳ Thinking... Generating the best response for you..."):
        try:
            # 🧠 Modify based on mode
            if "Child-Friendly" in mode:
                modified_input = f"Explain '{input_text}' like I am 10 years old using real-life examples."
                st.subheader("🧒 Explaining like you're 10...")
            elif "Examples Only" in mode:
                modified_input = f"Explain '{input_text}' with examples only!"
                st.subheader("📚 Explaining using examples...")
            elif "Expert" in mode:
                modified_input = f"Explain '{input_text}' using technical and complex terminology."
                st.subheader("🧠 Explaining like a Pro...")
            else:
                modified_input = input_text
                st.subheader("💡 Standard Explanation")

            # 🚀 Call the chain
            response = chain.invoke({"question": modified_input})

            # Store in memory
            memory.chat_memory.add_user_message(modified_input)
            memory.chat_memory.add_ai_message(response)

            # Display response
            st.write(response)

        except Exception as e:
            st.error(f"⚠️ Something went wrong: {e}")

# 💬 Show conversation history
with st.expander("📜 Show Conversation History"):
    messages = memory.chat_memory.messages
    if messages:
        for i, msg in enumerate(messages):
            role = "👤 User" if msg.type == "human" else "🤖 Bot"
            st.markdown(f"**{role}:** {msg.content}")
    else:
        st.info("No conversation history yet.")
