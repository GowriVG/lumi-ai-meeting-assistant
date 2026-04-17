import logging
from memory.session_store import store_meeting, get_meeting, update_summary, add_qa
from services.retrieval_service import store_embeddings
from services.openai_service import summarize_meeting, ask_question
from exceptions.custom_exceptions import MeetingNotFoundError, PromptValidationError

logger = logging.getLogger(__name__)


def clean_transcript(text: str):
    return (
        text.replace("\n", " ")
            .replace("\r", " ")
            .replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
            .strip()
    )


def load_meeting_service(meeting_id: str, transcript: str):
    logger.info(f"Loading meeting: {meeting_id}")
    if len(transcript) > 20000:
        raise PromptValidationError("Transcript too large")
    
    if not transcript or transcript.strip() == "":
       raise PromptValidationError("Transcript cannot be empty")
     
    cleaned = clean_transcript(transcript)

    store_meeting(meeting_id, cleaned)
    store_embeddings(meeting_id, cleaned)
    logger.warning(f"Meeting not found: {meeting_id}")

    return {
        "status": "success",
        
        "message": "Transcript loaded successfully"
    }

def summarize_service(meeting_id: str):
    logger.info(f"Summarizing meeting: {meeting_id}")
    meeting = get_meeting(meeting_id)

    if not meeting:
        raise MeetingNotFoundError("Meeting not found")

    if not meeting.get("transcript"):
        raise PromptValidationError("Transcript is empty")

    summary = summarize_meeting(meeting["transcript"])
    update_summary(meeting_id, summary)
    logger.info(f"Summary generated for meeting: {meeting_id}")

    return {"summary": summary}


def ask_service(meeting_id: str, question: str):
    logger.info(f"Question received for {meeting_id}: {question}")
    meeting = get_meeting(meeting_id)

    if not meeting:
        logger.warning(f"Meeting not found: {meeting_id}")
        raise MeetingNotFoundError("Meeting not found")

    answer = ask_question(meeting_id, meeting["transcript"], question)
    add_qa(meeting_id, question, answer)
    logger.info(f"Answer generated for {meeting_id}: {answer}")

    return {"answer": answer}


def get_meeting_service(meeting_id: str):
    meeting = get_meeting(meeting_id)

    if not meeting:
        raise MeetingNotFoundError("Meeting not found")

    return meeting