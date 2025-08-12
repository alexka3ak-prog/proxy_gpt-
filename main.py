
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

STOP_WORDS = ["пока", "стоп", "хватит", "выход", "до свидания"]

def ask_llm(prompt: str) -> str:
    api_url = os.getenv("OPENAI_PROXY_URL", "https://openrouter.ai/api/v1/chat/completions")
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return "Мяу... Ключ API не настроен. Попроси человека добавить OPENAI_API_KEY."

    model = "openai/gpt-3.5-turbo" if "openrouter.ai" in api_url else "gpt-3.5-turbo"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if "openrouter.ai" in api_url:
        headers["HTTP-Referer"] = os.getenv("PUBLIC_REFERER", "https://example.com")
        headers["X-Title"] = os.getenv("APP_TITLE", "Yandex Cat Skill")

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Отвечай кратко и дружелюбно, как кот-ассистент. В начале ответа избегай лишних междометий."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        r = requests.post(api_url, headers=headers, json=data, timeout=15)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.HTTPError as e:
        try:
            body = e.response.json()
        except Exception:
            body = e.response.text if e.response is not None else ""
        return f"Мяу... LLM ответил ошибкой {e.response.status_code}. {body}"
    except Exception as e:
        return f"Мяу... не могу связаться с моделью: {e}"

@app.post("/")
async def handle(request: Request):
    event = await request.json()
    req = event.get("request", {})

    command = (req.get("command") or "").strip()
    original = (req.get("original_utterance") or "").strip()

    print(">> command:", command, "| original:", original)

    if not command:
        text = "Привет! Я кот-ассистент. Спроси меня о чём угодно."
    elif any(w in command.lower() for w in STOP_WORDS):
        return JSONResponse({
            "version": event.get("version", "1.0"),
            "response": {"text": "Мяу! До встречи!", "tts": "Мяу! До встречи!", "end_session": True}
        })
    else:
        text = ask_llm(command)

    tts = f"Мяу! Кот подсказывает: {text}"

    response = {
        "version": event.get("version", "1.0"),
        "response": {
            "text": text,
            "tts": tts,
            "end_session": False
        }
    }
    print("<< response:", response)
    return JSONResponse(response)
