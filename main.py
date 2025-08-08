
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Загружаем сессии
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

@app.post("/")
async def handle(request: Request):
    event = await request.json()
    command = event.get("request", {}).get("command", "").lower()
    session_key = event.get("session", {}).get("user_id", "default")

    if session_key not in sessions:
        sessions[session_key] = {"points": 0}
        save_sessions()

    response_text = "Мяу! Кот подсказывает: Привет! Можешь задать мне любой вопрос, мурр."

    if "спасибо" in command:
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

    return JSONResponse({
        "version": "1.0",
        "response": {
            "text": response_text,
            "tts": response_text,
            "end_session": False
        }
    })
