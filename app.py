import os
import io
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS

# --------------------------------------------------
# Page configuration - MUST BE FIRST STREAMLIT COMMAND
# --------------------------------------------------
st.set_page_config(
    page_title="DarkCoder AI | Codex",
    page_icon="🤖",
    layout="wide"
)

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

# Current stable Flash model
MODEL = "gemini-3.5-flash"

# --------------------------------------------------
# Professional UI
# --------------------------------------------------
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        .stChatMessage {
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Codex AI Assistant")
st.caption("Advanced Voice, Image & Text Chatbot by DarkCoder")

# --------------------------------------------------
# Initialize chat history
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# Display previous messages
# --------------------------------------------------
for message in st.session_state.messages:

    ui_role = "assistant" if message["role"] == "model" else "user"

    with st.chat_message(ui_role):

        # Display image if message contains one
        if message.get("image") is not None:
            st.image(message["image"], width="stretch")

        if message.get("content"):
            st.markdown(message["content"])

# --------------------------------------------------
# IMAGE UPLOAD
# --------------------------------------------------
st.subheader("🖼️ Image Upload (Optional)")

uploaded_file = st.file_uploader(
    "Upload an image to ask Gemini about it",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=False
)

uploaded_image = None

if uploaded_file:

    uploaded_image = uploaded_file.getvalue()

    st.image(
        uploaded_image,
        caption="Uploaded Image",
        width="stretch"
    )

    st.caption(
        "Image is attached to your next message."
    )

# --------------------------------------------------
# VOICE INPUT
# --------------------------------------------------
with st.expander("🎤 Tap here to send a Voice Message"):

    audio_input = st.audio_input(
        "Record a voice message"
    )

# --------------------------------------------------
# TEXT INPUT
# --------------------------------------------------
text_input = st.chat_input(
    "Type your message..."
)

# --------------------------------------------------
# Determine user input
# --------------------------------------------------
user_prompt = None
audio_data = None

if text_input:
    user_prompt = text_input

if audio_input:
    user_prompt = "Please listen to this audio and reply."
    audio_data = audio_input.getvalue()

# --------------------------------------------------
# If user sent something
# --------------------------------------------------
if user_prompt:

    # ------------------------------------------------
    # Display user message
    # ------------------------------------------------
    with st.chat_message("user"):

        if text_input:
            st.markdown(text_input)

        elif audio_input:
            st.audio(audio_input)

        if uploaded_image:
            st.image(
                uploaded_image,
                caption="Uploaded Image",
                width="stretch"
            )

    # ------------------------------------------------
    # Save user message
    # ------------------------------------------------
    st.session_state.messages.append({
        "role": "user",
        "content": (
            text_input
            if text_input
            else "🎤 Voice Note"
        ),
        "image": uploaded_image
    })

    # ------------------------------------------------
    # Build Gemini conversation
    # ------------------------------------------------
    conversation = []

    for message in st.session_state.messages:

        parts = []

        # Text
        if message.get("content"):
            parts.append(
                types.Part.from_text(
                    text=message["content"]
                )
            )

        # Image
        if message.get("image"):

            parts.append(
                types.Part.from_bytes(
                    data=message["image"],
                    mime_type="image/jpeg"
                )
            )

        conversation.append(
            types.Content(
                role=message["role"],
                parts=parts
            )
        )

    # ------------------------------------------------
    # Replace latest message with audio if needed
    # ------------------------------------------------
    if audio_input:

        conversation.pop()

        conversation.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(
                        data=audio_data,
                        mime_type="audio/wav"
                    ),
                    types.Part.from_text(
                        text="Please listen to this audio and reply."
                    )
                ]
            )
        )

    # ------------------------------------------------
    # Generate Gemini response
    # ------------------------------------------------
    with st.chat_message("assistant"):

        with st.spinner("Codex is thinking..."):

            try:

                response = client.models.generate_content(
                    model=MODEL,
                    contents=conversation
                )

                ai_response = response.text

                # ------------------------------------
                # Display AI response
                # ------------------------------------
                st.markdown(ai_response)

                # ------------------------------------
                # Text to Speech
                # ------------------------------------
                try:

                    tts = gTTS(
                        text=ai_response,
                        lang="en"
                    )

                    audio_bytes_io = io.BytesIO()

                    tts.write_to_fp(
                        audio_bytes_io
                    )

                    audio_bytes_io.seek(0)

                    st.audio(
                        audio_bytes_io.getvalue(),
                        format="audio/mp3",
                        autoplay=True
                    )

                except Exception as tts_error:

                    st.warning(
                        f"Voice output unavailable: {tts_error}"
                    )

            except Exception as e:

                ai_response = (
                    "Sorry, I couldn't generate a response.\n\n"
                    f"Error: `{str(e)}`"
                )

                st.error(ai_response)

    # ------------------------------------------------
    # Save AI response
    # ------------------------------------------------
    st.session_state.messages.append({
        "role": "model",
        "content": ai_response
    })
