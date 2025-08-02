import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI, RateLimitError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class AliceRequest(BaseModel):
    request: dict
    version: str

@app.post("/")
async def chat_with_gpt(alice_request: AliceRequest):
    command = alice_request.request.get("command", "").strip()
    print(f"[Команда от Алисы]: {command}")

    if not command:
        text = "Привет! Я готов ответить на твой вопрос."
    else:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": command}],
                max_tokens=50,
                temperature=0.5
            )
            text = response.choices[0].message.content.strip()
            print(f"[Ответ GPT]: {text}")
        except RateLimitError:
            print("[Ошибка]: Превышен лимит запросов (429)")
            text = "Слишком много запросов. Попробуй позже."
        except Exception as e:
            print(f"[Ошибка OpenAI]: {str(e)}")
            text = "Что-то пошло не так. Попробуй позже."

    return {
        "version": alice_request.version,
        "response": {
            "text": text,
            "end_session": False
