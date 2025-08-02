import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from openai import RateLimitError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class AliceRequest(BaseModel):
    request: dict
    version: str

@app.post("/")
async def chat_with_gpt(alice_request: AliceRequest):
    command = alice_request.request.get("command", "").strip()

    if not command:
        text = "Привет! Я готов ответить на твой вопрос."
    else:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": command}],
                max_tokens=150,
                temperature=0.7
            )
            text = response.choices[0].message.content.strip()
        except RateLimitError:
            time.sleep(2)
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": command}],
                    max_tokens=150,
                    temperature=0.7
                )
                text = response.choices[0].message.content.strip()
            except Exception:
                text = "[Ошибка]: Слишком много запросов. Попробуй позже."
        except Exception:
            text = "[Ошибка]: Невозможно получить ответ."

    return {
        "version": alice_request.version,
        "response": {
            "text": text,
            "end_session": False
        }
    }
