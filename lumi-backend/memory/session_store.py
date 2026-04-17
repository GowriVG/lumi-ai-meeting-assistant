from datetime import datetime

meeting_store = {}

def store_meeting(meeting_id, transcript):
    meeting_store[meeting_id] = {
        "transcript": transcript,
        "summary": None,
        "qa_history": [],
        "created_at": datetime.utcnow(),
        "last_updated": datetime.utcnow()
    }

def get_meeting(meeting_id):
    return meeting_store.get(meeting_id)

def update_summary(meeting_id, summary):
    if meeting_id in meeting_store:
        meeting_store[meeting_id]["summary"] = summary
        meeting_store[meeting_id]["last_updated"] = datetime.utcnow()

def add_qa(meeting_id, question, answer):
    if meeting_id in meeting_store:
        meeting_store[meeting_id]["qa_history"].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow()
        })
        meeting_store[meeting_id]["last_updated"] = datetime.utcnow()