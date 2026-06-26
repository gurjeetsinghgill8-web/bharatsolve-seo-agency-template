<div align="center">

# 🚀 BHARATSOLVE SEO AGENCY

**Single Person AI-Powered SEO Agency — Fully Automated**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP-NAME.streamlit.app)
[![Made in India](https://img.shields.io/badge/Made%20in-India-🇮🇳-orange)](https://github.com/YOUR-USERNAME/bharatsolve-seo-agency)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🤖 देश का पहला AI SEO Agent जो आपकी पूरी SEO agency चलाएगा!

</div>

---

## ✨ Features

| Agent | Role | Status |
|-------|------|--------|
| 🤖 **Manager Agent** | Hinglish AI chat, task delegation, strategy | ✅ Active |
| 🔑 **Keyword Agent** | AI-powered keyword research & clustering | ✅ Active |
| 📝 **Content Agent** | SEO-optimized blogs, articles, schema markup | ✅ Active |
| 📊 **Rank Agent** | Keyword position tracking & insights | ✅ Active |
| 📱 **Social Agent** | Cross-platform social media content | ✅ Active |
| 📈 **Reports** | PDF report generation | ✅ Active |

### 🔜 Coming Soon
- 📸 Instagram auto-posting
- 📘 Facebook Page auto-posting
- 📧 Email newsletters & reports
- 📍 Google Business Profile integration
- ✈️ Telegram bot posting
- 🏠 PWA installable app

---

## 🚀 One-Click Deploy (No Coding)

### Option 1: Streamlit Cloud (FREE — Recommended)

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy)

1. **Fork this repo** on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"Deploy an app"**
4. Select your forked repo → branch `main` → file `app.py`
5. **Set secrets** (see below) → **Deploy!** ✅
6. Your app is live at: `https://YOUR-APP-NAME.streamlit.app`

### Option 2: Run Locally

```bash
# 1. Install Python 3.11 or 3.12
# 2. Clone & enter directory
git clone https://github.com/YOUR-USERNAME/bharatsolve-seo-agency.git
cd bharatsolve-seo-agency

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API keys (create .env file)
echo "GROQ_API_KEY=gsk_your_key_here" >> .env
echo "GEMINI_API_KEY=AIza_your_key_here" >> .env

# 5. Run!
streamlit run app.py
```

---

## 🔑 API Keys Setup

You need **free API keys** for the AI to work:

| Provider | How to Get | Cost |
|----------|-----------|------|
| **Groq** 🏆 (Recommended) | [console.groq.com](https://console.groq.com) | Free |
| **Gemini** | [aistudio.google.com](https://aistudio.google.com/apikey) | Free |

### Streamlit Cloud Secrets

1. In your deployed app dashboard → **Settings** → **Secrets**
2. Add these:

```toml
GROQ_API_KEY = "gsk_your_key_here"
GEMINI_API_KEY = "AIza_your_key_here"
OPENAI_API_KEY = ""  # optional
DEEPSEEK_API_KEY = ""  # optional
```

---

## 📁 Project Structure

```
bharatsolve-seo-agency/
├── app.py                  # Main entry point
├── config.json             # App configuration
├── requirements.txt        # Python dependencies
├── static/                 # PWA files
│   ├── manifest.json       # PWA manifest
│   └── sw.js               # Service worker
├── agents/                 # AI Agents
│   ├── manager_agent.py    # 🤖 Manager
│   ├── keyword_agent.py    # 🔑 Keyword Research
│   ├── content_agent.py    # 📝 Content Writer
│   ├── rank_agent.py       # 📊 Rank Tracker
│   └── social_agent.py     # 📱 Social Media
├── ui/                     # Streamlit UI Pages
│   ├── auth.py             # Login/Register
│   ├── dashboard.py        # Main dashboard
│   ├── clients.py          # Client management
│   ├── keywords.py         # Keywords page
│   ├── content.py          # Content page
│   ├── rankings.py         # Rankings page
│   ├── social.py           # Social media page
│   ├── reports.py          # Reports page
│   └── settings.py         # Settings page
├── db/                     # Database
│   ├── schema.py           # SQLite schema
│   └── operations.py       # CRUD operations
├── utils/                  # Utilities
│   ├── llm_client.py       # Multi-provider LLM client
│   └── helpers.py          # Helper functions
├── harness/                # Automation
│   ├── scheduler.py        # Task scheduler
│   └── auto_pilot.py       # Auto-pilot mode
├── secure_vault.py         # Encrypted key storage
├── .gitignore
└── README.md
```

---

## 💎 Subscription Plans

| Plan | Price | Clients | Features |
|------|-------|---------|----------|
| 🚀 **Freelancer** | ₹499/mo | 3 | Core agents |
| 💼 **Pro** | ₹1,499/mo | 10 | All agents |
| 🏢 **Agency** | ₹4,999/mo | Unlimited | White-label |
| 🏥 **Clinic** | ₹999/mo | 1 | Clinic SEO |
| 👑 **Lifetime** | ₹29,999 | Unlimited | Everything |

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────┐
│            BHARATSOLVE APP                   │
│          (Streamlit Frontend)                │
├─────────────────────────────────────────────┤
│  Manager Agent ◄──── User Chat (Hinglish)   │
├──────┬──────┬──────┬──────┬──────┬──────────┤
│Keyword│Content│Rank │Social│ Email│ Reports  │
│Agent  │Agent │Agent│Agent │Agent │ Generator│
├──────┴──────┴──────┴──────┴──────┴──────────┤
│           LLM Client (Multi-Provider)        │
│  Groq ◄── Gemini ◄── OpenAI ◄── DeepSeek    │
├─────────────────────────────────────────────┤
│           SQLite Database (seo_agency.db)    │
│  Users │ Clients │ Projects │ Keywords ...   │
└─────────────────────────────────────────────┘
```

---

## 🤝 Contributing

This is a single-person project, but suggestions are welcome! Open an issue or PR.

## 📜 License

MIT License — use freely, modify, and share.

---

<div align="center">
Made with ❤️ in India 🇮🇳
</div>
