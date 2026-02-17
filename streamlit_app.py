import streamlit as st
import requests
import json
import re
from typing import Any, Dict, Tuple

st.set_page_config(page_title="Hustad AI Assistant", layout="wide")
st.title("Hustad AI Assistant")

N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL", "")

if not N8N_WEBHOOK_URL:
    st.warning("Set N8N_WEBHOOK_URL in Streamlit Secrets.")
    st.stop()

# Session init
if "sessionId" not in st.session_state:
    st.session_state.sessionId = "test123"
if "messages" not in st.session_state:
    st.session_state.messages = []

def normalize_reply(payload: Any) -> Tuple[str, Dict[str, Any]]:
    """
    Returns (clean_text, raw_payload_dict)
    Handles cases:
    - {"message": "..."}
    - {"reply": {...}}
    - {"output": "giant string with embedded json"}
    - string responses
    """
    raw = payload if isinstance(payload, dict) else {"raw": payload}

    # 1) If n8n returns {"message": "..."} use that
    if isinstance(payload, dict) and isinstance(payload.get("message"), str) and payload["message"].strip():
        return payload["message"].strip(), raw

    # 2) If n8n returns {"reply": "..."} or {"reply": {...}}
    if isinstance(payload, dict) and "reply" in payload:
        r = payload["reply"]
        if isinstance(r, str) and r.strip():
            return r.strip(), raw
        if isinstance(r, dict):
            # pretty compact summary if it's router output
            if "Agent Name" in r and ("user input" in r or "user_input" in r):
                user_input = r.get("user_input", r.get("user input", ""))
                return f"Routed to: {r.get('Agent Name')}\nUser input: {user_input}", raw
            return json.dumps(r, indent=2), raw

    # 3) If n8n returns {"output": "..."} (common with agents)
    if isinstance(payload, dict) and isinstance(payload.get("output"), str):
        out = payload["output"]

        # If it already contains "Here is ..." keep only the human part before huge JSON objects
        # Heuristic: split before first '{"entityType"' or '"chosen":' or a big JSON blob
        cut_points = [
            out.find('{"entityType"'),
            out.find('"entityType"'),
            out.find('"chosen"'),
            out.find('{"chosen"'),
        ]
        cut_points = [p for p in cut_points if p != -1]
        if cut_points:
            out = out[: min(cut_points)].strip()

        # Also remove leading labels like: "Here is the information that you requested\n\n"
        out = re.sub(r"^\s*output\s*[:=]\s*", "", out, flags=re.IGNORECASE).strip()

        if out:
            return out, raw

    # 4) If the response is a string that itself is JSON, parse and retry
    if isinstance(payload, str):
        s = payload.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                parsed = json.loads(s)
                return normalize_reply(parsed)
            except Exception:
                pass
        return s, raw

    # Fallback
    return "I received a response, but couldn’t format it cleanly. See details below.", raw


# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "message": prompt,
        "sessionId": st.session_state.sessionId,
        "userId": "aminul@hustadcompanies.com",
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=120)
                # Don’t crash UI on non-200; show debug
                if resp.status_code != 200:
                    st.error(f"Backend error {resp.status_code}")
                    st.code(resp.text)
                    st.stop()

                data = resp.json()
                clean_text, raw = normalize_reply(data)

                st.markdown(clean_text)

                with st.expander("Debug / Raw response"):
                    st.json(raw)

                st.session_state.messages.append({"role": "assistant", "content": clean_text})

            except Exception as e:
                st.error(f"Request failed: {e}")
