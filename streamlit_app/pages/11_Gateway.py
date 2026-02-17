"""Gateway Control page - Start/stop the gateway server."""

import streamlit as st
from pathlib import Path
import sys
import subprocess
import threading
import time
import os
import signal

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Gateway Control")
st.markdown("Start, stop, and monitor the nanobot gateway server")

if "gateway_process" not in st.session_state:
    st.session_state.gateway_process = None

if "gateway_logs" not in st.session_state:
    st.session_state.gateway_logs = []

if "gateway_running" not in st.session_state:
    st.session_state.gateway_running = False

try:
    from nanobot.config.loader import load_config, get_data_dir
    from nanobot.cron.service import CronService
    
    config = load_config()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Host", config.gateway.host)
    
    with col2:
        st.metric("Port", config.gateway.port)
    
    with col3:
        cron_store_path = get_data_dir() / "cron" / "jobs.json"
        cron = CronService(cron_store_path)
        jobs = cron.list_jobs()
        st.metric("Cron Jobs", len(jobs))
    
    st.markdown("---")
    
    col_start, col_stop, col_status = st.columns(3)
    
    with col_start:
        if st.button("▶️ Start Gateway", type="primary", disabled=st.session_state.gateway_running):
            st.session_state.gateway_logs = []
            
            def run_gateway():
                try:
                    process = subprocess.Popen(
                        [sys.executable, "-m", "nanobot", "gateway"],
                        cwd=str(NANOBOT_ROOT),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                    st.session_state.gateway_process = process
                    st.session_state.gateway_running = True
                    
                    for line in process.stdout:
                        st.session_state.gateway_logs.append(line)
                        if len(st.session_state.gateway_logs) > 100:
                            st.session_state.gateway_logs.pop(0)
                    
                    process.wait()
                    st.session_state.gateway_running = False
                except Exception as e:
                    st.session_state.gateway_logs.append(f"Error: {e}\n")
                    st.session_state.gateway_running = False
            
            thread = threading.Thread(target=run_gateway, daemon=True)
            thread.start()
            
            time.sleep(2)
            st.session_state.gateway_running = True
            st.rerun()
    
    with col_stop:
        if st.button("⏹️ Stop Gateway", disabled=not st.session_state.gateway_running):
            if st.session_state.gateway_process:
                try:
                    if os.name == 'nt':
                        st.session_state.gateway_process.terminate()
                    else:
                        os.killpg(os.getpgid(st.session_state.gateway_process.pid), signal.SIGTERM)
                except:
                    pass
                st.session_state.gateway_process = None
            st.session_state.gateway_running = False
            st.rerun()
    
    with col_status:
        status = " Running" if st.session_state.gateway_running else " Stopped"
        st.metric("Status", status)
    
    st.markdown("---")
    
    st.subheader("Gateway Logs")
    
    if st.session_state.gateway_logs:
        log_text = "".join(st.session_state.gateway_logs[-50:])
        st.code(log_text, language="log")
        
        if st.button("Clear Logs"):
            st.session_state.gateway_logs = []
            st.rerun()
    else:
        st.info("No logs yet. Start the gateway to see logs.")
    
    st.markdown("---")
    
    st.subheader("Channel Status")
    
    channels_info = []
    
    for name, cfg in [
        ("Telegram", config.channels.telegram),
        ("Discord", config.channels.discord),
        ("WhatsApp", config.channels.whatsapp),
        ("Feishu", config.channels.feishu),
        ("Slack", config.channels.slack),
        ("Email", config.channels.email),
        ("Mochat", config.channels.mochat),
        ("DingTalk", config.channels.dingtalk),
        ("QQ", config.channels.qq),
    ]:
        channels_info.append({
            "Channel": name,
            "Enabled": "" if cfg.enabled else "N",
            "Allow List": len(cfg.allow_from) if hasattr(cfg, 'allow_from') else 0
        })
    
    st.dataframe(channels_info, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("""
    **Gateway Features:**
    - Starts all enabled channels (Telegram, WhatsApp, etc.)
    - Runs the agent loop for message processing
    - Executes scheduled cron jobs
    - Runs heartbeat service every 30 minutes
    
    **CLI Equivalent:**
    ```
    nanobot gateway
    nanobot gateway --port 18790 --verbose
    ```
    """)
    
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed.")