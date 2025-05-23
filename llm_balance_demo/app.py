from fastapi import FastAPI
from pydantic import BaseModel
from openai_handler import chat_with_gpt

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    prompt: str

@app.post("/chat")
def chat(request: ChatRequest):
    response = chat_with_gpt(request.prompt, request.user_id)
    return {"response": response}
