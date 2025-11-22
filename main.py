# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.parent_agent import build_response

app = FastAPI(title="Tourism Multi-Agent API")

class RequestBody(BaseModel):
    input: str

@app.post("/plan")
def plan_trip(req: RequestBody):
    result = build_response(req.input)

    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return {
        "message": result["message"],
        "data": result["data"]
    }

@app.get("/")
def root():
    return {"message": "Use POST /plan with {'input': 'your question'}"}
