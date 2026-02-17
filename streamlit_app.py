import streamlit as st
import requests
import json
import uuid
from datetime import datetime

# ---------------------------
# Page + Theme
# ---------------------------
st.set_page_config(page_title="Hustad AI Assistant", page_icon="🧠", layout="wide")

CUSTOM_CSS = """
<style>
/* Global */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }
[data-testid="stSidebar"] { background: rgba(20, 22, 28, 0.65); backdrop-filter: blur(8px); }
h1, h2, h3 { letter-spacing: -0.02em; }

/* Header */
.hustad-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-radius: 14px;
  background: linear-gradient(90deg, rgba(35,40,55,0.85), rgba(25,27,34,0.85));
  border: 1px solid rgba(255,255,255,0.08);
}
.hustad-badge {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 12px;
  color: rgba(255,255,255,0.82);
}

/* Cards */
.card {
  border-radius: 16px;
  padding: 16px 16px;
  background: rgba(22,24,30,0.85);
  border: 1px solid rgba(255,255,255,0.08);
}
.card-title {
  font-size: 14px;
  color: rgba(255,255,255,0.75);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
}
hr.soft {
  border: none;
  height: 1px;
  background: rgba(255,255,255,0.07);
  margin: 12px 0;
}

/* Chat box */
.chat-wrap {
  border-radius: 16px;
  background: rgba(18,20,26,0.75);
  border: 1px solid rgba(255,255,255,0.08);
  padding: 12px;

  /* ChatGPT-like behavior */
  height: 70vh;
  overflow-y: auto;
}

.small-muted { color: rgba(255,255,255,0.6); font-size: 12px; }
.kv {
  display: grid;
  grid-template-columns: 170px 1fr;
  gap: 8px 14px;
  margin-top: 6px;
}
.k { color: rgba(255,255,255,0.70); font-size: 13px; }
.v { color: rgba(255,255,255,0.92); font-size: 13px; }
.pill {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 12px;
  color: rgba(255,255,255,0.82);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------
# Config / Secrets
# ---------------------------
# Streamlit Cloud → Settings → Secrets:
# N8N_WEBHOOK_URL = "https://.../webhook/...."  (PRODUCTION url)
N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL", "").strip()

# ---------------------------
# Session State
# ---------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_debug" not in st.session_state:
    st.session_state.last_debug = None
if "prefill" not in st.session_state:
    st.session_state.prefill = ""

# ---------------------------
# Helpers
# ---------------------------
def safe_json(obj):
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)

def post_to_n8n(message: str, session_id: str, user_id: str):
    if not N8N_WEBHOOK_URL:
        raise RuntimeError("Missing N8N_WEBHOOK_URL in Streamlit secrets.")

    payload = {
        "message": message,
        "sessionId": session_id,
        "userId": user_id,
    }
    r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=120)

    # Keep debug
    st.session_state.last_debug = {
        "status_code": r.status_code,
        "request_url": N8N_WEBHOOK_URL,
        "payload": payload,
        "raw_text": r.text[:5000],
    }

    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"raw": r.text}

def normalize_reply(data: dict):
    """
    Expected n8n response:
      { reply: <obj/string>, sessionId: "...", userId: "..." }
    But handle variations safely.
    """
    reply = data.get("reply", data)

    # If n8n returns { "output": "..."} style
    if isinstance(reply, dict) and "output" in reply and len(reply.keys()) == 1:
        reply = reply["output"]

    # If reply is JSON in string form
    if isinstance(reply, str):
        try:
            return json.loads(reply)
        except Exception:
            return {"message": reply}

    return reply if isinstance(reply, dict) else {"message": str(reply)}

def render_capabilities():
    st.markdown(
        """
        <div class="card">
          <div class="card-title">This assistant can do</div>
          <ul style="margin:0; padding-left: 1.2rem; color: rgba(255,255,255,0.9); line-height: 1.5;">
            <li>Find company information (name / address / ID)</li>
            <li>Find property information (name / address / ID)</li>
            <li>Find ticket information (property, description, price, link) by ticket ID</li>
            <li>Find invoice for a ticket by ticket ID</li>
            <li>Show 5 most recent service / opportunity tickets (by property)</li>
            <li>Show all notes for a property</li>
            <li>Write executive summary report + draft client response (by property)</li>
            <li>Create service ticket in CenterPoint Connect (property + issue)</li>
            <li>Chat history per session (can reset)</li>
            <li>Check weather at a property / company</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_quick_actions():
    st.markdown('<div class="card"><div class="card-title">Quick actions</div>', unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("🏢 Find a property", use_container_width=True):
            st.session_state.prefill = "show property "
    with colB:
        if st.button("🎫 Check tickets", use_container_width=True):
            st.session_state.prefill = "show tickets for property "
    with colC:
        if st.button("🛠️ Create service ticket", use_container_width=True):
            st.session_state.prefill = "create service ticket for property  issue: "

    st.markdown('<hr class="soft"/>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧾 Find invoice (ticket id)", use_container_width=True):
            st.session_state.prefill = "show invoice for ticket "
    with c2:
        if st.button("📝 Exec summary (property)", use_container_width=True):
            st.session_state.prefill = "write executive summary for property "

    st.markdown("</div>", unsafe_allow_html=True)

def render_reply(reply_obj: dict):
    """
    Make output look clean instead of dumping JSON.
    Detect common shapes and present nicely.
    """
    if not isinstance(reply_obj, dict):
        st.markdown(str(reply_obj))
        return

    # Common simplest: {message: "..."}
    if set(reply_obj.keys()) <= {"message"}:
        st.markdown(reply_obj.get("message", ""))
        return

    title = reply_obj.get("title") or reply_obj.get("heading") or reply_obj.get("name")
    message = reply_obj.get("message") or reply_obj.get("summary")

    if title:
        st.markdown(f"### {title}")
    if message:
        st.markdown(message)

    # Render "fields" as key/value
    fields = reply_obj.get("fields")
    if isinstance(fields, dict) and fields:
        st.markdown('<div class="kv">', unsafe_allow_html=True)
        for k, v in fields.items():
            st.markdown(f'<div class="k">{k}</div><div class="v">{v}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Friendly compact view
        compact = {}
        for k, v in reply_obj.items():
            if k in ("raw", "data", "response", "output"):
                continue
            if isinstance(v, (dict, list)) and len(str(v)) > 300:
                continue
            compact[k] = v

        if compact and compact != reply_obj:
            st.markdown('<div class="kv">', unsafe_allow_html=True)
            for k, v in compact.items():
                st.markdown(f'<div class="k">{k}</div><div class="v">{v}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    link = reply_obj.get("link") or reply_obj.get("url")
    if link:
        st.markdown(f"**Link:** {link}")

# ---------------------------
# Sidebar (SaaS style)
# ---------------------------
with st.sidebar:
    st.markdown("## Hustad AI OS")
    st.markdown('<span class="pill">Internal Tool</span>', unsafe_allow_html=True)
    st.markdown('<hr class="soft"/>', unsafe_allow_html=True)

    user_id = st.text_input("User ID", value="aminul@hustadcompanies.com")
    st.markdown(
        f'<div class="small-muted">Session</div><div class="pill">{st.session_state.session_id}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<hr class="soft"/>', unsafe_allow_html=True)
    if st.button("🧹 New chat session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.last_debug = None
        st.session_state.prefill = ""
        st.rerun()

    st.markdown('<hr class="soft"/>', unsafe_allow_html=True)
    st.markdown("### Status")
    if N8N_WEBHOOK_URL:
        st.success("Connected to n8n webhook")
    else:
        st.warning("Missing N8N_WEBHOOK_URL (set in Streamlit Secrets)")

# ---------------------------
# Main Layout
# ---------------------------
st.markdown(
    f"""
    <div class="hustad-header">
      <div>
        <div style="font-size: 24px; font-weight: 700;">Enterprise Assistant</div>
        <div style="color: rgba(255,255,255,0.65); font-size: 13px;">
          AI Operating System for CenterPoint Connect • Tickets • Properties • Reports
        </div>
      </div>
      <div class="hustad-badge">🕒 {datetime.now().strftime("%b %d, %Y • %I:%M %p")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
left, right = st.columns([0.30, 0.70], gap="large")

with left:
    render_quick_actions()
    st.write("")
    render_capabilities()

with right:
    # Chat card wrapper
    st.markdown('<div class="card"><div class="card-title">Chat</div>', unsafe_allow_html=True)

    # Scrollable chat region
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    chat_area = st.container()
    st.markdown("</div>", unsafe_allow_html=True)

    # Debug expander (kept inside card)
    with st.expander("Debug / Raw response"):
        st.write("Last request/response:")
        st.code(safe_json(st.session_state.last_debug), language="json")

    st.markdown("</div>", unsafe_allow_html=True)  # close card

    # Render history INSIDE the chat box
    with chat_area:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if isinstance(msg.get("content"), dict):
                    render_reply(msg["content"])
                else:
                    st.markdown(msg.get("content", ""))

    # ChatGPT-style input (Streamlit's fixed input)
    prompt = st.chat_input("Message Hustad AI…", key="chat_input")

    # Prefill helper line (optional)
    if (not prompt) and st.session_state.prefill:
        st.markdown(
            f'<div class="small-muted">Suggested command: <span class="pill">{st.session_state.prefill}</span> (copy & paste)</div>',
            unsafe_allow_html=True
        )

    # IMPORTANT: Handle send here so reply renders INSIDE chat box, not below it
    if prompt:
        # Save + render user message immediately inside the chat box
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_area:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Call n8n + render assistant reply immediately inside the chat box
        with chat_area:
            with st.chat_message("assistant"):
                with st.spinner("Working…"):
                    try:
                        resp = post_to_n8n(prompt, st.session_state.session_id, user_id)
                        reply_obj = normalize_reply(resp)

                        # If huge payload, keep details in debug
                        if isinstance(reply_obj, dict) and len(str(reply_obj)) > 2000:
                            st.markdown("✅ Got the result. It’s a large payload — open **Debug / Raw response** to view full details.")
                        else:
                            render_reply(reply_obj)

                        st.session_state.messages.append({"role": "assistant", "content": reply_obj})

                    except Exception as e:
                        st.error(f"Request failed: {e}")
                        st.session_state.messages.append(
                            {"role": "assistant", "content": {"message": f"Request failed: {e}"}}
                        )
