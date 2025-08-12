
import os
import logging
import requests
from fastapi import FastAPI, Request

app = FastAPI()

logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY_URL = os.getenv("OPENAI_PROXY_URL", "https://api.openai.com/v1/chat/completions")

def cat_fallback():
    return "Мяу! Я кот-ассистент, но у меня нет доступа к ChatGPT. Задай мне что-нибудь простое!"

def ask_chatgpt(question: str) -> str:
    if not OPENAI_API_KEY:
        return cat_fallback()
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo" if "openai.com" in OPENAI_PROXY_URL else "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 200,
            "temperature": 0.7
        }
        # Helpful headers for OpenRouter (ignored by OpenAI)
        if "openrouter.ai" in OPENAI_PROXY_URL:
            headers["HTTP-Referer"] = os.getenv("PUBLIC_REFERER", "https://example.com")
            headers["X-Title"] = os.getenv("APP_TITLE", "Yandex Cat Skill")

        resp = requests.post(OPENAI_PROXY_URL, headers=headers, json=data, timeout=15)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        else:
            logging.error(f"OpenAI-like API error {resp.status_code}: {resp.text}")
            return cat_fallback()
    except Exception as e:
        logging.exception("Exception while calling LLM")
        return cat_fallback()

@app.post("/")
async def yandex_handler(request: Request):
    event = await request.json()
    command = (event.get("request", {}) or {}).get("command", "") or ""

    if not command.strip():
        text = "Привет! Я кот-ассистент. Задай мне вопрос, и я постараюсь ответить."
    else:
        text = ask_chatgpt(command.strip())

    logging.info(f"Ответ Алисе: {text}")

    return {
        "version": event.get("version", "1.0"),
        "response": {
            "text": text,
            "tts": text,
            "end_session": False
        }
    }
