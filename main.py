import os
import requests
import random
from fastapi import FastAPI
from pydantic import BaseModel

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openai/gpt-3.5-turbo"

SOUNDS = [
    '<speaker audio="alice-sounds-game-win-1.opus"/>',
    '<speaker audio="alice-sounds-things-bell-1.opus"/>',
    '<speaker audio="alice-sounds-game-lose-2.opus"/>',
    ''
]

app = FastAPI()

class AliceRequest(BaseModel):
    request: dict
    version: str

def build_tts(text: str) -> str:
    sound = random.choice(SOUNDS)
    return f'<speak>{sound}<break time="0.5s"/>{text}</speak>'

@app.post("/")
async def handle_request(alice_request: AliceRequest):
    command = alice_request.request.get("command", "").strip()

    if not command:
        text = "Привет! Я готов ответить на твой вопрос."
    else:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": command}],
                "max_tokens": 150,
                "temperature": 0.7
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            text = "Не удалось получить ответ. Попробуй позже."

    return {
        "version": alice_request.version,
        "response": {
            "text": text,
            "tts": build_tts(text),
            "end_session": False
        }
    }
