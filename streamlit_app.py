import streamlit as st
import streamlit.components.v1 as components
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
# Level 11 Cyberpunk Styling (Background + Grid + Scanlines + Neon Buttons)
# ----------------------------
st.markdown(
    """
    <style>
    /* =====================================================
       🔥 LEVEL 11: CYBERPUNK HOLOGRAPHIC OVERDRIVE
       ===================================================== */

    :root{
      --pink: #ff00ff;
      --cyan: #00ffff;
      --mint: #00ff88;
      --amber:#ff7a00;
      --violet:#7f00ff;

      --glass: rgba(255,255,255,.06);
      --glass2: rgba(255,255,255,.10);
      --stroke: rgba(255,255,255,.18);
      --stroke2: rgba(255,255,255,.28);
    }

    /* Streamlit base paddings */
    .block-container { padding-top: 1.25rem; padding-bottom: 2rem; }

    html, body, [data-testid="stAppViewContainer"]{
      height: 100%;
      overflow-x: hidden;
      background:
        radial-gradient(circle at 12% 18%, rgba(255,0,255,.55), transparent 42%),
        radial-gradient(circle at 85% 14%, rgba(0,255,255,.50), transparent 46%),
        radial-gradient(circle at 20% 88%, rgba(0,255,140,.42), transparent 52%),
        radial-gradient(circle at 88% 82%, rgba(255,120,0,.40), transparent 54%),
        radial-gradient(circle at 55% 45%, rgba(127,0,255,.30), transparent 60%),
        linear-gradient(180deg, #02020a 0%, #050514 45%, #020208 100%);
      background-attachment: fixed;
    }

    /* ===== Glow field (z=0) ===== */
    [data-testid="stAppViewContainer"]::before{
      content:"";
      position: fixed;
      inset:-55%;
      pointer-events:none;
      background:
        radial-gradient(circle at 20% 25%, rgba(255,0,255,.40), transparent 40%),
        radial-gradient(circle at 70% 25%, rgba(0,255,255,.40), transparent 45%),
        radial-gradient(circle at 30% 80%, rgba(0,255,140,.32), transparent 52%),
        radial-gradient(circle at 85% 75%, rgba(255,120,0,.30), transparent 52%),
        radial-gradient(circle at 55% 55%, rgba(127,0,255,.25), transparent 60%);
      filter: blur(75px);
      animation: auroraFloat 10s ease-in-out infinite alternate;
      z-index: 0;
    }

    @keyframes auroraFloat{
      0%   { transform: translate(-6%, -4%) scale(1.05) rotate(0deg); }
      50%  { transform: translate(6%, 5%)   scale(1.18) rotate(7deg); }
      100% { transform: translate(10%, -7%) scale(1.25) rotate(-7deg); }
    }

    /* ===== Tron grid floor (z=0) ===== */
    [data-testid="stAppViewContainer"]::after{
      content:"";
      position: fixed;
      left:0; right:0;
      bottom:-35vh;
      height: 70vh;
      pointer-events:none;
      background:
        linear-gradient(to top, rgba(0,255,255,.24), rgba(0,0,0,0) 60%),
        repeating-linear-gradient(
          90deg,
          rgba(0,255,255,.18) 0px,
          rgba(0,255,255,.18) 1px,
          rgba(0,0,0,0) 1px,
          rgba(0,0,0,0) 38px
        ),
        repeating-linear-gradient(
          0deg,
          rgba(255,0,255,.16) 0px,
          rgba(255,0,255,.16) 1px,
          rgba(0,0,0,0) 1px,
          rgba(0,0,0,0) 42px
        );
      transform-origin: bottom;
      transform: perspective(900px) rotateX(62deg);
      filter: blur(.2px);
      opacity: .75;
      animation: gridPulse 2.8s ease-in-out infinite alternate;
      z-index: 0;
    }

    @keyframes gridPulse{
      0%   { opacity: .55; }
      100% { opacity: .85; }
    }

    /* Keep Streamlit content above FX layers */
    [data-testid="stAppViewContainer"] > .main{
      position: relative;
      z-index: 2;
    }

    /* ===== Scanlines + flicker (z=3) ===== */
    body::before{
      content:"";
      position: fixed;
      inset: 0;
      pointer-events:none;
      background:
        repeating-linear-gradient(
          to bottom,
          rgba(255,255,255,.05) 0px,
          rgba(255,255,255,.05) 1px,
          rgba(0,0,0,0) 3px,
          rgba(0,0,0,0) 6px
        );
      mix-blend-mode: overlay;
      opacity: .10;
      z-index: 3;
      animation: scanFlicker 6s ease-in-out infinite;
    }

    @keyframes scanFlicker{
      0%, 100% { opacity: .08; }
      50%      { opacity: .13; }
    }

    /* ===== Sparkle texture (z=3) ===== */
    body::after{
      content:"";
      position: fixed;
      inset: 0;
      pointer-events:none;
      background-image:
        radial-gradient(rgba(255,255,255,.35) 1px, transparent 1px),
        radial-gradient(rgba(0,255,255,.25) 1px, transparent 1px),
        radial-gradient(rgba(255,0,255,.18) 1px, transparent 1px);
      background-size: 120px 120px, 180px 180px, 240px 240px;
      background-position: 0 0, 40px 70px, 90px 30px;
      opacity: .08;
      z-index: 3;
      animation: sparkleDrift 14s linear infinite;
    }

    @keyframes sparkleDrift{
      0%   { transform: translate(0,0); }
      100% { transform: translate(-120px, -180px); }
    }

    /* Sidebar hologlass */
    [data-testid="stSidebar"]{
      background: rgba(6,8,18,.78) !important;
      backdrop-filter: blur(20px);
      border-right: 1px solid var(--stroke) !important;
      box-shadow:
        0 0 25px rgba(0,255,255,.14),
        0 0 40px rgba(255,0,255,.10);
    }

    /* Topbar + Cards */
    .topbar, .card{
      background: linear-gradient(135deg, rgba(255,255,255,.07), rgba(255,255,255,.03)) !important;
      border: 1px solid var(--stroke2) !important;
      backdrop-filter: blur(18px);
      border-radius: 14px;
      box-shadow:
        0 0 18px rgba(255,0,255,.14),
        0 0 22px rgba(0,255,255,.12),
        inset 0 0 0 1px rgba(255,255,255,.08);
      position: relative;
      overflow: hidden;
    }

    .topbar::before, .card::before{
      content:"";
      position:absolute;
      inset:-40%;
      background: linear-gradient(
        90deg,
        rgba(255,0,255,.0),
        rgba(0,255,255,.22),
        rgba(0,255,140,.18),
        rgba(255,120,0,.16),
        rgba(255,0,255,.0)
      );
      transform: rotate(10deg);
      filter: blur(18px);
      opacity: .0;
      animation: holoSweep 5.2s ease-in-out infinite;
      pointer-events:none;
    }

    @keyframes holoSweep{
      0%   { transform: translateX(-20%) rotate(10deg); opacity: 0; }
      35%  { opacity: .55; }
      60%  { opacity: .35; }
      100% { transform: translateX(20%) rotate(10deg); opacity: 0; }
    }

    /* Animated gradient header text */
    .brand, h1, h2, h3{
      background: linear-gradient(90deg, var(--pink), var(--cyan), var(--mint), var(--amber), var(--violet), var(--pink));
      background-size: 300% 100%;
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent !important;
      animation: textFlow 4s linear infinite;
      text-shadow:
        0 0 12px rgba(255,0,255,.22),
        0 0 14px rgba(0,255,255,.18);
    }

    @keyframes textFlow{
      0%   { background-position: 0% 50%; }
      100% { background-position: 100% 50%; }
    }

    /* Chips + subtle text */
    .chip {
      display:inline-flex; align-items:center; gap:.45rem;
      padding: .25rem .55rem; border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.18);
      background: rgba(255,255,255,0.06);
      font-size: .82rem;
      color: rgba(255,255,255,0.80);
      box-shadow: 0 0 14px rgba(0,255,255,.10);
    }
    .subtle { color: rgba(255,255,255,0.72); font-size: 0.9rem; }
    .tiny { font-size: 0.82rem; color: rgba(255,255,255,0.72); }
    .divider { height:1px; background: rgba(255,255,255,0.12); margin: .75rem 0; }

    /* ULTRA NEON buttons */
    div.stButton > button{
      border-radius: 999px !important;
      border: 1px solid rgba(255,255,255,.28) !important;
      background: rgba(255,255,255,.09) !important;
      color: white !important;
      padding: .70rem 1.25rem !important;
      font-weight: 700 !important;
      letter-spacing: .4px;
      transition: transform .16s ease, box-shadow .2s ease, background .2s ease, border-color .2s ease;
      position: relative;
      overflow: hidden;
      box-shadow: 0 0 0 rgba(0,0,0,0);
    }

    div.stButton > button::before{
      content:"";
      position:absolute;
      inset:-3px;
      background: linear-gradient(90deg, var(--pink), var(--cyan), var(--mint), var(--amber), var(--violet), var(--pink));
      background-size: 320% 320%;
      filter: blur(14px);
      opacity: 0;
      transition: opacity .18s ease;
      animation: auraFlow 3.2s linear infinite;
      z-index: 0;
      pointer-events:none;
    }

    @keyframes auraFlow{
      0%   { background-position: 0% 50%; }
      100% { background-position: 100% 50%; }
    }

    div.stButton > button > div{
      position: relative;
      z-index: 1;
    }

    div.stButton > button:hover{
      transform: translateY(-3px) scale(1.05);
      border-color: rgba(255,255,255,.65) !important;
      background: rgba(255,255,255,.14) !important;
      box-shadow:
        0 0 22px rgba(255,0,255,.55),
        0 0 32px rgba(0,255,255,.42),
        0 0 44px rgba(0,255,140,.30),
        0 0 70px rgba(255,120,0,.24);
    }

    div.stButton > button:hover::before{
      opacity: 1;
    }

    div.stButton > button:active{
      transform: translateY(0px) scale(.98);
      box-shadow:
        0 0 18px rgba(255,0,255,.42),
        0 0 24px rgba(0,255,255,.30);
    }

    /* Chat bubble glow */
    [data-testid="stChatMessage"]{
      background: rgba(255,255,255,.05);
      border: 1px solid var(--stroke2);
      border-radius: 18px;
      backdrop-filter: blur(14px);
      box-shadow:
        0 0 14px rgba(255,0,255,.16),
        0 0 18px rgba(0,255,255,.14);
    }

    /* Scrollbar neon */
    ::-webkit-scrollbar { width: 9px; }
    ::-webkit-scrollbar-thumb{
      background: linear-gradient(var(--pink), var(--cyan), var(--mint));
      border-radius: 12px;
      box-shadow: 0 0 14px rgba(0,255,255,.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Neon particle canvas overlay (REAL particles)
# ----------------------------
def neon_particles_overlay(
    particle_count: int = 110,
    max_speed: float = 0.60,
    link_distance: int = 150,
    opacity: float = 0.70,
):
    html = f"""
    <style>
      #neon-particles-wrap {{
        position: fixed;
        inset: 0;
        z-index: 1;              /* behind Streamlit content (z=2), above background (z=0) */
        pointer-events: none;
      }}
      canvas#neon-particles {{
        width: 100%;
        height: 100%;
        display: block;
        filter: drop-shadow(0 0 10px rgba(0,255,255,.15)) drop-shadow(0 0 16px rgba(255,0,255,.10));
        opacity: {opacity};
      }}
    </style>

    <div id="neon-particles-wrap">
      <canvas id="neon-particles"></canvas>
    </div>

    <script>
      (function() {{
        const canvas = document.getElementById("neon-particles");
        const ctx = canvas.getContext("2d");

        const COLORS = [
          [255, 0, 255],
          [0, 255, 255],
          [0, 255, 136],
          [255, 122, 0],
          [127, 0, 255]
        ];

        function resize() {{
          const dpr = window.devicePixelRatio || 1;
          canvas.width = Math.floor(window.innerWidth * dpr);
          canvas.height = Math.floor(window.innerHeight * dpr);
          canvas.style.width = window.innerWidth + "px";
          canvas.style.height = window.innerHeight + "px";
          ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }}
        window.addEventListener("resize", resize);
        resize();

        const W = () => window.innerWidth;
        const H = () => window.innerHeight;

        const N = {particle_count};
        const MAX_SPEED = {max_speed};
        const LINK_DIST = {link_distance};

        const particles = [];
        for (let i = 0; i < N; i++) {{
          const c = COLORS[Math.floor(Math.random() * COLORS.length)];
          particles.push({{
            x: Math.random() * W(),
            y: Math.random() * H(),
            vx: (Math.random() * 2 - 1) * MAX_SPEED,
            vy: (Math.random() * 2 - 1) * MAX_SPEED,
            r: 1.2 + Math.random() * 1.9,
            c
          }});
        }}

        let mx = W() / 2, my = H() / 2;
        window.addEventListener("mousemove", (e) => {{
          mx = e.clientX; my = e.clientY;
        }});

        function rgba(rgb, a) {{
          return `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${a})`;
        }}

        function step() {{
          ctx.clearRect(0, 0, W(), H());

          for (const p of particles) {{
            const dxm = mx - p.x;
            const dym = my - p.y;
            const distm = Math.sqrt(dxm*dxm + dym*dym) + 0.001;
            const pull = Math.min(0.018, 0.9 / distm);
            p.vx += (dxm / distm) * pull * 0.03;
            p.vy += (dym / distm) * pull * 0.03;

            const sp = Math.sqrt(p.vx*p.vx + p.vy*p.vy) + 0.001;
            const cap = MAX_SPEED * 1.6;
            if (sp > cap) {{
              p.vx = (p.vx / sp) * cap;
              p.vy = (p.vy / sp) * cap;
            }}

            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0) {{ p.x = 0; p.vx *= -1; }}
            if (p.x > W()) {{ p.x = W(); p.vx *= -1; }}
            if (p.y < 0) {{ p.y = 0; p.vy *= -1; }}
            if (p.y > H()) {{ p.y = H(); p.vy *= -1; }}

            ctx.beginPath();
            ctx.fillStyle = rgba(p.c, 0.82);
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fill();

            ctx.beginPath();
            ctx.fillStyle = "rgba(255,255,255,0.65)";
            ctx.arc(p.x, p.y, Math.max(0.6, p.r * 0.35), 0, Math.PI * 2);
            ctx.fill();
          }}

          for (let i = 0; i < particles.length; i++) {{
            for (let j = i + 1; j < particles.length; j++) {{
              const a = particles[i];
              const b = particles[j];
              const dx = a.x - b.x;
              const dy = a.y - b.y;
              const d = Math.sqrt(dx*dx + dy*dy);
              if (d < LINK_DIST) {{
                const t = 1 - (d / LINK_DIST);
                const c = [
                  (a.c[0] + b.c[0]) / 2,
                  (a.c[1] + b.c[1]) / 2,
                  (a.c[2] + b.c[2]) / 2
                ];
                ctx.strokeStyle = rgba(c, 0.22 * t);
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();
              }}
            }}
          }}

          requestAnimationFrame(step);
        }}

        step();
      }})();
    </script>
    """
    components.html(html, height=0, width=0)

# Call it once (top-level)
neon_particles_overlay()

# ----------------------------
# Session state
# ----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess-{int(datetime.utcnow().timestamp())}"

if "user_id" not in st.session_state:
    st.session_state.user_id = "aminul@hustadcompanies.com"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "page" not in st.session_state:
    st.session_state.page = "Chat"

# ----------------------------
# Helpers (FIX: normalize n8n shapes + prevent double output)
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

    try:
        resp = r.json()
    except Exception:
        return {"message": r.text, "data": {}, "raw": {"rawText": r.text}}

    raw = resp

    # n8n often returns a list: [{...}]
    if isinstance(resp, list):
        resp = resp[0] if resp else {}

    message_out = ""
    data_out = {}

    if isinstance(resp, dict):
        if isinstance(resp.get("message"), str):
            message_out = resp["message"]
            data_out = resp.get("data") or {}

        elif "reply" in resp:
            reply = resp["reply"]
            if isinstance(reply, dict):
                message_out = reply.get("message") or reply.get("output") or ""
                data_out = reply.get("data") or reply
            else:
                message_out = str(reply)

        elif "output" in resp:
            message_out = str(resp["output"])
            data_out = resp.get("data") or {}

        else:
            # IMPORTANT: don't dump full json as message (that creates the "second output" feel)
            message_out = "Done."
            data_out = resp
    else:
        message_out = str(resp)

    # If backend duplicates text in data.output, drop it to avoid double-render patterns
    if isinstance(data_out, dict) and isinstance(data_out.get("output"), str):
        data_out.pop("output", None)

    return {"message": message_out or "—", "data": data_out or {}, "raw": raw}

def looks_like_property(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    if "chosen" in data and isinstance(data["chosen"], dict):
        attrs = data["chosen"].get("attributes", {}) or {}
        return "name" in attrs or "streetAddress" in attrs
    return any(k in data for k in ["Property name", "roofType", "numberOfBuildings", "attributes"])

def render_property_card(data: dict):
    attrs = {}
    link = None

    if isinstance(data, dict) and "chosen" in data and isinstance(data["chosen"], dict):
        attrs = data["chosen"].get("attributes", {}) or {}
        opt = data["chosen"].get("options", {}) or {}
        link = opt.get("text") or data.get("link")

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
    st.markdown(
        f"""
        <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:1rem;">
          <div>
            <div style="font-size:1.15rem; font-weight:800;">{name or "Property"}</div>
            <div class="subtle">{address or "—"}</div>
          </div>
          <div class="chip">🏢 Property</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Buildings", buildings if buildings is not None else "—")
    c2.metric("Squares", squares if squares is not None else "—")
    c3.metric("Close Rate", f"{close_rate}%" if close_rate is not None else "—")
    c4.metric("Roof", roof if roof else "—")

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

# ----------------------------
# Sidebar (Navigation + Debug Toggle)
# ----------------------------
with st.sidebar:
    st.markdown("### Hustad AI")
    st.caption("Internal assistant dashboard")

    show_debug = st.checkbox("Show debug (raw responses)", value=False)

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
    """
    <div class="topbar" style="display:flex; align-items:center; justify-content:space-between; padding:0.85rem 1rem;">
      <div>
        <div class="brand" style="font-size:1.1rem; font-weight:900; letter-spacing:.2px;">Hustad AI Assistant</div>
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
    left, right = st.columns([2.2, 1], gap="large")

    with left:
        # Chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if show_debug and msg.get("raw") is not None and msg["role"] == "assistant":
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
                    st.write(resp.get("message", "Here’s what I found:"))
                    render_property_card(resp.get("data", {}))
                    assistant_text = resp.get("message", "Here’s what I found:")
                else:
                    st.write(resp.get("message", "") or "—")
                    assistant_text = resp.get("message", "") or "—"

                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_text, "raw": resp.get("raw")}
                )

                if show_debug:
                    with st.expander("Debug / Raw response (latest)", expanded=False):
                        st.json(resp.get("raw"))

            st.rerun()

    with right:
        st.markdown('<div class="card" style="padding:1rem;">', unsafe_allow_html=True)
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
            st.session_state.messages.append(
                {"role": "user", "content": "create service ticket for Riverport Landings Senior"}
            )
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Recent Activity":
    st.markdown("## Recent Activity")
    st.caption("A simple timeline of user requests + assistant responses.")

    if not st.session_state.messages:
        st.info("No activity yet.")
    else:
        for m in st.session_state.messages[-30:]:
            st.markdown('<div class="card" style="padding:1rem;">', unsafe_allow_html=True)
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
