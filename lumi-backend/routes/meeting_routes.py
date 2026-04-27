from fastapi import APIRouter
from logger import logger
from fastapi import Depends
from auth.api_key import verify_api_key
from models.request_models import TranscriptRequest, QuestionRequest
from services.meeting_service import (
    load_meeting_service,
    summarize_service,
    ask_service,
    get_meeting_service
)

router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

@router.post("/load-meeting/{meeting_id}")
def load_meeting(meeting_id: str, request: TranscriptRequest):
    logger.info(f"API hit: load-meeting {meeting_id}")
    return load_meeting_service(meeting_id, request.transcript)


@router.post("/summarize/{meeting_id}")
def summarize(meeting_id: str):
    result = summarize_service(meeting_id)

    return {
        "status": "success",
        "data": result["summary"]
    }

@router.post("/ask/{meeting_id}")
def ask(meeting_id: str, request: QuestionRequest):
    result = ask_service(meeting_id, request.question)

    return {
        "status": "success",
        "data": result["answer"]
    }

@router.get("/meeting/{meeting_id}")
def get_meeting(meeting_id: str):
    result = get_meeting_service(meeting_id)

    return {
        "status": "success",
        "data": result
    }