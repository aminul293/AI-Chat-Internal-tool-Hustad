import streamlit as st
import requests
import json
import uuid
from datetime import datetime

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Hustad AI • Operating System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Dark Neon Cyber SaaS CSS
# ---------------------------
CUSTOM_CSS = """
<style>
/* --- Global layout --- */
.block-container { padding-top: 0.9rem; padding-bottom: 1.2rem; max-width: 1600px; }
section[data-testid="stSidebar"] { background: rgba(10, 12, 18, 0.72) !important; backdrop-filter: blur(12px); }
[data-testid="stSidebar"] .stButton>button { border-radius: 12px; }

/* Hide Streamlit default menu/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* --- Background glow --- */
.stApp {
  background:
    radial-gradient(800px 450px at 20% 10%, rgba(120, 80, 255, 0.22), transparent 60%),
    radial-gradient(700px 420px at 80% 20%, rgba(0, 200, 255, 0.18), transparent 55%),
    radial-gradient(900px 520px at 55% 90%, rgba(0, 255, 170, 0.10), transparent 60%),
    linear-gradient(180deg, rgba(8,10,16,1) 0%, rgba(7,9,14,1) 100%);
}

/* --- Top bar --- */
.topbar {
  display:flex; justify-content:space-between; align-items:center;
  padding: 14px 18px;
  border-radius: 18px;
  background: rgba(16, 18, 26, 0.65);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.brand {
  display:flex; gap:12px; align-items:center;
}
.logo {
  width:34px; height:34px; border-radius: 12px;
  background: linear-gradient(135deg, rgba(120,80,255,1), rgba(0,200,255,1));
  box-shadow: 0 10px 25px rgba(120,80,255,0.25);
}
.brand-title { font-size: 18px; font-weight: 700; color: rgba(255,255,255,0.92); }
.brand-sub { font-size: 12px; color: rgba(255,255,255,0.55); margin-top:-2px; }
.badges { display:flex; gap:10px; align-items:center; }
.badge {
  display:inline-flex; gap:8px; align-items:center;
  padding: 6px 10px; border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  font-size: 12px;
  color: rgba(255,255,255,0.80);
}
.dot { width:8px; height:8px; border-radius:50%; background: #2dff9d; box-shadow: 0 0 12px rgba(45,255,157,0.35); }
.dot-warn { background:#ffcc66; box-shadow: 0 0 12px rgba(255,204,102,0.35); }

/* --- Cards --- */
.card {
  border-radius: 18px;
  padding: 14px 14px;
  background: rgba(16, 18, 26, 0.62);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 10px 30px rgba(0,0,0,0.22);
}
.card-title {
  font-size: 12px;
  color: rgba(255,255,255,0.62);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  margin-bottom: 10px;
}
.soft-hr { border:none; height:1px; background: rgba(255,255,255,0.08); margin: 10px 0; }

/* --- Pills / Buttons --- */
.pill {
  display:inline-flex; align-items:center; gap:8px;
  padding: 6px 10px; border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  font-size: 12px; color: rgba(255,255,255,0.78);
}

/* --- Chat area --- */
.chat-shell {
  border-radius: 18px;
  background: rgba(12, 14, 20, 0.62);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 10px 30px rgba(0,0,0,0.22);
  padding: 14px;
  min-height: 70vh;
}
.chat-hint { color: rgba(255,255,255,0.55); font-size: 12px; }

/* Make chat messages wider & cleaner */
[data-testid="stChatMessage"] { padding: 10px 8px; }
[data-testid="stChatMessageContent"] {
  border-radius: 16px !important;
  padding: 12px 14px !important;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(18, 20, 28, 0.75);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
  font-size: 14px;
  line-height: 1.55;
}

/* Differentiate user vs assistant */
[data-testid="stChatMessage"][aria-label="chat message user"] [data-testid="stChatMessageContent"]{
  background: linear-gradient(135deg, rgba(120,80,255,0.18), rgba(0,200,255,0.10));
  border: 1px solid rgba(120,80,255,0.20);
}
[data-testid="stChatMessage"][aria-label="chat message assistant"] [data-testid="stChatMessageContent"]{
  background: rgba(18, 20, 28, 0.78);
}

/* --- KV grid --- */
.kv {
  display:grid;
  grid-template-columns: 170px 1fr;
  gap: 8px 14px;
  margin-top: 8px;
}
.k { color: rgba(255,255,255,0.62); font-size: 12px; }
.v { color: rgba(255,255,255,0.92); font-size: 13px; }

/* --- Context dock --- */
.dock {
  border-radius: 18px;
  background: rgba(16, 18, 26, 0.62);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 10px 30px rgba(0,0,0,0.22);
  padding: 14px;
  position: sticky;
  top: 12px;
}
.dock-title {
  display:flex; justify-content:space-between; align-items:center;
}
.dock-title h3 { margin:0; font-size: 14px; color: rgba(255,255,255,0.88); }
.small { font-size: 12px; color: rgba(255,255,255,0.55); }
.link-btn a { color: rgba(0, 200, 255, 0.95); text-decoration: none; }
.link-btn a:hover { text-decoration: underline; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------
# Secrets / Config
# ---------------------------
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
if "context" not in st.session_state:
    # right-dock context derived from last assistant reply
    st.session_state.context = {
        "title": "Nothing yet",
        "subtitle": "Ask about a property, ticket, or company.",
        "fields": {},
        "link": None,
        "raw": None,
    }

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
    payload = {"message": message, "sessionId": session_id, "userId": user_id}
    r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=120)

    st.session_state.last_debug = {
        "status_code": r.status_code,
        "request_url": N8N_WEBHOOK_URL,
        "payload": payload,
        "raw_text": r.text[:6000],
    }

    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"raw": r.text}

def normalize_reply(data: dict):
    reply = data.get("reply", data)
    if isinstance(reply, dict) and "output" in reply and len(reply.keys()) == 1:
        reply = reply["output"]
    if isinstance(reply, str):
        # if JSON string, parse it
        try:
            return json.loads(reply)
        except Exception:
            return {"message": reply}
    return reply if isinstance(reply, dict) else {"message": str(reply)}

def extract_context(reply_obj: dict):
    """
    Update right dock based on last assistant reply.
    Works with:
      - {message:"..."}
      - {title, message, fields:{}, link}
      - raw CPC objects: tries to pick a few meaningful keys
    """
    ctx = {"title": "Result", "subtitle": "", "fields": {}, "link": None, "raw": reply_obj}

    # Friendly structured format
    title = reply_obj.get("title") or reply_obj.get("heading") or reply_obj.get("name")
    msg = reply_obj.get("message") or reply_obj.get("summary") or ""
    fields = reply_obj.get("fields") if isinstance(reply_obj.get("fields"), dict) else None
    link = reply_obj.get("link") or reply_obj.get("url")

    if title:
        ctx["title"] = str(title)
    ctx["subtitle"] = (msg[:140] + "…") if len(msg) > 140 else msg

    if fields:
        # show top fields
        ctx["fields"] = {k: str(v) for k, v in list(fields.items())[:10]}
    else:
        # try to pick useful keys from raw
        preferred_keys = ["entityType", "id", "name", "address", "status", "priority", "total", "price"]
        picked = {}
        for k in preferred_keys:
            if k in reply_obj and reply_obj[k] is not None:
                picked[k] = reply_obj[k]
        # pick a few more small scalars
        for k, v in reply_obj.items():
            if k in picked or k in ("raw", "data", "response", "output"):
                continue
            if isinstance(v, (str, int, float, bool)) and len(str(v)) <= 80:
                picked[k] = v
            if len(picked) >= 10:
                break
        ctx["fields"] = {k: str(v) for k, v in picked.items()} if picked else {}

    ctx["link"] = link
    st.session_state.context = ctx

def render_reply(reply_obj: dict):
    """
    Clean, ChatGPT-like: show message + structured KV (if present).
    """
    msg = reply_obj.get("message") or reply_obj.get("summary")
    title = reply_obj.get("title") or reply_obj.get("heading")
    fields = reply_obj.get("fields") if isinstance(reply_obj.get("fields"), dict) else None
    link = reply_obj.get("link") or reply_obj.get("url")

    if title:
        st.markdown(f"**{title}**")
    if msg:
        st.markdown(msg)

    if fields:
        st.markdown('<div class="kv">', unsafe_allow_html=True)
        for k, v in fields.items():
            st.markdown(f'<div class="k">{k}</div><div class="v">{v}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if link:
        st.markdown(f"🔗 {link}")

# ---------------------------
# Sidebar (OS Navigation)
# ---------------------------
with st.sidebar:
    st.markdown("### Hustad AI OS")
    st.caption("Internal tool • Cyber SaaS mode")

    user_id = st.text_input("User ID", value="aminul@hustadcompanies.com")

    connected = bool(N8N_WEBHOOK_URL)
    status_dot = "dot" if connected else "dot-warn"
    status_text = "Connected to n8n" if connected else "Missing N8N_WEBHOOK_URL"
    st.markdown(
        f'<div class="badge"><span class="{status_dot}"></span>{status_text}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<hr class="soft-hr"/>', unsafe_allow_html=True)

    if st.button("＋ New Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.last_debug = None
        st.session_state.prefill = ""
        st.session_state.context = {
            "title": "Nothing yet",
            "subtitle": "Ask about a property, ticket, or company.",
            "fields": {},
            "link": None,
            "raw": None,
        }
        st.rerun()

    st.markdown('<div class="pill">Session</div>', unsafe_allow_html=True)
    st.code(st.session_state.session_id, language="text")

    st.markdown('<hr class="soft-hr"/>', unsafe_allow_html=True)
    st.markdown("#### Quick actions")

    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("🏢 Property", use_container_width=True):
            st.session_state.prefill = "show property "
    with qa2:
        if st.button("🎫 Tickets", use_container_width=True):
            st.session_state.prefill = "show tickets for property "
    with qa3:
        if st.button("🛠️ Create", use_container_width=True):
            st.session_state.prefill = "create service ticket for property  issue: "

    qa4, qa5 = st.columns(2)
    with qa4:
        if st.button("🧾 Invoice", use_container_width=True):
            st.session_state.prefill = "show invoice for ticket "
    with qa5:
        if st.button("📝 Summary", use_container_width=True):
            st.session_state.prefill = "write executive summary for property "

    st.markdown('<hr class="soft-hr"/>', unsafe_allow_html=True)
    with st.expander("Debug / Last request"):
        st.code(safe_json(st.session_state.last_debug), language="json")

# ---------------------------
# Top Bar
# ---------------------------
now_str = datetime.now().strftime("%b %d, %Y • %I:%M %p")
env = "PROD"  # change if you want
env_badge = f"🟢 {env}" if connected else f"🟠 {env}"

st.markdown(
    f"""
    <div class="topbar">
      <div class="brand">
        <div class="logo"></div>
        <div>
          <div class="brand-title">Enterprise Assistant</div>
          <div class="brand-sub">AI Operating System for CenterPoint Connect • Tickets • Properties • Reports</div>
        </div>
      </div>
      <div class="badges">
        <div class="badge">{env_badge}</div>
        <div class="badge">🕒 {now_str}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---------------------------
# Main 3-Panel OS Layout
# ---------------------------
col_chat, col_dock = st.columns([0.72, 0.28], gap="large")

with col_chat:
    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
    st.markdown('<div class="chat-hint">Tip: Use the quick actions on the left, or type “show property …”</div>', unsafe_allow_html=True)
    st.markdown('<hr class="soft-hr"/>', unsafe_allow_html=True)

    # Render conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            content = msg.get("content")
            if isinstance(content, dict):
                render_reply(content)
            else:
                st.markdown(str(content))

    # Prefill helper
    if st.session_state.prefill:
        st.markdown(
            f'<div class="chat-hint">Suggested command: <span class="pill">{st.session_state.prefill}</span></div>',
            unsafe_allow_html=True
        )

    prompt = st.chat_input("Message Hustad AI…")

    st.markdown("</div>", unsafe_allow_html=True)

with col_dock:
    ctx = st.session_state.context

    st.markdown('<div class="dock">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="dock-title">
          <h3>Context Dock</h3>
          <span class="small">Live</span>
        </div>
        <div class="soft-hr"></div>
        <div style="font-weight:700; color: rgba(255,255,255,0.92);">{ctx.get("title","")}</div>
        <div class="small" style="margin-top:6px;">{ctx.get("subtitle","")}</div>
        """,
        unsafe_allow_html=True
    )

    if ctx.get("fields"):
        st.markdown('<div class="kv">', unsafe_allow_html=True)
        for k, v in ctx["fields"].items():
            st.markdown(f'<div class="k">{k}</div><div class="v">{v}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if ctx.get("link"):
        st.markdown(f'<div class="soft-hr"></div><div class="link-btn">🔗 <a href="{ctx["link"]}" target="_blank">Open in CenterPoint</a></div>', unsafe_allow_html=True)

    with st.expander("Raw object (for dev)"):
        st.code(safe_json(ctx.get("raw")), language="json")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Handle send
# ---------------------------
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                resp = post_to_n8n(prompt, st.session_state.session_id, user_id)
                reply_obj = normalize_reply(resp)

                # Update right dock context
                if isinstance(reply_obj, dict):
                    extract_context(reply_obj)

                # Render in chat
                if isinstance(reply_obj, dict) and len(str(reply_obj)) > 5000:
                    st.markdown("✅ Got the result. It’s a large payload — check **Context Dock → Raw object**.")
                    st.session_state.messages.append({"role": "assistant", "content": {"message": "✅ Got the result. It’s a large payload — check Context Dock → Raw object."}})
                else:
                    if isinstance(reply_obj, dict):
                        render_reply(reply_obj)
                    else:
                        st.markdown(str(reply_obj))
                    st.session_state.messages.append({"role": "assistant", "content": reply_obj})

            except Exception as e:
                st.error(f"Request failed: {e}")
                st.session_state.messages.append({"role": "assistant", "content": {"message": f"Request failed: {e}"}})
