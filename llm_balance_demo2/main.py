from fastapi import FastAPI
from pydantic import BaseModel
from agent_handler import chat_with_agent

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    prompt: str

@app.post("/agent/chat")
def chat(request: ChatRequest):
    response = chat_with_agent(request.prompt, request.user_id)
    return {"response": response}
