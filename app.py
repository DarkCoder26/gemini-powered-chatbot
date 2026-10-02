import os
import io
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error(
        "GEMINI_API_KEY was not found. "
        "Please add it to Streamlit Secrets or your local .env file."
    )
    st.stop()

# --------------------------------------------------
# Configure Gemini
# --------------------------------------------------
client = genai.Client(api_key=API_KEY)

# --------------------------------------------------
# Streamlit page configuration & Professional UI
# --------------------------------------------------
st.set_page_config(
    page_title="DarkCoder AI | Codex",
    page_icon="🤖",
    layout="wide"
)

# Inject custom CSS to clean up the UI
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stChatMessage { border-radius: 10px; padding: 15px; margin-bottom: 10px; }
        .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Codex AI Assistant")
st.caption("Advanced Voice & Text Chatbot by DarkCoder")

# --------------------------------------------------
# Initialize chat history
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# Display previous messages
# --------------------------------------------------
for message in st.session_state.messages:
    # Use "assistant" for Streamlit's built-in bot UI icon, "user" for human
    ui_role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(ui_role):
        st.markdown(message["content"])

# --------------------------------------------------
# User input (Text and Voice) - MOVED OUT OF SIDEBAR
# --------------------------------------------------
# Placed in a clean expander right above the chat input
with st.expander("🎤 Tap here to send a Voice Message"):
    audio_input = st.audio_input("Record a voice message")

text_input = st.chat_input("Type your message...")

user_prompt = None
audio_data = None

if text_input:
    user_prompt = text_input

if audio_input:
    user_prompt = "Please listen to this audio and reply."
    audio_data = audio_input.getvalue()

if user_prompt:
    # ----------------------------------------------
    # Display user message
    # ----------------------------------------------
    with st.chat_message("user"):
        if text_input:
            st.markdown(text_input)
        else:
            st.audio(audio_input)

    # ----------------------------------------------
    # Save user message to UI history
    # ----------------------------------------------
    st.session_state.messages.append({
        "role": "user",
        "content": text_input if text_input else "🎤 Voice Note"
    })

    # ----------------------------------------------
    # Convert Streamlit history to Gemini SDK format
    # ----------------------------------------------
    conversation = []
    for message in st.session_state.messages:
        conversation.append(
            types.Content(
                role=message["role"],
                parts=[types.Part.from_text(text=message["content"])]
            )
        )

    if audio_input:
        conversation.pop() 
        conversation.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=audio_data, mime_type='audio/wav'),
                    types.Part.from_text(text="Please listen to this audio and reply.")
                ]
            )
        )

    # ----------------------------------------------
    # Generate Gemini response & Audio Output
    # ----------------------------------------------
    with st.chat_message("assistant"):
        with st.spinner("Codex is thinking..."):
            try:
                # FIXED: Changed model to 1.5-flash to resolve the 404 error
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=conversation
                )
                ai_response = response.text
                
                st.markdown(ai_response)
                
                # Convert text response to voice
                tts = gTTS(text=ai_response, lang='en')
                audio_bytes_io = io.BytesIO()
                tts.write_to_fp(audio_bytes_io)
                
                # Autoplay the generated voice
                st.audio(audio_bytes_io.getvalue(), format="audio/mp3", autoplay=True)

            except Exception as e:
                ai_response = f"Sorry, I couldn't generate a response.\n\nError: `{str(e)}`"
                st.error(ai_response)

    # ----------------------------------------------
    # Save AI response
    # ----------------------------------------------
    st.session_state.messages.append({
        "role": "model",
        "content": ai_response
    })

    
