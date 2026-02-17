import streamlit as st
import requests
import json
from datetime import datetime

# ----------------------------
# Config
# ----------------------------
st.set_page_config(
    page_title="Hustad AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL", "")

# ----------------------------
# Minimal “SaaS” styling
# ----------------------------
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
      [data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.08); }
      .topbar {
        display:flex; align-items:center; justify-content:space-between;
        padding: 0.85rem 1rem; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; background: rgba(255,255,255,0.03);
      }
      .brand { font-size: 1.1rem; font-weight: 700; letter-spacing: 0.2px; }
      .subtle { color: rgba(255,255,255,0.65); font-size: 0.9rem; }
      .card {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1rem;
        background: rgba(255,255,255,0.03);
      }
      .chip {
        display:inline-flex; align-items:center; gap:.45rem;
        padding: .25rem .55rem; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.02);
        font-size: .82rem;
        color: rgba(255,255,255,0.72);
      }
      .muted { color: rgba(255,255,255,0.62); }
      .tiny { font-size: 0.82rem; color: rgba(255,255,255,0.60); }
      .divider { height:1px; background: rgba(255,255,255,0.08); margin: .75rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Session state
# ----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess-{int(datetime.utcnow().timestamp())}"

if "user_id" not in st.session_state:
    # You can later make this dynamic (SSO/login). For now:
    st.session_state.user_id = "aminul@hustadcompanies.com"

if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role":"user"/"assistant","content":...,"raw":...}]

if "page" not in st.session_state:
    st.session_state.page = "Chat"

# ----------------------------
# Helpers
# ----------------------------
def call_n8n(message: str) -> dict:
    if not N8N_WEBHOOK_URL:
        return {"message": "Missing N8N_WEBHOOK_URL in Streamlit secrets.", "data": {}, "raw": {}}

    payload = {
        "message": message,
        "sessionId": st.session_state.session_id,
        "userId": st.session_state.user_id,
    }

    r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=120)
    r.raise_for_status()

    # n8n might return different shapes; normalize here:
    try:
        resp = r.json()
    except Exception:
        return {"message": r.text, "data": {}, "raw": {"rawText": r.text}}

    # Expected-ish: { reply: <obj/string>, sessionId, userId } OR { message, data } etc.
    raw = resp

    # Normalize message/data
    message_out = None
    data_out = {}

    if isinstance(resp, dict):
        if "message" in resp and isinstance(resp["message"], str):
            message_out = resp["message"]
            data_out = resp.get("data", {}) or {}
        elif "reply" in resp:
            reply = resp["reply"]
            if isinstance(reply, dict):
                # Sometimes reply itself includes "message"
                message_out = reply.get("message") or reply.get("output") or None
                data_out = reply
            else:
                message_out = str(reply)
        elif "output" in resp:
            message_out = str(resp["output"])
        else:
            message_out = json.dumps(resp, indent=2)
    else:
        message_out = str(resp)

    return {"message": message_out or "", "data": data_out or {}, "raw": raw}


def render_property_card(data: dict):
    """
    Tries to render a nice property card from structured fields.
    Works even if fields differ slightly.
    """
    # Common keys you’ve shown:
    # data might contain: chosen -> attributes -> ... OR direct keys.
    attrs = {}
    link = None

    # If your n8n final "reply" includes this:
    # { "chosen": { "attributes": {...}, "options": {"text":"..."} }, ... }
    if isinstance(data, dict) and "chosen" in data and isinstance(data["chosen"], dict):
        attrs = data["chosen"].get("attributes", {}) or {}
        opt = data["chosen"].get("options", {}) or {}
        link = opt.get("text")

    # Fallback if you send a flattened payload later
    if not attrs and isinstance(data, dict):
        attrs = data.get("attributes", {}) or {}

    name = attrs.get("name") or data.get("Property name") or data.get("property_name")
    roof = attrs.get("roofType") or data.get("Roof Type") or data.get("roofType")
    buildings = attrs.get("numberOfBuildings") or data.get("Number of Buildings") or data.get("numberOfBuildings")
    squares = attrs.get("squares") or data.get("Squares") or data.get("squares")
    close_rate = attrs.get("closeRate") or data.get("Close Rate") or data.get("closeRate")
    activity = attrs.get("activity") or data.get("Activity") or data.get("activity")
    street = attrs.get("streetAddress") or data.get("Address") or data.get("streetAddress")
    city = attrs.get("city")
    state = attrs.get("state")
    postal = attrs.get("postalCode")

    address = None
    if street:
        addr_parts = [street]
        tail = ", ".join([p for p in [city, state, postal] if p])
        if tail:
            addr_parts.append(tail)
        address = " • ".join(addr_parts)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Header
    st.markdown(
        f"""
        <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:1rem;">
          <div>
            <div style="font-size:1.15rem; font-weight:700;">{name or "Property"}</div>
            <div class="subtle">{address or "—"}</div>
          </div>
          <div class="chip">🏢 Property</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Buildings", buildings if buildings is not None else "—")
    c2.metric("Squares", squares if squares is not None else "—")
    c3.metric("Close Rate", f"{close_rate}%" if close_rate is not None else "—")
    c4.metric("Roof", roof if roof else "—")

    # Extra
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="tiny">
          <b>Activity:</b> {activity or "—"}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if link:
        st.markdown(f"🔗 For more info: {link}")

    st.markdown("</div>", unsafe_allow_html=True)


def looks_like_property(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    # Heuristics based on what you showed
    if "chosen" in data and isinstance(data["chosen"], dict):
        attrs = data["chosen"].get("attributes", {}) or {}
        return "name" in attrs or "streetAddress" in attrs
    # fallback heuristics
    return any(k in data for k in ["Property name", "roofType", "numberOfBuildings", "attributes"])


# ----------------------------
# Sidebar (SaaS Navigation)
# ----------------------------
with st.sidebar:
    st.markdown("### Hustad AI")
    st.caption("Internal assistant dashboard")

    st.session_state.page = st.radio(
        "Navigate",
        ["Chat", "Recent Activity", "Settings"],
        index=["Chat", "Recent Activity", "Settings"].index(st.session_state.page),
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("**Session**")
    st.code(st.session_state.session_id, language="text")
    st.markdown("**User**")
    st.code(st.session_state.user_id, language="text")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if st.button("🧹 Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ----------------------------
# Top bar
# ----------------------------
st.markdown(
    f"""
    <div class="topbar">
      <div>
        <div class="brand">Hustad AI Assistant</div>
        <div class="subtle">Chat + tools + property/ticket workflows</div>
      </div>
      <div class="chip">🟢 Online</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# ----------------------------
# Pages
# ----------------------------
if st.session_state.page == "Chat":
    # Two-column SaaS layout: Chat + Right panel
    left, right = st.columns([2.2, 1], gap="large")

    with left:
        # Chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

                # Optional debug per message
                if msg.get("raw") is not None and msg["role"] == "assistant":
                    with st.expander("Debug / Raw response", expanded=False):
                        st.json(msg["raw"])

        prompt = st.chat_input("Type your message…")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Working…"):
                    try:
                        resp = call_n8n(prompt)
                    except requests.exceptions.HTTPError as e:
                        st.error("Request failed.")
                        st.code(str(e))
                        resp = {"message": "HTTP error calling backend.", "data": {}, "raw": {"error": str(e)}}
                    except Exception as e:
                        st.error("Unexpected error.")
                        st.code(str(e))
                        resp = {"message": "Unexpected error calling backend.", "data": {}, "raw": {"error": str(e)}}

                # Render nicely if property-like
                if looks_like_property(resp.get("data", {})):
                    # short chat line + card
                    st.write("Here’s what I found:")
                    render_property_card(resp.get("data", {}))
                    assistant_text = "Here’s what I found (see details above)."
                else:
                    st.write(resp.get("message", "") or "—")
                    assistant_text = resp.get("message", "") or "—"

                # Save message + raw for debug
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_text, "raw": resp.get("raw")}
                )

                # Optional global debug for latest
                with st.expander("Debug / Raw response (latest)", expanded=False):
                    st.json(resp.get("raw"))

            st.rerun()

    with right:
        # Right panel: quick stats + helpful shortcuts
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Overview")
        st.caption("Quick glance at your assistant usage")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Session", st.session_state.session_id)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("#### Quick actions")
        if st.button("🏢 Find a property"):
            st.session_state.messages.append({"role": "user", "content": "show company Riverport Landings Senior"})
            st.rerun()
        if st.button("🎟️ Check tickets"):
            st.session_state.messages.append({"role": "user", "content": "show tickets"})
            st.rerun()
        if st.button("📝 Create service ticket"):
            st.session_state.messages.append({"role": "user", "content": "create service ticket for Riverport Landings Senior"})
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Recent Activity":
    st.markdown("## Recent Activity")
    st.caption("A simple timeline of user requests + assistant responses.")

    if not st.session_state.messages:
        st.info("No activity yet.")
    else:
        # show last 30 messages
        for i, m in enumerate(st.session_state.messages[-30:], start=1):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**{m['role'].upper()}**")
            st.write(m["content"])
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

elif st.session_state.page == "Settings":
    st.markdown("## Settings")
    st.caption("Control app behavior")

    st.markdown("### Backend")
    st.write("Webhook configured:", "✅" if bool(N8N_WEBHOOK_URL) else "❌")
    if not N8N_WEBHOOK_URL:
        st.warning("Add `N8N_WEBHOOK_URL` to Streamlit Secrets.")

    st.markdown("### User")
    new_user = st.text_input("User ID", st.session_state.user_id)
    if new_user and new_user != st.session_state.user_id:
        st.session_state.user_id = new_user
        st.success("User updated.")
        st.rerun()
