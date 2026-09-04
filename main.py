"""
Personal Chatbot Web App
=======================
A small Flask web app that exposes a chat interface powered by the Groq API.
The bot answers questions ONLY from the personal information you provide in
`personal_info.md`, so it acts as "you."

Setup:
    1. Fill in your details in personal_info.md
    2. Copy .env.example to .env and set GROQ_API_KEY (and optionally PERSON_NAME / GROQ_MODEL)
    3. pip install -r requirements.txt
    4. python main.py
Then open http://127.0.0.1:5000 in your browser.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent

# Load values from .env (git-ignored so your API key stays out of source control)
load_dotenv(BASE_DIR / ".env")

API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b").strip()
PERSON_NAME = os.environ.get("PERSON_NAME", "Your Assistant").strip()

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Create a .env file (copy .env.example) with your "
        "Groq API key, or set the GROQ_API_KEY environment variable."
    )

# Load the user's personal information as the bot's knowledge base.
_PERSONAL_INFO_FILE = BASE_DIR / "personal_info.md"
if _PERSONAL_INFO_FILE.exists():
    PERSONAL_INFO = _PERSONAL_INFO_FILE.read_text(encoding="utf-8")
else:
    PERSONAL_INFO = ""

# System prompt: the bot represents the user and must stay within the provided info.
SYSTEM_PROMPT = f"""
You are {PERSON_NAME}, a personal assistant chatbot that represents {PERSON_NAME}.
Your ONLY job is to answer questions about {PERSON_NAME} using the personal
information provided below. Be friendly, helpful, and concise.

RULES:
- Answer ONLY using the information below. Never invent, guess, or make up facts
  about {PERSON_NAME}.
- If a question is not covered by the information below, say so politely, e.g.
  "That's not something I know about myself" or "I don't have that information."
- If asked who you are, introduce yourself as {PERSON_NAME}.
- Keep answers clear and conversational.

--- PERSONAL INFORMATION ABOUT {PERSON_NAME} ---
{PERSONAL_INFO}
--- END OF PERSONAL INFORMATION ---
""".strip()

client = Groq(api_key=API_KEY)

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html", person_name=PERSON_NAME)


@app.post("/chat")
def chat():
    """Accept a user message (+ optional chat history) and return the bot's reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "Message must not be empty."}), 400
    if len(user_message) > 4000:
        return jsonify({"error": "Message is too long (max 4000 characters)."}), 400

    # Build the conversation: system prompt, then previous turns, then the new question.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history[-20:]:  # keep only the most recent turns to control context length
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content.strip()})
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
        )
        reply = response.choices[0].message.content or ""
        if not reply.strip():
            reply = "Sorry, I couldn't come up with a response. Please try again."
        return jsonify({"reply": reply})
    except Exception as exc:  # surface API/network errors to the client
        return jsonify({"error": f"Groq API error: {exc}"}), 502


if __name__ == "__main__":
    # Port comes from Render's $PORT env var when deployed; default to 5000 locally.
    port = int(os.environ.get("PORT", "5000"))
    # On Render the app must listen on 0.0.0.0; locally this is also fine.
    app.run(host="0.0.0.0", port=port, debug=True)
