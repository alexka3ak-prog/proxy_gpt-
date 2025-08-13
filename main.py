
import os
import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_PROXY_URL = os.getenv("OPENAI_PROXY_URL", "").strip() or "https://api.openai.com/v1/chat/completions"
OVERRIDE_MODEL = os.getenv("MODEL", "").strip()  # опционально можно указать модель руками

# --- HTTP session with retries ---
session = requests.Session()
retry = Retry(total=3, read=3, connect=3, backoff_factor=0.7,
              status_forcelist=[429, 500, 502, 503, 504],
              allowed_methods=["POST"])
session.mount("https://", HTTPAdapter(max_retries=retry))
session.mount("http://", HTTPAdapter(max_retries=retry))

def pick_model() -> str:
    if OVERRIDE_MODEL:
        return OVERRIDE_MODEL
    # Для OpenRouter требуется неймспейс 'openai/...'
    if "openrouter.ai" in OPENAI_PROXY_URL:
        return "openai/gpt-3.5-turbo"
    return "gpt-3.5-turbo"

def ask_chatgpt(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "Мяу! Ключ API не настроен. Добавь OPENAI_API_KEY."

    model = pick_model()
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    # Рекомендуемые заголовки для OpenRouter
    if "openrouter.ai" in OPENAI_PROXY_URL:
        headers["HTTP-Referer"] = os.getenv("PUBLIC_REFERER", "https://example.com")
        headers["X-Title"] = os.getenv("APP_TITLE", "Yandex Cat Skill")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 180
    }

    connect_timeout, read_timeout = 5, 45
    try:
        resp = session.post(OPENAI_PROXY_URL, headers=headers, json=payload,
                            timeout=(connect_timeout, read_timeout))
        if resp.status_code == 200:
            data = resp.json()
            # Параноидально проверим формат
            try:
                return data["choices"][0]["message"]["content"].strip()
            except Exception:
                logging.error("Unexpected LLM response format: %s", data)
                return "Мяу... Модель ответила в неожиданном формате."
        else:
            # Логи для диагностики 400/401/404 и пр.
            snippet = resp.text[:500]
            logging.error("LLM HTTP %s: %s", resp.status_code, snippet)
            # Частая причина 400 на OpenRouter — неправильное имя модели
            if resp.status_code == 400 and "openrouter.ai" in OPENAI_PROXY_URL:
                return "Мяу... Похоже, указанная модель не поддерживается на OpenRouter. Проверь MODEL/URL."
            return f"Мяу... LLM вернул ошибку {resp.status_code}. Попробуем позже."
    except requests.exceptions.ReadTimeout:
        logging.warning("LLM read timeout")
        return "Мяу... Сервер долго отвечает. Попробуем позже."
    except Exception as e:
        logging.exception("LLM call failed: %s", e)
        return "Мяу... Не удалось связаться с моделью."

@app.post("/")
async def yandex_alice(request: Request):
    data = await request.json()
    command = (data.get("request", {}) or {}).get("command", "") or ""
    command = command.strip()
    if not command:
        text = "Привет! Я кот-ассистент. Задай мне вопрос, и я постараюсь ответить."
    else:
        text = ask_chatgpt(command)

    resp = {
        "version": data.get("version", "1.0"),
        "response": {"text": text, "tts": text, "end_session": False}
    }
    logging.info("Ответ Алисе: %s", resp)
    return JSONResponse(resp)

@app.get("/health")
def health():
    mode = "openrouter" if "openrouter.ai" in OPENAI_PROXY_URL else "openai"
    return {"status": "ok", "mode": mode}

@app.get("/debug")
def debug():
    return {
        "proxy_url": OPENAI_PROXY_URL,
        "model": pick_model(),
        "using_openrouter": "openrouter.ai" in OPENAI_PROXY_URL,
        "api_key_set": bool(OPENAI_API_KEY)
    }
