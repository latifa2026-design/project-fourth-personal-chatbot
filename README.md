# Personal Chatbot Web App

A run-local chatbot that represents **you**. People ask it questions and it answers
**only** from the information you put in `personal_info.md`, powered by the
[Groq API](https://console.groq.com) and served by Flask.

## Features

- Chat web UI served locally at `http://127.0.0.1:5000`
- Answers only from **your** information (never invents facts)
- Remembers conversation context within a session
- Simple, clean, mobile-friendly interface

## Requirements

- Python 3.9+ (tested on 3.12)
- A [Groq API key](https://console.groq.com/keys)

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your personal info (this is the bot's knowledge base)
#    edit personal_info.md

# 3. Configure secrets — copy the example then fill in your key
copy .env.example .env
#    edit .env and set GROQ_API_KEY=your_key_here
```

## Run

```bash
python main.py
```

Open http://127.0.0.1:5000 in your browser.

The variables you can configure in `.env`:

| Variable       | Purpose                                       | Default               |
|----------------|-----------------------------------------------|-----------------------|
| `GROQ_API_KEY` | Your Groq API key (**required**)             | —                     |
| `GROQ_MODEL`   | The Groq model to use                        | `openai/gpt-oss-20b`  |
| `PERSON_NAME`  | Name the bot introduces itself with          | `Your Assistant`      |

## Security note

Your API key lives in `.env`, which is listed in `.gitignore` so it won't be
committed. If your key was ever shared or leaked, regenerate it in the
[Groq dashboard](https://console.groq.com/keys).

> ⚠️ This server is bound to `127.0.0.1` (local only). Do not expose it publicly
> unless you add authentication, because anyone who can reach it can use your
> API key through this app.