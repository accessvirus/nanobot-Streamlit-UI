"""Memory page - View and manage agent memory."""

import streamlit as st
from pathlib import Path
import sys

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Memory")
st.markdown("View and manage your agent's persistent memory")

try:
    from nanobot.config.loader import load_config
    from nanobot.agent.memory import MemoryStore
    
    config = load_config()
    workspace = config.workspace_path
    memory = MemoryStore(workspace)
    
    tab1, tab2, tab3 = st.tabs(["Long-term Memory", "History Log", "Edit Memory"])
    
    with tab1:
        st.subheader("MEMORY.md")
        st.markdown("Long-term facts about the user, preferences, and important context.")
        
        long_term = memory.read_long_term()
        
        if long_term:
            st.markdown(long_term)
        else:
            st.info("No long-term memory yet. Memory will be built as you interact with the agent.")
        
        st.markdown("---")
        st.markdown(f"**File location:** `{memory.memory_file}`")
        
        if memory.memory_file.exists():
            stat = memory.memory_file.stat()
            from datetime import datetime
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Last modified: {modified} | Size: {stat.st_size} bytes")
    
    with tab2:
        st.subheader("HISTORY.md")
        st.markdown("Append-only log of conversation events and decisions (grep-searchable).")
        
        if memory.history_file.exists():
            history_content = memory.history_file.read_text(encoding="utf-8")
            
            if history_content:
                search = st.text_input("Search history", placeholder="Enter search term...")
                
                if search:
                    lines = history_content.split("\n")
                    matching = [l for l in lines if search.lower() in l.lower()]
                    
                    st.markdown(f"**Found {len(matching)} matching lines:**")
                    for line in matching[:50]:
                        if line.strip():
                            st.markdown(f"> {line}")
                    
                    if len(matching) > 50:
                        st.info(f"Showing 50 of {len(matching)} results")
                else:
                    with st.expander("View Full History", expanded=False):
                        st.markdown(history_content)
                    
                    lines = history_content.split("\n")
                    non_empty = [l for l in lines if l.strip()]
                    st.caption(f"Total entries: {len(non_empty)}")
            else:
                st.info("History log is empty. Events will be logged as memory consolidation occurs.")
        else:
            st.info("No history log exists yet. It will be created during memory consolidation.")
        
        st.markdown("---")
        st.markdown(f"**File location:** `{memory.history_file}`")
    
    with tab3:
        st.subheader("Edit Long-term Memory")
        st.markdown("Manually add or modify facts stored in MEMORY.md")
        
        current_memory = memory.read_long_term()
        
        new_content = st.text_area(
            "Memory Content",
            value=current_memory,
            height=400,
            help="Edit this content to add or modify long-term memory"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Memory", type="primary"):
                memory.write_long_term(new_content)
                st.success("Memory saved!")
                st.rerun()
        
        with col2:
            if st.button("Append to History"):
                entry = st.text_area("Entry to append", height=100)
                if entry:
                    memory.append_history(entry)
                    st.success("Entry appended to history!")
        
        st.markdown("---")
        st.markdown("""
        **Memory Guidelines:**
        - **Long-term Memory (MEMORY.md)**: Store facts, preferences, and important context
        - **History Log (HISTORY.md)**: Append-only event log for grep-searchable records
        
        The agent automatically consolidates old conversations into memory during sessions.
        You can manually edit these files to add or correct information.
        """)
    
    st.markdown("---")
    
    st.subheader("Memory Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        memory_exists = memory.memory_file.exists()
        st.metric("Memory File", "" if memory_exists else "N")
    
    with col2:
        history_exists = memory.history_file.exists()
        st.metric("History File", "" if history_exists else "N")
    
    with col3:
        if memory.memory_file.exists():
            content = memory.read_long_term()
            st.metric("Memory Lines", len(content.split("\n")))
        else:
            st.metric("Memory Lines", 0)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")