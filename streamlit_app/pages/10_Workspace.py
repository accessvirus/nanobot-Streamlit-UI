"""Workspace page - Manage workspace files and templates."""

import streamlit as st
from pathlib import Path
import sys

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Workspace")
st.markdown("Manage workspace files, templates, and heartbeat tasks")

try:
    from nanobot.config.loader import load_config
    
    config = load_config()
    workspace = config.workspace_path
    
    if not workspace.exists():
        workspace.mkdir(parents=True, exist_ok=True)
    
    st.markdown(f"**Workspace:** `{workspace}`")
    
    tab1, tab2, tab3, tab4 = st.tabs(["AGENTS.md", "SOUL.md", "USER.md", "HEARTBEAT.md"])
    
    def render_file_editor(filename, description, default_content=None):
        file_path = workspace / filename
        
        col1, col2 = st.columns([4, 1])
        
        with col2:
            if file_path.exists():
                stat = file_path.stat()
                from datetime import datetime
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                st.caption(f"Modified: {modified}")
                st.caption(f"Size: {stat.st_size} bytes")
        
        content = ""
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
        elif default_content:
            content = default_content
        
        new_content = st.text_area(
            description,
            value=content,
            height=400,
            key=f"editor_{filename}"
        )
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("Save", key=f"save_{filename}"):
                file_path.write_text(new_content, encoding="utf-8")
                st.success(f"Saved {filename}!")
                st.rerun()
        
        with col_b:
            if st.button("Reset to Default", key=f"reset_{filename}") and default_content:
                file_path.write_text(default_content, encoding="utf-8")
                st.success(f"Reset {filename} to default!")
                st.rerun()
        
        with col_c:
            if file_path.exists() and content:
                st.download_button(
                    "Download",
                    content,
                    file_name=filename,
                    mime="text/markdown",
                    key=f"download_{filename}"
                )
        
        return file_path
    
    with tab1:
        st.subheader("Agent Instructions")
        st.markdown("Instructions that define how the agent behaves.")
        
        default_agents = """# Agent Instructions

You are a helpful AI assistant. Be concise, accurate, and friendly.

## Guidelines

- Always explain what you're doing before taking actions
- Ask for clarification when the request is ambiguous
- Use tools to help accomplish tasks
- Remember important information in memory/MEMORY.md; past events are logged in memory/HISTORY.md
"""
        render_file_editor("AGENTS.md", "Agent instructions", default_agents)
    
    with tab2:
        st.subheader("Agent Soul/Personality")
        st.markdown("Defines the agent's personality and values.")
        
        default_soul = """# Soul

I am nanobot, a lightweight AI assistant.

## Personality

- Helpful and friendly
- Concise and to the point
- Curious and eager to learn

## Values

- Accuracy over speed
- User privacy and safety
- Transparency in actions
"""
        render_file_editor("SOUL.md", "Agent personality", default_soul)
    
    with tab3:
        st.subheader("User Information")
        st.markdown("Information about the user (preferences, context).")
        
        default_user = """# User

Information about the user goes here.

## Preferences

- Communication style: (casual/formal)
- Timezone: (your timezone)
- Language: (your preferred language)

## Projects

(Information about ongoing projects)

## Important Dates

(Birthdays, anniversaries, deadlines)
"""
        render_file_editor("USER.md", "User information", default_user)
    
    with tab4:
        st.subheader("Heartbeat Tasks")
        st.markdown("Tasks that run periodically (checked every 30 minutes).")
        
        heartbeat_path = workspace / "HEARTBEAT.md"
        
        st.markdown("""
        **How Heartbeat Works:**
        - The service checks this file every 30 minutes
        - If the file contains actionable content, it's sent to the agent
        - Leave empty or with non-actionable text to skip
        """)
        
        default_heartbeat = """# Heartbeat Tasks

This file is checked periodically for tasks to execute.

## Current Tasks

(Add tasks here for the agent to process periodically)

Example:
- Check for any urgent emails and summarize
- Review calendar for upcoming meetings today
- Check system status and report any issues
"""
        
        content = ""
        if heartbeat_path.exists():
            content = heartbeat_path.read_text(encoding="utf-8")
        else:
            content = default_heartbeat
        
        new_content = st.text_area(
            "Heartbeat content",
            value=content,
            height=300,
            key="editor_heartbeat"
        )
        
        if st.button("Save HEARTBEAT.md", key="save_heartbeat"):
            heartbeat_path.write_text(new_content, encoding="utf-8")
            st.success("Saved HEARTBEAT.md!")
        
        st.markdown("---")
        
        st.subheader("Other Workspace Files")
        
        skills_dir = workspace / "skills"
        if skills_dir.exists():
            st.markdown(f"**Skills Directory:** `{skills_dir}`")
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    st.markdown(f"-  `{skill_dir.name}/`")
        
        memory_dir = workspace / "memory"
        if memory_dir.exists():
            st.markdown(f"**Memory Directory:** `{memory_dir}`")
            for mem_file in memory_dir.iterdir():
                if mem_file.is_file():
                    st.markdown(f"-  `{mem_file.name}`")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")