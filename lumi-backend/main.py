from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.ado_service import ADOService
from pydantic import BaseModel
from typing import List, Optional
from exceptions.custom_exceptions import (
    LumiBaseException, 
    OpenAIServiceError, 
    MeetingNotFoundError, 
    PromptValidationError
)
from models.request_models import TranscriptRequest, QuestionRequest
from services.openai_service import summarize_meeting, ask_question
from memory.session_store import store_meeting, get_meeting, update_summary, add_qa
from routes.meeting_routes import router as meeting_router
from routes.ado_routes import router as ado_router

from logger import logger
logger.info("LUMI Backend started successfully")

app = FastAPI(title="LUMI AI Backend")
logger.info("LUMI Backend initialized")

ado_service = ADOService()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://teams.microsoft.com",
        "http://localhost:4200",
        "https://a1strlumi01t.z19.web.core.windows.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WorkItem(BaseModel):
    title: str
    description: str
    type: str
    priority: Optional[str] = None
    story_points: Optional[int] = None
    owner: Optional[str] = None

# --- GLOBAL ERROR HANDLER ---
@app.exception_handler(LumiBaseException)
async def lumi_exception_handler(request: Request, exc: LumiBaseException):
    status_code = 500
    logger.error(f"Error occurred: {str(exc)}", exc_info=True)
    
    if isinstance(exc, MeetingNotFoundError):
        status_code = 404
    elif isinstance(exc, PromptValidationError):
        status_code = 422
    elif isinstance(exc, OpenAIServiceError):
        status_code = 502

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "type": exc.__class__.__name__,
            "message": str(exc)
        }
    )

# --- ROOT ---
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message": "LUMI Backend Running"}

# HEALTH CHECK
@app.get("/health")
def health():
    logger.info("Health check OK")
    return {"status": "ok"}

app.include_router(meeting_router)
app.include_router(ado_router)



