import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import uuid
import os
import time
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Hustad AI OS", page_icon="🧠", layout="wide")

# In Streamlit Cloud → App → Settings → Secrets:
# N8N_WEBHOOK_URL = "https://.../webhook/...."
N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL", "").strip()

# Lightweight persistence for recent chats (best-effort)
STORE_FILE = ".hustad_ai_os_chats.json"


# =========================================================
# THEME / UI (Neon SaaS + ChatGPT-like layout)
# =========================================================
CUSTOM_CSS = """
<style>
/* -------------------------
   GLOBAL
--------------------------*/
html, body, [class*="css"]  {
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}
.block-container { 
  padding-top: 0.9rem; 
  padding-bottom: 0.6rem; 
  max-width: 1600px; 
}
header { visibility: hidden; height: 0px; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Background: multi-neon */
.stApp {
  background:
    radial-gradient(900px 600px at 10% 10%, rgba(151,71,255,.20), transparent 55%),
    radial-gradient(900px 600px at 90% 15%, rgba(0,255,209,.14), transparent 55%),
    radial-gradient(900px 600px at 80% 90%, rgba(255,77,166,.12), transparent 55%),
    radial-gradient(900px 600px at 10% 90%, rgba(80,180,255,.12), transparent 55%),
    linear-gradient(180deg, #0b0f17 0%, #070a10 100%);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
  background: rgba(9, 12, 18, 0.72);
  border-right: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] .block-container {
  padding-top: 1.0rem;
}

/* Typography */
h1,h2,h3 { letter-spacing: -0.02em; }
.small-muted { color: rgba(255,255,255,0.62); font-size: 12px; }
.muted { color: rgba(255,255,255,0.7); }

/* -------------------------
   TOP HEADER BAR
--------------------------*/
.topbar {
  display:flex; align-items:center; justify-content:space-between;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(14,18,27,0.58);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 12px 60px rgba(0,0,0,.35);
}
.brand {
  display:flex; align-items:center; gap:12px;
}
.logo {
  width: 38px; height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(151,71,255,.9), rgba(0,255,209,.75));
  box-shadow: 0 0 24px rgba(151,71,255,.35), 0 0 30px rgba(0,255,209,.12);
}
.title {
  font-weight: 800;
  font-size: 18px;
  color: rgba(255,255,255,.92);
  margin: 0;
  line-height: 1.15;
}
.subtitle {
  font-size: 12px;
  color: rgba(255,255,255,.62);
  margin-top: 2px;
}
.badge {
  display:inline-flex; gap:8px; align-items:center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  font-size: 12px;
  color: rgba(255,255,255,0.80);
}

/* -------------------------
   PANELS / CARDS
--------------------------*/
.panel {
  border-radius: 18px;
  background: rgba(12,15,22,0.55);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 14px 70px rgba(0,0,0,.32);
}
.panel-header {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  display:flex; align-items:center; justify-content:space-between;
}
.panel-title {
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.62);
}
.panel-body {
  padding: 12px 14px;
}
.hr-soft {
  height: 1px;
  background: rgba(255,255,255,0.08);
  border: none;
  margin: 10px 0;
}

/* -------------------------
   CHAT AREA (fixed input, scroll messages)
--------------------------*/
.chat-shell {
  position: relative;
  height: calc(100vh - 210px);
  display:flex;
  flex-direction:column;
}
.chat-scroll {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 10px 10px 18px 10px;
}
.chat-inputbar {
  flex: 0 0 auto;
  padding: 10px;
  border-top: 1px solid rgba(255,255,255,0.08);
  background: rgba(10,12,18,0.45);
  border-bottom-left-radius: 18px;
  border-bottom-right-radius: 18px;
}

/* Make Streamlit chat input feel like ChatGPT */
[data-testid="stChatInput"] textarea {
  font-size: 16px !important;
  line-height: 1.35 !important;
  padding: 14px 14px !important;
  border-radius: 14px !important;
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
}
[data-testid="stChatInput"] textarea:focus {
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(151,71,255,0.20), 0 0 0 2px rgba(0,255,209,0.12) !important;
  border-color: rgba(151,71,255,0.45) !important;
}

/* -------------------------
   CHAT BUBBLES (compact)
--------------------------*/
.msg {
  display:flex;
  gap: 10px;
  margin: 10px 0;
}
.avatar {
  width: 34px; height: 34px;
  border-radius: 12px;
  display:flex; align-items:center; justify-content:center;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  flex: 0 0 auto;
}
.avatar.user { background: rgba(255,255,255,0.06); }
.avatar.assistant {
  background: linear-gradient(135deg, rgba(151,71,255,.55), rgba(0,255,209,.18));
  box-shadow: 0 0 22px rgba(151,71,255,.18);
}
.bubble {
  max-width: 860px;
  border-radius: 16px;
  padding: 10px 12px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.04);
}
.bubble.user {
  background: rgba(255,255,255,0.06);
}
.bubble.assistant {
  background: rgba(12,15,22,0.55);
}
.meta {
  margin-top: 6px;
  display:flex; gap:10px; align-items:center; justify-content:space-between;
  font-size: 12px;
  color: rgba(255,255,255,0.55);
}
.msg-actions { opacity: 0; transform: translateY(-2px); transition: .14s ease; }
.msg:hover .msg-actions { opacity: 1; transform: translateY(0px); }

/* Copy + Neon buttons */
.neon-btn button, .neon-btn div[data-testid="stButton"] button {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  background: rgba(255,255,255,0.06) !important;
  color: rgba(255,255,255,0.88) !important;
  transition: all 0.15s ease !important;
}
.neon-btn button:hover {
  transform: translateY(-1px);
  border-color: rgba(151,71,255,0.55) !important;
  box-shadow: 0 0 0 3px rgba(151,71,255,0.14), 0 0 0 2px rgba(0,255,209,0.10) !important;
}
.neon-primary button, .neon-primary div[data-testid="stButton"] button {
  background: linear-gradient(135deg, rgba(151,71,255,.95), rgba(0,255,209,.75)) !important;
  border: 0 !important;
  color: #061018 !important;
  font-weight: 700 !important;
  box-shadow: 0 10px 30px rgba(151,71,255,0.18), 0 10px 30px rgba(0,255,209,0.10) !important;
}
.neon-primary button:hover {
  filter: brightness(1.06);
  box-shadow: 0 0 0 4px rgba(151,71,255,0.14), 0 0 0 2px rgba(0,255,209,0.12) !important;
}
.copy-chip {
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  cursor: pointer;
  user-select: none;
}

/* Typing animation */
.typing {
  display:inline-flex;
  gap:6px;
  align-items:center;
  color: rgba(255,255,255,0.72);
}
.dots span{
  display:inline-block;
  width: 6px; height: 6px;
  margin: 0 2px;
  border-radius: 50%;
  background: rgba(255,255,255,0.55);
  animation: bounce 1.1s infinite ease-in-out;
}
.dots span:nth-child(2){ animation-delay: .15s; }
.dots span:nth-child(3){ animation-delay: .30s; }
@keyframes bounce{
  0%,80%,100%{ transform: translateY(0); opacity:.55; }
  40%{ transform: translateY(-5px); opacity:1; }
}

/* Result Panel: key/value */
.kv {
  display:grid;
  grid-template-columns: 140px 1fr;
  gap: 8px 12px;
}
.k { color: rgba(255,255,255,0.65); font-size: 13px; }
.v { color: rgba(255,255,255,0.92); font-size: 13px; overflow-wrap:anywhere; }
.pill {
  display:inline-flex; align-items:center; gap:8px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  color: rgba(255,255,255,0.80);
  font-size: 12px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =========================================================
# STORAGE HELPERS (Recent chats like ChatGPT)
# =========================================================
def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def load_store():
    try:
        if os.path.exists(STORE_FILE):
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"sessions": {}, "order": []}


def save_store(store):
    try:
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
    except Exception:
        # best-effort; Streamlit Cloud may restrict writes in some environments
        pass


def ensure_session(store, session_id: str):
    if session_id not in store["sessions"]:
        store["sessions"][session_id] = {
            "title": "New chat",
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "messages": [],
        }
        store["order"].insert(0, session_id)
    return store


def session_preview(sess: dict):
    msgs = sess.get("messages", [])
    for m in reversed(msgs):
        if m.get("role") == "user":
            t = (m.get("content") or "").strip()
            return t[:48] + ("…" if len(t) > 48 else "")
    return "No messages yet"


# =========================================================
# API / NORMALIZE
# =========================================================
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


def normalize_reply(data):
    """
    Handle common shapes:
    - { reply: ... }
    - { output: "..." }
    - reply string that contains JSON
    """
    if isinstance(data, dict) and "reply" in data:
        reply = data["reply"]
    else:
        reply = data

    if isinstance(reply, dict) and set(reply.keys()) == {"output"}:
        reply = reply["output"]

    if isinstance(reply, str):
        s = reply.strip()
        # Try parse JSON string
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                return json.loads(s)
            except Exception:
                return {"message": reply}
        return {"message": reply}

    if isinstance(reply, dict):
        return reply

    return {"message": str(reply)}


def extract_structured(reply_obj: dict):
    """
    Decide what goes into the Result Panel (structured data),
    while chat stays clean.
    """
    if not isinstance(reply_obj, dict):
        return None

    # Preferred: explicit fields
    if isinstance(reply_obj.get("fields"), dict) and reply_obj["fields"]:
        return {
            "title": reply_obj.get("title") or reply_obj.get("heading") or "Result",
            "fields": reply_obj["fields"],
            "link": reply_obj.get("link") or reply_obj.get("url"),
            "raw": reply_obj,
        }

    # If CPC-like object: entityType / chosen / attributes
    if "entityType" in reply_obj or "chosen" in reply_obj or "attributes" in reply_obj:
        fields = {}
        if isinstance(reply_obj.get("attributes"), dict):
            attrs = reply_obj["attributes"]
            for k in ["name", "address", "phone", "roofType", "numberOfBuildings", "squares", "closeRate", "activityDate"]:
                if k in attrs and attrs[k] not in (None, "", []):
                    fields[k] = attrs[k]
        if isinstance(reply_obj.get("chosen"), dict):
            ch = reply_obj["chosen"]
            if "id" in ch:
                fields["id"] = ch["id"]
            if "type" in ch:
                fields["type"] = ch["type"]

        if fields:
            return {
                "title": reply_obj.get("title") or reply_obj.get("name") or "Structured Result",
                "fields": fields,
                "link": reply_obj.get("link") or reply_obj.get("url"),
                "raw": reply_obj,
            }

    return None


def chat_summary(reply_obj: dict):
    """
    Keep chat clean: show a short message only.
    Put structured data in Result Panel.
    """
    if not isinstance(reply_obj, dict):
        return str(reply_obj)

    msg = reply_obj.get("message") or reply_obj.get("summary") or reply_obj.get("output")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()

    # If no message, try infer friendly line
    if "fields" in reply_obj and isinstance(reply_obj["fields"], dict) and reply_obj["fields"]:
        title = reply_obj.get("title") or "Result ready"
        return f"✅ {title} (see Result Panel)"

    if "entityType" in reply_obj:
        return "✅ Result found (see Result Panel)"

    # fallback compact
    return "✅ Done (see Result Panel for structured details)"


# =========================================================
# SESSION STATE
# =========================================================
if "store" not in st.session_state:
    st.session_state.store = load_store()

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = str(uuid.uuid4())

st.session_state.store = ensure_session(st.session_state.store, st.session_state.active_session_id)

if "user_id" not in st.session_state:
    st.session_state.user_id = "aminul@hustadcompanies.com"

if "last_debug" not in st.session_state:
    st.session_state.last_debug = None

if "result_panel" not in st.session_state:
    st.session_state.result_panel = None

if "prefill" not in st.session_state:
    st.session_state.prefill = ""


def get_active_session():
    return st.session_state.store["sessions"][st.session_state.active_session_id]


def set_active_session(session_id: str):
    st.session_state.active_session_id = session_id
    st.session_state.store = ensure_session(st.session_state.store, session_id)
    # Clear result panel when switching sessions (optional; keeps things tidy)
    st.session_state.result_panel = None
    save_store(st.session_state.store)


# =========================================================
# UI HELPERS
# =========================================================
def js_copy_button(text: str, key: str, label="Copy"):
    # Hover-only chip + clipboard copy via JS
    safe = json.dumps(text)
    html = f"""
    <div class="msg-actions">
      <span class="copy-chip" onclick='navigator.clipboard.writeText({safe}); this.innerText="✅ Copied"; setTimeout(()=>this.innerText="📋 {label}", 900);'>
        📋 {label}
      </span>
    </div>
    """
    components.html(html, height=36, key=key)


def autoscroll_anchor():
    # Scroll to bottom after render
    components.html(
        """
        <script>
          const el = window.parent.document.getElementById("hustad-chat-bottom");
          if (el) { el.scrollIntoView({behavior: "smooth", block:"end"}); }
        </script>
        """,
        height=0,
    )


def render_message(role: str, content: str, ts: str, idx: int):
    is_user = role == "user"
    avatar = "🧑" if is_user else "🤖"
    bubble_class = "user" if is_user else "assistant"

    # Render message container
    st.markdown(f'<div class="msg">', unsafe_allow_html=True)
    st.markdown(f'<div class="avatar {bubble_class}">{avatar}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bubble {bubble_class}">', unsafe_allow_html=True)

    # Message text
    st.markdown(content)

    # Meta row: timestamp + actions
    st.markdown(
        f"""
        <div class="meta">
          <span>{datetime.fromisoformat(ts).strftime("%b %d • %I:%M %p")}</span>
          <span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Actions (copy only for assistant, hover-only)
    if not is_user:
        js_copy_button(content, key=f"copy_{idx}", label="Copy")

    st.markdown("</div>", unsafe_allow_html=True)  # bubble
    st.markdown("</div>", unsafe_allow_html=True)  # msg


def render_typing():
    st.markdown(
        """
        <div class="msg">
          <div class="avatar assistant">🤖</div>
          <div class="bubble assistant">
            <div class="typing">
              Hustad AI is typing
              <span class="dots"><span></span><span></span><span></span></span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_panel():
    rp = st.session_state.result_panel
    if not rp:
        st.markdown(
            '<div class="muted">No structured result yet. Ask for a property, ticket, invoice, or summary and I’ll pin it here.</div>',
            unsafe_allow_html=True,
        )
        return

    title = rp.get("title", "Result")
    fields = rp.get("fields", {})
    link = rp.get("link")

    st.markdown(f"### {title}")
    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    if isinstance(fields, dict) and fields:
        st.markdown('<div class="kv">', unsafe_allow_html=True)
        for k, v in fields.items():
            st.markdown(f'<div class="k">{k}</div><div class="v">{v}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if link:
        st.markdown("")
        st.markdown(f"**Link:** {link}")

    with st.expander("Raw / Debug (structured)"):
        st.code(json.dumps(rp.get("raw", rp), indent=2)[:12000], language="json")


# =========================================================
# CHAT ACTIONS
# =========================================================
def add_message(role: str, content: str):
    sess = get_active_session()
    sess["messages"].append({"role": role, "content": content, "ts": _now_iso()})
    sess["updated_at"] = _now_iso()

    # Auto-title: first user message
    if sess.get("title") in ("New chat", "", None) and role == "user":
        t = content.strip()
        sess["title"] = t[:28] + ("…" if len(t) > 28 else "")

    save_store(st.session_state.store)


def regenerate_last(user_id: str):
    sess = get_active_session()
    msgs = sess["messages"]

    # Need last user message
    last_user = None
    # Remove last assistant if present
    if msgs and msgs[-1]["role"] == "assistant":
        msgs.pop()

    for m in reversed(msgs):
        if m["role"] == "user":
            last_user = m["content"]
            break

    if not last_user:
        return

    # Call n8n again
    resp = post_to_n8n(last_user, st.session_state.active_session_id, user_id)
    reply_obj = normalize_reply(resp)

    structured = extract_structured(reply_obj)
    if structured:
        st.session_state.result_panel = structured

    add_message("assistant", chat_summary(reply_obj))


# =========================================================
# SIDEBAR (Recent chats + controls like ChatGPT)
# =========================================================
with st.sidebar:
    st.markdown("### Hustad AI OS")
    st.markdown('<div class="small-muted">Internal tool • Cyber SaaS mode</div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    st.session_state.user_id = st.text_input("User ID", value=st.session_state.user_id)

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    # Connection status
    if N8N_WEBHOOK_URL:
        st.markdown('<span class="pill">🟢 Connected to n8n</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill">🟡 Missing N8N_WEBHOOK_URL</span>', unsafe_allow_html=True)

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    # New chat
    st.markdown('<div class="neon-primary">', unsafe_allow_html=True)
    if st.button("＋ New chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.store = ensure_session(st.session_state.store, new_id)
        set_active_session(new_id)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Search chats (optional)
    q = st.text_input("Search chats", value="", placeholder="Search history…")
    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)
    st.markdown("#### Recent chats")

    # Render sessions list
    store = st.session_state.store
    order = store.get("order", [])

    def match_session(sid: str):
        s = store["sessions"][sid]
        hay = (s.get("title", "") + " " + session_preview(s)).lower()
        return q.strip().lower() in hay if q.strip() else True

    filtered = [sid for sid in order if sid in store["sessions"] and match_session(sid)]

    # Limit list length for UI
    for sid in filtered[:20]:
        s = store["sessions"][sid]
        is_active = sid == st.session_state.active_session_id
        title = s.get("title", "Chat")
        prev = session_preview(s)
        updated = s.get("updated_at", s.get("created_at", _now_iso()))
        try:
            updated_txt = datetime.fromisoformat(updated).strftime("%b %d")
        except Exception:
            updated_txt = ""

        label = f"{title}  ·  {updated_txt}\n{prev}"
        if st.button(label, key=f"sess_{sid}", use_container_width=True):
            set_active_session(sid)
            st.rerun()

        if is_active:
            # Rename + Delete for active session
            with st.expander("Manage chat"):
                new_title = st.text_input("Rename", value=title, key=f"rename_{sid}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
                    if st.button("Save", key=f"save_title_{sid}", use_container_width=True):
                        store["sessions"][sid]["title"] = new_title.strip() or "Chat"
                        store["sessions"][sid]["updated_at"] = _now_iso()
                        save_store(store)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
                    if st.button("Delete", key=f"del_{sid}", use_container_width=True):
                        # Remove session
                        store["sessions"].pop(sid, None)
                        store["order"] = [x for x in store["order"] if x != sid]
                        # Fallback to a new session
                        new_id = str(uuid.uuid4())
                        st.session_state.store = ensure_session(store, new_id)
                        set_active_session(new_id)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)

    # Quick actions
    st.markdown("#### Quick actions")
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
        if st.button("🏢 Property", use_container_width=True):
            st.session_state.prefill = "show property "
        st.markdown("</div>", unsafe_allow_html=True)
    with qa2:
        st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
        if st.button("🎫 Tickets", use_container_width=True):
            st.session_state.prefill = "show tickets for property "
        st.markdown("</div>", unsafe_allow_html=True)
    with qa3:
        st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
        if st.button("🛠️ Create", use_container_width=True):
            st.session_state.prefill = "create service ticket for property  issue: "
        st.markdown("</div>", unsafe_allow_html=True)

    qb1, qb2 = st.columns(2)
    with qb1:
        st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
        if st.button("🧾 Invoice", use_container_width=True):
            st.session_state.prefill = "show invoice for ticket "
        st.markdown("</div>", unsafe_allow_html=True)
    with qb2:
        st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
        if st.button("📝 Summary", use_container_width=True):
            st.session_state.prefill = "write executive summary for property "
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="hr-soft"/>', unsafe_allow_html=True)
    with st.expander("Debug / last request"):
        st.code(json.dumps(st.session_state.last_debug, indent=2)[:12000], language="json")


# =========================================================
# MAIN LAYOUT: Header + (Chat + Result Panel)
# =========================================================
st.markdown(
    f"""
    <div class="topbar">
      <div class="brand">
        <div class="logo"></div>
        <div>
          <div class="title">Enterprise Assistant</div>
          <div class="subtitle">AI Operating System for CenterPoint Connect • Tickets • Properties • Reports</div>
        </div>
      </div>
      <div class="badge">🕒 {datetime.now().strftime("%b %d, %Y • %I:%M %p")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# Two main columns: Chat + Result Panel
chat_col, result_col = st.columns([0.68, 0.32], gap="large")

# =========================
# CHAT PANEL
# =========================
with chat_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="panel-header">
          <div>
            <div class="panel-title">Chat</div>
            <div class="small-muted">Ask about properties, tickets, invoices, notes, summaries, or service ticket creation.</div>
          </div>
          <div class="pill">Connected Workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
    st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)

    sess = get_active_session()
    messages = sess.get("messages", [])

    if not messages:
        st.markdown(
            """
            <div class="muted" style="padding: 6px 4px;">
              Try: <span class="pill">show property Riverport Landings Senior</span> or <span class="pill">show tickets for property 4 Lake Properties</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for i, m in enumerate(messages):
        render_message(m["role"], m["content"], m["ts"], i)

    # anchor for auto-scroll
    st.markdown('<div id="hustad-chat-bottom"></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # chat-scroll

    # Input bar
    st.markdown('<div class="chat-inputbar">', unsafe_allow_html=True)

    if st.session_state.prefill:
        st.markdown(
            f'<div class="small-muted">Suggested command: <span class="pill">{st.session_state.prefill}</span></div>',
            unsafe_allow_html=True,
        )

    prompt = st.chat_input("Message Hustad AI…")

    # Regenerate (ChatGPT-like) appears when last message is assistant
    if messages and messages[-1]["role"] == "assistant":
        st.markdown('<div class="neon-btn">', unsafe_allow_html=True)
        if st.button("↻ Regenerate response", use_container_width=True):
            try:
                # Show typing quickly for UX
                typing_slot = st.empty()
                with typing_slot.container():
                    render_typing()
                time.sleep(0.25)

                regenerate_last(st.session_state.user_id)
                st.session_state.prefill = ""
                st.rerun()
            except Exception as e:
                st.error(f"Regenerate failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # chat-inputbar
    st.markdown("</div>", unsafe_allow_html=True)  # chat-shell
    st.markdown("</div>", unsafe_allow_html=True)  # panel

    # Handle send
    if prompt:
        # If user pasted prefill, clear it
        st.session_state.prefill = ""

        add_message("user", prompt)

        # Typing animation placeholder while calling API
        typing_slot = st.empty()
        with typing_slot.container():
            render_typing()

        try:
            resp = post_to_n8n(prompt, st.session_state.active_session_id, st.session_state.user_id)
            reply_obj = normalize_reply(resp)

            structured = extract_structured(reply_obj)
            if structured:
                st.session_state.result_panel = structured

            add_message("assistant", chat_summary(reply_obj))

            typing_slot.empty()
            st.rerun()

        except Exception as e:
            typing_slot.empty()
            add_message("assistant", f"❌ Request failed: {e}")
            st.rerun()

    # Auto-scroll after render
    autoscroll_anchor()


# =========================
# RESULT PANEL
# =========================
with result_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="panel-header">
          <div class="panel-title">Result Panel</div>
          <div class="pill">Pinned Structured Data</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="panel-body">', unsafe_allow_html=True)
    render_result_panel()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

save_store(st.session_state.store)
