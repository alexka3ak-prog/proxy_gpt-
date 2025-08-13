
import os
import time
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_PROXY_URL = os.getenv("OPENAI_PROXY_URL", "").strip() or "https://api.openai.com/v1/chat/completions"

def ask_chatgpt(prompt: str):
    if not OPENAI_API_KEY:
        return "Ключ API не настроен. Попроси человека добавить OPENAI_API_KEY."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    retries = 3
    for attempt in range(retries):
        try:
            resp = requests.post(
                OPENAI_PROXY_URL,
                headers=headers,
                json=data,
                timeout=45
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            elif resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            else:
                return f"Ошибка LLM: {resp.status_code} {resp.text}"
        except requests.exceptions.ReadTimeout:
            time.sleep(2 ** attempt)
            continue
        except Exception as e:
            return f"Ошибка запроса: {e}"

    return "Сервис LLM не ответил после нескольких попыток."

@app.get("/health")
def health():
    return {"status": "ok", "mode": "openrouter" if "openrouter" in OPENAI_PROXY_URL else "openai"}

@app.get("/debug")
def debug():
    return {
        "proxy_url": OPENAI_PROXY_URL,
        "api_key_set": bool(OPENAI_API_KEY),
        "mode": "openrouter" if "openrouter" in OPENAI_PROXY_URL else "openai"
    }

@app.post("/")
async def main_handler(request: Request):
    body = await request.json()
    command = body.get("request", {}).get("command", "").lower()
    answer = ask_chatgpt(command)
    return JSONResponse(content={
        "version": "1.0",
        "response": {
            "text": answer,
            "tts": answer,
            "end_session": False
        }
    })
