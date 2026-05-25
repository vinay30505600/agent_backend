from fastapi import FastAPI
from pydantic import BaseModel

# Import your root agent from agent.py
from agent import root_agent

# Create FastAPI server
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body structure
class ChatRequest(BaseModel):
    message: str

# Test route
@app.get("/")
def home():
    return {
        "status": "running"
    }

# Chat endpoint
@app.post("/chat")
async def chat(req: ChatRequest):

    result = await root_agent.run(req.message)
    response = result.text

    return {
        "response": response
    }
