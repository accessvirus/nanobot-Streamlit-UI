"""Chat page - Direct interaction with the agent."""

import streamlit as st
from pathlib import Path
import sys
import asyncio

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Chat")
st.markdown("Direct interaction with your Nanobot AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_loop" not in st.session_state:
    st.session_state.agent_loop = None

def init_agent():
    if st.session_state.agent_loop is not None:
        return st.session_state.agent_loop
    
    try:
        from nanobot.config.loader import load_config, get_data_dir
        from nanobot.bus.queue import MessageBus
        from nanobot.agent.loop import AgentLoop
        from nanobot.cron.service import CronService
        from nanobot.providers.litellm_provider import LiteLLMProvider
        from nanobot.providers.openai_codex_provider import OpenAICodexProvider
        from nanobot.providers.registry import find_by_name
        
        config = load_config()
        bus = MessageBus()
        
        model = config.agents.defaults.model
        provider_name = config.get_provider_name(model)
        p = config.get_provider(model)
        
        if provider_name == "openai_codex" or model.startswith("openai-codex/"):
            provider = OpenAICodexProvider(default_model=model)
        else:
            spec = find_by_name(provider_name)
            if not model.startswith("bedrock/") and not (p and p.api_key) and not (spec and spec.is_oauth):
                return None
            
            provider = LiteLLMProvider(
                api_key=p.api_key if p else None,
                api_base=config.get_api_base(model),
                default_model=model,
                extra_headers=p.extra_headers if p else None,
                provider_name=provider_name,
            )
        
        cron_store_path = get_data_dir() / "cron" / "jobs.json"
        cron = CronService(cron_store_path)
        
        agent_loop = AgentLoop(
            bus=bus,
            provider=provider,
            workspace=config.workspace_path,
            model=config.agents.defaults.model,
            temperature=config.agents.defaults.temperature,
            max_tokens=config.agents.defaults.max_tokens,
            max_iterations=config.agents.defaults.max_tool_iterations,
            memory_window=config.agents.defaults.memory_window,
            brave_api_key=config.tools.web.search.api_key or None,
            exec_config=config.tools.exec,
            cron_service=cron,
            restrict_to_workspace=config.tools.restrict_to_workspace,
            mcp_servers=config.tools.mcp_servers,
        )
        
        st.session_state.agent_loop = agent_loop
        return agent_loop
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return None

with st.sidebar:
    st.markdown("### Chat Settings")
    
    session_id = st.text_input("Session ID", value="cli:webui", key="session_id")
    
    st.markdown("### Session Commands")
    if st.button("Clear Session"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("New Session"):
        st.session_state.messages = []
        st.session_state.agent_loop = None
        st.rerun()

try:
    from nanobot.config.loader import load_config
    config = load_config()
    
    model = config.agents.defaults.model
    provider_name = config.get_provider_name() or "Not configured"
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Model:** {model}")
    with col2:
        st.info(f"**Provider:** {provider_name}")
    
except Exception as e:
    st.warning(f"Configuration not loaded: {str(e)[:50]}")

st.markdown("---")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Send a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            agent = init_agent()
            
            if agent is None:
                response = "Error: Agent not initialized. Please check your provider configuration."
                st.error(response)
            else:
                try:
                    async def get_response():
                        return await agent.process_direct(
                            prompt, 
                            session_key=st.session_state.session_id
                        )
                    
                    response = asyncio.run(get_response())
                except Exception as e:
                    response = f"Error: {str(e)}"
                    st.error(response)
            
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")
st.markdown("""
**Commands:**
- `/new` - Start a new conversation
- `/help` - Show available commands
""")