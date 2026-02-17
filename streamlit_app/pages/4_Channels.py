"""Channels page - Configure chat channels."""

import streamlit as st
from pathlib import Path
import sys

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Channels")
st.markdown("Configure chat channels to connect your AI assistant to messaging platforms")

try:
    from nanobot.config.loader import load_config, save_config
    from nanobot.config.schema import (
        TelegramConfig, DiscordConfig, WhatsAppConfig,
        FeishuConfig, SlackConfig, EmailConfig,
        MochatConfig, DingTalkConfig, QQConfig
    )
    
    config = load_config()
    
    tab_telegram, tab_discord, tab_whatsapp, tab_feishu, tab_slack, tab_email, tab_mochat, tab_dingtalk, tab_qq = st.tabs([
        "Telegram", "Discord", "WhatsApp", "Feishu", "Slack", "Email", "Mochat", "DingTalk", "QQ"
    ])
    
    def render_allow_list(allow_from):
        st.markdown("**Allow List** (User IDs/usernames allowed to interact)")
        allow_text = st.text_area(
            "Allowed users (one per line)",
            value="\n".join(allow_from),
            height=100,
            help="Leave empty for public access, or list allowed user IDs/usernames"
        )
        return [x.strip() for x in allow_text.split("\n") if x.strip()]
    
    with tab_telegram:
        st.subheader("Telegram Configuration")
        st.markdown("Connect via Telegram Bot API. Get your bot token from [@BotFather](https://t.me/BotFather).")
        
        tg = config.channels.telegram
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=tg.enabled)
            token = st.text_input("Bot Token", value=tg.token, type="password")
            proxy = st.text_input("Proxy URL (optional)", value=tg.proxy or "", placeholder="http://127.0.0.1:7890")
        
        with col2:
            allow_from = render_allow_list(tg.allow_from)
        
        if st.button("Save Telegram Config", key="save_telegram"):
            config.channels.telegram = TelegramConfig(
                enabled=enabled,
                token=token,
                allow_from=allow_from,
                proxy=proxy or None
            )
            save_config(config)
            st.success("Telegram configuration saved!")
        
        st.markdown("""
        **Setup Instructions:**
        1. Create a bot via [@BotFather](https://t.me/BotFather) and get the token
        2. Paste the token above
        3. Optionally add allowed user IDs to restrict access
        4. Enable the channel and restart the gateway
        """)
    
    with tab_discord:
        st.subheader("Discord Configuration")
        st.markdown("Connect via Discord Gateway WebSocket.")
        
        dc = config.channels.discord
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=dc.enabled)
            token = st.text_input("Bot Token", value=dc.token, type="password")
        
        with col2:
            gateway_url = st.text_input("Gateway URL", value=dc.gateway_url)
            intents = st.number_input("Intents", value=dc.intents, help="Discord gateway intents bitmask")
            allow_from = render_allow_list(dc.allow_from)
        
        if st.button("Save Discord Config", key="save_discord"):
            config.channels.discord = DiscordConfig(
                enabled=enabled,
                token=token,
                allow_from=allow_from,
                gateway_url=gateway_url,
                intents=intents
            )
            save_config(config)
            st.success("Discord configuration saved!")
        
        st.markdown("""
        **Setup Instructions:**
        1. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications)
        2. Enable Message Content Intent
        3. Copy the bot token and paste above
        4. Invite the bot to your server with appropriate permissions
        """)
    
    with tab_whatsapp:
        st.subheader("WhatsApp Configuration")
        st.markdown("Connect via WhatsApp Web bridge (requires Node.js).")
        
        wa = config.channels.whatsapp
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=wa.enabled)
            bridge_url = st.text_input("Bridge URL", value=wa.bridge_url)
            bridge_token = st.text_input("Bridge Token (optional)", value=wa.bridge_token, type="password")
        
        with col2:
            allow_from = render_allow_list(wa.allow_from)
        
        if st.button("Save WhatsApp Config", key="save_whatsapp"):
            config.channels.whatsapp = WhatsAppConfig(
                enabled=enabled,
                bridge_url=bridge_url,
                bridge_token=bridge_token,
                allow_from=allow_from
            )
            save_config(config)
            st.success("WhatsApp configuration saved!")
        
        st.markdown("""
        **Setup Instructions:**
        1. Run `nanobot channels login` to start the bridge and scan QR code
        2. The bridge connects to WhatsApp Web via Node.js
        3. Set a bridge_token for additional security (optional)
        """)
    
    with tab_feishu:
        st.subheader("Feishu/Lark Configuration")
        st.markdown("Connect via Feishu Open Platform WebSocket.")
        
        fs = config.channels.feishu
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=fs.enabled)
            app_id = st.text_input("App ID", value=fs.app_id)
            app_secret = st.text_input("App Secret", value=fs.app_secret, type="password")
        
        with col2:
            encrypt_key = st.text_input("Encrypt Key (optional)", value=fs.encrypt_key)
            verification_token = st.text_input("Verification Token (optional)", value=fs.verification_token)
            allow_from = render_allow_list(fs.allow_from)
        
        if st.button("Save Feishu Config", key="save_feishu"):
            config.channels.feishu = FeishuConfig(
                enabled=enabled,
                app_id=app_id,
                app_secret=app_secret,
                encrypt_key=encrypt_key,
                verification_token=verification_token,
                allow_from=allow_from
            )
            save_config(config)
            st.success("Feishu configuration saved!")
    
    with tab_slack:
        st.subheader("Slack Configuration")
        st.markdown("Connect via Slack Socket Mode (no public endpoint needed).")
        
        slack = config.channels.slack
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=slack.enabled)
            mode = st.selectbox("Mode", ["socket"], index=0)
            bot_token = st.text_input("Bot Token (xoxb-...)", value=slack.bot_token, type="password")
            app_token = st.text_input("App Token (xapp-...)", value=slack.app_token, type="password")
        
        with col2:
            group_policy = st.selectbox(
                "Group Policy",
                ["mention", "open", "allowlist"],
                index=["mention", "open", "allowlist"].index(slack.group_policy)
            )
            dm_enabled = st.checkbox("DM Enabled", value=slack.dm.enabled)
            dm_policy = st.selectbox("DM Policy", ["open", "allowlist"], index=0 if slack.dm.policy == "open" else 1)
            
            dm_allow_from = st.text_area(
                "DM Allow List",
                value="\n".join(slack.dm.allow_from),
                height=50
            ).split("\n")
            dm_allow_from = [x.strip() for x in dm_allow_from if x.strip()]
        
        if st.button("Save Slack Config", key="save_slack"):
            from nanobot.config.schema import SlackDMConfig
            config.channels.slack = SlackConfig(
                enabled=enabled,
                mode=mode,
                bot_token=bot_token,
                app_token=app_token,
                group_policy=group_policy,
                dm=SlackDMConfig(
                    enabled=dm_enabled,
                    policy=dm_policy,
                    allow_from=dm_allow_from
                )
            )
            save_config(config)
            st.success("Slack configuration saved!")
        
        st.markdown("""
        **Setup Instructions:**
        1. Create a Slack App in the [API Console](https://api.slack.com/apps)
        2. Enable Socket Mode
        3. Add the `connections:write` scope
        4. Install to workspace and get bot token (xoxb-...) and app token (xapp-...)
        """)
    
    with tab_email:
        st.subheader("Email Configuration")
        st.markdown("Connect via IMAP (receive) and SMTP (send).")
        
        em = config.channels.email
        
        col1, col2 = st.columns(2)
        
        with col1:
            enabled = st.checkbox("Enabled", value=em.enabled)
            consent = st.checkbox("Consent Granted", value=em.consent_granted, help="Explicit permission to access mailbox")
            
            st.markdown("**IMAP Settings**")
            imap_host = st.text_input("IMAP Host", value=em.imap_host)
            imap_port = st.number_input("IMAP Port", value=em.imap_port)
            imap_username = st.text_input("IMAP Username", value=em.imap_username)
            imap_password = st.text_input("IMAP Password", value=em.imap_password, type="password")
            imap_use_ssl = st.checkbox("Use SSL", value=em.imap_use_ssl)
            imap_mailbox = st.text_input("Mailbox", value=em.imap_mailbox)
        
        with col2:
            st.markdown("**SMTP Settings**")
            smtp_host = st.text_input("SMTP Host", value=em.smtp_host)
            smtp_port = st.number_input("SMTP Port", value=em.smtp_port)
            smtp_username = st.text_input("SMTP Username", value=em.smtp_username)
            smtp_password = st.text_input("SMTP Password", value=em.smtp_password, type="password")
            smtp_use_tls = st.checkbox("Use TLS", value=em.smtp_use_tls)
            from_address = st.text_input("From Address", value=em.from_address)
            
            st.markdown("**Behavior**")
            auto_reply = st.checkbox("Auto Reply", value=em.auto_reply_enabled)
            poll_interval = st.number_input("Poll Interval (seconds)", value=em.poll_interval_seconds)
        
        if st.button("Save Email Config", key="save_email"):
            config.channels.email = EmailConfig(
                enabled=enabled,
                consent_granted=consent,
                imap_host=imap_host,
                imap_port=imap_port,
                imap_username=imap_username,
                imap_password=imap_password,
                imap_use_ssl=imap_use_ssl,
                imap_mailbox=imap_mailbox,
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                smtp_username=smtp_username,
                smtp_password=smtp_password,
                smtp_use_tls=smtp_use_tls,
                from_address=from_address,
                auto_reply_enabled=auto_reply,
                poll_interval_seconds=poll_interval,
                allow_from=config.channels.email.allow_from
            )
            save_config(config)
            st.success("Email configuration saved!")
    
    with tab_mochat:
        st.subheader("Mochat Configuration")
        
        mc = config.channels.mochat
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=mc.enabled)
            base_url = st.text_input("Base URL", value=mc.base_url)
            socket_url = st.text_input("Socket URL", value=mc.socket_url)
            claw_token = st.text_input("Claw Token", value=mc.claw_token, type="password")
        
        with col2:
            agent_user_id = st.text_input("Agent User ID", value=mc.agent_user_id)
            sessions = st.text_area("Sessions", value="\n".join(mc.sessions), height=50)
            panels = st.text_area("Panels", value="\n".join(mc.panels), height=50)
            allow_from = render_allow_list(mc.allow_from)
        
        if st.button("Save Mochat Config", key="save_mochat"):
            config.channels.mochat = MochatConfig(
                enabled=enabled,
                base_url=base_url,
                socket_url=socket_url,
                claw_token=claw_token,
                agent_user_id=agent_user_id,
                sessions=[x.strip() for x in sessions.split("\n") if x.strip()],
                panels=[x.strip() for x in panels.split("\n") if x.strip()],
                allow_from=allow_from
            )
            save_config(config)
            st.success("Mochat configuration saved!")
    
    with tab_dingtalk:
        st.subheader("DingTalk Configuration")
        
        dt = config.channels.dingtalk
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=dt.enabled)
            client_id = st.text_input("Client ID (AppKey)", value=dt.client_id)
            client_secret = st.text_input("Client Secret (AppSecret)", value=dt.client_secret, type="password")
        
        with col2:
            allow_from = render_allow_list(dt.allow_from)
        
        if st.button("Save DingTalk Config", key="save_dingtalk"):
            config.channels.dingtalk = DingTalkConfig(
                enabled=enabled,
                client_id=client_id,
                client_secret=client_secret,
                allow_from=allow_from
            )
            save_config(config)
            st.success("DingTalk configuration saved!")
    
    with tab_qq:
        st.subheader("QQ Configuration")
        
        qq = config.channels.qq
        
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.checkbox("Enabled", value=qq.enabled)
            app_id = st.text_input("App ID", value=qq.app_id)
            secret = st.text_input("Secret", value=qq.secret, type="password")
        
        with col2:
            allow_from = render_allow_list(qq.allow_from)
        
        if st.button("Save QQ Config", key="save_qq"):
            config.channels.qq = QQConfig(
                enabled=enabled,
                app_id=app_id,
                secret=secret,
                allow_from=allow_from
            )
            save_config(config)
            st.success("QQ configuration saved!")
    
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")