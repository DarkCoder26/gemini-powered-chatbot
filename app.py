import os

import streamlit as st
from dotenv import load_dotenv
from google import genai


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error(
        "GEMINI_API_KEY was not found. "
        "Please add it to your .env file."
    )
    st.stop()


# --------------------------------------------------
# Configure Gemini
# --------------------------------------------------

client = genai.Client(api_key=API_KEY)


# --------------------------------------------------
# Streamlit page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("🤖 AI Chatbot")
st.caption("Chatbot powered by Gemini")


# --------------------------------------------------
# Initialize chat history
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# Display previous messages
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# User input
# --------------------------------------------------

user_input = st.chat_input("Type your message...")


if user_input:

    # ----------------------------------------------
    # Display user message
    # ----------------------------------------------

    with st.chat_message("user"):
        st.markdown(user_input)

    # ----------------------------------------------
    # Save user message
    # ----------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })


    # ----------------------------------------------
    # Convert Streamlit history to Gemini format
    # ----------------------------------------------

    conversation = []

    for message in st.session_state.messages:

        conversation.append({
            "role": message["role"],
            "parts": [
                {
                    "text": message["content"]
                }
            ]
        })


    # ----------------------------------------------
    # Generate Gemini response
    # ----------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=conversation
                )

                ai_response = response.text

            except Exception as e:

                ai_response = (
                    "Sorry, I couldn't generate a response.\n\n"
                    f"Error: `{str(e)}`"
                )

        st.markdown(ai_response)


    # ----------------------------------------------
    # Save AI response
    # ----------------------------------------------

    st.session_state.messages.append({
        "role": "model",
        "content": ai_response
    })
