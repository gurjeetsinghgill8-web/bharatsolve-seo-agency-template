# 🚀 Deploy BHARATSOLVE to Streamlit Cloud (FREE)

## Step 1: Get Free API Keys

### Gemini API Key (REQUIRED - for AI content/reviews/blogs)
1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account (gurjeetsinghgill8@gmail.com)
3. Click **"Create API Key"**
4. Copy the key (looks like: `AIzaSy...`)

### Groq API Key (OPTIONAL - faster/free alternative)
1. Go to https://console.groq.com/keys
2. Sign in with Google
3. Click **"Create API Key"**
4. Copy the key

---

## Step 2: Deploy on Streamlit Cloud

### On Mobile (Android Chrome) or Desktop:
1. Open **https://share.streamlit.io**
2. Click **"Sign in with GitHub"** → Login as `gurjeetsinghgill8-web`
3. Click **"Create app"** (blue button top-right)
4. Fill the form:
   ```
   Repository: gurjeetsinghgill8-web/bharatsolve-seo-agency-template
   Branch:     master
   Main file:  app.py
   App URL:    bharatsolve-seo-agency-template.streamlit.app
   ```
5. Click **⚙️ Advanced settings**
   - Python version: **3.11**
6. ⚠️ DON'T CLICK DEPLOY YET — First set up secrets below!

---

## Step 3: Add API Keys (Secrets)

On the same page, click **"Secrets"** tab (or after creating, go to App Settings → Secrets).

Paste this — replace `YOUR_GEMINI_KEY` with your actual Gemini API key:

```toml
# ── AI Models ──
GEMINI_API_KEY = "YOUR_GEMINI_KEY"

# ── Optional: Groq (faster + free) ──
GROQ_API_KEY = ""

# ── GitHub Blog Auto-Publishing (optional) ──
GITHUB_TOKEN = ""

# ── Google Business Profile (optional — for auto-reviews) ──
GOOGLE_BUSINESS_TOKEN = ""
GOOGLE_BUSINESS_ACCOUNT = ""
GOOGLE_BUSINESS_LOCATION = ""
```

**Minimum required**: Just `GEMINI_API_KEY` — Everything else is optional!

Click **"Save"**

---

## Step 4: DEPLOY! 🚀

Click the orange **"Deploy!"** button.

Wait 2-3 minutes for build. Then your app is live at:

👉 **https://bharatsolve-seo-agency-template.streamlit.app**

Open this URL on your Android phone Chrome browser!

---

## Step 5: First Login

1. The app opens on the **Login/Register** page
2. Click **"Register"** tab
3. Create your account:
   - Username: `drgill`
   - Password: (anything you want)
   - Full Name: `Dr. Gurjeet Singh Gill`
   - Email: `gurjeetsinghgill8@gmail.com`
4. Click Register → Login
5. You'll see the **🏥 Gill Clinic Command Center** homepage!

---

## 📱 Using on Android Phone

- Open Chrome → Go to your app URL
- Tap ⋮ (3 dots menu) → **"Add to Home Screen"**
- Now it works like a mobile app! 📲
- PWA install already configured (installable app icon)

---

## ⚠️ Important: Auto-Pilot & Sleep

Streamlit Cloud **free tier sleeps after inactivity** (few hours).

**Solution to keep auto-pilot running 24/7:**
1. Go to https://uptimerobot.com (free account)
2. Add a monitor → HTTP(s) → Your app URL
3. Set check every 5 minutes
4. This "pings" your app, keeping it awake + triggers auto-pilot tasks!

OR upgrade to Streamlit Cloud **Starter plan** (~₹1,500/month for always-on).

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| App shows error | Check Secrets — Gemini API key is required |
| Blank page | Refresh, wait for cold start (~30 sec) |
| Auto-pilot not working | App sleeping — use UptimeRobot pinger |
| Blog not publishing | Add GITHUB_TOKEN in Secrets |

Need help? Ask BHARATSOLVE support or reply here!
