"""Setup page - Initialize and onboard nanobot."""

import streamlit as st
from pathlib import Path
import sys
import json

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title("Setup & Onboarding")
st.markdown("Initialize nanobot configuration and workspace")

try:
    from nanobot.config.loader import load_config, save_config, get_config_path
    from nanobot.utils.helpers import get_workspace_path
    from nanobot.config.schema import Config
    from nanobot.providers.registry import PROVIDERS
    
    config_path = get_config_path()
    workspace = get_workspace_path()
    
    st.markdown(f"**Config path:** `{config_path}`")
    st.markdown(f"**Workspace path:** `{workspace}`")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuration Status")
        
        if config_path.exists():
            st.success("Config file exists")
            
            try:
                config = load_config()
                
                provider_name = config.get_provider_name()
                if provider_name:
                    st.success(f"Provider: {provider_name}")
                else:
                    st.warning("No provider configured")
                
                if workspace.exists():
                    st.success("Workspace exists")
                else:
                    st.warning("Workspace not created")
                
            except Exception as e:
                st.error(f"Error loading config: {e}")
        else:
            st.warning("Config file not found")
            st.info("Click 'Initialize Config' below to create it.")
    
    with col2:
        st.subheader("Quick Stats")
        
        if config_path.exists():
            config = load_config()
            
            providers_configured = sum(
                1 for spec in PROVIDERS 
                if getattr(config.providers, spec.name, None) and 
                getattr(config.providers, spec.name).api_key
            )
            
            channels_enabled = sum(
                1 for name, cfg in [
                    ("telegram", config.channels.telegram),
                    ("discord", config.channels.discord),
                    ("whatsapp", config.channels.whatsapp),
                    ("feishu", config.channels.feishu),
                    ("slack", config.channels.slack),
                    ("email", config.channels.email),
                    ("mochat", config.channels.mochat),
                    ("dingtalk", config.channels.dingtalk),
                    ("qq", config.channels.qq),
                ] if cfg.enabled
            )
            
            st.metric("Providers Configured", providers_configured)
            st.metric("Channels Enabled", channels_enabled)
            st.metric("Model", config.agents.defaults.model.split("/")[-1])
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Initialize", "Quick Setup", "Import/Export"])
    
    with tab1:
        st.subheader("Initialize Configuration")
        
        if config_path.exists():
            st.warning("Config already exists. Choose an action:")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Reset to Defaults", type="secondary"):
                    config = Config()
                    save_config(config)
                    st.success("Config reset to defaults!")
                    st.rerun()
            
            with col_b:
                if st.button("Refresh Config"):
                    config = load_config()
                    save_config(config)
                    st.success("Config refreshed (existing values preserved)!")
                    st.rerun()
        else:
            if st.button("Initialize New Config", type="primary"):
                config = Config()
                save_config(config)
                
                workspace.mkdir(parents=True, exist_ok=True)
                
                (workspace / "memory").mkdir(exist_ok=True)
                (workspace / "skills").mkdir(exist_ok=True)
                
                templates = {
                    "AGENTS.md": "# Agent Instructions\n\nYou are a helpful AI assistant. Be concise, accurate, and friendly.\n",
                    "SOUL.md": "# Soul\n\nI am nanobot, a lightweight AI assistant.\n",
                    "USER.md": "# User\n\nInformation about the user goes here.\n",
                    "memory/MEMORY.md": "# Long-term Memory\n\nImportant facts and preferences.\n",
                    "memory/HISTORY.md": "",
                }
                
                for filename, content in templates.items():
                    file_path = workspace / filename
                    if not file_path.exists():
                        file_path.write_text(content)
                
                st.success("Configuration initialized!")
                st.rerun()
    
    with tab2:
        st.subheader("Quick Setup Wizard")
        st.markdown("Quickly configure the essential settings.")
        
        st.markdown("### 1. Provider")
        
        provider_options = {spec.label: spec.name for spec in PROVIDERS if not spec.is_oauth}
        selected_provider = st.selectbox("Select Provider", list(provider_options.keys()))
        provider_name_selected = provider_options[selected_provider]
        
        api_key = st.text_input("API Key", type="password")
        
        st.markdown("### 2. Model")
        
        default_model = st.text_input("Default Model", value="anthropic/claude-opus-4-5")
        
        st.markdown("### 3. Workspace")
        
        custom_workspace = st.text_input(
            "Custom Workspace Path (optional)", 
            value="",
            placeholder="~/.nanobot/workspace"
        )
        
        if st.button("Apply Quick Setup", type="primary"):
            if not api_key:
                st.error("API key is required")
            else:
                config = load_config() if config_path.exists() else Config()
                
                p = getattr(config.providers, provider_name_selected)
                p.api_key = api_key
                
                config.agents.defaults.model = default_model
                
                if custom_workspace:
                    config.agents.defaults.workspace = custom_workspace
                
                save_config(config)
                
                ws = Path(custom_workspace) if custom_workspace else workspace
                ws.mkdir(parents=True, exist_ok=True)
                (ws / "memory").mkdir(exist_ok=True)
                (ws / "skills").mkdir(exist_ok=True)
                
                st.success("Quick setup complete!")
                st.rerun()
    
    with tab3:
        st.subheader("Import/Export Configuration")
        
        col_imp, col_exp = st.columns(2)
        
        with col_exp:
            st.markdown("### Export")
            
            if config_path.exists():
                config = load_config()
                config_json = json.dumps(config.model_dump(by_alias=True), indent=2)
                
                st.download_button(
                    "Download config.json",
                    config_json,
                    file_name="nanobot_config.json",
                    mime="application/json"
                )
            else:
                st.info("No config to export")
        
        with col_imp:
            st.markdown("### Import")
            
            uploaded_file = st.file_uploader("Upload config.json", type=["json"])
            
            if uploaded_file is not None:
                try:
                    data = json.load(uploaded_file)
                    
                    st.json(data)
                    
                    if st.button("Import Configuration"):
                        config = Config.model_validate(data)
                        save_config(config)
                        st.success("Configuration imported!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Invalid config file: {e}")
    
    st.markdown("---")
    
    st.markdown("""
    **Next Steps:**
    1. Configure your API key in the **Providers** page
    2. Optionally enable channels in the **Channels** page
    3. Start the gateway from the **Gateway** page (or run `nanobot gateway`)
    4. Chat with your assistant in the **Chat** page
    
    **CLI Commands:**
    ```
    nanobot onboard          # Initialize config
    nanobot status           # Show status
    nanobot agent -m "..."   # Single message
    nanobot agent            # Interactive chat
    nanobot gateway          # Start gateway server
    ```
    """)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed.")