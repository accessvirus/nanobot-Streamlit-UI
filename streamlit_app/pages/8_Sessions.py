"""Sessions page - View and manage conversation sessions."""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Sessions")
st.markdown("View and manage conversation sessions")

try:
    from nanobot.config.loader import load_config
    from nanobot.session.manager import SessionManager
    
    config = load_config()
    workspace = config.workspace_path
    session_manager = SessionManager(workspace)
    
    sessions = session_manager.list_sessions()
    
    tab1, tab2 = st.tabs(["Sessions List", "Session Details"])
    
    with tab1:
        if sessions:
            st.subheader("All Sessions")
            
            sessions_data = []
            for session in sessions:
                key = session.get("key", "Unknown")
                created = session.get("created_at", "N/A")
                updated = session.get("updated_at", "N/A")
                
                sessions_data.append({
                    "Session Key": key[:40] + "..." if len(key) > 40 else key,
                    "Created": created[:16] if created and created != "N/A" else "N/A",
                    "Updated": updated[:16] if updated and updated != "N/A" else "N/A"
                })
            
            st.dataframe(sessions_data, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.metric("Total Sessions", len(sessions))
            
            st.markdown(f"**Sessions directory:** `{session_manager.sessions_dir}`")
        else:
            st.info("No sessions found. Sessions are created when you interact with the agent.")
    
    with tab2:
        st.subheader("View Session Content")
        
        if sessions:
            session_keys = [s.get("key", "Unknown") for s in sessions]
            selected_key = st.selectbox("Select Session", session_keys)
            
            if selected_key:
                session = session_manager.get_or_create(selected_key)
                
                st.markdown(f"**Session Key:** `{selected_key}`")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Messages", len(session.messages))
                with col2:
                    st.metric("Last Consolidated", session.last_consolidated)
                with col3:
                    created_str = session.created_at.strftime("%Y-%m-%d %H:%M") if session.created_at else "N/A"
                    st.metric("Created", created_str)
                
                st.markdown("---")
                
                if session.messages:
                    st.subheader("Conversation History")
                    
                    filter_role = st.selectbox("Filter by Role", ["All", "user", "assistant"])
                    
                    messages_to_show = session.messages
                    if filter_role != "All":
                        messages_to_show = [m for m in messages_to_show if m.get("role") == filter_role]
                    
                    for i, msg in enumerate(messages_to_show[-50:]):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        timestamp = msg.get("timestamp", "")
                        tools_used = msg.get("tools_used", [])
                        
                        with st.chat_message(role):
                            st.markdown(content[:500] + "..." if len(content) > 500 else content)
                            
                            if tools_used:
                                st.caption(f"Tools: {', '.join(tools_used)}")
                            
                            if timestamp:
                                st.caption(f"Time: {timestamp[:19]}")
                    
                    if len(messages_to_show) > 50:
                        st.info(f"Showing last 50 of {len(messages_to_show)} messages")
                    
                    st.markdown("---")
                    
                    with st.expander("Export Session"):
                        export_format = st.selectbox("Format", ["JSON", "Markdown"])
                        
                        if export_format == "JSON":
                            export_data = json.dumps(session.messages, indent=2)
                            st.download_button(
                                "Download JSON",
                                export_data,
                                file_name=f"session_{selected_key.replace(':', '_')}.json",
                                mime="application/json"
                            )
                        else:
                            md_lines = []
                            for msg in session.messages:
                                role = msg.get("role", "unknown")
                                content = msg.get("content", "")
                                md_lines.append(f"**{role.upper()}:** {content}\n")
                            
                            export_data = "\n".join(md_lines)
                            st.download_button(
                                "Download Markdown",
                                export_data,
                                file_name=f"session_{selected_key.replace(':', '_')}.md",
                                mime="text/markdown"
                            )
                else:
                    st.info("No messages in this session.")
                
                st.markdown("---")
                
                st.subheader("Session Actions")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("Clear Session Messages"):
                        session.clear()
                        session_manager.save(session)
                        session_manager.invalidate(selected_key)
                        st.success("Session cleared!")
                        st.rerun()
                
                with col_b:
                    if st.button("Delete Session File"):
                        session_path = session_manager._get_session_path(selected_key)
                        if session_path.exists():
                            import os
                            session_path.unlink()
                            session_manager.invalidate(selected_key)
                            st.success("Session file deleted!")
                            st.rerun()
        else:
            st.info("No sessions available to view.")
    
    st.markdown("---")
    
    st.markdown("""
    **About Sessions:**
    
    - Sessions store conversation history in JSONL format
    - Each session is keyed by `channel:chat_id` (e.g., `cli:direct`, `telegram:12345`)
    - Messages are append-only for LLM cache efficiency
    - Old messages are consolidated into memory (MEMORY.md / HISTORY.md)
    - Sessions persist across restarts
    """)
    
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")