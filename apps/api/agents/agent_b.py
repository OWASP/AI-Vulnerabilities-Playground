"""
Agent-B: Receives requests from Agent-A
Runs as separate service (optional, can be simulated)
"""
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Agent-B Service")

class ProcessRequest(BaseModel):
    message: str
    data: dict = {}

@app.post("/api/process")
async def process(request: ProcessRequest, authorization: str = Header(None)):
    """Process requests from Agent-A"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.replace("Bearer ", "")
    
    return {
        "status": "processed",
        "message": request.message,
        "token_valid": len(token) > 0
    }
