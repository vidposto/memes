# 😂 Telegram Meme Bot

> A Python bot that automatically posts memes to a Telegram channel every 6 hours — sourced from Reddit or AI-generated, with zero human intervention.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203.3-orange)
![Telegram](https://img.shields.io/badge/Platform-Telegram-2CA5E0)
![Reddit](https://img.shields.io/badge/Source-Reddit-FF4500)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ What It Does

Every 6 hours, the bot automatically picks one of two modes at random:

| Mode | Chance | How |
|------|--------|-----|
| 🤖 AI Generated | 50% | Groq writes funny text → fetches relevant image → draws meme with Pillow |
| 📥 Reddit Meme | 50% | Fetches a real viral meme from top Reddit posts |

If Reddit fails for any reason, the bot automatically falls back to AI generation.

---

## 🤖 AI Meme Topics

```
😴 Monday morning struggle       💻 Programmer life
🐛 When you finally fix the bug  💪 Gym motivation fails
🧾 Adulting problems              📹 Online meetings
🥗 Eating healthy vs junk food   🌙 Sleeping late
😰 Social anxiety                 ☕ Coffee addiction
📚 Student life                   🏠 Working from home
📱 Checking phone every 5 mins   🤯 Overthinking everything
📡 When the wifi goes down        🎭 Pretending to be busy
📅 Waiting for the weekend        💸 Trying to save money
```

---

## 📥 Reddit Sources

```
r/memes              r/dankmemes
r/funny              r/me_irl
r/AdviceAnimals      r/wholesomememes
r/terriblefacebookmemes
```

Only fetches posts with score > 500, images only, SFW.

---

## 📁 Project Structure

```
telegram-meme-bot/
│
├── main.py                  ← Entry point + 6-hour scheduler
├── requirements.txt         ← Python dependencies
├── nixpacks.toml            ← Railway build config
├── Procfile                 ← Railway start command
├── .gitignore
├── README.md
│
└── src/
    ├── __init__.py
    ├── pipeline.py          ← Orchestrates AI vs Reddit choice
    ├── meme_generator.py    ← AI meme: Groq + image + Pillow text
    ├── reddit_fetcher.py    ← Fetches viral memes from Reddit
    ├── telegram_poster.py   ← Posts to Telegram channel
    ├── cleanup.py           ← Temp file cleanup
    └── logger.py            ← Logging setup
```

---

## 🔑 Required API Keys

| Service | Purpose | Link | Cost |
|---------|---------|------|------|
| Groq | AI meme text generation | [groq.com](https://groq.com) | Free |
| Pexels | Meme background images | [pexels.com/api](https://pexels.com/api) | Free |
| Pixabay | Meme background images | [pixabay.com/api](https://pixabay.com/api/docs) | Free |
| Unsplash | Meme background images | [unsplash.com/developers](https://unsplash.com/developers) | Free |
| Telegram Bot | Posting to channel | [t.me/BotFather](https://t.me/BotFather) | Free |
| Reddit | Real memes (no key needed) | Public JSON API | Free |

---

## 🚀 Deploy on Railway

### 1. Create a Telegram Bot

- Open [@BotFather](https://t.me/BotFather) on Telegram
- Send `/newbot` and follow the steps
- Copy the bot token
- Add the bot as **admin** in your channel with "Post Messages" permission

### 2. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/USERNAME/telegram-meme-bot.git
git push -u origin main
```

### 3. Connect to Railway

Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub** → select your repo

### 4. Add Environment Variables

Go to **Variables** → **RAW Editor** → paste:

```env
GROQ_API_KEY=your_groq_key
PEXELS_API_KEY=your_pexels_key
PIXABAY_API_KEY=your_pixabay_key
UNSPLASH_ACCESS_KEY=your_unsplash_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
```

### 5. Set Service Type

**Settings** → Service Type → **Worker**

### 6. Deploy ✅

---

## ⚙️ Customization

### Change Post Frequency

In `main.py`:
```python
INTERVAL_HOURS = 6   # every 6 hours (default)
INTERVAL_HOURS = 12  # every 12 hours
INTERVAL_HOURS = 3   # every 3 hours
```

### Change AI vs Reddit Ratio

In `src/pipeline.py`:
```python
# Default: 50/50
source_type = random.choice(["ai", "reddit"])

# Always AI:
source_type = "ai"

# Always Reddit:
source_type = "reddit"
```

### Add More Meme Topics

In `src/meme_generator.py`:
```python
MEME_TOPICS = [
    "monday morning struggle",
    "your new topic here",  # add here
]
```

### Add More Reddit Subreddits

In `src/reddit_fetcher.py`:
```python
SUBREDDITS = [
    "memes",
    "your_subreddit",  # add here
]
```

---

## 📊 Expected Output

| Metric | Value |
|--------|-------|
| Posts per day | 4 |
| Posts per month | ~120 |
| AI memes | ~50% |
| Reddit memes | ~50% |
| Language | English |
| Automation | 100% |

---

## 🐛 Troubleshooting

**Bot not posting to channel**
→ Make sure the bot is added as **admin** in the channel with "Post Messages" permission

**Reddit memes not loading**
→ Reddit may be rate-limiting — bot falls back to AI automatically

**Font looks bad on meme**
→ DejaVu fonts are installed via `nixpacks.toml` on Railway automatically

**"Chat not found" error**
→ Double check `TELEGRAM_CHANNEL_ID` format — use numeric ID for private channels (e.g. `-1002081951501`)

---

## 📄 License

MIT — free to use, modify, and deploy.
