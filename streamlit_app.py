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
:root{
  --bg:#0b1220;
  --panel: rgba(17, 24, 39, 0.72);
  --panel2: rgba(17, 24, 39, 0.50);
  --border: rgba(255,255,255,0.10);
  --text: rgba(255,255,255,0.92);
  --muted: rgba(255,255,255,0.65);
  --accent: #60a5fa;   /* blue */
  --accent2:#a78bfa;   /* purple */
  --good:#22c55e;
  --warn:#f59e0b;
}

html, body, [data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1200px 800px at 18% 0%, rgba(96,165,250,0.22), transparent 55%),
    radial-gradient(900px 700px at 88% 0%, rgba(167,139,250,0.20), transparent 55%),
    radial-gradient(1000px 700px at 50% 100%, rgba(34,197,94,0.10), transparent 60%),
    var(--bg);
  color: var(--text);
}

.block-container{
  padding-top: 0.9rem !important;
  padding-bottom: 1.2rem !important;
  max-width: 1700px !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(15,23,42,0.92), rgba(2,6,23,0.92));
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container{ padding-top: 1.1rem; }

.sidebar-title{
  display:flex; gap:10px; align-items:center;
  font-weight: 800; font-size: 14px;
  color: var(--text);
}
.logo-dot{
  width:28px; height:28px; border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  box-shadow: 0 10px 28px rgba(96,165,250,0.22);
}
.small-muted{ color: var(--muted); font-size: 12px; }
.divider{ height:1px; background: rgba(255,255,255,0.08); margin: 12px 0; border: none; }

/* Topbar */
.topbar{
  display:flex; justify-content:space-between; align-items:center;
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(90deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.10);
}
.topbar h2{ margin: 0; font-size: 16px; font-weight: 800; }
.status-pill{
  display:inline-flex; gap:8px; align-items:center;
  padding: 6px 10px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  font-size: 12px; color: var(--muted);
}
.dot{
  width:8px; height:8px; border-radius:999px; background: var(--good);
  box-shadow: 0 0 0 4px rgba(34,197,94,0.12);
}

/* Cards */
.card{
  border-radius: 16px;
  padding: 14px 14px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
}
.card-title{
  color: rgba(255,255,255,0.75);
  font-size: 12px;
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.pill{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  font-size: 12px;
  color: rgba(255,255,255,0.78);
}

/* Buttons */
.stButton>button{
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  background: rgba(255,255,255,0.06) !important;
  color: var(--text) !important;
  padding: 0.7rem 0.9rem !important;
  transition: all 0.15s ease !important;
}
.stButton>button:hover{
  transform: translateY(-1px);
  border-color: rgba(96,165,250,0.45) !important;
  box-shadow: 0 12px 26px rgba(96,165,250,0.18);
}

/* Chat shell */
.chat-shell{
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(2, 6, 23, 0.35);
  padding: 12px 14px;
  min-height: 70vh;
}

/* Chat bubbles */
.bubble{
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.06);
}
.bubble.user{
  background: linear-gradient(135deg, rgba(96,165,250,0.18), rgba(167,139,250,0.12));
  border-color: rgba(96,165,250,0.25);
}
.bubble.assistant{
  background: rgba(255,255,255,0.06);
}
.kv{
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 8px 14px;
  margin-top: 10px;
}
.k{ color: rgba(255,255,255,0.70); font-size: 13px; }
.v{ color: rgba(255,255,255,0.92); font-size: 13px; }

/* Composer */
.composer{
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.05);
  padding: 12px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------
# Config / Secrets
# ---------------------------
N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL", "").strip()

# ---------------------------
# Session State (SaaS-style sessions)
# ---------------------------
def _new_session():
    return {
        "id": str(uuid.uuid4()),
        "title": "New session",
        "messages": [],
        "last_debug": None,
        "created": datetime.now().isoformat(),
    }

if "sessions" not in st.session_state:
    st.session_state.sessions = [_new_session()]
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = st.session_state.sessions[0]["id"]
if "draft" not in st.session_state:
    st.session_state.draft = ""

def get_active_session():
    for s in st.session_state.sessions:
        if s["id"] == st.session_state.active_session_id:
            return s
    # fallback
    st.session_state.sessions.insert(0, _new_session())
    st.session_state.active_session_id = st.session_state.sessions[0]["id"]
    return st.session_state.sessions[0]

active = get_active_session()

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

    debug = {
        "status_code": r.status_code,
        "request_url": N8N_WEBHOOK_URL,
        "payload": payload,
        "raw_text": r.text[:8000],
    }
    active["last_debug"] = debug

    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"raw": r.text}

def normalize_reply(data: dict):
    reply = data.get("reply", data)
    if isinstance(reply, dict) and "output" in reply and len(reply.keys()) == 1:
        reply = reply["output"]

    # string -> maybe json
    if isinstance(reply, str):
        try:
            return json.loads(reply)
        except Exception:
            return {"message": reply}

    return reply if isinstance(reply, dict) else {"message": str(reply)}

def infer_session_title_from_prompt(prompt: str) -> str:
    p = (prompt or "").strip()
    if not p:
        return "New session"
    # short title
    p = p.replace("\n", " ")
    return (p[:40] + "…") if len(p) > 40 else p

def render_capabilities_card():
    st.markdown(
        """
        <div class="card">
          <div class="card-title">Capabilities</div>
          <div style="color: rgba(255,255,255,0.88); line-height:1.7;">
            <ul style="margin:0; padding-left: 1.2rem;">
              <li>Find company / property info (name / address / ID)</li>
              <li>Ticket details & invoice lookup (by ticket ID)</li>
              <li>5 most recent service / opportunity tickets (by property)</li>
              <li>All notes from a property</li>
              <li>Executive summary + client draft response</li>
              <li>Create service ticket in CenterPoint Connect</li>
              <li>Weather at property/company</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def set_draft(text: str):
    st.session_state.draft = text

def render_quick_actions():
    st.markdown('<div class="card"><div class="card-title">Quick actions</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏢 Find a property", use_container_width=True):
            set_draft("show property ")
    with c2:
        if st.button("🎫 Check tickets", use_container_width=True):
            set_draft("show tickets for property ")
    with c3:
        if st.button("🛠️ Create service ticket", use_container_width=True):
            set_draft("create service ticket for property  issue: ")

    c4, c5 = st.columns(2)
    with c4:
        if st.button("🧾 Find invoice (ticket id)", use_container_width=True):
            set_draft("show invoice for ticket ")
    with c5:
        if st.button("📝 Exec summary (property)", use_container_width=True):
            set_draft("write executive summary for property ")

    st.markdown("</div>", unsafe_allow_html=True)

def render_reply(reply_obj: dict):
    """
    Cleaner rendering:
    - If {message} => markdown
    - If title/fields/link => nice card style
    - Otherwise show compact summary + raw expander
    """
    if not isinstance(reply_obj, dict):
        st.markdown(str(reply_obj))
        return

    # 1) simplest
    if set(reply_obj.keys()) <= {"message"}:
        st.markdown(reply_obj.get("message", ""))
        return

    title = reply_obj.get("title") or reply_obj.get("heading") or reply_obj.get("name")
    message = reply_obj.get("message") or reply_obj.get("summary")
    fields = reply_obj.get("fields") if isinstance(reply_obj.get("fields"), dict) else None
    link = reply_obj.get("link") or reply_obj.get("url")

    if title:
        st.markdown(f"**{title}**")
    if message:
        st.markdown(message)

    if fields:
        st.markdown('<div class="kv">', unsafe_allow_html=True)
        for k, v in fields.items():
            st.markdown(f'<div class="k">{k}</div><div class="v">{v}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Compact fallback (skip huge nested blobs)
    if not fields:
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

    if link:
        st.markdown(f"🔗 **Open:** {link}")

    # Always offer raw view
    with st.expander("Raw payload"):
        st.code(safe_json(reply_obj), language="json")

# ---------------------------
# Sidebar (SaaS Nav)
# ---------------------------
with st.sidebar:
    st.markdown(
        '<div class="sidebar-title"><span class="logo-dot"></span> Hustad Companies</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="small-muted">Internal Enterprise Assistant</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

    user_id = st.text_input("User ID", value="aminul@hustadcompanies.com")
    st.markdown('<div class="small-muted">Status</div>', unsafe_allow_html=True)
    if N8N_WEBHOOK_URL:
        st.markdown('<span class="pill">🟢 Connected to n8n</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill">🟠 Missing N8N_WEBHOOK_URL</span>', unsafe_allow_html=True)

    st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

    if st.button("＋ New Session", use_container_width=True):
        s = _new_session()
        st.session_state.sessions.insert(0, s)
        st.session_state.active_session_id = s["id"]
        st.session_state.draft = ""
        st.rerun()

    st.markdown('<div class="small-muted" style="margin-top:10px;">RECENT CONTEXT</div>', unsafe_allow_html=True)
    for s in st.session_state.sessions[:8]:
        label = s["title"] if s["title"] else "New session"
        if st.button(label, use_container_width=True, key=f"session_{s['id']}"):
            st.session_state.active_session_id = s["id"]
            st.session_state.draft = ""
            st.rerun()

    st.markdown('<hr class="divider"/>', unsafe_allow_html=True)
    with st.expander("Tools"):
        render_quick_actions()
        st.write("")
        render_capabilities_card()

# ---------------------------
# Main Topbar
# ---------------------------
st.markdown(
    f"""
    <div class="topbar">
      <div>
        <h2>Enterprise Assistant</h2>
        <div class="small-muted">Ask about properties, tickets, invoices, summaries, and service ticket creation.</div>
      </div>
      <div class="status-pill">
        <span class="dot"></span>
        {datetime.now().strftime("%b %d, %Y • %I:%M %p")}
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.write("")

# ---------------------------
# Main Chat Area (Full width like SaaS)
# ---------------------------
st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

# Welcome block if empty
if len(active["messages"]) == 0:
    st.markdown(
        """
        <div class="card" style="max-width: 820px; margin: 10px auto;">
          <div class="card-title">Welcome</div>
          <div style="color: rgba(255,255,255,0.88); line-height: 1.7;">
            Hello! I’m the Hustad AI Agent. Use the left menu for quick actions, or ask your question below.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Render chat history
for msg in active["messages"]:
    role = msg.get("role", "assistant")
    content = msg.get("content", "")

    with st.chat_message(role):
        klass = "user" if role == "user" else "assistant"
        st.markdown(f'<div class="bubble {klass}">', unsafe_allow_html=True)
        if isinstance(content, dict):
            render_reply(content)
        else:
            st.markdown(content)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Composer (prefillable, SaaS feel)
# ---------------------------
st.write("")
st.markdown('<div class="composer">', unsafe_allow_html=True)

with st.form("composer_form", clear_on_submit=False):
    colL, colR = st.columns([0.85, 0.15], vertical_alignment="bottom")

    with colL:
        draft = st.text_area(
            "Message",
            value=st.session_state.draft,
            key="draft_input",
            height=90,
            label_visibility="collapsed",
            placeholder="Ask about tickets, properties, invoices…"
        )

    with colR:
        send = st.form_submit_button("Send", use_container_width=True)
        clear = st.form_submit_button("Clear", use_container_width=True)

    if clear:
        st.session_state.draft = ""
        st.rerun()

    if send:
        prompt = (draft or "").strip()
        if not prompt:
            st.warning("Type a message first.")
        else:
            # set a nice session title on first message
            if active["title"] == "New session":
                active["title"] = infer_session_title_from_prompt(prompt)

            active["messages"].append({"role": "user", "content": prompt})

            with st.spinner("Working…"):
                try:
                    resp = post_to_n8n(prompt, active["id"], user_id)
                    reply_obj = normalize_reply(resp)

                    # If huge raw dump, show friendly and keep raw in expander
                    if isinstance(reply_obj, dict) and len(safe_json(reply_obj)) > 12000:
                        reply_obj = {
                            "message": "✅ Got the result (large payload). Open **Raw payload** to view details.",
                            "fields": {"Tip": "We can format this into a clean card/table if you tell me which fields you want."}
                        }

                    active["messages"].append({"role": "assistant", "content": reply_obj})

                    st.session_state.draft = ""
                    st.rerun()

                except Exception as e:
                    active["messages"].append({"role": "assistant", "content": {"message": f"Request failed: {e}"}})
                    st.error(f"Request failed: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Debug (Global)
# ---------------------------
with st.expander("Debug (last request)"):
    st.code(safe_json(active.get("last_debug")), language="json")
