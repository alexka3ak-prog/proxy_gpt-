import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openai/gpt-4-turbo"

app = FastAPI()

class AliceRequest(BaseModel):
    request: dict
    version: str

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
            "end_session": False
        }
    }
