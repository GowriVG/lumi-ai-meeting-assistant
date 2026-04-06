from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.ado_service import ADOService

from exceptions.custom_exceptions import (
    LumiBaseException, 
    OpenAIServiceError, 
    MeetingNotFoundError, 
    PromptValidationError
)

from models.request_models import TranscriptRequest, QuestionRequest
from services.openai_service import summarize_meeting, ask_question
from memory.session_store import store_meeting, get_meeting, update_summary, add_qa

app = FastAPI(title="LUMI AI Backend")
ado_service = ADOService()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL ERROR HANDLER ---
@app.exception_handler(LumiBaseException)
async def lumi_exception_handler(request: Request, exc: LumiBaseException):
    status_code = 500
    
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
    return {"message": "LUMI Backend Running"}

# --- LOAD MEETING (TEST / TEAMS ENTRY POINT) ---
@app.post("/load-meeting/{meeting_id}")
def load_meeting(meeting_id: str, request: TranscriptRequest):
    store_meeting(meeting_id, request.transcript)
    return {"message": "Meeting loaded successfully"}

# --- SUMMARIZE (FOR ADO PREVIEW) ---
@app.post("/summarize/{meeting_id}")
def summarize(meeting_id: str):

    meeting = get_meeting(meeting_id)

    # ✅ Auto-create meeting (for safety)
    if not meeting:
        store_meeting(meeting_id, "No transcript available yet.")
        meeting = get_meeting(meeting_id)

    # 🔥 Generate summary
    summary = summarize_meeting(meeting["transcript"])

    # 🔥 Store summary for later ADO sync
    update_summary(meeting_id, summary)

    return {"summary": summary}

# --- CHAT Q&A ---
@app.post("/ask/{meeting_id}")
def ask(meeting_id: str, request: QuestionRequest):

    meeting = get_meeting(meeting_id)

    # ✅ Auto-create if missing
    if not meeting:
        store_meeting(meeting_id, "No transcript available yet.")
        meeting = get_meeting(meeting_id)

    answer = ask_question(meeting["transcript"], request.question)

    add_qa(meeting_id, request.question, answer)

    return {"answer": answer}

# --- GET FULL MEETING STATE ---
@app.get("/meeting/{meeting_id}")
def get_meeting_details(meeting_id: str):

    meeting = get_meeting(meeting_id)

    # ✅ Auto-create (optional but recommended)
    if not meeting:
        store_meeting(meeting_id, "No transcript available yet.")
        meeting = get_meeting(meeting_id)

    return meeting

# --- SYNC TO AZURE DEVOPS ---
@app.post("/sync-to-ado/{meeting_id}")
async def sync_meeting_items(meeting_id: str):

    meeting = get_meeting(meeting_id)

    if not meeting:
        raise Exception("Meeting not found")

    summary = meeting.get("summary")

    if not summary:
        raise Exception("Summary not generated yet")

    action_items = summary.get("action_items", [])

    results = ado_service.sync_all_items(action_items)

    return {
        "status": "success",
        "synced_items": results
    }