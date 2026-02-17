# Nanobot Streamlit UI

A full-featured web interface for the Nanobot AI Assistant framework.

## Overview

This Streamlit-based UI provides complete control over all nanobot functionality through a modern web interface. It covers configuration, channels, providers, scheduling, memory, skills, sessions, and real-time chat with the AI agent.

## Quick Start

```bash
cd nanobot
pip install -r streamlit_requirements.txt
python start_ui.py
```

Or run directly:
```bash
streamlit run streamlit_app/app.py --server.port 8858
```

Open **http://localhost:8858** in your browser.

---

## Pages & Features

### 🏠 Setup & Onboarding

| Feature | Description |
|---------|-------------|
| Initialize Config | Create new configuration file with default values |
| Quick Setup Wizard | Fast configuration of provider, API key, and model |
| Import/Export | Download/upload config.json files |
| Configuration Status | View config/workspace status and quick stats |
| Reset/Refresh | Reset to defaults or refresh preserving values |

### 📊 Dashboard

| Feature | Description |
|---------|-------------|
| System Overview | Config, workspace, model, and settings metrics |
| Provider Status Table | All 16+ providers with configuration status |
| Channel Status Table | All 9 channels with enabled/allow-list info |
| Scheduled Jobs | Recent cron jobs with next run times |
| Recent Sessions | Latest conversation sessions |

### 💬 Chat

| Feature | Description |
|---------|-------------|
| Direct Agent Chat | Real-time conversation with the AI assistant |
| Session Management | Custom session IDs, clear/new session buttons |
| Message History | Persistent chat history in sidebar |
| Model/Provider Display | Shows active model and provider |
| Async Response | Streaming agent responses with spinner |

### 🔌 Providers

| Feature | Description |
|---------|-------------|
| Default Model Config | Set and auto-detect default model |
| API Gateways Section | OpenRouter, AiHubMix, Custom endpoint |
| Standard Providers | Anthropic, OpenAI, DeepSeek, Gemini, etc. |
| OAuth Providers | OpenAI Codex, GitHub Copilot info |
| Local Deployments | vLLM configuration with custom base URL |
| Provider Registry | Full list of supported providers with details |
| API Key Management | Secure password fields for all keys |
| Custom Base URLs | Override default API endpoints |

**Supported Providers:**
- OpenRouter, AiHubMix (Gateways)
- Anthropic, OpenAI, DeepSeek, Gemini
- Zhipu, DashScope (Qwen), Moonshot (Kimi)
- MiniMax, Groq, vLLM (Local)
- OpenAI Codex, GitHub Copilot (OAuth)

### 📡 Channels

Configure 9 chat platform integrations:

| Channel | Features |
|---------|----------|
| **Telegram** | Bot token, proxy, allow-list |
| **Discord** | Bot token, gateway URL, intents |
| **WhatsApp** | Bridge URL, QR code login, Node.js bridge |
| **Feishu** | App ID/Secret, encrypt key, verification token |
| **Slack** | Socket mode, bot/app tokens, DM/group policies |
| **Email** | IMAP receive, SMTP send, auto-reply, poll interval |
| **Mochat** | Socket.IO connection, sessions, panels |
| **DingTalk** | Client ID/Secret, Stream mode |
| **QQ** | App ID/Secret |

Each channel includes:
- Enable/disable toggle
- Allow-list for user access control
- Platform-specific settings
- Setup instructions

### ⏰ Cron Jobs

| Feature | Description |
|---------|-------------|
| Job List | View all scheduled jobs with status |
| Create Jobs | Add new scheduled tasks |
| Schedule Types | Interval, Cron expression, One-time |
| Timezone Support | IANA timezone for cron expressions |
| Delivery Options | Send response to specific channel/recipient |
| Job Actions | Run now, enable/disable, delete |
| Job Details | Next run, last status, error messages |

**Schedule Types:**
- **Interval**: Run every N seconds
- **Cron Expression**: Standard cron format (e.g., `0 9 * * *`)
- **One-time**: Run once at specific datetime

### 🧠 Memory

| Feature | Description |
|---------|-------------|
| Long-term Memory | View MEMORY.md content |
| History Log | View/search HISTORY.md |
| Memory Editor | Edit long-term memory directly |
| Append History | Add entries to history log |
| Statistics | File existence and line counts |
| File Info | Location, size, last modified |

**Two-Layer Memory System:**
- **MEMORY.md**: Long-term facts, preferences, context
- **HISTORY.md**: Append-only event log (grep-searchable)

### 🎯 Skills

| Feature | Description |
|---------|-------------|
| Available Skills | List all built-in and workspace skills |
| Skill Details | Description, availability, requirements |
| Create Skill | Make new custom skills with frontmatter |
| Always-Loaded Skills | Skills always in agent context |
| SKILL.md Viewer | View skill content |
| Requirements Check | CLI bins and env vars validation |

**Built-in Skills:**
- memory, cron, github, weather
- summarize, tmux, clawhub, skill-creator

### 📝 Sessions

| Feature | Description |
|---------|-------------|
| Sessions List | All conversation sessions |
| Session Details | Messages, consolidation status |
| Conversation History | Filter by role (user/assistant) |
| Export Session | JSON or Markdown download |
| Clear/Delete | Remove session messages or file |
| Tools Used | See which tools were called |

**Session Features:**
- Keyed by `channel:chat_id` format
- JSONL format for persistence
- Messages are append-only
- Auto-consolidation into memory

### 🔧 Tools Configuration

| Tab | Features |
|-----|----------|
| **Agent Defaults** | Model, max tokens, temperature, iterations, memory window, workspace |
| **Web Search** | Brave Search API key, max results |
| **Shell Execution** | Command timeout |
| **MCP Servers** | Add/remove MCP servers (Stdio or HTTP) |
| **Security** | Restrict to workspace, gateway host/port |

**MCP Server Types:**
- **Stdio**: Command with args and env vars
- **HTTP**: URL endpoint

### 📁 Workspace

| Feature | Description |
|---------|-------------|
| AGENTS.md Editor | Agent instructions/behavior |
| SOUL.md Editor | Agent personality and values |
| USER.md Editor | User information and preferences |
| HEARTBEAT.md Editor | Periodic tasks (checked every 30m) |
| File Management | Save, reset to default, download |
| Directory Browser | Skills and memory directories |

**Template Files:**
- AGENTS.md - Agent behavior instructions
- SOUL.md - Agent personality
- USER.md - User context
- HEARTBEAT.md - Periodic tasks

### 🚀 Gateway Control

| Feature | Description |
|---------|-------------|
| Start/Stop Gateway | Control the main gateway server |
| Gateway Status | Running/stopped indicator |
| Live Logs | Real-time gateway output |
| Channel Status Table | All channels with enable status |
| Server Metrics | Host, port, cron job count |

**Gateway Features:**
- Starts all enabled channels
- Runs agent message loop
- Executes cron jobs
- Heartbeat service (30 min interval)

### 🛠️ Agent Tools

View all available tools the agent can use:

| Category | Tools |
|----------|-------|
| **Filesystem** | read_file, write_file, edit_file, list_dir |
| **Shell** | exec (with safety guards) |
| **Web** | web_search, web_fetch |
| **Communication** | message |
| **Agent** | spawn (background subagents) |
| **Scheduling** | cron |
| **MCP** | mcp (Model Context Protocol) |

**Safety Features:**
- Path traversal protection
- Dangerous command blocking
- Command timeout
- Output truncation
- Workspace restriction option

---

## Sidebar Features

The sidebar provides quick status at all times:
- Active provider name
- Current model
- Enabled channels list

---

## Technical Details

### File Structure

```
nanobot/
├── streamlit_app/
│   ├── __init__.py
│   ├── app.py                    # Main app with navigation
│   └── pages/
│       ├── __init__.py
│       ├── 0_Setup.py            # Setup & Onboarding
│       ├── 1_Dashboard.py        # System Overview
│       ├── 2_Chat.py             # Agent Chat
│       ├── 3_Providers.py        # LLM Providers
│       ├── 4_Channels.py         # Chat Channels
│       ├── 5_Cron.py             # Scheduled Jobs
│       ├── 6_Memory.py           # Agent Memory
│       ├── 7_Skills.py           # Agent Skills
│       ├── 8_Sessions.py         # Conversation Sessions
│       ├── 9_Tools.py            # Tools Configuration
│       ├── 10_Workspace.py       # Workspace Files
│       ├── 11_Gateway.py         # Gateway Control
│       └── 12_Agent_Tools.py     # Available Tools
├── streamlit_requirements.txt    # Dependencies
├── start_ui.py                   # Launch script
└── run_streamlit.bat             # Windows batch file
```

### Dependencies

- streamlit >= 1.28.0
- litellm >= 1.0.0
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- loguru >= 0.7.0
- httpx >= 0.25.0
- croniter >= 2.0.0
- json-repair >= 0.7.0

### Integration with Nanobot

The UI directly imports and uses nanobot's Python modules:
- `nanobot.config.loader` - Configuration management
- `nanobot.agent.loop` - Agent loop for chat
- `nanobot.cron.service` - Cron job management
- `nanobot.session.manager` - Session storage
- `nanobot.agent.memory` - Memory store
- `nanobot.agent.skills` - Skills loader
- `nanobot.providers.registry` - Provider info

---

## CLI Equivalents

| UI Page | CLI Command |
|---------|-------------|
| Setup | `nanobot onboard` |
| Status | `nanobot status` |
| Chat | `nanobot agent` |
| Gateway | `nanobot gateway` |
| Cron List | `nanobot cron list` |
| Cron Add | `nanobot cron add` |
| Channels Status | `nanobot channels status` |
| Provider Login | `nanobot provider login openai-codex` |

---

## Configuration File

All settings are stored in `~/.nanobot/config.json`:

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "maxTokens": 8192,
      "temperature": 0.7,
      "maxToolIterations": 20,
      "memoryWindow": 50,
      "workspace": "~/.nanobot/workspace"
    }
  },
  "providers": {
    "openrouter": { "apiKey": "sk-or-..." },
    "anthropic": { "apiKey": "sk-ant-..." }
  },
  "channels": {
    "telegram": { "enabled": true, "token": "..." }
  },
  "tools": {
    "web": { "search": { "apiKey": "..." } },
    "exec": { "timeout": 60 },
    "restrictToWorkspace": false,
    "mcpServers": {}
  },
  "gateway": { "host": "0.0.0.0", "port": 18790 }
}
```

---

## License

Same as nanobot (MIT License).

---

## Links

- **Nanobot GitHub**: https://github.com/HKUDS/nanobot
- **Streamlit Docs**: https://docs.streamlit.io