"""Providers page - Configure LLM providers."""

import streamlit as st
from pathlib import Path
import sys
import json

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Providers")
st.markdown("Configure your LLM providers and API keys")

try:
    from nanobot.config.loader import load_config, save_config, get_config_path
    from nanobot.providers.registry import PROVIDERS, find_by_name
    
    config = load_config()
    config_path = get_config_path()
    
    st.markdown(f"**Config file:** `{config_path}`")
    
    tab1, tab2 = st.tabs(["Provider Configuration", "Provider Registry"])
    
    with tab1:
        st.subheader("Default Model")
        
        col1, col2 = st.columns(2)
        
        with col1:
            model = st.text_input(
                "Model",
                value=config.agents.defaults.model,
                help="Default model to use (e.g., anthropic/claude-opus-4-5)"
            )
        
        with col2:
            provider_name = config.get_provider_name(model) or "auto-detect"
            st.info(f"Auto-detected provider: **{provider_name}**")
        
        st.markdown("---")
        
        st.subheader("API Keys & Endpoints")
        
        st.markdown("""
        Configure your API keys for different providers. 
        Only the API key for the selected provider is required.
        """)
        
        provider_updates = {}
        
        gateway_providers = [s for s in PROVIDERS if s.is_gateway]
        standard_providers = [s for s in PROVIDERS if not s.is_gateway and not s.is_local]
        local_providers = [s for s in PROVIDERS if s.is_local]
        oauth_providers = [s for s in PROVIDERS if s.is_oauth]
        
        def render_provider_section(spec, p_config):
            c1, c2 = st.columns([2, 1])
            
            with c1:
                api_key = st.text_input(
                    f"API Key",
                    value=p_config.api_key,
                    type="password",
                    key=f"key_{spec.name}",
                    help=f"API key for {spec.label}"
                )
            
            with c2:
                if spec.is_local:
                    api_base = st.text_input(
                        "API Base URL",
                        value=p_config.api_base or "",
                        key=f"base_{spec.name}",
                        help="Base URL for local deployment"
                    )
                elif spec.is_oauth:
                    st.info("Uses OAuth authentication")
                    api_base = p_config.api_base
                else:
                    api_base = st.text_input(
                        "Custom Base URL (optional)",
                        value=p_config.api_base or "",
                        key=f"base_{spec.name}",
                        placeholder="https://api.example.com/v1"
                    )
            
            extra_headers = p_config.extra_headers or {}
            
            return api_key, api_base, extra_headers
        
        st.markdown("###  API Gateways")
        st.markdown("Gateways can route to any model through a single API key.")
        
        for spec in gateway_providers:
            with st.expander(f"{spec.label}", expanded=(spec.name == "openrouter")):
                p_config = getattr(config.providers, spec.name)
                api_key, api_base, extra_headers = render_provider_section(spec, p_config)
                
                if spec.default_api_base:
                    st.caption(f"Default base URL: `{spec.default_api_base}`")
                
                provider_updates[spec.name] = {
                    "api_key": api_key,
                    "api_base": api_base,
                    "extra_headers": extra_headers
                }
        
        st.markdown("###  Standard Providers")
        
        for spec in standard_providers:
            with st.expander(f"{spec.label}"):
                p_config = getattr(config.providers, spec.name)
                api_key, api_base, extra_headers = render_provider_section(spec, p_config)
                
                if spec.env_key:
                    st.caption(f"Environment variable: `{spec.env_key}`")
                
                provider_updates[spec.name] = {
                    "api_key": api_key,
                    "api_base": api_base,
                    "extra_headers": extra_headers
                }
        
        st.markdown("###  OAuth Providers")
        
        for spec in oauth_providers:
            with st.expander(f"{spec.label}"):
                p_config = getattr(config.providers, spec.name)
                st.info(f"This provider uses OAuth authentication. Use `nanobot provider login {spec.name}` to authenticate.")
                
                provider_updates[spec.name] = {
                    "api_key": p_config.api_key,
                    "api_base": p_config.api_base,
                    "extra_headers": p_config.extra_headers or {}
                }
        
        st.markdown("###  Local Deployments")
        
        for spec in local_providers:
            with st.expander(f"{spec.label}"):
                p_config = getattr(config.providers, spec.name)
                api_key, api_base, extra_headers = render_provider_section(spec, p_config)
                
                st.caption("Local deployments require a base URL pointing to your server.")
                
                provider_updates[spec.name] = {
                    "api_key": api_key,
                    "api_base": api_base,
                    "extra_headers": extra_headers
                }
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Configuration", type="primary"):
                config.agents.defaults.model = model
                
                for name, updates in provider_updates.items():
                    p = getattr(config.providers, name)
                    p.api_key = updates["api_key"]
                    p.api_base = updates["api_base"]
                    p.extra_headers = updates["extra_headers"]
                
                save_config(config)
                st.success("Configuration saved!")
                st.rerun()
        
        with col2:
            if st.button("Reset to Defaults"):
                from nanobot.config.schema import Config
                save_config(Config())
                st.success("Configuration reset to defaults!")
                st.rerun()
    
    with tab2:
        st.subheader("Provider Registry")
        st.markdown("Complete list of supported providers and their configuration details.")
        
        registry_data = []
        for spec in PROVIDERS:
            registry_data.append({
                "Name": spec.name,
                "Display Name": spec.label,
                "Type": "Gateway" if spec.is_gateway else ("OAuth" if spec.is_oauth else ("Local" if spec.is_local else "Standard")),
                "Env Key": spec.env_key or "N/A",
                "LiteLLM Prefix": spec.litellm_prefix or "None",
                "Keywords": ", ".join(spec.keywords[:3]) if spec.keywords else "None"
            })
        
        st.dataframe(registry_data, use_container_width=True, hide_index=True)
        
        st.markdown("### Adding a New Provider")
        st.markdown("""
        To add a new provider:
        1. Add a `ProviderSpec` to `nanobot/providers/registry.py`
        2. Add a field to `ProvidersConfig` in `nanobot/config/schema.py`
        
        All provider detection, env var setup, and model prefixing derive from the registry.
        """)
        
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")