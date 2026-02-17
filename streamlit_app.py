import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time
import re

# ---------------------------
# Page + Theme
# ---------------------------
st.set_page_config(page_title="Hustad AI Assistant", page_icon="🧠", layout="wide")

CUSTOM_CSS = """
<style>
/* --- Global layout --- */
.block-container { padding-top: 1.0rem; padding-bottom: 1.8rem; max-width: 1550px; }
[data-testid="stSidebar"] { background: rgba(20, 22, 28, 0.72); backdrop-filter: blur(10px); border-right: 1px solid rgba(255,255,255,0.06); }
h1, h2, h3 { letter-spacing: -0.02em; }

/* --- Background glow --- */
body {
  background:
    radial-gradient(900px 500px at 10% 10%, rgba(140, 80, 255, 0.18), transparent 60%),
    radial-gradient(900px 500px at 90% 30%, rgba(0, 200, 255, 0.12), transparent 55%),
    radial-gradient(900px 500px at 60% 95%, rgba(0, 255, 150, 0.10), transparent 55%),
    #0b0f17;
}

/* --- Top header --- */
.hustad-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; border-radius: 14px;
  background: linear-gradient(90deg, rgba(35,40,55,0.88), rgba(25,27,34,0.88));
  border: 1px solid rgba(255,255,255,0.08);
}
.hustad-badge {
  display:inline-flex; gap:8px; align-items:center;
  padding:6px 10px; border-radius:999px;
  background: rgba(255,255,255,0.06);
  border:1px solid rgba(255,255,255,0.08);
  font-size:12px; color: rgba(255,255,255,0.82);
}
.pill {
  display:inline-block; padding:5px 10px; border-radius:999px;
  background: rgba(255,255,255,0.06);
  border:1px solid rgba(255,255,255,0.08);
  font-size:12px; color: rgba(255,255,255,0.82);
}
.small-muted { color: rgba(255,255,255,0.60); font-size: 12px; }

/* --- Card shells --- */
.card {
  border-radius: 16px;
  padding: 14px 14px;
  background: rgba(18,20,26,0.72);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}
.card-title {
  font-size: 12px;
  color: rgba(255,255,255,0.70);
  text-transform: uppercase;
  letter-spacing: 0.10em;
  margin-bottom: 10px;
}
hr.soft { border: none; height: 1px; background: rgba(255,255,255,0.07); margin: 12px 0; }

/* --- Chat panel (ChatGPT-ish) --- */
.chat-shell {
  border-radius: 18px;
  background: rgba(10,12,16,0.58);
  border: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
}
.chat-topbar {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(18,20,26,0.55);
}
.chat-wrap {
  height: 68vh;
  overflow-y: auto;
  padding: 16px 14px;
}

/* compact bubbles */
.msg {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: flex-start;
}
.avatar {
  width: 30px; height: 30px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center; justify-content: center;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.08);
  flex: 0 0 auto;
}
.bubble {
  max-width: 86%;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  line-height: 1.45;
}
.bubble.user {
  background: rgba(120,80,255,0.10);
  border: 1px solid rgba(120,80,255,0.24);
}
.bubble.assistant {
  background: rgba(0,200,255,0.06);
  border: 1px solid rgba(0,200,255,0.16);
}
.ts {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(255,255,255,0.55);
}

/* --- Right result panel --- */
.result-kv { display: grid; grid-template-columns: 130px 1fr; gap: 6px 12px; }
.result-k { color: rgba(255,255,255,0.65); font-size: 12px; }
.result-v { color: rgba(255,255,255,0.93); font-size: 12px; overflow-wrap: anywhere; }

.result-badge {
  display:inline-flex; gap:8px; align-items:center;
  padding:6px 10px; border-radius:999px;
  background: rgba(0,255,150,0.08);
  border:1px solid rgba(0,255,150,0.18);
  font-size:12px; color: rgba(255,255,255,0.85);
}

/* --- Sticky helpers --- */
.sticky-note {
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------
# Config / Secrets
# ---------------------------
N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL", "").strip()

# ---------------------------
# Session State
# ---------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    # each message: {"role": "user"/"assistant", "content": "... or dict", "ts": "HH:MM PM"}
    st.session_state.messages = []

if "last_debug" not in st.session_state:
    st.session_state.last_debug = None

if "prefill" not in st.session_state:
    st.session_state.prefill = ""

if "last_result" not in st.session_state:
    # structured result to show in right panel
    st.session_state.last_result = None

# ---------------------------
# Helpers
# ---------------------------
def now_ts():
    return datetime.now().strftime("%I:%M %p").lstrip("0")

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
        "raw_text": r.text[:8000],
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
        try:
            return json.loads(reply)
        except Exception:
            return {"message": reply}

    return reply if isinstance(reply, dict) else {"message": str(reply)}

def try_extract_structured_result(reply_obj: dict):
    """
    Pull a clean "Result Panel" object out of various shapes.
    Works with your current n8n outputs (property/ticket payloads, fields blocks, etc.)
    """
    if not isinstance(reply_obj, dict):
        return None

    # If you already have a friendly structured format
    if isinstance(reply_obj.get("fields"), dict):
        return {
            "title": reply_obj.get("title") or reply_obj.get("heading") or reply_obj.get("name") or "Result",
            "type": reply_obj.get("entityType") or reply_obj.get("type") or "info",
            "fields": reply_obj.get("fields"),
            "link": reply_obj.get("link") or reply_obj.get("url"),
        }

    # If it looks like your CPC property response nested in chosen/attributes
    chosen = reply_obj.get("chosen")
    if isinstance(chosen, dict):
        et = chosen.get("type") or reply_obj.get("entityType") or "entity"
        attrs = chosen.get("attributes") if isinstance(chosen.get("attributes"), dict) else {}
        name = chosen.get("name") or attrs.get("name") or reply_obj.get("Property name") or "Result"

        fields = {}
        # Try common CPC fields
        for k in ["name", "address", "city", "state", "postalCode", "roofType", "numberOfBuildings", "squares", "closeRate", "activity"]:
            if k in attrs and attrs.get(k) is not None:
                fields[k] = attrs.get(k)

        # Sometimes you send formatted strings already, so fallback to minimal keys
        if not fields and attrs:
            # only small values
            for k, v in attrs.items():
                if isinstance(v, (str, int, float)) and len(str(v)) <= 120:
                    fields[k] = v

        link = chosen.get("links", {}).get("0", {}).get("href") if isinstance(chosen.get("links"), dict) else None

        return {"title": name, "type": et, "fields": fields or None, "link": link}

    # If reply contains a "message" and that's it, keep panel empty
    return None

def md_escape(text: str) -> str:
    # safe-ish minimal escape for markdown in HTML bubble
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_message(role: str, content, ts: str):
    avatar = "🧑" if role == "user" else "🧠"
    bubble_cls = "user" if role == "user" else "assistant"

    # content can be dict or string; keep chat clean
    if isinstance(content, dict):
        # prefer message/summary/title in chat; keep heavy data in result panel / debug
        text = content.get("message") or content.get("summary") or ""
        if not text:
            # fallback: show a compact statement
            text = "✅ Result ready. See the Result Panel on the right."
    else:
        text = str(content)

    st.markdown(
        f"""
        <div class="msg">
          <div class="avatar">{avatar}</div>
          <div>
            <div class="bubble {bubble_cls}">{md_escape(text)}</div>
            <div class="ts">{ts}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_result_panel():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Result Panel</div>', unsafe_allow_html=True)

    result = st.session_state.last_result
    if not result:
        st.markdown(
            '<div class="sticky-note small-muted">No structured result yet. Ask for a property, ticket, invoice, or summary and I’ll pin it here.</div>',
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    title = result.get("title") or "Result"
    typ = (result.get("type") or "info").upper()
    link = result.get("link")
    fields = result.get("fields") if isinstance(result.get("fields"), dict) else {}

    st.markdown(f"### {title}")
    st.markdown(f'<span class="result-badge">📌 {typ}</span>', unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    if fields:
        st.markdown('<div class="result-kv">', unsafe_allow_html=True)
        for k, v in fields.items():
            st.markdown(f'<div class="result-k">{md_escape(str(k))}</div><div class="result-v">{md_escape(str(v))}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="small-muted">No parsed fields available (check Debug for raw payload).</div>', unsafe_allow_html=True)

    if link:
        st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
        st.markdown(f"**Open:** {link}")

    st.markdown("</div>", unsafe_allow_html=True)

def autoscroll_js():
    # Scroll the chat container to bottom after each render
    # This targets Streamlit's DOM - reliable enough for Streamlit Cloud.
    st.components.v1.html(
        """
        <script>
          const chat = window.parent.document.querySelector('.chat-wrap');
          if (chat) { chat.scrollTop = chat.scrollHeight; }
        </script>
        """,
        height=0,
    )

def typing_animation(container, seconds=0.8):
    # Lightweight “thinking…” dots (safe + smooth)
    start = time.time()
    dots = 0
    while time.time() - start < seconds:
        dots = (dots + 1) % 4
        container.markdown(
            f"""
            <div class="msg">
              <div class="avatar">🧠</div>
              <div>
                <div class="bubble assistant">Thinking{'.'*dots}</div>
                <div class="ts">{now_ts()}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(0.18)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("## Hustad AI OS")
    st.markdown('<span class="pill">Internal Tool • Cyber SaaS Mode</span>', unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    user_id = st.text_input("User ID", value="aminul@hustadcompanies.com")

    st.markdown("<div class='small-muted'>Status</div>", unsafe_allow_html=True)
    if N8N_WEBHOOK_URL:
        st.success("Connected to n8n")
    else:
        st.warning("Missing N8N_WEBHOOK_URL (Streamlit Secrets)")

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    if st.button("➕ New Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.last_debug = None
        st.session_state.prefill = ""
        st.session_state.last_result = None
        st.rerun()

    st.markdown("<div class='small-muted'>Session</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pill'>{st.session_state.session_id}</div>", unsafe_allow_html=True)

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("### Quick actions")

    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("🏢 Property", use_container_width=True):
            st.session_state.prefill = "show property "
    with q2:
        if st.button("🎫 Tickets", use_container_width=True):
            st.session_state.prefill = "show tickets for property "
    with q3:
        if st.button("🛠 Create", use_container_width=True):
            st.session_state.prefill = "create service ticket for property  issue: "

    q4, q5 = st.columns(2)
    with q4:
        if st.button("🧾 Invoice", use_container_width=True):
            st.session_state.prefill = "show invoice for ticket "
    with q5:
        if st.button("📝 Summary", use_container_width=True):
            st.session_state.prefill = "write executive summary for property "

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    with st.expander("Debug / Last request"):
        st.code(safe_json(st.session_state.last_debug), language="json")

# ---------------------------
# Top header
# ---------------------------
st.markdown(
    f"""
    <div class="hustad-header">
      <div>
        <div style="font-size: 22px; font-weight: 800;">Enterprise Assistant</div>
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

# ---------------------------
# Main Layout: Chat + Result Panel
# ---------------------------
chat_col, result_col = st.columns([0.68, 0.32], gap="large")

with result_col:
    render_result_panel()

with chat_col:
    # Chat shell
    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="chat-topbar">
          <div>
            <div style="font-weight: 700;">Chat</div>
            <div class="small-muted">Ask about properties, tickets, invoices, summaries, and service ticket creation.</div>
          </div>
          <div class="pill">Connected Workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    chat_area = st.container()
    st.markdown("</div>", unsafe_allow_html=True)  # close chat-wrap
    st.markdown("</div>", unsafe_allow_html=True)  # close chat-shell

    # Render history inside chat area
    with chat_area:
        if not st.session_state.messages:
            st.markdown(
                """
                <div class="msg">
                  <div class="avatar">🧠</div>
                  <div>
                    <div class="bubble assistant">
                      Hello! I’m the Hustad AI Agent. Try:
                      <br/>• <b>show property Riverport Landings Senior</b>
                      <br/>• <b>show tickets for property 4 lake properties</b>
                      <br/>• <b>show invoice for ticket 12345</b>
                    </div>
                    <div class="ts">{}</div>
                  </div>
                </div>
                """.format(now_ts()),
                unsafe_allow_html=True,
            )

        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"], msg["ts"])

    # Suggested command pill
    if st.session_state.prefill:
        st.markdown(
            f"<div class='small-muted' style='margin-top:10px;'>Suggested command:</div> "
            f"<span class='pill'>{st.session_state.prefill}</span>",
            unsafe_allow_html=True
        )

    # Input (ChatGPT-like)
    prompt = st.chat_input("Message Hustad AI…")

    # ---------------------------
    # Handle Send (render reply INSIDE the chat box)
    # ---------------------------
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "ts": now_ts()})

        with chat_area:
            render_message("user", prompt, now_ts())

            # typing animation placeholder
            typing_slot = st.empty()
            typing_animation(typing_slot, seconds=0.9)
            typing_slot.empty()

            # real response
            try:
                resp = post_to_n8n(prompt, st.session_state.session_id, user_id)
                reply_obj = normalize_reply(resp)

                # update result panel (structured extract)
                extracted = try_extract_structured_result(reply_obj)
                if extracted:
                    st.session_state.last_result = extracted

                # keep chat clean: if huge payload -> show short message in chat
                to_chat = reply_obj
                if isinstance(reply_obj, dict) and len(str(reply_obj)) > 2600:
                    to_chat = {"message": "✅ Result ready. I pinned the important details in the Result Panel → (right side)."}

                st.session_state.messages.append({"role": "assistant", "content": to_chat, "ts": now_ts()})
                render_message("assistant", to_chat, now_ts())

            except Exception as e:
                err = {"message": f"Request failed: {e}"}
                st.session_state.messages.append({"role": "assistant", "content": err, "ts": now_ts()})
                render_message("assistant", err, now_ts())

        # auto-scroll after new messages
        autoscroll_js()
        # refresh the right panel immediately
        st.rerun()

# also scroll on normal render
autoscroll_js()
