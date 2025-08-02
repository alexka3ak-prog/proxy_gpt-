
import os
from fastapi import FastAPI
from pydantic import BaseModel
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class AliceRequest(BaseModel):
    request: dict
    version: str

@app.post("/")
async def chat_with_gpt(alice_request: AliceRequest):
    command = alice_request.request.get("command", "").strip()

    if not command:
        text = "Привет! Я готов ответить на твой вопрос. Что хочешь узнать?"
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": command}],
                max_tokens=200
            )
            text = response.choices[0].message.content.strip()
        except Exception as e:
            text = f"[Ошибка]: {str(e)}"

    return {
        "version": alice_request.version,
        "response": {
            "text": text,
            "end_session": False
        }
    }
