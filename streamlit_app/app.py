"""
Nanobot Streamlit UI - Full-featured web interface for nanobot AI assistant.
"""

import streamlit as st
from pathlib import Path
import sys

NANOBOT_ROOT = Path(__file__).parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.set_page_config(
    page_title="Nanobot",
    page_icon="🐈",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Nanobot - Lightweight AI Assistant Framework",
        "Get Help": "https://github.com/HKUDS/nanobot",
    }
)

st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    section[data-testid="stSidebar"] {
        display: none;
    }
    section[data-testid="stSidebar"] + div {
        margin-left: 0;
    }
    .top-nav {
        background-color: #1f77b4;
        padding: 10px 20px;
        margin: -10px -20px 20px -20px;
        border-radius: 5px;
    }
    .nav-title {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
    }
    div.stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="top-nav"><span class="nav-title">Nanobot</span></div>', unsafe_allow_html=True)

pages = {
    "Setup": "0_Setup",
    "Dashboard": "1_Dashboard",
    "Chat": "2_Chat",
    "Providers": "3_Providers",
    "Channels": "4_Channels",
    "Cron": "5_Cron",
    "Memory": "6_Memory",
    "Skills": "7_Skills",
    "Sessions": "8_Sessions",
    "Tools": "9_Tools",
    "Workspace": "10_Workspace",
    "Gateway": "11_Gateway",
    "Agent Tools": "12_Agent_Tools",
}

if "current_page" not in st.session_state:
    st.session_state.current_page = "1_Dashboard"

cols_per_row = 7
page_list = list(pages.items())

for row_start in range(0, len(page_list), cols_per_row):
    row_pages = page_list[row_start:row_start + cols_per_row]
    cols = st.columns(len(row_pages))
    for i, (title, page_id) in enumerate(row_pages):
        with cols[i]:
            btn_type = "primary" if st.session_state.current_page == page_id else "secondary"
            if st.button(title, key=f"btn_{page_id}", use_container_width=True, type=btn_type):
                st.session_state.current_page = page_id
                st.rerun()

try:
    from nanobot.config.loader import load_config
    config = load_config()
    
    provider_name = config.get_provider_name() or "Not configured"
    model = config.agents.defaults.model
    
    enabled_channels = []
    for name, cfg in [
        ("Telegram", config.channels.telegram),
        ("Discord", config.channels.discord),
        ("WhatsApp", config.channels.whatsapp),
        ("Slack", config.channels.slack),
    ]:
        if cfg.enabled:
            enabled_channels.append(name)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"Provider: {provider_name}")
    with col2:
        st.caption(f"Model: {model.split('/')[-1]}")
    with col3:
        st.caption(f"Channels: {', '.join(enabled_channels) if enabled_channels else 'None'}")
except Exception:
    pass

st.markdown("---")

page_file = Path(__file__).parent / "pages" / f"{st.session_state.current_page}.py"
if page_file.exists():
    with open(page_file, encoding="utf-8") as f:
        code = compile(f.read(), page_file, "exec")
        exec(code, {"__name__": "__main__", "__file__": str(page_file)})