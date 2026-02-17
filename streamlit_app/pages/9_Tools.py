"""Tools Config page - Configure agent tools and settings."""

import streamlit as st
from pathlib import Path
import sys
import json

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Tools Configuration")
st.markdown("Configure agent tools, web search, shell execution, and MCP servers")

try:
    from nanobot.config.loader import load_config, save_config
    from nanobot.config.schema import ToolsConfig, WebSearchConfig, ExecToolConfig, MCPServerConfig
    
    config = load_config()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Agent Defaults", "Web Search", "Shell Execution", "MCP Servers", "Security"
    ])
    
    with tab1:
        st.subheader("Agent Defaults")
        st.markdown("Configure default agent behavior.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            model = st.text_input(
                "Default Model",
                value=config.agents.defaults.model,
                help="Default model for agent (e.g., anthropic/claude-opus-4-5)"
            )
            
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=128000,
                value=config.agents.defaults.max_tokens,
                help="Maximum tokens in LLM response"
            )
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=config.agents.defaults.temperature,
                step=0.1,
                help="Sampling temperature (0 = deterministic, 2 = creative)"
            )
        
        with col2:
            max_tool_iterations = st.number_input(
                "Max Tool Iterations",
                min_value=1,
                max_value=50,
                value=config.agents.defaults.max_tool_iterations,
                help="Maximum tool call iterations per message"
            )
            
            memory_window = st.number_input(
                "Memory Window",
                min_value=10,
                max_value=500,
                value=config.agents.defaults.memory_window,
                help="Number of messages to keep in context before consolidation"
            )
            
            workspace = st.text_input(
                "Workspace Path",
                value=config.agents.defaults.workspace,
                help="Path to the workspace directory"
            )
        
        if st.button("Save Agent Defaults", key="save_agent"):
            config.agents.defaults.model = model
            config.agents.defaults.max_tokens = max_tokens
            config.agents.defaults.temperature = temperature
            config.agents.defaults.max_tool_iterations = max_tool_iterations
            config.agents.defaults.memory_window = memory_window
            config.agents.defaults.workspace = workspace
            save_config(config)
            st.success("Agent defaults saved!")
    
    with tab2:
        st.subheader("Web Search Configuration")
        st.markdown("Configure Brave Search API for web search tool.")
        
        web_config = config.tools.web.search
        
        api_key = st.text_input(
            "Brave Search API Key",
            value=web_config.api_key,
            type="password",
            help="API key from https://brave.com/search/api/"
        )
        
        max_results = st.number_input(
            "Max Results",
            min_value=1,
            max_value=20,
            value=web_config.max_results,
            help="Maximum number of search results to return"
        )
        
        if st.button("Save Web Search Config", key="save_web"):
            config.tools.web.search = WebSearchConfig(
                api_key=api_key,
                max_results=max_results
            )
            save_config(config)
            st.success("Web search configuration saved!")
        
        st.markdown("""
        **Getting a Brave Search API Key:**
        1. Go to https://brave.com/search/api/
        2. Sign up for a free account
        3. Create an API key
        4. Paste the key above
        """)
    
    with tab3:
        st.subheader("Shell Execution Configuration")
        st.markdown("Configure the `exec` tool for running shell commands.")
        
        exec_config = config.tools.exec
        
        timeout = st.number_input(
            "Command Timeout (seconds)",
            min_value=1,
            max_value=600,
            value=exec_config.timeout,
            help="Maximum time for command execution before timeout"
        )
        
        if st.button("Save Shell Config", key="save_shell"):
            config.tools.exec = ExecToolConfig(timeout=timeout)
            save_config(config)
            st.success("Shell configuration saved!")
        
        st.markdown("""
        **Security Notes:**
        - Dangerous commands are blocked (rm -rf /, fork bombs, etc.)
        - Commands run in the workspace directory
        - Output is truncated to 10KB
        - Use `restrictToWorkspace` in Security tab to limit file access
        """)
    
    with tab4:
        st.subheader("MCP Servers")
        st.markdown("Configure Model Context Protocol servers for extended capabilities.")
        
        mcp_servers = dict(config.tools.mcp_servers)
        
        st.markdown("### Configured MCP Servers")
        
        if mcp_servers:
            for name, server_cfg in list(mcp_servers.items()):
                with st.expander(f"{name}", expanded=False):
                    st.markdown(f"**Type:** {'HTTP' if server_cfg.url else 'Stdio'}")
                    
                    if server_cfg.command:
                        st.markdown(f"**Command:** `{server_cfg.command}`")
                        st.markdown(f"**Args:** `{server_cfg.args}`")
                        if server_cfg.env:
                            st.markdown(f"**Env:** `{server_cfg.env}`")
                    
                    if server_cfg.url:
                        st.markdown(f"**URL:** `{server_cfg.url}`")
                    
                    if st.button("Remove", key=f"remove_mcp_{name}"):
                        del config.tools.mcp_servers[name]
                        save_config(config)
                        st.success(f"Removed MCP server: {name}")
                        st.rerun()
        else:
            st.info("No MCP servers configured.")
        
        st.markdown("---")
        st.markdown("### Add MCP Server")
        
        server_name = st.text_input("Server Name", placeholder="filesystem")
        server_type = st.selectbox("Type", ["Stdio", "HTTP"])
        
        if server_type == "Stdio":
            command = st.text_input("Command", placeholder="npx")
            args_str = st.text_input("Arguments (comma-separated)", placeholder="-y, @modelcontextprotocol/server-filesystem, /path")
            env_str = st.text_area("Environment Variables (JSON)", placeholder='{"API_KEY": "xxx"}', height=80)
            url = ""
        else:
            command = ""
            args_str = ""
            env_str = ""
            url = st.text_input("URL", placeholder="http://localhost:8080/mcp")
        
        if st.button("Add MCP Server", key="add_mcp"):
            if not server_name:
                st.error("Server name is required")
            else:
                args = [a.strip() for a in args_str.split(",") if a.strip()] if args_str else []
                
                try:
                    env = json.loads(env_str) if env_str else {}
                except json.JSONDecodeError:
                    env = {}
                
                config.tools.mcp_servers[server_name] = MCPServerConfig(
                    command=command,
                    args=args,
                    env=env,
                    url=url
                )
                save_config(config)
                st.success(f"Added MCP server: {server_name}")
                st.rerun()
        
        st.markdown("""
        **Example MCP Servers:**
        
        **Filesystem (Stdio):**
        - Name: `filesystem`
        - Command: `npx`
        - Args: `-y, @modelcontextprotocol/server-filesystem, /path/to/dir`
        
        **GitHub (Stdio):**
        - Name: `github`
        - Command: `npx`
        - Args: `-y, @modelcontextprotocol/server-github`
        - Env: `{"GITHUB_TOKEN": "ghp_xxx"}`
        """)
    
    with tab5:
        st.subheader("Security Settings")
        st.markdown("Configure security restrictions for agent tools.")
        
        restrict = st.checkbox(
            "Restrict to Workspace",
            value=config.tools.restrict_to_workspace,
            help="If enabled, file tools can only access files in the workspace directory"
        )
        
        if st.button("Save Security Settings", key="save_security"):
            config.tools.restrict_to_workspace = restrict
            save_config(config)
            st.success("Security settings saved!")
        
        st.markdown("""
        **Security Features:**
        
        - **Restrict to Workspace**: Limits file operations to the workspace directory
        - **Dangerous Commands Blocked**: `rm -rf /`, fork bombs, `mkfs`, `dd if=`, shutdown/reboot
        - **Command Timeout**: Limits execution time (default 60s)
        - **Output Truncation**: Limits output to 10KB
        - **Path Traversal Protection**: Prevents `../` escapes
        - **Allow Lists**: Channels can restrict access to specific users
        """)
        
        st.markdown("---")
        
        st.subheader("Gateway Configuration")
        
        gateway_host = st.text_input("Host", value=config.gateway.host)
        gateway_port = st.number_input("Port", value=config.gateway.port)
        
        if st.button("Save Gateway Config", key="save_gateway"):
            config.gateway.host = gateway_host
            config.gateway.port = gateway_port
            save_config(config)
            st.success("Gateway configuration saved!")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")