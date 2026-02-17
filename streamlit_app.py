import streamlit as st
import requests
import json

st.set_page_config(page_title="Hustad AI Assistant", layout="wide")
st.title("Hustad AI Assistant")

# Put your n8n PROD webhook in Streamlit secrets
N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]

if "sessionId" not in st.session_state:
    st.session_state.sessionId = "test123"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    payload = {
        "message": prompt,
        "sessionId": st.session_state.sessionId,
        "userId": "aminul@hustadcompanies.com"
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()

            reply_obj = data.get("reply", data)
            # make it readable if it's a dict
            reply_text = reply_obj if isinstance(reply_obj, str) else json.dumps(reply_obj, indent=2)

            st.write(reply_text)
            st.session_state.messages.append({"role": "assistant", "content": reply_text})
