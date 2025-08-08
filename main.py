
import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

SESSIONS_FILE = "sessions.json"
if os.path.exists(SESSIONS_FILE):
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        sessions = json.load(f)
else:
    sessions = {}

def save_sessions():
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def get_level(points):
    if points >= 30:
        return "кото-магистр 🧙‍♂️"
    elif points >= 20:
        return "кото-мастер"
    elif points >= 10:
        return "кото-ученик"
    else:
        return "котёнок"

def ask_openai(question: str) -> str:
    api_url = os.getenv("OPENAI_PROXY_URL", "https://openrouter.ai/api/v1/chat/completions")
    api_key = os.getenv("OPENAI_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7,
    }

    try:
        r = requests.post(api_url, headers=headers, json=data, timeout=10)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Мяу? Что-то пошло не так... ({e})"

@app.post("/")
async def handle(request: Request):
    event = await request.json()
    command = event.get("request", {}).get("command", "").lower().strip()
    session_key = event.get("session", {}).get("user_id", "default")

    if session_key not in sessions:
        sessions[session_key] = {"points": 0}
        save_sessions()

    response_text = "Мяу! Кот подсказывает: Привет! Можешь задать мне любой вопрос, мурр."

    if not command:
        response_text = "Мяу! Кот подсказывает: Привет! Можешь задать мне любой вопрос, мурр."
    elif "спасибо" in command:
        points = sessions[session_key].get("points", 0) + 1
        sessions[session_key]["points"] = points
        save_sessions()
        response_text = f"Мур-р! Обожаю вежливых людей! Тебе +1 балл! У тебя теперь {points} баллов."
    elif "баллов" in command or "очки" in command or "сколько" in command:
        points = sessions[session_key].get("points", 0)
        level = get_level(points)
        response_text = f"У тебя {points} баллов. Твой уровень: {level}."
    elif "сюрприз" in command:
        points = sessions[session_key].get("points", 0)
        if points >= 5:
            sessions[session_key]["points"] = points - 5
            save_sessions()
            response_text = "Ты получил виртуальную рыбку и обнимашки от кота! -5 баллов списано."
        else:
            response_text = "Недостаточно баллов для сюрприза. Нужно минимум 5."
    else:
        response_text = ask_openai(command)

    return JSONResponse({
        "version": "1.0",
        "response": {
            "text": response_text,
            "tts": response_text,
            "end_session": False
        }
    })
