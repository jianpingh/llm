from fastapi import FastAPI
from pydantic import BaseModel
from agent_executor import agent_executor

app = FastAPI()

class AgentRequest(BaseModel):
    prompt: str

@app.post("/agent/run")
def run_agent(req: AgentRequest):
    response = agent_executor.run(req.prompt)
    return {"response": response}
