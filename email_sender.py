import smtplib
from email.message import EmailMessage
import streamlit as st


def send_email(to_address, subject, body):
    gmail_address = st.secrets["GMAIL_ADDRESS"]
    gmail_app_password = st.secrets["GMAIL_APP_PASSWORD"]

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = gmail_address
    message["To"] = to_address
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.send_message(message)