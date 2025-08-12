from fastapi import FastAPI, Request
import os
import requests
import random

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY_URL = os.getenv("OPENAI_PROXY_URL", "https://api.openai.com/v1/chat/completions")

cat_phrases = [
    "Мяу! Чем могу помочь, человек?",
    "Мурр... расскажи мне что-нибудь интересное.",
    "Хвост трубой! Что спросишь сегодня?",
    "Мурлыкаю от радости тебя слышать!",
    "Мяу! Давай поболтаем!"
]

cat_sounds = [
    "Мяу-мяу!",
    "Муррр!",
    "Прыг на коленки!",
    "Шшш... я думаю...",
    "Хлоп-хлоп лапками!"
]

def ask_chatgpt(question: str) -> str:
    if not OPENAI_API_KEY:
        return random.choice(cat_phrases) + " " + random.choice(cat_sounds)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        r = requests.post(OPENAI_PROXY_URL, headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            return random.choice(cat_phrases) + " " + random.choice(cat_sounds)
    except Exception:
        return random.choice(cat_phrases) + " " + random.choice(cat_sounds)

@app.post("/")
async def handler(request: Request):
    body = await request.json()
    command = body.get("request", {}).get("command", "").strip()

    if not command:
        answer = random.choice(cat_phrases)
    else:
        answer = ask_chatgpt(command)

    response = {
        "version": body.get("version", "1.0"),
        "response": {
            "text": answer,
            "tts": answer,
            "end_session": False
        }
    }
    return response
