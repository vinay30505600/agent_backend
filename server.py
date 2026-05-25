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

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import uuid

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="devops_agent", session_service=session_service)

@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name="devops_agent", user_id="user", session_id=session_id)

    message = Content(role="user", parts=[Part(text=req.message)])
    response_text = ""

    async for event in runner.run_async(user_id="user", session_id=session_id, new_message=message):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    return {"response": response_text}
