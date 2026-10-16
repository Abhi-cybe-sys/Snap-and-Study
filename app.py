import time
from google.genai.errors import ServerError, ClientError
import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)
from email_sender import send_email


MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="centered",
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    message = {
        "role": role,
        "kind": kind,
        "content": content,
    }
    st.session_state.messages.append(message)
    render_message(message)



def ask_gemini(parts):
    for attempt in range(3):
        try:
            response = st.session_state.chat.send_message(parts)

            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")

            return response.text

        except ClientError as error:
            error_message = str(error)

            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                return (
                    "⚠️ Gemini API quota exceeded. Your Snap & Study app "
                    "is running, but Gemini has reached its request limit. "
                    "Please wait until your quota resets, or check your "
                    "Gemini API quota and billing settings. Do not keep "
                    "retrying right now."
                )

            print(f"Gemini client error: {error}")
            return "Gemini could not process your request. Check the terminal for details."

        except ServerError as error:
            print(f"Gemini server error (attempt {attempt + 1}/3): {error}")

            if attempt == 2:
                return "Gemini is still unavailable. Please try again later."

            time.sleep(2 ** (attempt + 1))





# ONBOARDING
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Snap a question. Understand it. Save your notes.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        email_address = st.text_input(
            "Your email address",
            placeholder="student@example.com",
        )
        submitted = st.form_submit_button("Start learning 🚀")

    if submitted:
        if not name.strip() or not email_address.strip():
            st.warning("Please enter your name and email address.")

        elif (
            "@" not in email_address
            or "." not in email_address.rsplit("@", 1)[-1]
        ):
            st.warning("Please enter a valid-looking email address.")

        else:
            try:
                chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )

                st.session_state.name = name.strip()
                st.session_state.email_address = email_address.strip()
                st.session_state.chat = chat
                st.session_state.messages = []
                st.session_state.onboarded = True

                st.rerun()

            except Exception as error:
                st.error(f"Could not start the study session: {error}")

    st.stop()


# MAIN HEADER
header_col, button_col = st.columns(
    [5, 3],
    vertical_alignment="center",
)

with header_col:
    st.title("📚 Snap & Study")

with button_col:
    if st.button(
        "📧 Send Study Notes",
        use_container_width=True,
        disabled=len(st.session_state.messages) < 2,
    ):
        try:
            with st.spinner("Preparing your study notes..."):
                summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

            with st.spinner("Sending your email..."):
                send_email(
                    to_address=st.session_state.email_address,
                    subject="Your Snap & Study Revision Notes",
                    body=summary,
                )

            st.success(
                f"Study notes sent to {st.session_state.email_address}!"
            )

        except Exception as error:
            st.error(f"Could not prepare or send your notes: {error}")


st.caption(
    f"Student: {st.session_state.name} | "
    f"Email: {st.session_state.email_address}"
)

st.divider()


# DISPLAY CHAT HISTORY
if not st.session_state.messages:
    welcome = WELCOME_MESSAGE_TEMPLATE.format(
        name=st.session_state.name
    )
    add_message("assistant", "text", welcome)
else:
    for message in st.session_state.messages:
        render_message(message)


# QUESTION AND PHOTO INPUT
user_input = st.chat_input(
    "Ask a question or upload a study photo...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = (user_input.text or "").strip()

    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()

        add_message("user", "image", photo_bytes)

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)

    elif photo is not None:
        parts.append(
            "Explain this question or study material step by step."
        )

    if parts:
        try:
            with st.spinner("Your AI tutor is thinking..."):
                answer = ask_gemini(parts)

            add_message("assistant", "text", answer)

        except Exception as error:
            st.error(f"Gemini could not process your request: {error}")