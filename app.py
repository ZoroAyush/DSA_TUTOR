import streamlit as st
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Page Configuration 
st.set_page_config(page_title="DSA AI Tutor", page_icon="🧠", layout="centered")

# 2. Load API Key securely
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

st.title("🧠 Personal DSA Tutor")
st.caption("Ask for conceptual hints, time complexity analysis, or request a quiz on algorithms!")

if not API_KEY:
    st.error("Error: Could not find the API key. Please check your .env file.")
    st.stop()

# 3. Initialize the AI Client AND Chat Session in Streamlit State
# ---> THIS IS THE FIX: We now save the client so it doesn't close between reruns <---
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API_KEY)

if "chat_session" not in st.session_state:
    tutor_rules = """
    You are an expert, highly analytical Data Structures and Algorithms (DSA) tutor.
    Your goal is to help the user prepare for rigorous technical interviews.
    
    CRITICAL RULES:
    1. NEVER give the complete code or the direct answer right away.
    2. If the user is stuck, provide a conceptual hint or ask a guiding question.
    3. Focus heavily on time/space complexity and edge cases.
    4. Encourage the user to dry-run their logic and understand line-by-line execution.
    5. Keep your responses concise, readable, and well-formatted.
    """
    
    # Create the chat session using the saved client
    st.session_state.chat_session = st.session_state.client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=tutor_rules,
            temperature=0.3
        )
    )
    # List to store messages for the UI
    st.session_state.messages = []

# 4. Display the chat history on the screen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Get user input from the chat box at the bottom
user_input = st.chat_input("E.g., How do I detect a cycle in a linked list?")

if user_input:
    # Immediately show the user's message on screen
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send message to the AI and show the response
    with st.chat_message("assistant"):
        try:
            # We use a spinner so the user knows the AI is thinking
            with st.spinner("Analyzing logic..."):
                response = st.session_state.chat_session.send_message(user_input)
                st.markdown(response.text)
                # Save the response to the UI history
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Server error or traffic spike. Please wait a moment and try again. (Error: {e})")