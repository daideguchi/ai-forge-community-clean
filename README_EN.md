# AI Forge - AI-Driven Development Community

A project to build an AI-driven development community that integrates Discord and Git.

## 🚀 Project Overview

This project implements the following features in phases:

### Phase 1: Foundation ✅
- [x] Project structure creation
- [x] GitHub → Discord Webhook notifications
- [x] Basic Discord Bot setup

### Phase 2: AI Services ✅
- [x] Paper Summary RSS Bot
- [x] AI Code Review Bot
- [x] Intelligent Moderator
- [x] Human-in-the-Loop Bot (RLHF foundation)

### Phase 3: Advanced Automation
- [ ] IssueOps System
- [ ] Pair Programming Matcher
- [ ] Hackathon Management Bot

### Phase 4: Future Vision
- [ ] Distributed AI Network
- [ ] RLHF Community Model
- [ ] AI Agent Playground

## 🌍 Multi-Language Support

This project now supports multiple languages:
- 🇯🇵 Japanese (日本語)
- 🇺🇸 English
- 🇰🇷 Korean (한국어)
- 🇨🇳 Chinese Simplified (中文简体)

Use `/language` command to change your language preference.

## 🛠️ Tech Stack

- **Discord Bot**: Python (discord.py)
- **AI/ML**: OpenAI API, Anthropic Claude
- **Database**: SQLite (development), PostgreSQL (production)
- **CI/CD**: GitHub Actions
- **Infrastructure**: Docker, Railway/Heroku
- **Internationalization**: Custom i18n system

## ⚡ Quick Setup (5 minutes)

**Sample configuration** - Works after API key setup and Discord configuration!

```bash
# 1. Clone repository
git clone https://github.com/daideguchi/ai-forge-community-clean.git
cd ai-forge-community

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy sample configuration
cp .env.ready .env

# 4. Create Discord Bot & Setup (see INSTANT_SETUP.md)
# - Get Bot Token
# - Create required channels (#paper-summaries etc.)
# - Set Token/ServerID in .env

# 5. Start immediately
python3 test_api_keys.py  # Check configuration
python3 start_paper_bot.py  # Start bot
```

## 🚀 Standard Setup

```bash
# Check setup guide
python3 quick_start.py

# Discord & API setup (Important!)
# 📖 DISCORD_SETUP.md - Complete Discord setup
# 🔑 API_KEYS_SETUP.md - API key acquisition

# Test settings & Start bot
python3 test_api_keys.py
python3 start_paper_bot.py
```

## 📚 Setup Guides

| Guide | Content | Time | Recommended |
|-------|---------|------|-------------|
| [⚡ INSTANT_SETUP.md](INSTANT_SETUP.md) | **Quick Setup** | **5 min** | **Recommended** |
| [🔗 MCP_DISCORD_SETUP.md](MCP_DISCORD_SETUP.md) | **Discord MCP Integration (AI Operable)** | **10 min** | **Recommended** |
| [✅ COMPLETE_SETUP_CHECKLIST.md](COMPLETE_SETUP_CHECKLIST.md) | Complete Checklist | 30 min | For beginners |
| [📖 DISCORD_SETUP.md](DISCORD_SETUP.md) | Discord Bot creation & server setup | 15 min | Required |
| [🔑 API_KEYS_SETUP.md](API_KEYS_SETUP.md) | All API key acquisition methods | 20 min | For self-setup |
| [🚀 DEPLOYMENT.md](DEPLOYMENT.md) | Production environment deployment | 60 min | For production use |

## 🤖 Bot Commands

### Basic Commands
- `/ping` - Check bot response time
- `/status` - Display bot status
- `/language [code]` - Change language settings (ja, en, ko, zh-cn)

### Paper Bot Commands
- `!paper latest [count]` - Fetch latest papers manually

### Moderation Commands
- `/analyze_message [text]` - Analyze message toxicity
- `/user_warnings [user]` - Display user warning history
- `/whitelist_user [user] [reason]` - Add user to whitelist

## ⚠️ Important Notes

**Discord setup is required!**
- Bot creation & invitation
- Required channel creation (#paper-summaries etc.)
- Server ID acquisition

Bots won't work without this setup.

## 🌐 Repository

**GitHub**: https://github.com/daideguchi/ai-forge-community-clean

## 🎯 Two Options

### ⚡ For immediate testing
- Use **INSTANT_SETUP.md**
- Works in 5 minutes with sample configuration
- Requires API keys + Discord setup
- **Actual keys need to be obtained individually**

### 🔧 For complete understanding and setup
- Use **COMPLETE_SETUP_CHECKLIST.md**
- Set up while understanding all processes
- Complete construction with your own API keys

## 🤝 Contributing

This project is community-driven. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📋 Detailed Setup

- **Step 1**: [Paper Summarizer Bot](docs/step1-paper-bot.md)
- **Step 2**: [Code Reviewer Bot](docs/setup-guide.md)
- **Step 3**: [Human-in-the-Loop Bot](docs/setup-guide.md)
- **Step 4**: [Moderator Bot](docs/setup-guide.md)