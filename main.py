from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AliceRequest(BaseModel):
    request: dict
    version: str

@app.post("/")
async def test_skill(alice_request: AliceRequest):
    return {
        "version": alice_request.version,
        "response": {
            "text": "Привет! Это пидора ответ. Заебали меня уже!",
            "end_session": False
        }
    }
