"""Dashboard page - Overview of Nanobot status."""

import streamlit as st
from pathlib import Path
import sys
import time
from datetime import datetime

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Dashboard")
st.markdown("Overview of your Nanobot AI Assistant")

col1, col2, col3, col4 = st.columns(4)

try:
    from nanobot.config.loader import load_config, get_config_path, get_data_dir
    
    config = load_config()
    config_path = get_config_path()
    workspace = config.workspace_path
    data_dir = get_data_dir()
    
    with col1:
        st.metric("Config", "" if config_path.exists() else "", 
                  delta=str(config_path.parent))
    
    with col2:
        st.metric("Workspace", "" if workspace.exists() else "",
                  delta=str(workspace)[:20] + "...")
    
    with col3:
        model = config.agents.defaults.model
        st.metric("Model", model.split("/")[-1][:15], delta=config.get_provider_name() or "N/A")
    
    with col4:
        temperature = config.agents.defaults.temperature
        max_tokens = config.agents.defaults.max_tokens
        st.metric("Settings", f"T:{temperature}", delta=f"Max tokens: {max_tokens}")

    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader(" Provider Status")
        
        from nanobot.providers.registry import PROVIDERS
        
        provider_data = []
        for spec in PROVIDERS:
            p = getattr(config.providers, spec.name, None)
            if p is None:
                continue
            
            if spec.is_local:
                status = "" if p.api_base else "N"
                value = p.api_base[:30] + "..." if p.api_base else "Not configured"
            elif spec.is_oauth:
                status = "O"
                value = "OAuth"
            else:
                status = "" if p.api_key else "N"
                value = "Configured" if p.api_key else "Not set"
            
            provider_data.append({
                "Provider": spec.label,
                "Status": status,
                "Details": value
            })
        
        if provider_data:
            st.dataframe(provider_data, use_container_width=True, hide_index=True)
        else:
            st.info("No providers found in registry")
    
    with col_right:
        st.subheader(" Channel Status")
        
        channels_data = []
        
        channels_config = [
            ("Telegram", config.channels.telegram),
            ("Discord", config.channels.discord),
            ("WhatsApp", config.channels.whatsapp),
            ("Feishu", config.channels.feishu),
            ("Slack", config.channels.slack),
            ("Email", config.channels.email),
            ("Mochat", config.channels.mochat),
            ("DingTalk", config.channels.dingtalk),
            ("QQ", config.channels.qq),
        ]
        
        for name, cfg in channels_config:
            channels_data.append({
                "Channel": name,
                "Enabled": "" if cfg.enabled else "N",
                "Allow List": len(cfg.allow_from) if hasattr(cfg, 'allow_from') else 0
            })
        
        st.dataframe(channels_data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.subheader("Scheduled Jobs")
    
    try:
        from nanobot.cron.service import CronService
        
        cron_store_path = data_dir / "cron" / "jobs.json"
        cron = CronService(cron_store_path)
        jobs = cron.list_jobs(include_disabled=True)
        
        if jobs:
            jobs_data = []
            for job in jobs[:5]:
                next_run = ""
                if job.state.next_run_at_ms:
                    ts = job.state.next_run_at_ms / 1000
                    next_run = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
                
                jobs_data.append({
                    "ID": job.id,
                    "Name": job.name,
                    "Enabled": "" if job.enabled else "N",
                    "Next Run": next_run
                })
            
            st.dataframe(jobs_data, use_container_width=True, hide_index=True)
            if len(jobs) > 5:
                st.info(f"Showing 5 of {len(jobs)} jobs")
        else:
            st.info("No scheduled jobs")
    except Exception as e:
        st.warning(f"Could not load cron jobs: {str(e)[:50]}")
    
    st.markdown("---")
    
    st.subheader(" Recent Sessions")
    
    try:
        from nanobot.session.manager import SessionManager
        
        session_manager = SessionManager(workspace)
        sessions = session_manager.list_sessions()
        
        if sessions:
            sessions_data = []
            for session in sessions[:5]:
                sessions_data.append({
                    "Session Key": session.get("key", "Unknown")[:30],
                    "Updated": session.get("updated_at", "N/A")[:16] if session.get("updated_at") else "N/A"
                })
            
            st.dataframe(sessions_data, use_container_width=True, hide_index=True)
            if len(sessions) > 5:
                st.info(f"Showing 5 of {len(sessions)} sessions")
        else:
            st.info("No sessions found")
    except Exception as e:
        st.warning(f"Could not load sessions: {str(e)[:50]}")

except Exception as e:
    st.error(f"Error loading configuration: {e}")
    st.info("Run `nanobot onboard` to initialize your configuration.")
