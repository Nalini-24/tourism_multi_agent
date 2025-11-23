# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from agents.parent_agent import build_response

app = FastAPI(title="Tourism Multi-Agent API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_methods=["*"],
   allow_headers=["*"],
)




@app.get("/plan")
def plan_trip(input: str = Query(..., description="User input text")):
    result = build_response(input)

    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return {
        "message": result["message"],
        "data": result["data"]
    }

@app.get("/")
def root():
    return {"message": "Use POST /plan with {'input': 'your question'}"}
