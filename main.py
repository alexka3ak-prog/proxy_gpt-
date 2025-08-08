
import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openai/gpt-3.5-turbo"

app = FastAPI()

# Контексты по session_id

sessions = {}
import threading

SESSIONS_FILE = "sessions.json"
lock = threading.Lock()

def load_sessions():
    global sessions
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            sessions.update(json.load(f))
    except FileNotFoundError:
        sessions = {}

def save_sessions():
    with lock:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False)

load_sessions()


# Режимы кота
MODES = {
    "весёлый": "😺 Мяу! С радостью подсказываю:",
    "ворчливый": "😾 Ну ладно... Слушай внимательно:",
    "сонный": "😴 Мрр... Сейчас попробую сказать...",
    "учёный": "🎩 Позволь проинформировать:",
    "базовый": "Мяу! Кот подсказывает:"
}

STOP_COMMANDS = ["пока", "стоп", "хватит", "до свидания", "выход"]

class AliceRequest(BaseModel):
    request: dict
    session: dict
    version: str

def build_tts(text: str, mode: str, command: str) -> str:
    prefix = MODES.get(mode, MODES["базовый"])
    repeat = f"Ты спросил: «{command}». "
    return f"{repeat}{prefix} {text}"

@app.post("/")
async def handle_request(alice_request: AliceRequest):
    command = alice_request.request.get("command", "").strip().lower()
    session_id = alice_request.session.get("session_id")
    user_id = alice_request.session.get("user_id")
    session_key = f"{user_id}_{session_id}"

    if session_key not in sessions:
        sessions[session_key] = {"mode": "базовый", "history": []}

    current_mode = sessions[session_key]["mode"]


    if "спасибо" in command:
        points = sessions[session_key].get("points", 0) + 1
        sessions[session_key]["points"] = points
save_sessions()

    if "сюрприз" in command:
        points = sessions[session_key].get("points", 0)
        if points >= 5:
            sessions[session_key]["points"] = points
save_sessions() - 5
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "🎁 Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "tts": "Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "end_session": False
                }
            }
        else:
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "У тебя пока недостаточно баллов для сюрприза. Нужно 5.",
                    "tts": "Недостаточно баллов для сюрприза. Нужно пять.",
                    "end_session": False
                }
            }


            "version": alice_request.version,
            "response": {
                "text": f"Мур-р! Обожаю вежливых людей! Тебе +1 балл! Всего: {points}",
                "tts": f"Мур-р! Обожаю вежливых людей! Тебе плюс один балл! Сейчас у тебя {points} баллов!",
                "end_session": False,
                "buttons": [{"title": "Сколько у меня баллов?"}]
            }
        }

    if "баллов" in command:
        points = sessions[session_key].get("points", 0)

    if "сюрприз" in command:
        points = sessions[session_key].get("points", 0)
        if points >= 5:
            sessions[session_key]["points"] = points
save_sessions() - 5
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "🎁 Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "tts": "Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "end_session": False
                }
            }
        else:
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "У тебя пока недостаточно баллов для сюрприза. Нужно 5.",
                    "tts": "Недостаточно баллов для сюрприза. Нужно пять.",
                    "end_session": False
                }
            }


            "version": alice_request.version,
            "response": {
                "text": f"У тебя {points} котобаллов. Мур-р!",

    "tts": f"У тебя {points} котобаллов. Мур-р!",
    "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
,
                "end_session": False
            }
        }

    if any(word in command for word in STOP_COMMANDS):


    if "сюрприз" in command:
        points = sessions[session_key].get("points", 0)
        if points >= 5:
            sessions[session_key]["points"] = points
save_sessions() - 5
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "🎁 Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "tts": "Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "end_session": False
                }
            }
        else:
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "У тебя пока недостаточно баллов для сюрприза. Нужно 5.",
                    "tts": "Недостаточно баллов для сюрприза. Нужно пять.",
                    "end_session": False
                }
            }


            "version": alice_request.version,

    "response": {
        "buttons": [{"title": "Поменять режим"}, {"title": "Сколько у меня баллов?"}],

                "text": "Мяу! До встречи, человек!",
                "tts": "Мяу! До встречи, человек!",
                "end_session": True
            }
        }

    for mode in MODES:
        if f"режим {mode}" in command or f"включи {mode}" in command:
            sessions[session_key]["mode"] = mode

    if "сюрприз" in command:
        points = sessions[session_key].get("points", 0)
        if points >= 5:
            sessions[session_key]["points"] = points
save_sessions() - 5
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "🎁 Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "tts": "Сюрприз! Ты получил виртуальную рыбку и обнимашки от кота!",
                    "end_session": False
                }
            }
        else:
            points = sessions[session_key].get("points", 0)
level = "котёнок"
if points >= 30:
    level = "Кото-магистр"
elif points >= 20:
    level = "Кото-мастер"
elif points >= 10:
    level = "Кото-ученик"
info = f"У тебя {points} котобаллов. Уровень — {level}."

return {
    "version": alice_request.version,
    "response": {
        "text": info,
        "tts": info,
        "end_session": False,
        "buttons": [{"title": "Сюрприз!"}] if points >= 5 else []
    }

                    "text": "У тебя пока недостаточно баллов для сюрприза. Нужно 5.",
                    "tts": "Недостаточно баллов для сюрприза. Нужно пять.",
                    "end_session": False
                }
            }


                "version": alice_request.version,

    "response": {
        "buttons": [{"title": "Поменять режим"}, {"title": "Сколько у меня баллов?"}],

                    "text": f"Кот переключился в режим «{mode}».",
                    "tts": f"Теперь я говорю как {mode} кот.",
                    "end_session": False
                }
            }

    if not command:
        text = "Привет! Можешь задать мне любой вопрос, мурр."
    else:
        try:
            history = sessions[session_key]["history"][-4:]  # последние 4 реплики
            messages = [{"role": "system", "content": "Отвечай как дружелюбный кот-ассистент."}]
            for turn in history:
                messages.append({"role": "user", "content": turn["user"]})
                messages.append({"role": "assistant", "content": turn["bot"]})
            messages.append({"role": "user", "content": command})

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": MODEL_NAME,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()

            sessions[session_key]["history"].append({"user": command, "bot": text})
save_sessions()

        except Exception:
            text = "Мяу... Что-то пошло не так. Попробуй ещё раз."

    json_response = {
        "version": alice_request.version,

    "response": {
        "buttons": [{"title": "Поменять режим"}, {"title": "Сколько у меня баллов?"}],

            "text": text,
            "tts": build_tts(text, sessions[session_key]["mode"], command),
            "end_session": False
        }
    }

    print("Ответ Алисе:", json_response)
    return json_response
