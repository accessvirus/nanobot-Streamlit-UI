"""Tools page - View available agent tools."""

import streamlit as st
from pathlib import Path
import sys

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title("️ Agent Tools")
st.markdown("View available tools the agent can use")

TOOLS_INFO = [
    {
        "name": "read_file",
        "description": "Read file contents from the filesystem",
        "parameters": ["path: str - Path to the file to read"],
        "category": "Filesystem"
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating it if it doesn't exist",
        "parameters": ["path: str - Path to write to", "content: str - Content to write"],
        "category": "Filesystem"
    },
    {
        "name": "edit_file",
        "description": "Replace text in a file (find and replace)",
        "parameters": ["path: str - Path to the file", "old_text: str - Text to find", "new_text: str - Replacement text"],
        "category": "Filesystem"
    },
    {
        "name": "list_dir",
        "description": "List contents of a directory",
        "parameters": ["path: str - Directory path to list"],
        "category": "Filesystem"
    },
    {
        "name": "exec",
        "description": "Execute shell commands with safety guards",
        "parameters": ["command: str - Command to execute", "timeout: int - Timeout in seconds (default 60)"],
        "category": "Shell"
    },
    {
        "name": "web_search",
        "description": "Search the web using Brave Search API",
        "parameters": ["query: str - Search query", "max_results: int - Max results (default 5)"],
        "category": "Web"
    },
    {
        "name": "web_fetch",
        "description": "Fetch and extract content from URLs",
        "parameters": ["url: str - URL to fetch"],
        "category": "Web"
    },
    {
        "name": "message",
        "description": "Send messages to chat channels",
        "parameters": ["content: str - Message content", "channel: str - Target channel", "chat_id: str - Target chat"],
        "category": "Communication"
    },
    {
        "name": "spawn",
        "description": "Create background subagents for independent tasks",
        "parameters": ["task: str - Task description", "context: str - Additional context"],
        "category": "Agent"
    },
    {
        "name": "cron",
        "description": "Schedule reminders and recurring tasks",
        "parameters": ["action: str - 'add', 'list', or 'remove'", "name: str - Job name", "schedule: dict - Schedule config"],
        "category": "Scheduling"
    },
    {
        "name": "mcp",
        "description": "Connect to MCP servers and use their tools",
        "parameters": ["server: str - Server name", "tool: str - Tool name", "args: dict - Tool arguments"],
        "category": "MCP"
    }
]

categories = sorted(set(t["category"] for t in TOOLS_INFO))

tab_all = st.tabs(["All Tools"] + categories)

with tab_all[0]:
    for tool in TOOLS_INFO:
        with st.expander(f"`{tool['name']}` - {tool['category']}", expanded=False):
            st.markdown(f"**Description:** {tool['description']}")
            st.markdown("**Parameters:**")
            for param in tool["parameters"]:
                st.markdown(f"- `{param}`")

for i, category in enumerate(categories):
    with tab_all[i + 1]:
        for tool in TOOLS_INFO:
            if tool["category"] == category:
                with st.expander(f"`{tool['name']}`", expanded=False):
                    st.markdown(f"**Description:** {tool['description']}")
                    st.markdown("**Parameters:**")
                    for param in tool["parameters"]:
                        st.markdown(f"- `{param}`")

st.markdown("---")
st.markdown("## Tool Safety Features")

safety_features = [
    ("Path Traversal Protection", "Prevents `../` escapes from workspace"),
    ("Dangerous Command Blocking", "Blocks `rm -rf /`, fork bombs, `mkfs`, `dd if=`, shutdown/reboot"),
    ("Command Timeout", "Limits execution time (default 60s)"),
    ("Output Truncation", "Limits output to 10KB"),
    ("Workspace Restriction", "Optional mode to restrict file access to workspace directory"),
]

for feature, desc in safety_features:
    st.markdown(f"- **{feature}:** {desc}")

st.markdown("---")
st.markdown("## Blocked Patterns")

blocked = [
    "rm -rf /",
    "rm -rf /*",
    ":(){ :|:& };:",  # Fork bomb
    "mkfs",
    "dd if=",
    "dd of=/dev/",
    "shutdown",
    "reboot",
    "init 0",
    "init 6",
]

st.code("\n".join(blocked), language="bash")