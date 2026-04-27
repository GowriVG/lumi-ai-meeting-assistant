import json
from datetime import datetime
from services.blob_service import upload_text, download_text, blob_exists


# meeting_store = {}

# def store_meeting(meeting_id, transcript):
#     meeting_store[meeting_id] = {
#         "transcript": transcript,
#         "summary": None,
#         "qa_history": [],
#         "created_at": datetime.utcnow(),
#         "last_updated": datetime.utcnow()
#     }

# def get_meeting(meeting_id):
#     return meeting_store.get(meeting_id)

# def update_summary(meeting_id, summary):
#     if meeting_id in meeting_store:
#         meeting_store[meeting_id]["summary"] = summary
#         meeting_store[meeting_id]["last_updated"] = datetime.utcnow()

# def add_qa(meeting_id, question, answer):
#     if meeting_id in meeting_store:
#         meeting_store[meeting_id]["qa_history"].append({
#             "question": question,
#             "answer": answer,
#             "timestamp": datetime.utcnow()
#         })
#         meeting_store[meeting_id]["last_updated"] = datetime.utcnow()


def store_meeting(meeting_id, transcript):
    data = {
        "transcript": transcript,
        "summary": None,
        "qa_history": [],
        "created_at": str(datetime.utcnow()),
        "last_updated": str(datetime.utcnow())
    }

    upload_text(f"{meeting_id}/meeting.json", json.dumps(data))

def get_meeting(meeting_id):
    blob = f"{meeting_id}/meeting.json"

    if not blob_exists(blob):
        return None

    return json.loads(download_text(blob))

def update_summary(meeting_id, summary):
    data = get_meeting(meeting_id)

    if data:
        data["summary"] = summary
        upload_text(f"{meeting_id}/meeting.json", json.dumps(data))

def add_qa(meeting_id, question, answer):
    data = get_meeting(meeting_id)

    if data:
        data["qa_history"].append({
            "question": question,
            "answer": answer
        })

        upload_text(f"{meeting_id}/meeting.json", json.dumps(data))